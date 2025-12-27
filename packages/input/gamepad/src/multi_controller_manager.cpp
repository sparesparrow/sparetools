#include "multi_controller_manager.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <chrono>
#include <algorithm>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <ifaddrs.h>
#include <sys/ioctl.h>
#include <linux/if.h>
#include <linux/input.h>
#include <dirent.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <execinfo.h>
#include <signal.h>

// External dependencies
#include <nlohmann/json.hpp>
#include <curl/curl.h>

using json = nlohmann::json;

namespace gamepad_mapper {

// Voice Alert System Implementation
class VoiceAlertSystem::Impl {
public:
    Impl() : initialized_(false), voice_("default"), speed_(1.0f), volume_(1.0f) {}
    
    bool initialize() {
        if (initialized_) return true;
        
        // Check if speech-dispatcher is available
        int result = system("which spd-say > /dev/null 2>&1");
        if (result != 0) {
            std::cerr << "Warning: spd-say not found. Voice alerts will be disabled." << std::endl;
            return false;
        }
        
        initialized_ = true;
        return true;
    }
    
    void cleanup() {
        initialized_ = false;
    }
    
    void speak(const std::string& text, bool interrupt) {
        if (!initialized_) return;
        
        std::string cmd = "spd-say";
        if (interrupt) cmd += " --interrupt";
        if (voice_ != "default") cmd += " --voice=" + voice_;
        cmd += " --speed=" + std::to_string(speed_);
        cmd += " --volume=" + std::to_string(volume_);
        cmd += " \"" + text + "\"";
        
        system(cmd.c_str());
    }
    
    void speak_async(const std::string& text) {
        std::thread([this, text]() {
            speak(text, false);
        }).detach();
    }
    
    void set_voice(const std::string& voice) { voice_ = voice; }
    void set_speed(float speed) { speed_ = std::max(0.1f, std::min(2.0f, speed)); }
    void set_volume(float volume) { volume_ = std::max(0.0f, std::min(1.0f, volume)); }
    
    void alert_controller_connected(const std::string& controller_name) {
        speak_async("Controller " + controller_name + " connected successfully!");
    }
    
    void alert_controller_disconnected(const std::string& controller_name) {
        speak_async("Controller " + controller_name + " disconnected!");
    }
    
    void alert_mapping_loaded(const std::string& mapping_name) {
        speak_async("Mapping " + mapping_name + " loaded successfully!");
    }
    
    void alert_error(const std::string& error) {
        speak_async("Error: " + error);
    }
    
    void alert_system_ready() {
        speak_async("Multi-controller system ready! All systems operational!");
    }

private:
    bool initialized_;
    std::string voice_;
    float speed_;
    float volume_;
};

VoiceAlertSystem::VoiceAlertSystem() : impl_(std::make_unique<Impl>()) {}
VoiceAlertSystem::~VoiceAlertSystem() = default;

bool VoiceAlertSystem::initialize() { return impl_->initialize(); }
void VoiceAlertSystem::cleanup() { impl_->cleanup(); }
void VoiceAlertSystem::speak(const std::string& text, bool interrupt) { impl_->speak(text, interrupt); }
void VoiceAlertSystem::speak_async(const std::string& text) { impl_->speak_async(text); }
void VoiceAlertSystem::set_voice(const std::string& voice) { impl_->set_voice(voice); }
void VoiceAlertSystem::set_speed(float speed) { impl_->set_speed(speed); }
void VoiceAlertSystem::set_volume(float volume) { impl_->set_volume(volume); }
void VoiceAlertSystem::alert_controller_connected(const std::string& controller_name) { impl_->alert_controller_connected(controller_name); }
void VoiceAlertSystem::alert_controller_disconnected(const std::string& controller_name) { impl_->alert_controller_disconnected(controller_name); }
void VoiceAlertSystem::alert_mapping_loaded(const std::string& mapping_name) { impl_->alert_mapping_loaded(mapping_name); }
void VoiceAlertSystem::alert_error(const std::string& error) { impl_->alert_error(error); }
void VoiceAlertSystem::alert_system_ready() { impl_->alert_system_ready(); }

// Network Remote Control Implementation
class NetworkRemoteControl::Impl {
public:
    Impl() : initialized_(false) {
        curl_global_init(CURL_GLOBAL_DEFAULT);
    }
    
    ~Impl() {
        curl_global_cleanup();
    }
    
    bool initialize() {
        if (initialized_) return true;
        initialized_ = true;
        return true;
    }
    
    void cleanup() {
        initialized_ = false;
    }
    
    bool connect_to_remote(const std::string& host, int port) {
        // Implementation for remote computer connection
        // This would establish a network connection to the remote system
        return true; // Placeholder
    }
    
    bool disconnect_from_remote(const std::string& host) {
        // Implementation for disconnecting from remote
        return true; // Placeholder
    }
    
    bool send_input_to_remote(const std::string& host, const MultiControllerEvent& event) {
        // Implementation for sending input events to remote computer
        return true; // Placeholder
    }
    
    bool connect_kde_device(const std::string& device_id) {
        // Implementation for KDE Connect integration
        return true; // Placeholder
    }
    
    bool send_kde_input(const std::string& device_id, const MultiControllerEvent& event) {
        // Implementation for sending input via KDE Connect
        return true; // Placeholder
    }
    
    bool execute_ssh_command(const std::string& host, const std::string& command) {
        // Implementation for SSH command execution
        std::string ssh_cmd = "ssh " + host + " \"" + command + "\"";
        int result = system(ssh_cmd.c_str());
        return result == 0;
    }
    
    bool send_ssh_input(const std::string& host, const MultiControllerEvent& event) {
        // Implementation for sending input via SSH
        return true; // Placeholder
    }
    
    bool send_tasker_command(const std::string& device_id, const std::string& command) {
        // Implementation for Tasker/Join integration
        return true; // Placeholder
    }
    
    bool send_join_notification(const std::string& device_id, const std::string& message) {
        // Implementation for Join notifications
        return true; // Placeholder
    }

private:
    bool initialized_;
};

NetworkRemoteControl::NetworkRemoteControl() : impl_(std::make_unique<Impl>()) {}
NetworkRemoteControl::~NetworkRemoteControl() = default;

bool NetworkRemoteControl::initialize() { return impl_->initialize(); }
void NetworkRemoteControl::cleanup() { impl_->cleanup(); }
bool NetworkRemoteControl::connect_to_remote(const std::string& host, int port) { return impl_->connect_to_remote(host, port); }
bool NetworkRemoteControl::disconnect_from_remote(const std::string& host) { return impl_->disconnect_from_remote(host); }
bool NetworkRemoteControl::send_input_to_remote(const std::string& host, const MultiControllerEvent& event) { return impl_->send_input_to_remote(host, event); }
bool NetworkRemoteControl::connect_kde_device(const std::string& device_id) { return impl_->connect_kde_device(device_id); }
bool NetworkRemoteControl::send_kde_input(const std::string& device_id, const MultiControllerEvent& event) { return impl_->send_kde_input(device_id, event); }
bool NetworkRemoteControl::execute_ssh_command(const std::string& host, const std::string& command) { return impl_->execute_ssh_command(host, command); }
bool NetworkRemoteControl::send_ssh_input(const std::string& host, const MultiControllerEvent& event) { return impl_->send_ssh_input(host, event); }
bool NetworkRemoteControl::send_tasker_command(const std::string& device_id, const std::string& command) { return impl_->send_tasker_command(device_id, command); }
bool NetworkRemoteControl::send_join_notification(const std::string& device_id, const std::string& message) { return impl_->send_join_notification(device_id, message); }

// Advanced Device Scanner Implementation
class AdvancedDeviceScanner::Impl {
public:
    Impl() : initialized_(false), monitoring_(false) {}
    
    bool initialize() {
        if (initialized_) return true;
        initialized_ = true;
        return true;
    }
    
    void cleanup() {
        stop_device_monitoring();
        initialized_ = false;
    }
    
    std::vector<ControllerDevice> scan_bluetooth_devices() {
        std::vector<ControllerDevice> devices;
        
        // Use bluetoothctl to scan for devices
        FILE* pipe = popen("bluetoothctl devices", "r");
        if (!pipe) return devices;
        
        char buffer[256];
        while (fgets(buffer, sizeof(buffer), pipe)) {
            std::string line(buffer);
            if (line.find("Device") != std::string::npos) {
                ControllerDevice device;
                device.connection_type = ConnectionType::BLUETOOTH;
                device.is_connected = false;
                device.is_active = false;
                device.last_seen = std::chrono::steady_clock::now();
                
                // Parse device information
                std::istringstream iss(line);
                std::string token;
                std::vector<std::string> tokens;
                while (iss >> token) {
                    tokens.push_back(token);
                }
                
                if (tokens.size() >= 3) {
                    device.device_id = tokens[1];
                    device.mac_address = tokens[1];
                    device.name = tokens[2];
                    for (size_t i = 3; i < tokens.size(); ++i) {
                        device.name += " " + tokens[i];
                    }
                }
                
                devices.push_back(device);
            }
        }
        pclose(pipe);
        
        return devices;
    }
    
    std::vector<ControllerDevice> scan_bluetooth_devices_advanced() {
        std::vector<ControllerDevice> devices;
        
        // Run btscanner for advanced scanning
        run_btscanner_scan("advanced_scan.log");
        
        // Parse the log file for devices
        std::ifstream file("advanced_scan.log");
        std::string line;
        while (std::getline(file, line)) {
            if (line.find("Device") != std::string::npos) {
                ControllerDevice device;
                device.connection_type = ConnectionType::BLUETOOTH;
                device.is_connected = false;
                device.is_active = false;
                device.last_seen = std::chrono::steady_clock::now();
                
                // Parse advanced device information
                // This would parse the btscanner output format
                devices.push_back(device);
            }
        }
        
        return devices;
    }
    
    std::vector<ControllerDevice> scan_network_devices(const std::string& subnet) {
        std::vector<ControllerDevice> devices;
        
        // Use nmap to scan for network devices
        std::string nmap_cmd = "nmap -sn " + subnet + " 2>/dev/null";
        FILE* pipe = popen(nmap_cmd.c_str(), "r");
        if (!pipe) return devices;
        
        char buffer[256];
        while (fgets(buffer, sizeof(buffer), pipe)) {
            std::string line(buffer);
            if (line.find("Nmap scan report") != std::string::npos) {
                ControllerDevice device;
                device.connection_type = ConnectionType::NETWORK;
                device.is_connected = false;
                device.is_active = false;
                device.last_seen = std::chrono::steady_clock::now();
                
                // Parse IP address
                size_t start = line.find("for ") + 4;
                size_t end = line.find(" ", start);
                if (start != std::string::npos && end != std::string::npos) {
                    device.ip_address = line.substr(start, end - start);
                    device.device_id = device.ip_address;
                }
                
                devices.push_back(device);
            }
        }
        pclose(pipe);
        
        return devices;
    }
    
    std::vector<ControllerDevice> scan_usb_devices() {
        std::vector<ControllerDevice> devices;
        
        // Scan /dev/input for gamepad devices
        DIR* dir = opendir("/dev/input");
        if (!dir) return devices;
        
        struct dirent* entry;
        while ((entry = readdir(dir)) != nullptr) {
            if (entry->d_type == DT_CHR && strncmp(entry->d_name, "event", 5) == 0) {
                std::string device_path = "/dev/input/" + std::string(entry->d_name);
                int fd = open(device_path.c_str(), O_RDONLY);
                if (fd != -1) {
                    char name[256] = {0};
                    if (ioctl(fd, EVIOCGNAME(sizeof(name)), name) >= 0) {
                        if (strstr(name, "gamepad") || strstr(name, "Gamepad") ||
                            strstr(name, "Xbox") || strstr(name, "xbox") ||
                            strstr(name, "PS4") || strstr(name, "ps4") ||
                            strstr(name, "Sony") || strstr(name, "DualShock") ||
                            strstr(name, "Wireless Controller")) {
                            
                            ControllerDevice device;
                            device.device_id = device_path;
                            device.name = name;
                            device.path = device_path;
                            device.connection_type = ConnectionType::USB;
                            device.is_connected = true;
                            device.is_active = false;
                            device.last_seen = std::chrono::steady_clock::now();
                            
                            // Get vendor and product ID
                            struct input_id id;
                            if (ioctl(fd, EVIOCGID, &id) >= 0) {
                                device.vendor_id = id.vendor;
                                device.product_id = id.product;
                            }
                            
                            devices.push_back(device);
                        }
                    }
                    close(fd);
                }
            }
        }
        closedir(dir);
        
        return devices;
    }
    
    std::vector<ControllerDevice> scan_wireless_devices() {
        std::vector<ControllerDevice> devices;
        
        // Scan for wireless dongles and other wireless devices
        // This would scan for specific wireless protocols
        return devices;
    }
    
    bool run_btscanner_scan(const std::string& output_file) {
        std::string cmd = "btscanner -b > " + output_file + " 2>&1";
        int result = system(cmd.c_str());
        return result == 0;
    }
    
    bool run_gatool_scan(const std::string& output_file) {
        std::string cmd = "gatool scan > " + output_file + " 2>&1";
        int result = system(cmd.c_str());
        return result == 0;
    }
    
    bool run_nmap_scan(const std::string& target) {
        std::string cmd = "nmap -sn " + target + " > nmap_scan.log 2>&1";
        int result = system(cmd.c_str());
        return result == 0;
    }
    
    void start_device_monitoring() {
        if (monitoring_) return;
        monitoring_ = true;
        monitor_thread_ = std::thread(&Impl::monitor_devices, this);
    }
    
    void stop_device_monitoring() {
        if (!monitoring_) return;
        monitoring_ = false;
        if (monitor_thread_.joinable()) {
            monitor_thread_.join();
        }
    }
    
    std::vector<ControllerDevice> get_connected_devices() {
        std::lock_guard<std::mutex> lock(devices_mutex_);
        return connected_devices_;
    }

private:
    void monitor_devices() {
        while (monitoring_) {
            auto usb_devices = scan_usb_devices();
            auto bluetooth_devices = scan_bluetooth_devices();
            
            std::lock_guard<std::mutex> lock(devices_mutex_);
            connected_devices_.clear();
            connected_devices_.insert(connected_devices_.end(), usb_devices.begin(), usb_devices.end());
            connected_devices_.insert(connected_devices_.end(), bluetooth_devices.begin(), bluetooth_devices.end());
            
            std::this_thread::sleep_for(std::chrono::seconds(2));
        }
    }
    
    bool initialized_;
    bool monitoring_;
    std::thread monitor_thread_;
    std::mutex devices_mutex_;
    std::vector<ControllerDevice> connected_devices_;
};

AdvancedDeviceScanner::AdvancedDeviceScanner() : impl_(std::make_unique<Impl>()) {}
AdvancedDeviceScanner::~AdvancedDeviceScanner() = default;

bool AdvancedDeviceScanner::initialize() { return impl_->initialize(); }
void AdvancedDeviceScanner::cleanup() { impl_->cleanup(); }
std::vector<ControllerDevice> AdvancedDeviceScanner::scan_bluetooth_devices() { return impl_->scan_bluetooth_devices(); }
std::vector<ControllerDevice> AdvancedDeviceScanner::scan_bluetooth_devices_advanced() { return impl_->scan_bluetooth_devices_advanced(); }
std::vector<ControllerDevice> AdvancedDeviceScanner::scan_network_devices(const std::string& subnet) { return impl_->scan_network_devices(subnet); }
std::vector<ControllerDevice> AdvancedDeviceScanner::scan_usb_devices() { return impl_->scan_usb_devices(); }
std::vector<ControllerDevice> AdvancedDeviceScanner::scan_wireless_devices() { return impl_->scan_wireless_devices(); }
bool AdvancedDeviceScanner::run_btscanner_scan(const std::string& output_file) { return impl_->run_btscanner_scan(output_file); }
bool AdvancedDeviceScanner::run_gatool_scan(const std::string& output_file) { return impl_->run_gatool_scan(output_file); }
bool AdvancedDeviceScanner::run_nmap_scan(const std::string& target) { return impl_->run_nmap_scan(target); }
void AdvancedDeviceScanner::start_device_monitoring() { impl_->start_device_monitoring(); }
void AdvancedDeviceScanner::stop_device_monitoring() { impl_->stop_device_monitoring(); }
std::vector<ControllerDevice> AdvancedDeviceScanner::get_connected_devices() { return impl_->get_connected_devices(); }

// Multi-Controller Manager Implementation
class MultiControllerManager::Impl {
public:
    Impl() : initialized_(false), running_(false), voice_alerts_enabled_(true) {}
    
    ~Impl() {
        cleanup();
    }
    
    bool initialize() {
        if (initialized_) return true;
        
        // Initialize components
        if (!voice_system_.initialize()) {
            std::cerr << "Warning: Voice alert system initialization failed" << std::endl;
        }
        
        if (!network_control_.initialize()) {
            std::cerr << "Warning: Network remote control initialization failed" << std::endl;
        }
        
        if (!device_scanner_.initialize()) {
            std::cerr << "Warning: Advanced device scanner initialization failed" << std::endl;
        }
        
        initialized_ = true;
        return true;
    }
    
    void cleanup() {
        if (!initialized_) return;
        
        stop_event_processing();
        stop_auto_detection();
        
        voice_system_.cleanup();
        network_control_.cleanup();
        device_scanner_.cleanup();
        
        initialized_ = false;
    }
    
    bool add_controller(const ControllerDevice& device) {
        std::lock_guard<std::mutex> lock(controllers_mutex_);
        
        controllers_[device.device_id] = device;
        
        if (voice_alerts_enabled_) {
            voice_system_.alert_controller_connected(device.name);
        }
        
        return true;
    }
    
    bool remove_controller(const std::string& device_id) {
        std::lock_guard<std::mutex> lock(controllers_mutex_);
        
        auto it = controllers_.find(device_id);
        if (it != controllers_.end()) {
            if (voice_alerts_enabled_) {
                voice_system_.alert_controller_disconnected(it->second.name);
            }
            controllers_.erase(it);
            return true;
        }
        
        return false;
    }
    
    bool connect_controller(const std::string& device_id) {
        std::lock_guard<std::mutex> lock(controllers_mutex_);
        
        auto it = controllers_.find(device_id);
        if (it != controllers_.end()) {
            it->second.is_connected = true;
            it->second.is_active = true;
            it->second.last_seen = std::chrono::steady_clock::now();
            return true;
        }
        
        return false;
    }
    
    bool disconnect_controller(const std::string& device_id) {
        std::lock_guard<std::mutex> lock(controllers_mutex_);
        
        auto it = controllers_.find(device_id);
        if (it != controllers_.end()) {
            it->second.is_connected = false;
            it->second.is_active = false;
            return true;
        }
        
        return false;
    }
    
    void start_event_processing() {
        if (running_) return;
        
        running_ = true;
        event_thread_ = std::thread(&Impl::event_loop, this);
    }
    
    void stop_event_processing() {
        if (!running_) return;
        
        running_ = false;
        if (event_thread_.joinable()) {
            event_thread_.join();
        }
    }
    
    bool load_controller_mapping(const std::string& device_id, const std::string& mapping_file) {
        std::lock_guard<std::mutex> lock(controllers_mutex_);
        
        auto it = controllers_.find(device_id);
        if (it == controllers_.end()) return false;
        
        // Load mapping file
        std::ifstream file(mapping_file);
        if (!file.is_open()) return false;
        
        json mapping_data;
        file >> mapping_data;
        
        // Store mapping for this controller
        controller_mappings_[device_id] = mapping_data;
        
        if (voice_alerts_enabled_) {
            voice_system_.alert_mapping_loaded(mapping_file);
        }
        
        return true;
    }
    
    bool set_controller_mapping(const std::string& device_id, const std::string& input, const std::string& output) {
        std::lock_guard<std::mutex> lock(controllers_mutex_);
        
        auto it = controllers_.find(device_id);
        if (it == controllers_.end()) return false;
        
        controller_mappings_[device_id][input] = output;
        return true;
    }
    
    bool enable_remote_control(const std::string& device_id, const std::string& target_host) {
        std::lock_guard<std::mutex> lock(controllers_mutex_);
        
        auto it = controllers_.find(device_id);
        if (it == controllers_.end()) return false;
        
        remote_controls_[device_id] = target_host;
        return true;
    }
    
    bool disable_remote_control(const std::string& device_id) {
        std::lock_guard<std::mutex> lock(controllers_mutex_);
        
        auto it = remote_controls_.find(device_id);
        if (it != remote_controls_.end()) {
            remote_controls_.erase(it);
            return true;
        }
        
        return false;
    }
    
    void enable_voice_alerts(bool enable) {
        voice_alerts_enabled_ = enable;
    }
    
    void set_voice_alert_callback(std::function<void(const std::string&)> callback) {
        voice_callback_ = callback;
    }
    
    void start_auto_detection() {
        if (auto_detection_running_) return;
        
        auto_detection_running_ = true;
        auto_detection_thread_ = std::thread(&Impl::auto_detection_loop, this);
    }
    
    void stop_auto_detection() {
        if (!auto_detection_running_) return;
        
        auto_detection_running_ = false;
        if (auto_detection_thread_.joinable()) {
            auto_detection_thread_.join();
        }
    }
    
    std::map<std::string, int> get_controller_statistics() {
        std::lock_guard<std::mutex> lock(controllers_mutex_);
        
        std::map<std::string, int> stats;
        stats["total_controllers"] = controllers_.size();
        stats["connected_controllers"] = 0;
        stats["active_controllers"] = 0;
        
        for (const auto& pair : controllers_) {
            if (pair.second.is_connected) stats["connected_controllers"]++;
            if (pair.second.is_active) stats["active_controllers"]++;
        }
        
        return stats;
    }
    
    std::vector<ControllerDevice> get_all_controllers() {
        std::lock_guard<std::mutex> lock(controllers_mutex_);
        
        std::vector<ControllerDevice> result;
        for (const auto& pair : controllers_) {
            result.push_back(pair.second);
        }
        
        return result;
    }
    
    std::vector<ControllerDevice> get_connected_controllers() {
        std::lock_guard<std::mutex> lock(controllers_mutex_);
        
        std::vector<ControllerDevice> result;
        for (const auto& pair : controllers_) {
            if (pair.second.is_connected) {
                result.push_back(pair.second);
            }
        }
        
        return result;
    }
    
    void set_event_callback(std::function<void(const MultiControllerEvent&)> callback) {
        event_callback_ = callback;
    }
    
    void set_connection_callback(std::function<void(const std::string&, bool)> callback) {
        connection_callback_ = callback;
    }

private:
    void event_loop() {
        while (running_) {
            // Process events from all connected controllers
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }
    
    void auto_detection_loop() {
        while (auto_detection_running_) {
            // Scan for new devices
            auto usb_devices = device_scanner_.scan_usb_devices();
            auto bluetooth_devices = device_scanner_.scan_bluetooth_devices();
            
            // Add new devices
            for (const auto& device : usb_devices) {
                if (controllers_.find(device.device_id) == controllers_.end()) {
                    add_controller(device);
                }
            }
            
            for (const auto& device : bluetooth_devices) {
                if (controllers_.find(device.device_id) == controllers_.end()) {
                    add_controller(device);
                }
            }
            
            std::this_thread::sleep_for(std::chrono::seconds(5));
        }
    }
    
    bool initialized_;
    bool running_;
    bool auto_detection_running_;
    bool voice_alerts_enabled_;
    
    std::mutex controllers_mutex_;
    std::map<std::string, ControllerDevice> controllers_;
    std::map<std::string, json> controller_mappings_;
    std::map<std::string, std::string> remote_controls_;
    
    std::thread event_thread_;
    std::thread auto_detection_thread_;
    
    VoiceAlertSystem voice_system_;
    NetworkRemoteControl network_control_;
    AdvancedDeviceScanner device_scanner_;
    
    std::function<void(const MultiControllerEvent&)> event_callback_;
    std::function<void(const std::string&, bool)> connection_callback_;
    std::function<void(const std::string&)> voice_callback_;
};

MultiControllerManager::MultiControllerManager() : impl_(std::make_unique<Impl>()) {}
MultiControllerManager::~MultiControllerManager() = default;

bool MultiControllerManager::initialize() { return impl_->initialize(); }
void MultiControllerManager::cleanup() { impl_->cleanup(); }
bool MultiControllerManager::add_controller(const ControllerDevice& device) { return impl_->add_controller(device); }
bool MultiControllerManager::remove_controller(const std::string& device_id) { return impl_->remove_controller(device_id); }
bool MultiControllerManager::connect_controller(const std::string& device_id) { return impl_->connect_controller(device_id); }
bool MultiControllerManager::disconnect_controller(const std::string& device_id) { return impl_->disconnect_controller(device_id); }
void MultiControllerManager::start_event_processing() { impl_->start_event_processing(); }
void MultiControllerManager::stop_event_processing() { impl_->stop_event_processing(); }
bool MultiControllerManager::load_controller_mapping(const std::string& device_id, const std::string& mapping_file) { return impl_->load_controller_mapping(device_id, mapping_file); }
bool MultiControllerManager::set_controller_mapping(const std::string& device_id, const std::string& input, const std::string& output) { return impl_->set_controller_mapping(device_id, input, output); }
bool MultiControllerManager::enable_remote_control(const std::string& device_id, const std::string& target_host) { return impl_->enable_remote_control(device_id, target_host); }
bool MultiControllerManager::disable_remote_control(const std::string& device_id) { return impl_->disable_remote_control(device_id); }
void MultiControllerManager::enable_voice_alerts(bool enable) { impl_->enable_voice_alerts(enable); }
void MultiControllerManager::set_voice_alert_callback(std::function<void(const std::string&)> callback) { impl_->set_voice_alert_callback(callback); }
void MultiControllerManager::start_auto_detection() { impl_->start_auto_detection(); }
void MultiControllerManager::stop_auto_detection() { impl_->stop_auto_detection(); }
std::map<std::string, int> MultiControllerManager::get_controller_statistics() { return impl_->get_controller_statistics(); }
std::vector<ControllerDevice> MultiControllerManager::get_all_controllers() { return impl_->get_all_controllers(); }
std::vector<ControllerDevice> MultiControllerManager::get_connected_controllers() { return impl_->get_connected_controllers(); }
void MultiControllerManager::set_event_callback(std::function<void(const MultiControllerEvent&)> callback) { impl_->set_event_callback(callback); }
void MultiControllerManager::set_connection_callback(std::function<void(const std::string&, bool)> callback) { impl_->set_connection_callback(callback); }

} // namespace gamepad_mapper