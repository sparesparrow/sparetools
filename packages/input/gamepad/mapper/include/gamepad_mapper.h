#pragma once

#include <memory>
#include <string>
#include <vector>
#include <functional>
#include <atomic>
#include "gamepad_events.h"

namespace gamepad_mapper {

// Forward declarations
enum class MouseButton { LEFT, RIGHT, MIDDLE };

// Controller information structure (forward declaration from controller_manager.h)
struct ControllerInfo;

// Abstract base class for input simulators
class InputSimulator {
public:
    virtual ~InputSimulator() = default;
    virtual bool initialize() = 0;
    virtual void cleanup() = 0;

    virtual void send_key_press(int key_code) = 0;
    virtual void send_key_release(int key_code) = 0;
    virtual void send_mouse_click(MouseButton button) = 0;
    virtual void send_mouse_move(float delta_x, float delta_y) = 0;
    virtual void send_mouse_scroll(int delta) = 0;
};

// Main gamepad mapper class
class GamepadMapper {
public:
    GamepadMapper();
    ~GamepadMapper();

    // Initialize the mapper (detects and initializes appropriate backend)
    bool initialize();

    // Start/stop the event processing loop
    void start();
    void stop();

    // Configuration management
    bool load_mappings(const std::string& config_file);
    bool add_mapping(const std::string& input, const std::string& output);
    bool remove_mapping(const std::string& input);

    // Controller management
    std::vector<ControllerInfo> get_connected_controllers() const;
    ControllerInfo get_controller_info(int controller_id) const;
    bool is_controller_connected(int controller_id) const;

    // Per-controller configuration
    bool load_controller_mappings(int controller_id, const std::string& config_file);
    bool set_controller_profile(int controller_id, const std::string& profile_name);

    // Device management
    void scan_for_controllers();
    void set_max_controllers(int max_controllers);

    // Clipboard management
#ifdef WITH_CLIPBOARD
    bool initialize_clipboard_monitor();
    void start_clipboard_monitoring();
    void stop_clipboard_monitoring();
    bool is_clipboard_monitoring() const;
    ClipboardContent get_current_content();
    bool set_text_content(const std::string& text);
    bool clear_clipboard();
#endif

    // Voice alerts system
    bool initialize_voice_alerts();
    void start_voice_alerts();
    void stop_voice_alerts();
    bool is_voice_alerts_enabled() const;

    // KDE Connect integration
    bool initialize_kde_connect();
    void start_kde_connect();
    void stop_kde_connect();
    bool is_kde_connect_enabled() const;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace gamepad_mapper