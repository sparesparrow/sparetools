#pragma once

#include <string>
#include <vector>
#include <map>
#include <chrono>
#include <memory>
#include "input_simulator.h"

namespace gamepad_mapper {

// Structure to represent a key combination
struct KeyCombination {
    std::vector<int> modifiers;  // Modifier keys (CTRL, ALT, SHIFT, META)
    int main_key;               // Main key to press
    std::chrono::milliseconds hold_duration;  // How long to hold the combination
    std::chrono::milliseconds delay_before;   // Delay before pressing
    std::chrono::milliseconds delay_after;    // Delay after releasing
};

// Keyboard shortcut handler for complex combinations
class KeyboardShortcutHandler {
public:
    KeyboardShortcutHandler(std::shared_ptr<InputSimulator> simulator);
    ~KeyboardShortcutHandler() = default;

    // Parse a shortcut string like "KEY_LEFTCTRL+KEY_ALT+KEY_A"
    bool parse_shortcut(const std::string& shortcut_string, KeyCombination& combination);
    
    // Execute a key combination
    bool execute_shortcut(const KeyCombination& combination);
    
    // Execute a shortcut from string
    bool execute_shortcut(const std::string& shortcut_string);
    
    // Hold modifier keys
    void hold_modifiers(const std::vector<int>& modifiers);
    
    // Release modifier keys
    void release_modifiers(const std::vector<int>& modifiers);
    
    // Press and release a key with modifiers
    bool press_key_with_modifiers(int key, const std::vector<int>& modifiers);
    
    // Set timing parameters
    void set_timing_params(int hold_duration_ms = 50, int delay_before_ms = 10, int delay_after_ms = 10);
    
    // Check if a key is currently held
    bool is_key_held(int key_code) const;
    
    // Get currently held modifiers
    std::vector<int> get_held_modifiers() const;
    
    // Clear all held keys
    void clear_all_held_keys();

private:
    std::shared_ptr<InputSimulator> simulator_;
    std::map<int, bool> held_keys_;
    std::vector<int> held_modifiers_;
    
    // Timing parameters
    std::chrono::milliseconds hold_duration_;
    std::chrono::milliseconds delay_before_;
    std::chrono::milliseconds delay_after_;
    
    // Parse individual key from string
    int parse_key(const std::string& key_string);
    
    // Split shortcut string by '+'
    std::vector<std::string> split_shortcut(const std::string& shortcut);
    
    // Check if key is a modifier
    bool is_modifier_key(int key_code) const;
    
    // Add delay
    void delay(std::chrono::milliseconds duration);
};

// Enhanced input simulator with shortcut support
class EnhancedInputSimulator : public InputSimulator {
public:
    EnhancedInputSimulator(std::shared_ptr<InputSimulator> base_simulator);
    ~EnhancedInputSimulator() = default;

    bool initialize() override;
    void cleanup() override;

    void send_key_press(int key_code) override;
    void send_key_release(int key_code) override;
    void send_mouse_click(MouseButton button) override;
    void send_mouse_move(float delta_x, float delta_y) override;
    void send_mouse_scroll(int delta) override;
    
    // Enhanced methods for shortcuts
    bool send_key_combination(const std::string& combination);
    bool send_key_combination(const KeyCombination& combination);
    void hold_modifier(int modifier_key);
    void release_modifier(int modifier_key);
    void release_all_modifiers();
    
    // Get the underlying simulator
    std::shared_ptr<InputSimulator> get_base_simulator() const { return base_simulator_; }

private:
    std::shared_ptr<InputSimulator> base_simulator_;
    std::unique_ptr<KeyboardShortcutHandler> shortcut_handler_;
};

} // namespace gamepad_mapper
