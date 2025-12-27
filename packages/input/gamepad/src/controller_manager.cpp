#include "controller_manager.h"
#include "gamepad_mapper.h"  // For GamepadEvent
#include <iostream>
#include <fstream>
#include <algorithm>
#include <chrono>
#include <thread>
#include <mutex>
#include <atomic>
#include <cstring>
#include <unistd.h>
#include <linux/input.h>
#include <fcntl.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/inotify.h>
#include <poll.h>

// Bluetooth includes (if available)
#if WITH_BLUETOOTH
#include "bluetooth_scanner.h"
#include "bluetooth_connector.h"
#include "hid_parser.h"
#endif

using namespace std::chrono_literals;

namespace gamepad_mapper {

class ControllerManager::Impl {
public:
    Impl() : running_(false), max_controllers_(4), bluetooth_enabled_(true),
             hotplug_enabled_(true), next_controller_id_(0) {}

    ~Impl() {
        shutdown();
    }

    bool initialize() {
        std::lock_guard<std::mutex> lock(mutex_);

        // Initialize Bluetooth components if enabled
#if WITH_BLUETOOTH
        if (bluetooth_enabled_) {
            bluetooth_scanner_ = std::make_unique<BluetoothScanner>();
            bluetooth_connector_ = std::make_unique<BluetoothConnector>();
            hid_parser_ = std::make_shared<HIDParser>();

            if (!bluetooth_scanner_->initialize()) {
                std::cerr << "Warning: Failed to initialize Bluetooth scanner" << std::endl;
            }

            if (!bluetooth_connector_->initialize()) {
                std::cerr << "Warning: Failed to initialize Bluetooth connector" << std::endl;
            }

            bluetooth_connector_->set_hid_parser(hid_parser_);
        }
#endif

        // Initialize inotify for hotplug detection
        if (hotplug_enabled_) {
            init_hotplug_monitoring();
        }

        return true;
    }

    void shutdown() {
        stop_monitoring();

        std::lock_guard<std::mutex> lock(mutex_);
        controllers_.clear();

#if WITH_BLUETOOTH
        bluetooth_scanner_.reset();
        bluetooth_connector_.reset();
        hid_parser_.reset();
#endif
    }

    void start_monitoring() {
        if (running_) return;

        running_ = true;

        // Start device monitoring threads
        if (hotplug_enabled_) {
            hotplug_thread_ = std::thread(&Impl::hotplug_monitor_loop, this);
        }

        event_thread_ = std::thread(&Impl::event_monitor_loop, this);
        bluetooth_thread_ = std::thread(&Impl::bluetooth_monitor_loop, this);
    }

    void stop_monitoring() {
        running_ = false;

        if (event_thread_.joinable()) {
            event_thread_.join();
        }

        if (hotplug_thread_.joinable()) {
            hotplug_thread_.join();
        }

        if (bluetooth_thread_.joinable()) {
            bluetooth_thread_.join();
        }
    }

    std::vector<ControllerInfo> get_connected_controllers() const {
        std::lock_guard<std::mutex> lock(mutex_);
        std::vector<ControllerInfo> result;
        for (const auto& pair : controllers_) {
            if (pair.second.state == ConnectionState::CONNECTED) {
                result.push_back(pair.second);
            }
        }
        return result;
    }

    ControllerInfo get_controller_info(int controller_id) const {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = controllers_.find(controller_id);
        if (it != controllers_.end()) {
            return it->second;
        }
        return ControllerInfo{-1, "", "", "", ControllerType::UNKNOWN, ConnectionState::DISCONNECTED, 0, 0, false};
    }

    bool is_controller_connected(int controller_id) const {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = controllers_.find(controller_id);
        return it != controllers_.end() && it->second.state == ConnectionState::CONNECTED;
    }

    void set_controller_connected_callback(ControllerConnectedCallback callback) {
        std::lock_guard<std::mutex> lock(mutex_);
        connected_callback_ = callback;
    }

    void set_controller_disconnected_callback(ControllerDisconnectedCallback callback) {
        std::lock_guard<std::mutex> lock(mutex_);
        disconnected_callback_ = callback;
    }

    void set_controller_event_callback(ControllerEventCallback callback) {
        std::lock_guard<std::mutex> lock(mutex_);
        event_callback_ = callback;
    }

    bool connect_controller(const std::string& device_path) {
        std::lock_guard<std::mutex> lock(mutex_);

        // Check if we're already at max controllers
        if (controllers_.size() >= static_cast<size_t>(max_controllers_)) {
            std::cerr << "Maximum number of controllers reached (" << max_controllers_ << ")" << std::endl;
            return false;
        }

        // Check if this device is already connected
        for (const auto& pair : controllers_) {
            if (pair.second.device_path == device_path) {
                std::cout << "Controller already connected: " << device_path << std::endl;
                return true;
            }
        }

        // Create new controller info
        ControllerInfo info;
        info.id = next_controller_id_++;
        info.device_path = device_path;
        info.state = ConnectionState::CONNECTING;
        info.is_bluetooth = device_path.find("bluetooth:") == 0;
        info.connected_at = std::chrono::steady_clock::now();
        info.last_seen = info.connected_at;

        // Detect controller type and get device info
        if (!detect_controller_info(info)) {
            std::cerr << "Failed to detect controller info for: " << device_path << std::endl;
            return false;
        }

        // Open device file descriptor
        int fd = open_device_file(info);
        if (fd == -1) {
            std::cerr << "Failed to open device: " << device_path << std::endl;
            return false;
        }

        // Store controller info and file descriptor
        info.state = ConnectionState::CONNECTED;
        controllers_[info.id] = info;
        controller_fds_[info.id] = fd;

        std::cout << "Controller connected: " << info.name << " (ID: " << info.id << ")" << std::endl;

        // Notify callback
        if (connected_callback_) {
            connected_callback_(info);
        }

        return true;
    }

    bool disconnect_controller(int controller_id) {
        std::lock_guard<std::mutex> lock(mutex_);

        auto it = controllers_.find(controller_id);
        if (it == controllers_.end()) {
            return false;
        }

        ControllerInfo info = it->second;

        // Close file descriptor
        auto fd_it = controller_fds_.find(controller_id);
        if (fd_it != controller_fds_.end()) {
            close(fd_it->second);
            controller_fds_.erase(fd_it);
        }

        // Remove from controllers map
        controllers_.erase(it);

        std::cout << "Controller disconnected: " << info.name << " (ID: " << controller_id << ")" << std::endl;

        // Notify callback
        if (disconnected_callback_) {
            disconnected_callback_(controller_id);
        }

        return true;
    }

    void scan_for_controllers() {
        std::cout << "Scanning for controllers..." << std::endl;

        // Scan HID devices
        scan_hid_devices();

        // Scan input devices
        scan_input_devices();

        // Scan Bluetooth devices
#if WITH_BLUETOOTH
        if (bluetooth_enabled_ && bluetooth_scanner_) {
            scan_bluetooth_devices();
        }
#endif
    }

    void set_max_controllers(int max_controllers) {
        std::lock_guard<std::mutex> lock(mutex_);
        max_controllers_ = max_controllers;
    }

    int get_max_controllers() const {
        return max_controllers_;
    }

    void set_bluetooth_enabled(bool enabled) {
        std::lock_guard<std::mutex> lock(mutex_);
        bluetooth_enabled_ = enabled;
    }

    void set_hotplug_detection_enabled(bool enabled) {
        std::lock_guard<std::mutex> lock(mutex_);
        hotplug_enabled_ = enabled;
    }

private:
    bool detect_controller_info(ControllerInfo& info) {
        if (info.is_bluetooth) {
            // For Bluetooth devices, info should already be populated
            return true;
        }

        // Open device to get information
        int fd = open(info.device_path.c_str(), O_RDONLY);
        if (fd == -1) {
            return false;
        }

        // Get device name
        char name[256] = {0};
        if (ioctl(fd, EVIOCGNAME(sizeof(name)), name) >= 0) {
            info.name = name;
        }

        // Get vendor and product IDs
        struct input_id device_info;
        if (ioctl(fd, EVIOCGID, &device_info) >= 0) {
            info.vendor_id = device_info.vendor;
            info.product_id = device_info.product;
        }

        // Determine controller type
        info.type = detect_controller_type(info.name, info.vendor_id, info.product_id);

        close(fd);
        return true;
    }

    ControllerType detect_controller_type(const std::string& name, uint16_t vendor_id, uint16_t product_id) {
        // Check by name first
        std::string lower_name = name;
        std::transform(lower_name.begin(), lower_name.end(), lower_name.begin(), ::tolower);

        if (lower_name.find("xbox") != std::string::npos || lower_name.find("microsoft") != std::string::npos) {
            return ControllerType::XBOX;
        }
        if (lower_name.find("playstation") != std::string::npos || lower_name.find("dualshock") != std::string::npos ||
            lower_name.find("sony") != std::string::npos) {
            return ControllerType::PLAYSTATION;
        }
        if (lower_name.find("nintendo") != std::string::npos) {
            return ControllerType::NINTENDO;
        }

        // Check by vendor/product ID
        if (vendor_id == 0x045e) { // Microsoft
            return ControllerType::XBOX;
        }
        if (vendor_id == 0x054c) { // Sony
            return ControllerType::PLAYSTATION;
        }
        if (vendor_id == 0x057e) { // Nintendo
            return ControllerType::NINTENDO;
        }

        return ControllerType::GENERIC;
    }

    int open_device_file(const ControllerInfo& info) {
        if (info.is_bluetooth) {
            // Bluetooth devices don't use file descriptors in the same way
            return -1; // Special marker for Bluetooth devices
        }

        return open(info.device_path.c_str(), O_RDONLY | O_NONBLOCK);
    }

    void scan_hid_devices() {
        std::cout << "Scanning HID devices..." << std::endl;
        for (int i = 0; i < 16; i++) {  // Check more devices
            std::string hid_device = "/dev/hidraw" + std::to_string(i);
            if (access(hid_device.c_str(), R_OK) == 0) {
                connect_controller(hid_device);
            }
        }
    }

    void scan_input_devices() {
        std::cout << "Scanning input devices..." << std::endl;
        DIR* dir = opendir("/dev/input");
        if (!dir) return;

        struct dirent* entry;
        while ((entry = readdir(dir)) != nullptr) {
            if (entry->d_type == DT_CHR && strncmp(entry->d_name, "event", 5) == 0) {
                std::string device_path = "/dev/input/" + std::string(entry->d_name);
                if (is_gamepad_device(device_path)) {
                    connect_controller(device_path);
                }
            }
        }

        closedir(dir);
    }

    bool is_gamepad_device(const std::string& device_path) {
        int fd = open(device_path.c_str(), O_RDONLY);
        if (fd == -1) return false;

        char name[256] = {0};
        bool is_gamepad = false;

        if (ioctl(fd, EVIOCGNAME(sizeof(name)), name) >= 0) {
            std::string device_name = name;
            std::transform(device_name.begin(), device_name.end(), device_name.begin(), ::tolower);

            if (device_name.find("gamepad") != std::string::npos ||
                device_name.find("xbox") != std::string::npos ||
                device_name.find("playstation") != std::string::npos ||
                device_name.find("dualshock") != std::string::npos ||
                device_name.find("wireless controller") != std::string::npos) {
                is_gamepad = true;
            }
        }

        close(fd);
        return is_gamepad;
    }

#if WITH_BLUETOOTH
    void scan_bluetooth_devices() {
        std::cout << "Scanning Bluetooth devices..." << std::endl;
        auto devices = bluetooth_scanner_->scan_devices(3); // 3 second scan

        for (const auto& device : devices) {
            if (is_bluetooth_gamepad(device)) {
                std::string device_path = "bluetooth:" + device.mac_address;

                // Check if already connected
                bool already_connected = false;
                for (const auto& pair : controllers_) {
                    if (pair.second.mac_address == device.mac_address) {
                        already_connected = true;
                        break;
                    }
                }

                if (!already_connected) {
                    ControllerInfo info;
                    info.id = next_controller_id_++;
                    info.name = device.name;
                    info.device_path = device_path;
                    info.mac_address = device.mac_address;
                    info.vendor_id = device.vendor_id;
                    info.product_id = device.product_id;
                    info.type = detect_controller_type(device.name, device.vendor_id, device.product_id);
                    info.is_bluetooth = true;
                    info.state = ConnectionState::CONNECTING;
                    info.connected_at = std::chrono::steady_clock::now();
                    info.last_seen = info.connected_at;

                    // Try to connect
                    if (bluetooth_connector_->connect_device(device.mac_address)) {
                        info.state = ConnectionState::CONNECTED;
                        controllers_[info.id] = info;
                        bluetooth_controllers_[info.id] = device;

                        std::cout << "Bluetooth controller connected: " << info.name << " (ID: " << info.id << ")" << std::endl;

                        if (connected_callback_) {
                            connected_callback_(info);
                        }
                    }
                }
            }
        }
    }

    bool is_bluetooth_gamepad(const BluetoothDevice& device) {
        // Check device class or name for gamepad characteristics
        std::string name = device.name;
        std::transform(name.begin(), name.end(), name.begin(), ::tolower);

        return name.find("controller") != std::string::npos ||
               name.find("gamepad") != std::string::npos ||
               name.find("dualshock") != std::string::npos ||
               name.find("xbox") != std::string::npos ||
               name.find("joy-con") != std::string::npos;
    }
#endif

    void init_hotplug_monitoring() {
        inotify_fd_ = inotify_init1(IN_NONBLOCK);
        if (inotify_fd_ == -1) {
            std::cerr << "Failed to initialize inotify for hotplug monitoring" << std::endl;
            return;
        }

        // Monitor /dev/input and /dev directories
        inotify_add_watch(inotify_fd_, "/dev/input", IN_CREATE | IN_DELETE);
        inotify_add_watch(inotify_fd_, "/dev", IN_CREATE | IN_DELETE);
    }

    void hotplug_monitor_loop() {
        if (inotify_fd_ == -1) return;

        char buffer[4096];
        struct pollfd pfd = {inotify_fd_, POLLIN, 0};

        while (running_) {
            int poll_result = poll(&pfd, 1, 1000); // 1 second timeout

            if (poll_result > 0 && (pfd.revents & POLLIN)) {
                ssize_t length = read(inotify_fd_, buffer, sizeof(buffer));
                if (length > 0) {
                    process_hotplug_events(buffer, length);
                }
            }

            std::this_thread::sleep_for(500ms); // Check every 500ms
        }

        close(inotify_fd_);
        inotify_fd_ = -1;
    }

    void process_hotplug_events(const char* buffer, ssize_t length) {
        const struct inotify_event* event;
        for (char* ptr = const_cast<char*>(buffer); ptr < buffer + length;
             ptr += sizeof(struct inotify_event) + event->len) {

            event = reinterpret_cast<const struct inotify_event*>(ptr);

            if (event->len > 0) {
                std::string filename = event->name;

                if (filename.find("event") == 0 || filename.find("hidraw") == 0) {
                    std::string device_path = "/dev/";
                    if (filename.find("event") == 0) {
                        device_path += "input/";
                    }
                    device_path += filename;

                    if (event->mask & IN_CREATE) {
                        std::cout << "Device added: " << device_path << std::endl;
                        // Delay connection to allow device initialization
                        std::this_thread::sleep_for(500ms);
                        connect_controller(device_path);
                    } else if (event->mask & IN_DELETE) {
                        std::cout << "Device removed: " << device_path << std::endl;
                        // Find and disconnect controller
                        std::lock_guard<std::mutex> lock(mutex_);
                        for (const auto& pair : controllers_) {
                            if (pair.second.device_path == device_path) {
                                disconnect_controller(pair.first);
                                break;
                            }
                        }
                    }
                }
            }
        }
    }

    void event_monitor_loop() {
        while (running_) {
            std::lock_guard<std::mutex> lock(mutex_);

            // Poll all connected controllers
            for (auto& pair : controllers_) {
                int controller_id = pair.first;
                ControllerInfo& info = pair.second;

                if (info.state == ConnectionState::CONNECTED) {
                    poll_controller_events(controller_id, info);
                }
            }

            std::this_thread::sleep_for(10ms); // ~100Hz polling
        }
    }

    void poll_controller_events(int controller_id, ControllerInfo& info) {
        GamepadEvent event;

        if (poll_single_controller_event(info, event)) {
            // Update last seen timestamp
            info.last_seen = std::chrono::steady_clock::now();

            // Create controller event and notify callback
            ControllerEvent controller_event{controller_id, event};

            if (event_callback_) {
                event_callback_(controller_event);
            }
        }
    }

    bool poll_single_controller_event(const ControllerInfo& info, GamepadEvent& event) {
        if (info.is_bluetooth) {
#if WITH_BLUETOOTH
            if (bluetooth_connector_ && bluetooth_connector_->is_connected()) {
                HIDReport report;
                if (bluetooth_connector_->read_hid_report(report)) {
                    // Parse HID report using the HID parser
                    if (hid_parser_ && hid_parser_->parse_report(report.data, event)) {
                        return true;
                    }
                }
            }
#endif
            return false;
        }

        // Handle regular input device
        auto fd_it = controller_fds_.find(info.id);
        if (fd_it == controller_fds_.end() || fd_it->second == -1) {
            return false;
        }

        int fd = fd_it->second;

        if (info.device_path.find("/dev/hidraw") != std::string::npos) {
            // HID device handling
            unsigned char buffer[64];
            ssize_t n = read(fd, buffer, sizeof(buffer));

            if (n > 0) {
                // Simplified HID parsing (same as original implementation)
                if (n >= 5) {
                    if (buffer[1] != 0) {
                        event.type = GamepadEvent::BUTTON;
                        event.button.code = buffer[1];
                        event.button.pressed = true;
                        return true;
                    }
                    // Add more HID parsing as needed
                }
            }
        } else {
            // Standard input event handling
            struct input_event ev;
            ssize_t n = read(fd, &ev, sizeof(ev));

            if (n == sizeof(ev)) {
                if (ev.type == EV_KEY) {
                    event.type = GamepadEvent::BUTTON;
                    event.button.code = ev.code;
                    event.button.pressed = (ev.value != 0);
                    return true;
                } else if (ev.type == EV_ABS) {
                    event.type = GamepadEvent::AXIS;
                    event.axis.code = ev.code;
                    event.axis.value = ev.value;
                    return true;
                }
            }
        }

        return false;
    }

    void bluetooth_monitor_loop() {
#if WITH_BLUETOOTH
        while (running_) {
            if (bluetooth_enabled_) {
                scan_bluetooth_devices();
            }
            std::this_thread::sleep_for(5s); // Scan every 5 seconds
        }
#endif
    }

    // Member variables
    mutable std::mutex mutex_;
    std::atomic<bool> running_;
    int max_controllers_;
    bool bluetooth_enabled_;
    bool hotplug_enabled_;
    int next_controller_id_;

    std::map<int, ControllerInfo> controllers_;
    std::map<int, int> controller_fds_; // controller_id -> file descriptor

    // Callbacks
    ControllerConnectedCallback connected_callback_;
    ControllerDisconnectedCallback disconnected_callback_;
    ControllerEventCallback event_callback_;

    // Monitoring threads
    std::thread event_thread_;
    std::thread hotplug_thread_;
    std::thread bluetooth_thread_;

    // Hotplug monitoring
    int inotify_fd_;

#if WITH_BLUETOOTH
    // Bluetooth components
    std::unique_ptr<BluetoothScanner> bluetooth_scanner_;
    std::unique_ptr<BluetoothConnector> bluetooth_connector_;
    std::shared_ptr<HIDParser> hid_parser_;
    std::map<int, BluetoothDevice> bluetooth_controllers_;
#endif
};

// Public interface implementation
ControllerManager::ControllerManager() : impl_(std::make_unique<Impl>()) {}
ControllerManager::~ControllerManager() = default;

bool ControllerManager::initialize() { return impl_->initialize(); }
void ControllerManager::shutdown() { impl_->shutdown(); }
void ControllerManager::start_monitoring() { impl_->start_monitoring(); }
void ControllerManager::stop_monitoring() { impl_->stop_monitoring(); }

std::vector<ControllerInfo> ControllerManager::get_connected_controllers() const {
    return impl_->get_connected_controllers();
}

ControllerInfo ControllerManager::get_controller_info(int controller_id) const {
    return impl_->get_controller_info(controller_id);
}

bool ControllerManager::is_controller_connected(int controller_id) const {
    return impl_->is_controller_connected(controller_id);
}

void ControllerManager::set_controller_connected_callback(ControllerConnectedCallback callback) {
    impl_->set_controller_connected_callback(callback);
}

void ControllerManager::set_controller_disconnected_callback(ControllerDisconnectedCallback callback) {
    impl_->set_controller_disconnected_callback(callback);
}

void ControllerManager::set_controller_event_callback(ControllerEventCallback callback) {
    impl_->set_controller_event_callback(callback);
}

bool ControllerManager::connect_controller(const std::string& device_path) {
    return impl_->connect_controller(device_path);
}

bool ControllerManager::disconnect_controller(int controller_id) {
    return impl_->disconnect_controller(controller_id);
}

void ControllerManager::scan_for_controllers() {
    impl_->scan_for_controllers();
}

void ControllerManager::set_max_controllers(int max_controllers) {
    impl_->set_max_controllers(max_controllers);
}

int ControllerManager::get_max_controllers() const {
    return impl_->get_max_controllers();
}

void ControllerManager::set_bluetooth_enabled(bool enabled) {
    impl_->set_bluetooth_enabled(enabled);
}

void ControllerManager::set_hotplug_detection_enabled(bool enabled) {
    impl_->set_hotplug_detection_enabled(enabled);
}

} // namespace gamepad_mapper