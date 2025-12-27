#include "kde_connect_client.h"
#include <iostream>
#include <sstream>
#include <cstring>
#include <chrono>
#include <thread>
#include <random>
#include <iomanip>
#include <sstream>

// For UDP communication
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

// For JSON handling
#include <nlohmann/json.hpp>

namespace gamepad_mapper {

using json = nlohmann::json;

class KDEConnectClient::Impl {
public:
    Impl() : running_(false), socket_fd_(-1), port_(1714), discovery_port_(1716) {
        // Generate random device ID
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(0, 15);
        
        std::stringstream ss;
        ss << "gamepad-mapper-";
        for (int i = 0; i < 8; ++i) {
            ss << std::hex << dis(gen);
        }
        device_id_ = ss.str();
    }
    
    ~Impl() {
        stop();
    }
    
    bool initialize() {
        // Create UDP socket for discovery
        socket_fd_ = socket(AF_INET, SOCK_DGRAM, 0);
        if (socket_fd_ < 0) {
            std::cerr << "Failed to create UDP socket" << std::endl;
            return false;
        }
        
        // Set socket options
        int broadcast = 1;
        if (setsockopt(socket_fd_, SOL_SOCKET, SO_BROADCAST, &broadcast, sizeof(broadcast)) < 0) {
            std::cerr << "Failed to set socket broadcast option" << std::endl;
            close(socket_fd_);
            socket_fd_ = -1;
            return false;
        }
        
        std::cout << "KDE Connect client initialized with device ID: " << device_id_ << std::endl;
        return true;
    }
    
    bool start() {
        if (running_) {
            return true;
        }
        
        if (socket_fd_ < 0) {
            std::cerr << "KDE Connect client not initialized" << std::endl;
            return false;
        }
        
        running_ = true;
        
        // Start discovery thread
        discovery_thread_ = std::thread(&Impl::discovery_loop, this);
        
        // Start message handling thread
        message_thread_ = std::thread(&Impl::message_loop, this);
        
        // Send initial discovery broadcast
        send_discovery_broadcast();
        
        std::cout << "KDE Connect client started" << std::endl;
        return true;
    }
    
    void stop() {
        if (!running_) {
            return;
        }
        
        running_ = false;
        
        // Wait for threads to finish
        if (discovery_thread_.joinable()) {
            discovery_thread_.join();
        }
        
        if (message_thread_.joinable()) {
            message_thread_.join();
        }
        
        // Close socket
        if (socket_fd_ >= 0) {
            close(socket_fd_);
            socket_fd_ = -1;
        }
        
        std::cout << "KDE Connect client stopped" << std::endl;
    }
    
    std::vector<KDEConnectDevice> get_available_devices() const {
        std::lock_guard<std::mutex> lock(devices_mutex_);
        std::vector<KDEConnectDevice> devices;
        
        for (const auto& pair : discovered_devices_) {
            devices.push_back(pair.second);
        }
        
        return devices;
    }
    
    std::vector<KDEConnectDevice> get_paired_devices() const {
        std::lock_guard<std::mutex> lock(devices_mutex_);
        std::vector<KDEConnectDevice> devices;
        
        for (const auto& pair : discovered_devices_) {
            if (pair.second.is_paired) {
                devices.push_back(pair.second);
            }
        }
        
        return devices;
    }
    
    KDEConnectDevice get_device_info(const std::string& device_id) const {
        std::lock_guard<std::mutex> lock(devices_mutex_);
        
        auto it = discovered_devices_.find(device_id);
        if (it != discovered_devices_.end()) {
            return it->second;
        }
        
        return KDEConnectDevice();
    }
    
    bool pair_device(const std::string& device_id) {
        std::lock_guard<std::mutex> lock(devices_mutex_);
        
        auto it = discovered_devices_.find(device_id);
        if (it == discovered_devices_.end()) {
            std::cerr << "Device not found: " << device_id << std::endl;
            return false;
        }
        
        // Send pairing request
        KDEConnectMessage message;
        message.type = KDEConnectMessageType::PAIR;
        message.device_id = device_id;
        message.payload = "pair_request";
        
        if (send_message_to_device(device_id, message)) {
            it->second.is_paired = true;
            return true;
        }
        
        return false;
    }
    
    bool unpair_device(const std::string& device_id) {
        std::lock_guard<std::mutex> lock(devices_mutex_);
        
        auto it = discovered_devices_.find(device_id);
        if (it == discovered_devices_.end()) {
            return false;
        }
        
        // Send unpair request
        KDEConnectMessage message;
        message.type = KDEConnectMessageType::UNPAIR;
        message.device_id = device_id;
        message.payload = "unpair_request";
        
        if (send_message_to_device(device_id, message)) {
            it->second.is_paired = false;
            return true;
        }
        
        return false;
    }
    
    bool is_device_paired(const std::string& device_id) const {
        std::lock_guard<std::mutex> lock(devices_mutex_);
        
        auto it = discovered_devices_.find(device_id);
        if (it != discovered_devices_.end()) {
            return it->second.is_paired;
        }
        
        return false;
    }
    
    bool send_message(const KDEConnectMessage& message) {
        return send_message_to_device(message.device_id, message);
    }
    
    bool send_ping(const std::string& device_id) {
        KDEConnectMessage message;
        message.type = KDEConnectMessageType::PING;
        message.device_id = device_id;
        message.payload = "ping";
        return send_message(message);
    }
    
    bool send_clipboard(const std::string& device_id, const std::string& content) {
        KDEConnectMessage message;
        message.type = KDEConnectMessageType::CLIPBOARD;
        message.device_id = device_id;
        message.payload = content;
        message.headers["content_type"] = "text/plain";
        return send_message(message);
    }
    
    bool send_notification(const std::string& device_id, const std::string& title, const std::string& body) {
        json notification;
        notification["title"] = title;
        notification["body"] = body;
        notification["appName"] = "Gamepad Mapper";
        notification["ticker"] = title;
        notification["isClearable"] = true;
        
        KDEConnectMessage message;
        message.type = KDEConnectMessageType::NOTIFICATION;
        message.device_id = device_id;
        message.payload = notification.dump();
        return send_message(message);
    }
    
    bool send_file(const std::string& device_id, const std::string& file_path) {
        // File transfer implementation would go here
        // This is a simplified version
        KDEConnectMessage message;
        message.type = KDEConnectMessageType::FILE_TRANSFER;
        message.device_id = device_id;
        message.payload = file_path;
        return send_message(message);
    }
    
    bool request_file(const std::string& device_id, const std::string& file_path) {
        // File request implementation would go here
        return false;
    }
    
    bool send_key_press(const std::string& device_id, int key_code) {
        // Remote key press implementation would go here
        return false;
    }
    
    bool send_key_release(const std::string& device_id, int key_code) {
        // Remote key release implementation would go here
        return false;
    }
    
    bool send_mouse_click(const std::string& device_id, int button, int x, int y) {
        // Remote mouse click implementation would go here
        return false;
    }
    
    bool send_mouse_move(const std::string& device_id, int x, int y) {
        // Remote mouse move implementation would go here
        return false;
    }
    
    bool send_text(const std::string& device_id, const std::string& text) {
        // Remote text input implementation would go here
        return false;
    }
    
    bool enable_clipboard_sync(bool enabled) {
        clipboard_sync_enabled_ = enabled;
        return true;
    }
    
    bool is_clipboard_sync_enabled() const {
        return clipboard_sync_enabled_;
    }
    
    void register_device_discovered_callback(DeviceDiscoveredCallback callback) {
        std::lock_guard<std::mutex> lock(callback_mutex_);
        device_discovered_callbacks_.push_back(callback);
    }
    
    void register_device_connected_callback(DeviceConnectedCallback callback) {
        std::lock_guard<std::mutex> lock(callback_mutex_);
        device_connected_callbacks_.push_back(callback);
    }
    
    void register_device_disconnected_callback(DeviceDisconnectedCallback callback) {
        std::lock_guard<std::mutex> lock(callback_mutex_);
        device_disconnected_callbacks_.push_back(callback);
    }
    
    void register_message_received_callback(MessageReceivedCallback callback) {
        std::lock_guard<std::mutex> lock(callback_mutex_);
        message_received_callbacks_.push_back(callback);
    }
    
    void register_clipboard_received_callback(ClipboardReceivedCallback callback) {
        std::lock_guard<std::mutex> lock(callback_mutex_);
        clipboard_received_callbacks_.push_back(callback);
    }
    
    bool is_running() const {
        return running_;
    }
    
    bool is_connected_to_device(const std::string& device_id) const {
        std::lock_guard<std::mutex> lock(devices_mutex_);
        
        auto it = discovered_devices_.find(device_id);
        return it != discovered_devices_.end() && it->second.is_online;
    }
    
private:
    void discovery_loop() {
        while (running_) {
            send_discovery_broadcast();
            std::this_thread::sleep_for(std::chrono::seconds(5));
        }
    }
    
    void message_loop() {
        char buffer[1024];
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        
        while (running_) {
            fd_set read_fds;
            FD_ZERO(&read_fds);
            FD_SET(socket_fd_, &read_fds);
            
            struct timeval timeout;
            timeout.tv_sec = 1;
            timeout.tv_usec = 0;
            
            int result = select(socket_fd_ + 1, &read_fds, nullptr, nullptr, &timeout);
            if (result > 0 && FD_ISSET(socket_fd_, &read_fds)) {
                ssize_t bytes_received = recvfrom(socket_fd_, buffer, sizeof(buffer) - 1, 0,
                                                (struct sockaddr*)&client_addr, &client_len);
                
                if (bytes_received > 0) {
                    buffer[bytes_received] = '\0';
                    handle_received_message(buffer, client_addr);
                }
            }
        }
    }
    
    void send_discovery_broadcast() {
        json discovery_message;
        discovery_message["id"] = device_id_;
        discovery_message["type"] = "kdeconnect.identity";
        discovery_message["body"] = {
            {"deviceId", device_id_},
            {"deviceName", "Gamepad Mapper"},
            {"deviceType", "desktop"},
            {"protocolVersion", 7},
            {"deviceName", "Gamepad Mapper"},
            {"incomingCapabilities", {"kdeconnect.notification", "kdeconnect.clipboard"}},
            {"outgoingCapabilities", {"kdeconnect.notification", "kdeconnect.clipboard"}}
        };
        
        std::string message = discovery_message.dump();
        
        struct sockaddr_in broadcast_addr;
        broadcast_addr.sin_family = AF_INET;
        broadcast_addr.sin_port = htons(discovery_port_);
        broadcast_addr.sin_addr.s_addr = INADDR_BROADCAST;
        
        sendto(socket_fd_, message.c_str(), message.length(), 0,
               (struct sockaddr*)&broadcast_addr, sizeof(broadcast_addr));
    }
    
    void handle_received_message(const std::string& message, const struct sockaddr_in& sender_addr) {
        try {
            json received_message = json::parse(message);
            
            if (received_message.contains("type") && received_message["type"] == "kdeconnect.identity") {
                handle_identity_message(received_message, sender_addr);
            } else if (received_message.contains("type") && received_message["type"] == "kdeconnect.ping") {
                handle_ping_message(received_message, sender_addr);
            } else if (received_message.contains("type") && received_message["type"] == "kdeconnect.clipboard") {
                handle_clipboard_message(received_message, sender_addr);
            }
        } catch (const json::exception& e) {
            std::cerr << "Failed to parse KDE Connect message: " << e.what() << std::endl;
        }
    }
    
    void handle_identity_message(const json& message, const struct sockaddr_in& sender_addr) {
        if (!message.contains("body")) return;
        
        json body = message["body"];
        std::string device_id = body.value("deviceId", "");
        std::string device_name = body.value("deviceName", "");
        std::string device_type = body.value("deviceType", "");
        
        if (device_id.empty() || device_id == device_id_) {
            return; // Ignore our own messages
        }
        
        KDEConnectDevice device;
        device.device_id = device_id;
        device.device_name = device_name;
        device.device_type = device_type;
        device.is_online = true;
        device.is_paired = false; // Would need to check pairing status
        
        {
            std::lock_guard<std::mutex> lock(devices_mutex_);
            discovered_devices_[device_id] = device;
        }
        
        // Notify callbacks
        notify_device_discovered(device);
    }
    
    void handle_ping_message(const json& message, const struct sockaddr_in& sender_addr) {
        // Handle ping messages
        std::cout << "Received ping from device" << std::endl;
    }
    
    void handle_clipboard_message(const json& message, const struct sockaddr_in& sender_addr) {
        if (!message.contains("body")) return;
        
        std::string content = message["body"].value("content", "");
        if (!content.empty()) {
            notify_clipboard_received(content);
        }
    }
    
    bool send_message_to_device(const std::string& device_id, const KDEConnectMessage& message) {
        // This would need to implement the actual KDE Connect protocol
        // For now, this is a placeholder
        return true;
    }
    
    void notify_device_discovered(const KDEConnectDevice& device) {
        std::lock_guard<std::mutex> lock(callback_mutex_);
        for (const auto& callback : device_discovered_callbacks_) {
            try {
                callback(device);
            } catch (const std::exception& e) {
                std::cerr << "Error in device discovered callback: " << e.what() << std::endl;
            }
        }
    }
    
    void notify_clipboard_received(const std::string& content) {
        std::lock_guard<std::mutex> lock(callback_mutex_);
        for (const auto& callback : clipboard_received_callbacks_) {
            try {
                callback(content);
            } catch (const std::exception& e) {
                std::cerr << "Error in clipboard received callback: " << e.what() << std::endl;
            }
        }
    }
    
    std::atomic<bool> running_;
    int socket_fd_;
    int port_;
    int discovery_port_;
    std::string device_id_;
    
    std::thread discovery_thread_;
    std::thread message_thread_;
    
    mutable std::mutex devices_mutex_;
    std::map<std::string, KDEConnectDevice> discovered_devices_;
    
    bool clipboard_sync_enabled_;
    
    mutable std::mutex callback_mutex_;
    std::vector<DeviceDiscoveredCallback> device_discovered_callbacks_;
    std::vector<DeviceConnectedCallback> device_connected_callbacks_;
    std::vector<DeviceDisconnectedCallback> device_disconnected_callbacks_;
    std::vector<MessageReceivedCallback> message_received_callbacks_;
    std::vector<ClipboardReceivedCallback> clipboard_received_callbacks_;
};

// Public interface implementation
KDEConnectClient::KDEConnectClient() : impl_(std::make_unique<Impl>()) {}
KDEConnectClient::~KDEConnectClient() = default;

bool KDEConnectClient::initialize() { return impl_->initialize(); }
bool KDEConnectClient::start() { return impl_->start(); }
void KDEConnectClient::stop() { impl_->stop(); }
std::vector<KDEConnectDevice> KDEConnectClient::get_available_devices() const { return impl_->get_available_devices(); }
std::vector<KDEConnectDevice> KDEConnectClient::get_paired_devices() const { return impl_->get_paired_devices(); }
KDEConnectDevice KDEConnectClient::get_device_info(const std::string& device_id) const { return impl_->get_device_info(device_id); }
bool KDEConnectClient::pair_device(const std::string& device_id) { return impl_->pair_device(device_id); }
bool KDEConnectClient::unpair_device(const std::string& device_id) { return impl_->unpair_device(device_id); }
bool KDEConnectClient::is_device_paired(const std::string& device_id) const { return impl_->is_device_paired(device_id); }
bool KDEConnectClient::send_message(const KDEConnectMessage& message) { return impl_->send_message(message); }
bool KDEConnectClient::send_ping(const std::string& device_id) { return impl_->send_ping(device_id); }
bool KDEConnectClient::send_clipboard(const std::string& device_id, const std::string& content) { return impl_->send_clipboard(device_id, content); }
bool KDEConnectClient::send_notification(const std::string& device_id, const std::string& title, const std::string& body) { return impl_->send_notification(device_id, title, body); }
bool KDEConnectClient::send_file(const std::string& device_id, const std::string& file_path) { return impl_->send_file(device_id, file_path); }
bool KDEConnectClient::request_file(const std::string& device_id, const std::string& file_path) { return impl_->request_file(device_id, file_path); }
bool KDEConnectClient::send_key_press(const std::string& device_id, int key_code) { return impl_->send_key_press(device_id, key_code); }
bool KDEConnectClient::send_key_release(const std::string& device_id, int key_code) { return impl_->send_key_release(device_id, key_code); }
bool KDEConnectClient::send_mouse_click(const std::string& device_id, int button, int x, int y) { return impl_->send_mouse_click(device_id, button, x, y); }
bool KDEConnectClient::send_mouse_move(const std::string& device_id, int x, int y) { return impl_->send_mouse_move(device_id, x, y); }
bool KDEConnectClient::send_text(const std::string& device_id, const std::string& text) { return impl_->send_text(device_id, text); }
bool KDEConnectClient::enable_clipboard_sync(bool enabled) { return impl_->enable_clipboard_sync(enabled); }
bool KDEConnectClient::is_clipboard_sync_enabled() const { return impl_->is_clipboard_sync_enabled(); }
void KDEConnectClient::register_device_discovered_callback(DeviceDiscoveredCallback callback) { impl_->register_device_discovered_callback(callback); }
void KDEConnectClient::register_device_connected_callback(DeviceConnectedCallback callback) { impl_->register_device_connected_callback(callback); }
void KDEConnectClient::register_device_disconnected_callback(DeviceDisconnectedCallback callback) { impl_->register_device_disconnected_callback(callback); }
void KDEConnectClient::register_message_received_callback(MessageReceivedCallback callback) { impl_->register_message_received_callback(callback); }
void KDEConnectClient::register_clipboard_received_callback(ClipboardReceivedCallback callback) { impl_->register_clipboard_received_callback(callback); }
bool KDEConnectClient::is_running() const { return impl_->is_running(); }
bool KDEConnectClient::is_connected_to_device(const std::string& device_id) const { return impl_->is_connected_to_device(device_id); }

} // namespace gamepad_mapper