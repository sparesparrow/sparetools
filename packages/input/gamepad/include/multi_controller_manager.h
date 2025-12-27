#pragma once

#include <memory>
#include <vector>
#include <map>
#include <string>
#include <thread>
#include <atomic>
#include <mutex>
#include <functional>
#include <queue>
#include <condition_variable>

namespace gamepad_mapper {

// Controller connection types
enum class ConnectionType {
    USB,
    BLUETOOTH,
    NETWORK,
    WIRELESS_DONGLE,
    UNKNOWN
};

// Controller device information
struct ControllerDevice {
    std::string device_id;
    std::string name;
    std::string path;
    ConnectionType connection_type;
    uint16_t vendor_id;
    uint16_t product_id;
    std::string mac_address;
    std::string ip_address;
    int port;
    bool is_connected;
    bool is_active;
    std::chrono::steady_clock::time_point last_seen;
    std::map<std::string, std::string> capabilities;
};

// Controller event with device identification
struct MultiControllerEvent {
    std::string device_id;
    std::string controller_name;
    ConnectionType connection_type;
    struct {
        enum Type { BUTTON, AXIS, CONNECTION, DISCONNECTION } type;
        struct ButtonEvent {
            int code;
            bool pressed;
            float pressure; // For pressure-sensitive buttons
        } button;
        struct AxisEvent {
            int code;
            int value;  // -32767 to 32767
            float normalized_value; // -1.0 to 1.0
        } axis;
        struct ConnectionEvent {
            bool connected;
            std::string reason;
        } connection;
    } event;
};

// Voice alert system
class VoiceAlertSystem {
public:
    VoiceAlertSystem();
    ~VoiceAlertSystem();

    bool initialize();
    void cleanup();
    
    void speak(const std::string& text, bool interrupt = false);
    void speak_async(const std::string& text);
    void set_voice(const std::string& voice);
    void set_speed(float speed);
    void set_volume(float volume);
    
    // Predefined alerts
    void alert_controller_connected(const std::string& controller_name);
    void alert_controller_disconnected(const std::string& controller_name);
    void alert_mapping_loaded(const std::string& mapping_name);
    void alert_error(const std::string& error);
    void alert_system_ready();

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

// Network remote control
class NetworkRemoteControl {
public:
    NetworkRemoteControl();
    ~NetworkRemoteControl();

    bool initialize();
    void cleanup();
    
    // Remote computer control
    bool connect_to_remote(const std::string& host, int port = 8080);
    bool disconnect_from_remote(const std::string& host);
    bool send_input_to_remote(const std::string& host, const MultiControllerEvent& event);
    
    // KDE Connect integration
    bool connect_kde_device(const std::string& device_id);
    bool send_kde_input(const std::string& device_id, const MultiControllerEvent& event);
    
    // SSH integration
    bool execute_ssh_command(const std::string& host, const std::string& command);
    bool send_ssh_input(const std::string& host, const MultiControllerEvent& event);
    
    // Tasker/Join integration
    bool send_tasker_command(const std::string& device_id, const std::string& command);
    bool send_join_notification(const std::string& device_id, const std::string& message);

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

// Advanced device scanner
class AdvancedDeviceScanner {
public:
    AdvancedDeviceScanner();
    ~AdvancedDeviceScanner();

    bool initialize();
    void cleanup();
    
    // Bluetooth scanning with btscanner integration
    std::vector<ControllerDevice> scan_bluetooth_devices();
    std::vector<ControllerDevice> scan_bluetooth_devices_advanced();
    
    // Network device discovery
    std::vector<ControllerDevice> scan_network_devices(const std::string& subnet = "192.168.1.0/24");
    
    // USB device scanning
    std::vector<ControllerDevice> scan_usb_devices();
    
    // Wireless dongle detection
    std::vector<ControllerDevice> scan_wireless_devices();
    
    // Kali tools integration
    bool run_btscanner_scan(const std::string& output_file = "btscanner.log");
    bool run_gatool_scan(const std::string& output_file = "gatool.log");
    bool run_nmap_scan(const std::string& target = "192.168.1.0/24");
    
    // Device monitoring
    void start_device_monitoring();
    void stop_device_monitoring();
    std::vector<ControllerDevice> get_connected_devices();

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

// Multi-controller manager
class MultiControllerManager {
public:
    MultiControllerManager();
    ~MultiControllerManager();

    // Initialization
    bool initialize();
    void cleanup();
    
    // Controller management
    bool add_controller(const ControllerDevice& device);
    bool remove_controller(const std::string& device_id);
    bool connect_controller(const std::string& device_id);
    bool disconnect_controller(const std::string& device_id);
    
    // Event handling
    void start_event_processing();
    void stop_event_processing();
    
    // Mapping management per controller
    bool load_controller_mapping(const std::string& device_id, const std::string& mapping_file);
    bool set_controller_mapping(const std::string& device_id, const std::string& input, const std::string& output);
    
    // Remote control
    bool enable_remote_control(const std::string& device_id, const std::string& target_host);
    bool disable_remote_control(const std::string& device_id);
    
    // Voice alerts
    void enable_voice_alerts(bool enable = true);
    void set_voice_alert_callback(std::function<void(const std::string&)> callback);
    
    // Device monitoring
    void start_auto_detection();
    void stop_auto_detection();
    
    // Statistics and monitoring
    std::map<std::string, int> get_controller_statistics();
    std::vector<ControllerDevice> get_all_controllers();
    std::vector<ControllerDevice> get_connected_controllers();
    
    // Event callbacks
    void set_event_callback(std::function<void(const MultiControllerEvent&)> callback);
    void set_connection_callback(std::function<void(const std::string&, bool)> callback);

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace gamepad_mapper