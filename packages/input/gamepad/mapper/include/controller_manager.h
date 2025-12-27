#pragma once

#include <memory>
#include <string>
#include <vector>
#include <map>
#include <atomic>
#include <functional>
#include <thread>
#include <mutex>
#include "gamepad_events.h"

namespace gamepad_mapper {

// Forward declarations
struct ControllerInfo;

// Connection state enumeration
enum class ConnectionState {
    DISCONNECTED,
    CONNECTING,
    CONNECTED,
    RECONNECTING,
    ERROR
};

// Controller types
enum class ControllerType {
    UNKNOWN,
    XBOX,
    PLAYSTATION,
    NINTENDO,
    GENERIC
};

// Controller information structure
struct ControllerInfo {
    int id;  // Unique controller ID (0, 1, 2, ...)
    std::string name;
    std::string device_path;
    std::string mac_address;  // For Bluetooth devices
    ControllerType type;
    ConnectionState state;
    uint16_t vendor_id;
    uint16_t product_id;
    bool is_bluetooth;
    std::chrono::steady_clock::time_point last_seen;
    std::chrono::steady_clock::time_point connected_at;
};

// Controller event structure
struct ControllerEvent {
    int controller_id;
    GamepadEvent event;
};

// Callback types
using ControllerConnectedCallback = std::function<void(const ControllerInfo&)>;
using ControllerDisconnectedCallback = std::function<void(int controller_id)>;
using ControllerEventCallback = std::function<void(const ControllerEvent&)>;

// Controller Manager class
class ControllerManager {
public:
    ControllerManager();
    ~ControllerManager();

    // Initialization and lifecycle
    bool initialize();
    void shutdown();
    void start_monitoring();
    void stop_monitoring();

    // Controller enumeration
    std::vector<ControllerInfo> get_connected_controllers() const;
    ControllerInfo get_controller_info(int controller_id) const;
    bool is_controller_connected(int controller_id) const;

    // Event handling
    void set_controller_connected_callback(ControllerConnectedCallback callback);
    void set_controller_disconnected_callback(ControllerDisconnectedCallback callback);
    void set_controller_event_callback(ControllerEventCallback callback);

    // Device management
    bool connect_controller(const std::string& device_path);
    bool disconnect_controller(int controller_id);
    void scan_for_controllers();

    // Configuration
    void set_max_controllers(int max_controllers);
    int get_max_controllers() const;

    // Device detection settings
    void set_bluetooth_enabled(bool enabled);
    void set_hotplug_detection_enabled(bool enabled);

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace gamepad_mapper