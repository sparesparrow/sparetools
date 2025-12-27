#pragma once

#include <string>
#include <vector>
#include <memory>
#include <atomic>
#include <thread>
#include <mutex>
#include <map>
#include <functional>

namespace gamepad_mapper {

// KDE Connect device information
struct KDEConnectDevice {
    std::string device_id;
    std::string device_name;
    std::string device_type;
    bool is_paired;
    bool is_online;
    int battery_level;
    bool is_charging;
    std::string last_seen;
    
    KDEConnectDevice() : is_paired(false), is_online(false), battery_level(-1), is_charging(false) {}
};

// KDE Connect message types
enum class KDEConnectMessageType {
    PING,
    PONG,
    IDENTITY,
    PAIR,
    PAIRED,
    UNPAIR,
    UNPAIRED,
    CLIPBOARD,
    NOTIFICATION,
    FILE_TRANSFER,
    CUSTOM
};

// KDE Connect message structure
struct KDEConnectMessage {
    KDEConnectMessageType type;
    std::string device_id;
    std::string payload;
    std::map<std::string, std::string> headers;
    
    KDEConnectMessage() : type(KDEConnectMessageType::CUSTOM) {}
};

// KDE Connect callback function types
using DeviceDiscoveredCallback = std::function<void(const KDEConnectDevice& device)>;
using DeviceConnectedCallback = std::function<void(const KDEConnectDevice& device)>;
using DeviceDisconnectedCallback = std::function<void(const std::string& device_id)>;
using MessageReceivedCallback = std::function<void(const KDEConnectMessage& message)>;
using ClipboardReceivedCallback = std::function<void(const std::string& content)>;

// KDE Connect client for remote control
class KDEConnectClient {
public:
    KDEConnectClient();
    ~KDEConnectClient();
    
    // Initialize the KDE Connect client
    bool initialize();
    
    // Start/stop the client
    bool start();
    void stop();
    
    // Device management
    std::vector<KDEConnectDevice> get_available_devices() const;
    std::vector<KDEConnectDevice> get_paired_devices() const;
    KDEConnectDevice get_device_info(const std::string& device_id) const;
    
    // Device pairing
    bool pair_device(const std::string& device_id);
    bool unpair_device(const std::string& device_id);
    bool is_device_paired(const std::string& device_id) const;
    
    // Message sending
    bool send_message(const KDEConnectMessage& message);
    bool send_ping(const std::string& device_id);
    bool send_clipboard(const std::string& device_id, const std::string& content);
    bool send_notification(const std::string& device_id, const std::string& title, const std::string& body);
    
    // File transfer
    bool send_file(const std::string& device_id, const std::string& file_path);
    bool request_file(const std::string& device_id, const std::string& file_path);
    
    // Remote control
    bool send_key_press(const std::string& device_id, int key_code);
    bool send_key_release(const std::string& device_id, int key_code);
    bool send_mouse_click(const std::string& device_id, int button, int x, int y);
    bool send_mouse_move(const std::string& device_id, int x, int y);
    bool send_text(const std::string& device_id, const std::string& text);
    
    // Clipboard synchronization
    bool enable_clipboard_sync(bool enabled);
    bool is_clipboard_sync_enabled() const;
    
    // Callbacks
    void register_device_discovered_callback(DeviceDiscoveredCallback callback);
    void register_device_connected_callback(DeviceConnectedCallback callback);
    void register_device_disconnected_callback(DeviceDisconnectedCallback callback);
    void register_message_received_callback(MessageReceivedCallback callback);
    void register_clipboard_received_callback(ClipboardReceivedCallback callback);
    
    // Status
    bool is_running() const;
    bool is_connected_to_device(const std::string& device_id) const;
    
private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace gamepad_mapper