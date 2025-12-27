#include "gamepad_mapper.h"
#include "controller_manager.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <chrono>
#include <thread>
#include <cstring>
#include <unistd.h>
#include <linux/input.h>
#include <fcntl.h>
#include <dirent.h>
#include <sys/stat.h>
#include <nlohmann/json.hpp>

// Backend includes (conditionally compiled)
#ifdef WITH_X11
#include "backends/x11_simulator.h"
#endif

#ifdef WITH_WAYLAND
#include "backends/wayland_simulator.h"
#endif

#ifdef WITH_KDE
#include "backends/kde_simulator.h"
#endif

#ifdef WITH_SDL2
#include "backends/sdl2_simulator.h"
#endif

#ifdef WITH_UINPUT
#include "backends/uinput_simulator.h"
#endif

#ifdef WITH_MCP
#include "mcp_server.h"
#endif

#if WITH_BLUETOOTH
#include "bluetooth_scanner.h"
#include "bluetooth_connector.h"
#include "hid_parser.h"
#endif

#ifdef WITH_CLIPBOARD
#include "clipboard_monitor.h"
#endif
#include "voice_alerts.h"
#include "kde_connect_client.h"

using json = nlohmann::json;

namespace gamepad_mapper {

// Backend type enumeration
enum class BackendType {
    X11_BACKEND,
    WAYLAND_BACKEND,
    KDE_BACKEND,
    SDL2_BACKEND,
    UINPUT_BACKEND,
    NONE
};

// Backend priority (higher = preferred)
const std::map<BackendType, int> backend_priorities = {
    {BackendType::KDE_BACKEND, 100},
    {BackendType::WAYLAND_BACKEND, 80},
    {BackendType::X11_BACKEND, 60},
    {BackendType::SDL2_BACKEND, 40},
    {BackendType::UINPUT_BACKEND, 20},
};

// Gamepad button mappings
const std::map<std::string, int> gamepad_buttons = {
    {"A", BTN_A},
    {"B", BTN_B},
    {"X", BTN_X},
    {"Y", BTN_Y},
    {"LB", BTN_TL},
    {"RB", BTN_TR},
    {"LT", BTN_TL2},
    {"RT", BTN_TR2},
    {"SELECT", BTN_SELECT},
    {"START", BTN_START},
    {"LS", BTN_THUMBL},
    {"RS", BTN_THUMBR},
    {"DPAD_UP", BTN_DPAD_UP},
    {"DPAD_DOWN", BTN_DPAD_DOWN},
    {"DPAD_LEFT", BTN_DPAD_LEFT},
    {"DPAD_RIGHT", BTN_DPAD_RIGHT}
};

// Gamepad axis mappings
const std::map<std::string, int> gamepad_axes = {
    {"LEFT_X", ABS_X},
    {"LEFT_Y", ABS_Y},
    {"RIGHT_X", ABS_RX},
    {"RIGHT_Y", ABS_RY},
    {"LEFT_TRIGGER", ABS_Z},
    {"RIGHT_TRIGGER", ABS_RZ}
};

// Keyboard key mappings
const std::map<std::string, int> keyboard_keys = {
    {"ESC", KEY_ESC},
    {"1", KEY_1}, {"2", KEY_2}, {"3", KEY_3}, {"4", KEY_4}, {"5", KEY_5},
    {"Q", KEY_Q}, {"W", KEY_W}, {"E", KEY_E}, {"R", KEY_R}, {"T", KEY_T},
    {"A", KEY_A}, {"S", KEY_S}, {"D", KEY_D}, {"F", KEY_F}, {"G", KEY_G},
    {"Z", KEY_Z}, {"X", KEY_X}, {"C", KEY_C}, {"V", KEY_V}, {"B", KEY_B},
    {"CTRL", KEY_LEFTCTRL}, {"ALT", KEY_LEFTALT}, {"SHIFT", KEY_LEFTSHIFT},
    {"TAB", KEY_TAB}, {"SPACE", KEY_SPACE}, {"ENTER", KEY_ENTER},
    {"BACKSPACE", KEY_BACKSPACE}, {"UP", KEY_UP}, {"DOWN", KEY_DOWN},
    {"LEFT", KEY_LEFT}, {"RIGHT", KEY_RIGHT}
};

class GamepadMapper::Impl {
public:
    Impl() : current_backend_(BackendType::NONE), running_(false)
#if WITH_BLUETOOTH
             , bluetooth_scanner_(nullptr), bluetooth_connector_(nullptr), hid_parser_(nullptr)
#endif
    {
        controller_manager_ = std::make_unique<ControllerManager>();
    }
    ~Impl() { stop(); }

    bool initialize() {
        // Initialize ControllerManager
        if (!controller_manager_->initialize()) {
            std::cerr << "Failed to initialize ControllerManager!" << std::endl;
            return false;
        }

        // Set up controller event callbacks
        controller_manager_->set_controller_connected_callback(
            [this](const ControllerInfo& info) {
                on_controller_connected(info);
            }
        );

        controller_manager_->set_controller_disconnected_callback(
            [this](int controller_id) {
                on_controller_disconnected(controller_id);
            }
        );

        controller_manager_->set_controller_event_callback(
            [this](const ControllerEvent& event) {
                process_controller_event(event);
            }
        );

        // Initialize Bluetooth components if available (legacy support)
#if WITH_BLUETOOTH
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
        use_bluetooth_device_ = false;
#endif

        // Detect available backends
        BackendType detected = detect_backend();
        if (detected == BackendType::NONE) {
            std::cerr << "No suitable input backend detected!" << std::endl;
            return false;
        }

        // Initialize the selected backend
        if (!initialize_backend(detected)) {
            std::cerr << "Failed to initialize backend!" << std::endl;
            return false;
        }

        // Load default mappings
        if (!load_mappings("config/default_mappings.json")) {
            std::cout << "Warning: Could not load default mappings, using empty configuration" << std::endl;
        }

        // Start controller monitoring
        controller_manager_->start_monitoring();

        // Perform initial scan
        controller_manager_->scan_for_controllers();

        return true;
    }

    void start() {
        if (running_) return;

        running_ = true;
        // Event processing is now handled by ControllerManager
        // The worker thread is no longer needed for the main event loop
    }

    void stop() {
        running_ = false;
        controller_manager_->stop_monitoring();
        cleanup_backend();
    }

    bool load_mappings(const std::string& config_file) {
        try {
            std::ifstream file(config_file);
            if (!file.is_open()) {
                return false;
            }

            json config;
            file >> config;

            button_mappings_.clear();
            axis_mappings_.clear();

            // Load button mappings
            if (config.contains("mappings")) {
                for (const auto& mapping : config["mappings"].items()) {
                    std::string input_name = mapping.key();
                    std::string output_action = mapping.value();

                    // Look up the button code from the name
                    auto button_it = gamepad_buttons.find(input_name);
                    if (button_it != gamepad_buttons.end()) {
                        button_mappings_[button_it->second] = output_action;
                    }
                }
            }

            // Load analog/axis mappings
            if (config.contains("analog_mappings")) {
                for (const auto& mapping : config["analog_mappings"].items()) {
                    std::string input_name = mapping.key();
                    std::string output_action = mapping.value();

                    // Look up the axis code from the name
                    auto axis_it = gamepad_axes.find(input_name);
                    if (axis_it != gamepad_axes.end()) {
                        axis_mappings_[axis_it->second] = output_action;
                    }
                }
            }

            // Load Bluetooth-specific mappings if available
#if WITH_BLUETOOTH
            load_bluetooth_mappings();
#endif

            return true;
        } catch (const std::exception& e) {
            std::cerr << "Error loading mappings: " << e.what() << std::endl;
            return false;
        }
    }

    bool add_mapping(const std::string& input, const std::string& output) {
        mappings_[input] = output;
        return true;
    }

    bool remove_mapping(const std::string& input) {
        return mappings_.erase(input) > 0;
    }

    // Controller management methods
    std::vector<ControllerInfo> get_connected_controllers() const {
        return controller_manager_->get_connected_controllers();
    }

    ControllerInfo get_controller_info(int controller_id) const {
        return controller_manager_->get_controller_info(controller_id);
    }

    bool is_controller_connected(int controller_id) const {
        return controller_manager_->is_controller_connected(controller_id);
    }

    bool load_controller_mappings(int controller_id, const std::string& config_file) {
        try {
            std::ifstream file(config_file);
            if (!file.is_open()) {
                return false;
            }

            json config;
            file >> config;

            // Store per-controller mappings
            controller_mappings_[controller_id].clear();

            // Load button mappings
            if (config.contains("mappings")) {
                for (const auto& mapping : config["mappings"].items()) {
                    std::string input_name = mapping.key();
                    std::string output_action = mapping.value();

                    // Look up the button code from the name
                    auto button_it = gamepad_buttons.find(input_name);
                    if (button_it != gamepad_buttons.end()) {
                        controller_mappings_[controller_id][button_it->second] = output_action;
                    }
                }
            }

            // Load analog/axis mappings
            if (config.contains("analog_mappings")) {
                for (const auto& mapping : config["analog_mappings"].items()) {
                    std::string input_name = mapping.key();
                    std::string output_action = mapping.value();

                    // Look up the axis code from the name
                    auto axis_it = gamepad_axes.find(input_name);
                    if (axis_it != gamepad_axes.end()) {
                        controller_axis_mappings_[controller_id][axis_it->second] = output_action;
                    }
                }
            }

            return true;
        } catch (const std::exception& e) {
            std::cerr << "Error loading controller mappings: " << e.what() << std::endl;
            return false;
        }
    }

    bool set_controller_profile(int controller_id, const std::string& profile_name) {
        std::string config_file = "config/" + profile_name + "_mappings.json";
        return load_controller_mappings(controller_id, config_file);
    }

    void scan_for_controllers() {
        controller_manager_->scan_for_controllers();
    }

    void set_max_controllers(int max_controllers) {
        controller_manager_->set_max_controllers(max_controllers);
    }

#ifdef WITH_CLIPBOARD
    bool initialize_clipboard_monitor() {
        if (clipboard_monitor_) {
            return true; // Already initialized
        }

        clipboard_monitor_ = std::make_unique<ClipboardMonitor>();
        if (!clipboard_monitor_->initialize()) {
            std::cerr << "Failed to initialize clipboard monitor" << std::endl;
            clipboard_monitor_.reset();
            return false;
        }

        std::cout << "Clipboard monitor initialized successfully" << std::endl;
        return true;
    }

    void start_clipboard_monitoring() {
        if (clipboard_monitor_) {
            clipboard_monitor_->start();
        }
    }

    void stop_clipboard_monitoring() {
        if (clipboard_monitor_) {
            clipboard_monitor_->stop();
        }
    }

    bool is_clipboard_monitoring() const {
        return clipboard_monitor_ && clipboard_monitor_->is_monitoring();
    }

    ClipboardContent get_current_content() {
        if (clipboard_monitor_) {
            return clipboard_monitor_->get_current_content();
        }
        return ClipboardContent();
    }

    bool set_text_content(const std::string& text) {
        if (clipboard_monitor_) {
            return clipboard_monitor_->set_text_content(text);
        }
        return false;
    }

    bool clear_clipboard() {
        if (clipboard_monitor_) {
            return clipboard_monitor_->clear_clipboard();
        }
        return false;
    }
#endif

    bool initialize_voice_alerts() {
        if (voice_alerts_) {
            return true; // Already initialized
        }

        voice_alerts_ = std::make_unique<VoiceAlerts>();
        if (!voice_alerts_->initialize()) {
            std::cerr << "Failed to initialize voice alerts system" << std::endl;
            voice_alerts_.reset();
            return false;
        }

        std::cout << "Voice alerts system initialized successfully" << std::endl;
        return true;
    }

    void start_voice_alerts() {
        if (voice_alerts_) {
            voice_alerts_->start();
        }
    }

    void stop_voice_alerts() {
        if (voice_alerts_) {
            voice_alerts_->stop();
        }
    }

    bool is_voice_alerts_enabled() const {
        return voice_alerts_ && voice_alerts_->is_enabled();
    }

    bool initialize_kde_connect() {
        if (kde_connect_client_) {
            return true; // Already initialized
        }

        kde_connect_client_ = std::make_unique<KDEConnectClient>();
        if (!kde_connect_client_->initialize()) {
            std::cerr << "Failed to initialize KDE Connect client" << std::endl;
            kde_connect_client_.reset();
            return false;
        }

        // Register clipboard sync callback
        kde_connect_client_->register_clipboard_received_callback(
            [this](const std::string& content) {
                if (clipboard_monitor_) {
                    clipboard_monitor_->set_text_content(content);
                }
            }
        );

        std::cout << "KDE Connect client initialized successfully" << std::endl;
        return true;
    }

    void start_kde_connect() {
        if (kde_connect_client_) {
            kde_connect_client_->start();
        }
    }

    void stop_kde_connect() {
        if (kde_connect_client_) {
            kde_connect_client_->stop();
        }
    }

    bool is_kde_connect_enabled() const {
        return kde_connect_client_ && kde_connect_client_->is_running();
    }

private:
    // Controller event callbacks
    void on_controller_connected(const ControllerInfo& info) {
        std::cout << "Controller connected: " << info.name << " (ID: " << info.id << ")" << std::endl;

        // Voice alert for controller connection
        if (voice_alerts_) {
            voice_alerts_->alert_controller_connected(info.name);
        }

        // Load default mappings for this controller
        if (controller_mappings_[info.id].empty()) {
            load_controller_mappings(info.id, "config/default_mappings.json");
        }
    }

    void on_controller_disconnected(int controller_id) {
        std::cout << "Controller disconnected: ID " << controller_id << std::endl;

        // Voice alert for controller disconnection
        if (voice_alerts_) {
            voice_alerts_->alert_controller_disconnected("Controller " + std::to_string(controller_id));
        }

        // Clean up controller-specific mappings
        controller_mappings_.erase(controller_id);
        controller_axis_mappings_.erase(controller_id);
    }

    void process_controller_event(const ControllerEvent& controller_event) {
        if (!backend_) return;

        int controller_id = controller_event.controller_id;
        const GamepadEvent& event = controller_event.event;

        // Use controller-specific mappings if available, otherwise fall back to global mappings
        const auto& button_map = controller_mappings_.count(controller_id) ?
                                controller_mappings_[controller_id] : button_mappings_;
        const auto& axis_map = controller_axis_mappings_.count(controller_id) ?
                              controller_axis_mappings_[controller_id] : axis_mappings_;

        // Convert gamepad event to keyboard/mouse action
        if (event.type == GamepadEvent::BUTTON) {
            auto it = button_map.find(event.button.code);
            if (it != button_map.end()) {
                const std::string& action = it->second;
                if (action.find("KEY_") == 0) {
                    // Keyboard key
                    std::string key_name = action.substr(4);
                    auto key_it = keyboard_keys.find(key_name);
                    if (key_it != keyboard_keys.end()) {
                        if (event.button.pressed) {
                            backend_->send_key_press(key_it->second);
                        } else {
                            backend_->send_key_release(key_it->second);
                        }
                    }
                } else if (action.find("MOUSE_") == 0) {
                    // Mouse action
                    if (action == "MOUSE_LEFT_CLICK" && event.button.pressed) {
                        backend_->send_mouse_click(MouseButton::LEFT);
                    } else if (action == "MOUSE_RIGHT_CLICK" && event.button.pressed) {
                        backend_->send_mouse_click(MouseButton::RIGHT);
                    }
                }
            }
        } else if (event.type == GamepadEvent::AXIS) {
            auto it = axis_map.find(event.axis.code);
            if (it != axis_map.end()) {
                const std::string& action = it->second;
                if (action == "MOUSE_MOVE_X") {
                    backend_->send_mouse_move(event.axis.value / 32767.0f * 10, 0);
                } else if (action == "MOUSE_MOVE_Y") {
                    backend_->send_mouse_move(0, event.axis.value / 32767.0f * 10);
                }
            }
        }
    }

    BackendType detect_backend() {
        std::vector<std::pair<BackendType, int>> available_backends;

        // Check KDE environment first (highest priority)
        if (is_kde_environment() && has_kwin_dbus()) {
#ifdef WITH_KDE
            available_backends.emplace_back(BackendType::KDE_BACKEND, backend_priorities.at(BackendType::KDE_BACKEND));
#endif
        }

        // Check Wayland
        if (is_wayland_session()) {
#ifdef WITH_WAYLAND
            available_backends.emplace_back(BackendType::WAYLAND_BACKEND, backend_priorities.at(BackendType::WAYLAND_BACKEND));
#endif
        }

        // Check X11
        if (has_x11_display()) {
#ifdef WITH_X11
            available_backends.emplace_back(BackendType::X11_BACKEND, backend_priorities.at(BackendType::X11_BACKEND));
#endif
        }

        // Check SDL2 (cross-platform fallback)
#ifdef WITH_SDL2
        available_backends.emplace_back(BackendType::SDL2_BACKEND, backend_priorities.at(BackendType::SDL2_BACKEND));
#endif

        // UInput as last resort
#ifdef WITH_UINPUT
        available_backends.emplace_back(BackendType::UINPUT_BACKEND, backend_priorities.at(BackendType::UINPUT_BACKEND));
#endif

        // Sort by priority and return highest
        if (!available_backends.empty()) {
            std::sort(available_backends.begin(), available_backends.end(),
                     [](const auto& a, const auto& b) { return a.second > b.second; });
            return available_backends[0].first;
        }

        return BackendType::NONE;
    }

    bool initialize_backend(BackendType type) {
        cleanup_backend(); // Clean up any existing backend

        try {
            switch (type) {
#ifdef WITH_X11
                case BackendType::X11_BACKEND:
                    backend_ = std::make_unique<X11Simulator>();
                    std::cout << "Using X11 backend" << std::endl;
                    break;
#endif

#ifdef WITH_WAYLAND
                case BackendType::WAYLAND_BACKEND:
                    backend_ = std::make_unique<WaylandSimulator>();
                    std::cout << "Using Wayland backend" << std::endl;
                    break;
#endif

#ifdef WITH_KDE
                case BackendType::KDE_BACKEND:
                    backend_ = std::make_unique<KDESimulator>();
                    std::cout << "Using KDE backend" << std::endl;
                    break;
#endif

#ifdef WITH_SDL2
                case BackendType::SDL2_BACKEND:
                    backend_ = std::make_unique<SDL2Simulator>();
                    std::cout << "Using SDL2 backend" << std::endl;
                    break;
#endif

#ifdef WITH_UINPUT
                case BackendType::UINPUT_BACKEND:
                    backend_ = std::make_unique<UInputSimulator>();
                    std::cout << "Using UInput backend" << std::endl;
                    break;
#endif

                default:
                    return false;
            }

            current_backend_ = type;
            return backend_->initialize();
        } catch (const std::exception& e) {
            std::cerr << "Backend initialization failed: " << e.what() << std::endl;
            return false;
        }
    }

    void cleanup_backend() {
        if (backend_) {
            backend_->cleanup();
            backend_.reset();
        }
        current_backend_ = BackendType::NONE;
    }

    bool is_kde_environment() const {
        const char* desktop = getenv("XDG_CURRENT_DESKTOP");
        return desktop && (strcmp(desktop, "KDE") == 0 || strcmp(desktop, "plasma") == 0);
    }

    bool has_kwin_dbus() const {
        // Check if KWin DBus interface is available
        return system("dbus-send --session --dest=org.kde.KWin --type=method_call "
                     "/KWin org.freedesktop.DBus.Introspectable.Introspect > /dev/null 2>&1") == 0;
    }

    bool is_wayland_session() const {
        const char* wayland = getenv("WAYLAND_DISPLAY");
        return wayland && strlen(wayland) > 0;
    }

    bool has_x11_display() const {
        const char* display = getenv("DISPLAY");
        return display && strlen(display) > 0;
    }

    void event_loop() {
        while (running_) {
            // Poll for gamepad events
            GamepadEvent event;
            if (poll_gamepad_event(event)) {
                process_event(event);
            }

            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }

    bool poll_gamepad_event(GamepadEvent& event) {
        // Find gamepad device
        static std::string gamepad_device = find_gamepad_device();
        if (gamepad_device.empty()) {
            return false;
        }

        // Handle Bluetooth devices
#if WITH_BLUETOOTH
        if (use_bluetooth_device_ && bluetooth_connector_ && bluetooth_connector_->is_connected()) {
            HIDReport report;
            if (bluetooth_connector_->read_hid_report(report)) {
                // Parse HID report using the HID parser
                if (hid_parser_ && hid_parser_->parse_report(report.data, event)) {
                    return true;
                }
            }
            return false;
        }
#endif

        // Handle local devices (existing logic)
        static int fd = -1;
        if (fd == -1) {
            fd = open(gamepad_device.c_str(), O_RDONLY | O_NONBLOCK);
            if (fd == -1) return false;
        }

        // Check if this is a HID device
        if (gamepad_device.find("/dev/hidraw") != std::string::npos) {
            unsigned char buffer[64];
            ssize_t n = read(fd, buffer, sizeof(buffer));
            
            if (n > 0) {
                // Parse HID data for DualShock 4
                // This is a simplified parser - in a real implementation,
                // you'd need to properly parse the HID report format
                if (n >= 5) {
                    // Check for button presses (simplified)
                    if (buffer[1] != 0) {
                        event.type = GamepadEvent::BUTTON;
                        event.button.code = buffer[1];
                        event.button.pressed = true;
                        return true;
                    }
                    if (buffer[2] != 0) {
                        event.type = GamepadEvent::BUTTON;
                        event.button.code = buffer[2] + 8; // Offset for different button set
                        event.button.pressed = true;
                        return true;
                    }
                    if (buffer[3] != 0) {
                        event.type = GamepadEvent::AXIS;
                        event.axis.code = 0; // Left stick X
                        event.axis.value = (int)buffer[3] - 128; // Center around 0
                        return true;
                    }
                    if (buffer[4] != 0) {
                        event.type = GamepadEvent::AXIS;
                        event.axis.code = 1; // Left stick Y
                        event.axis.value = (int)buffer[4] - 128; // Center around 0
                        return true;
                    }
                }
            }
        } else {
            // Original input event handling
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

    std::string find_gamepad_device() {
        // First try Bluetooth devices
#if WITH_BLUETOOTH
        if (bluetooth_scanner_) {
            auto bt_devices = bluetooth_scanner_->scan_devices(5); // 5 second scan
            if (!bt_devices.empty()) {
                std::cout << "Found Bluetooth gamepad: " << bt_devices[0].name
                         << " (" << bt_devices[0].mac_address << ")" << std::endl;

                // Configure HID parser for this device
                hid_parser_->configure_for_device(bt_devices[0].vendor_id, bt_devices[0].product_id);

                // Attempt to connect
                if (bluetooth_connector_->connect_device(bt_devices[0].mac_address)) {
#if WITH_BLUETOOTH
                    use_bluetooth_device_ = true;
#endif
                    return "bluetooth:" + bt_devices[0].mac_address;
                }
            }
        }
#endif

        // Try HID devices first (for DualShock 4)
        std::cout << "Searching for HID gamepad devices..." << std::endl;
        for (int i = 0; i < 10; i++) {
            std::string hid_device = "/dev/hidraw" + std::to_string(i);
            int fd = open(hid_device.c_str(), O_RDONLY | O_NONBLOCK);
            if (fd != -1) {
                std::cout << "Testing HID device: " << hid_device << std::endl;
                // Test if this device produces data (likely a gamepad)
                // Wait a bit for data to be available
                for (int attempt = 0; attempt < 10; attempt++) {
                    unsigned char buffer[64];
                    int bytes_read = read(fd, buffer, sizeof(buffer));
                    if (bytes_read > 0) {
                        close(fd);
                        std::cout << "Found HID gamepad device: " << hid_device << " (read " << bytes_read << " bytes)" << std::endl;
#if WITH_BLUETOOTH
                        use_bluetooth_device_ = false;
#endif
                        return hid_device;
                    }
                    usleep(100000); // 100ms
                }
                close(fd);
            } else {
                std::cout << "Cannot open HID device: " << hid_device << " (errno: " << errno << ")" << std::endl;
            }
        }
        std::cout << "No HID gamepad devices found, trying input devices..." << std::endl;

        // Fall back to local input devices
        DIR* dir = opendir("/dev/input");
        if (!dir) return "";

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
                            close(fd);
                            closedir(dir);
#if WITH_BLUETOOTH
                            use_bluetooth_device_ = false;
#endif
                            return device_path;
                        }
                    }
                    close(fd);
                }
            }
        }

        closedir(dir);
        return "";
    }

    void process_event(const GamepadEvent& event) {
        if (!backend_) return;

        // Convert gamepad event to keyboard/mouse action
        if (event.type == GamepadEvent::BUTTON) {
            auto it = button_mappings_.find(event.button.code);
            if (it != button_mappings_.end()) {
                const std::string& action = it->second;
                if (action.find("KEY_") == 0) {
                    // Keyboard key
                    std::string key_name = action.substr(4);
                    auto key_it = keyboard_keys.find(key_name);
                    if (key_it != keyboard_keys.end()) {
                        if (event.button.pressed) {
                            backend_->send_key_press(key_it->second);
                        } else {
                            backend_->send_key_release(key_it->second);
                        }
                    }
                } else if (action.find("MOUSE_") == 0) {
                    // Mouse action
                    if (action == "MOUSE_LEFT_CLICK" && event.button.pressed) {
                        backend_->send_mouse_click(MouseButton::LEFT);
                    } else if (action == "MOUSE_RIGHT_CLICK" && event.button.pressed) {
                        backend_->send_mouse_click(MouseButton::RIGHT);
                    }
                }
            }
        } else if (event.type == GamepadEvent::AXIS) {
            auto it = axis_mappings_.find(event.axis.code);
            if (it != axis_mappings_.end()) {
                const std::string& action = it->second;
                if (action == "MOUSE_MOVE_X") {
                    backend_->send_mouse_move(event.axis.value / 32767.0f * 10, 0);
                } else if (action == "MOUSE_MOVE_Y") {
                    backend_->send_mouse_move(0, event.axis.value / 32767.0f * 10);
                }
            }
        }
    }

#if WITH_BLUETOOTH
    bool load_bluetooth_mappings() {
        try {
            std::ifstream file("config/bluetooth_mappings.json");
            if (!file.is_open()) {
                std::cout << "Warning: Could not load Bluetooth mappings file" << std::endl;
                return false;
            }

            json bt_config;
            file >> bt_config;

            // Store Bluetooth configuration for later use
            bluetooth_config_ = bt_config;

            // If using a Bluetooth device, load device-specific mappings
            if (use_bluetooth_device_ && bluetooth_connector_ && bluetooth_connector_->is_connected()) {
                auto device = bluetooth_connector_->get_connected_device();

                // Find device configuration by vendor/product ID
                if (bt_config.contains("devices")) {
                    for (const auto& device_config : bt_config["devices"]) {
                        std::string vendor_str = device_config["vendor_id"];
                        std::string product_str = device_config["product_id"];

                        uint16_t vendor_id = static_cast<uint16_t>(std::stoul(vendor_str, nullptr, 16));
                        uint16_t product_id = static_cast<uint16_t>(std::stoul(product_str, nullptr, 16));

                        if (vendor_id == device.vendor_id && product_id == device.product_id) {
                            std::cout << "Loading mappings for " << device_config["description"] << std::endl;

                            // Load device-specific button mappings
                            if (device_config.contains("mappings")) {
                                for (const auto& mapping : device_config["mappings"].items()) {
                                    std::string input_name = mapping.key();
                                    std::string output_action = mapping.value();

                                    // Convert input names to button codes (simplified mapping)
                                    int button_code = get_bluetooth_button_code(input_name);
                                    if (button_code != -1) {
                                        button_mappings_[button_code] = output_action;
                                    }
                                }
                            }

                            // Load device-specific axis mappings
                            if (device_config.contains("analog_mappings")) {
                                for (const auto& mapping : device_config["analog_mappings"].items()) {
                                    std::string input_name = mapping.key();
                                    std::string output_action = mapping.value();

                                    // Convert input names to axis codes (simplified mapping)
                                    int axis_code = get_bluetooth_axis_code(input_name);
                                    if (axis_code != -1) {
                                        axis_mappings_[axis_code] = output_action;
                                    }
                                }
                            }

                            break;
                        }
                    }
                }
            }

            return true;
        } catch (const std::exception& e) {
            std::cerr << "Error loading Bluetooth mappings: " << e.what() << std::endl;
            return false;
        }
    }

    int get_bluetooth_button_code(const std::string& button_name) {
        // Map Bluetooth HID button names to Linux input codes
        static const std::map<std::string, int> bt_button_map = {
            {"A", BTN_A}, {"B", BTN_B}, {"X", BTN_X}, {"Y", BTN_Y},
            {"CROSS", BTN_A}, {"CIRCLE", BTN_B}, {"SQUARE", BTN_X}, {"TRIANGLE", BTN_Y},
            {"LB", BTN_TL}, {"RB", BTN_TR}, {"L1", BTN_TL}, {"R1", BTN_TR},
            {"LT", BTN_TL2}, {"RT", BTN_TR2}, {"L2", BTN_TL2}, {"R2", BTN_TR2},
            {"SELECT", BTN_SELECT}, {"START", BTN_START},
            {"SHARE", BTN_SELECT}, {"OPTIONS", BTN_START},
            {"LS", BTN_THUMBL}, {"RS", BTN_THUMBR}, {"L3", BTN_THUMBL}, {"R3", BTN_THUMBR},
            {"DPAD_UP", BTN_DPAD_UP}, {"DPAD_DOWN", BTN_DPAD_DOWN},
            {"DPAD_LEFT", BTN_DPAD_LEFT}, {"DPAD_RIGHT", BTN_DPAD_RIGHT},
            {"BUTTON_A", BTN_A}, {"BUTTON_B", BTN_B}, {"BUTTON_X", BTN_X}, {"BUTTON_Y", BTN_Y},
            {"LEFT_BUMPER", BTN_TL}, {"RIGHT_BUMPER", BTN_TR},
            {"LEFT_TRIGGER", BTN_TL2}, {"RIGHT_TRIGGER", BTN_TR2},
            {"LEFT_STICK", BTN_THUMBL}, {"RIGHT_STICK", BTN_THUMBR}
        };

        auto it = bt_button_map.find(button_name);
        return (it != bt_button_map.end()) ? it->second : -1;
    }

    int get_bluetooth_axis_code(const std::string& axis_name) {
        // Map Bluetooth HID axis names to Linux input codes
        static const std::map<std::string, int> bt_axis_map = {
            {"LEFT_X", ABS_X}, {"LEFT_Y", ABS_Y},
            {"RIGHT_X", ABS_RX}, {"RIGHT_Y", ABS_RY},
            {"LEFT_STICK_X", ABS_X}, {"LEFT_STICK_Y", ABS_Y},
            {"RIGHT_STICK_X", ABS_RX}, {"RIGHT_STICK_Y", ABS_RY},
            {"LEFT_TRIGGER", ABS_Z}, {"RIGHT_TRIGGER", ABS_RZ},
            {"L2_TRIGGER", ABS_Z}, {"R2_TRIGGER", ABS_RZ}
        };

        auto it = bt_axis_map.find(axis_name);
        return (it != bt_axis_map.end()) ? it->second : -1;
    }
#endif

    BackendType current_backend_;
    std::unique_ptr<InputSimulator> backend_;
    std::unique_ptr<ControllerManager> controller_manager_;
    std::atomic<bool> running_;

    // Global mappings (for backward compatibility)
    std::map<std::string, std::string> mappings_;
    std::map<int, std::string> button_mappings_;
    std::map<int, std::string> axis_mappings_;

    // Per-controller mappings
    std::map<int, std::map<int, std::string>> controller_mappings_;      // controller_id -> (button_code -> action)
    std::map<int, std::map<int, std::string>> controller_axis_mappings_; // controller_id -> (axis_code -> action)

#if WITH_BLUETOOTH
    // Bluetooth components (legacy support)
    std::unique_ptr<BluetoothScanner> bluetooth_scanner_;
    std::unique_ptr<BluetoothConnector> bluetooth_connector_;
    std::shared_ptr<HIDParser> hid_parser_;
    bool use_bluetooth_device_;
    json bluetooth_config_;
#endif

#ifdef WITH_CLIPBOARD
    // Clipboard monitor
    std::unique_ptr<ClipboardMonitor> clipboard_monitor_;
#endif

    // Voice alerts system
    std::unique_ptr<VoiceAlerts> voice_alerts_;

    // KDE Connect integration
    std::unique_ptr<KDEConnectClient> kde_connect_client_;
};

// Public interface implementation
GamepadMapper::GamepadMapper() : impl_(std::make_unique<Impl>()) {}
GamepadMapper::~GamepadMapper() = default;

bool GamepadMapper::initialize() { return impl_->initialize(); }
void GamepadMapper::start() { impl_->start(); }
void GamepadMapper::stop() { impl_->stop(); }
bool GamepadMapper::load_mappings(const std::string& config_file) { return impl_->load_mappings(config_file); }
bool GamepadMapper::add_mapping(const std::string& input, const std::string& output) { return impl_->add_mapping(input, output); }
bool GamepadMapper::remove_mapping(const std::string& input) { return impl_->remove_mapping(input); }

// Controller management methods
std::vector<ControllerInfo> GamepadMapper::get_connected_controllers() const { return impl_->get_connected_controllers(); }
ControllerInfo GamepadMapper::get_controller_info(int controller_id) const { return impl_->get_controller_info(controller_id); }
bool GamepadMapper::is_controller_connected(int controller_id) const { return impl_->is_controller_connected(controller_id); }
bool GamepadMapper::load_controller_mappings(int controller_id, const std::string& config_file) { return impl_->load_controller_mappings(controller_id, config_file); }
bool GamepadMapper::set_controller_profile(int controller_id, const std::string& profile_name) { return impl_->set_controller_profile(controller_id, profile_name); }
void GamepadMapper::scan_for_controllers() { impl_->scan_for_controllers(); }
void GamepadMapper::set_max_controllers(int max_controllers) { impl_->set_max_controllers(max_controllers); }

#ifdef WITH_CLIPBOARD
bool GamepadMapper::initialize_clipboard_monitor() { return impl_->initialize_clipboard_monitor(); }
void GamepadMapper::start_clipboard_monitoring() { impl_->start_clipboard_monitoring(); }
void GamepadMapper::stop_clipboard_monitoring() { impl_->stop_clipboard_monitoring(); }
bool GamepadMapper::is_clipboard_monitoring() const { return impl_->is_clipboard_monitoring(); }
ClipboardContent GamepadMapper::get_current_content() { return impl_->get_current_content(); }
bool GamepadMapper::set_text_content(const std::string& text) { return impl_->set_text_content(text); }
bool GamepadMapper::clear_clipboard() { return impl_->clear_clipboard(); }
#endif

bool GamepadMapper::initialize_voice_alerts() { return impl_->initialize_voice_alerts(); }
void GamepadMapper::start_voice_alerts() { impl_->start_voice_alerts(); }
void GamepadMapper::stop_voice_alerts() { impl_->stop_voice_alerts(); }
bool GamepadMapper::is_voice_alerts_enabled() const { return impl_->is_voice_alerts_enabled(); }

bool GamepadMapper::initialize_kde_connect() { return impl_->initialize_kde_connect(); }
void GamepadMapper::start_kde_connect() { impl_->start_kde_connect(); }
void GamepadMapper::stop_kde_connect() { impl_->stop_kde_connect(); }
bool GamepadMapper::is_kde_connect_enabled() const { return impl_->is_kde_connect_enabled(); }

} // namespace gamepad_mapper