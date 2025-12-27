#include "backends/keyboard_shortcut_handler.h"
#include <iostream>
#include <sstream>
#include <algorithm>
#include <thread>
#include <linux/input.h>

namespace gamepad_mapper {

// Keyboard shortcut handler implementation
KeyboardShortcutHandler::KeyboardShortcutHandler(std::shared_ptr<InputSimulator> simulator)
    : simulator_(simulator), hold_duration_(50), delay_before_(10), delay_after_(10) {
}

bool KeyboardShortcutHandler::parse_shortcut(const std::string& shortcut_string, KeyCombination& combination) {
    auto keys = split_shortcut(shortcut_string);
    if (keys.empty()) {
        return false;
    }

    combination.modifiers.clear();
    combination.main_key = 0;
    combination.hold_duration = hold_duration_;
    combination.delay_before = delay_before_;
    combination.delay_after = delay_after_;

    for (const auto& key_str : keys) {
        int key_code = parse_key(key_str);
        if (key_code == 0) {
            std::cerr << "Unknown key: " << key_str << std::endl;
            return false;
        }

        if (is_modifier_key(key_code)) {
            combination.modifiers.push_back(key_code);
        } else {
            if (combination.main_key != 0) {
                std::cerr << "Multiple main keys in shortcut: " << shortcut_string << std::endl;
                return false;
            }
            combination.main_key = key_code;
        }
    }

    if (combination.main_key == 0) {
        std::cerr << "No main key in shortcut: " << shortcut_string << std::endl;
        return false;
    }

    return true;
}

bool KeyboardShortcutHandler::execute_shortcut(const KeyCombination& combination) {
    if (combination.main_key == 0) {
        return false;
    }

    // Delay before
    delay(combination.delay_before);

    // Press modifiers
    hold_modifiers(combination.modifiers);

    // Press main key
    simulator_->send_key_press(combination.main_key);

    // Hold duration
    delay(combination.hold_duration);

    // Release main key
    simulator_->send_key_release(combination.main_key);

    // Release modifiers
    release_modifiers(combination.modifiers);

    // Delay after
    delay(combination.delay_after);

    return true;
}

bool KeyboardShortcutHandler::execute_shortcut(const std::string& shortcut_string) {
    KeyCombination combination;
    if (!parse_shortcut(shortcut_string, combination)) {
        return false;
    }
    return execute_shortcut(combination);
}

void KeyboardShortcutHandler::hold_modifiers(const std::vector<int>& modifiers) {
    for (int modifier : modifiers) {
        if (!is_key_held(modifier)) {
            simulator_->send_key_press(modifier);
            held_keys_[modifier] = true;
            held_modifiers_.push_back(modifier);
        }
    }
}

void KeyboardShortcutHandler::release_modifiers(const std::vector<int>& modifiers) {
    for (int modifier : modifiers) {
        if (is_key_held(modifier)) {
            simulator_->send_key_release(modifier);
            held_keys_[modifier] = false;
            held_modifiers_.erase(
                std::remove(held_modifiers_.begin(), held_modifiers_.end(), modifier),
                held_modifiers_.end()
            );
        }
    }
}

bool KeyboardShortcutHandler::press_key_with_modifiers(int key, const std::vector<int>& modifiers) {
    KeyCombination combination;
    combination.modifiers = modifiers;
    combination.main_key = key;
    combination.hold_duration = hold_duration_;
    combination.delay_before = delay_before_;
    combination.delay_after = delay_after_;
    
    return execute_shortcut(combination);
}

void KeyboardShortcutHandler::set_timing_params(int hold_duration_ms, int delay_before_ms, int delay_after_ms) {
    hold_duration_ = std::chrono::milliseconds(hold_duration_ms);
    delay_before_ = std::chrono::milliseconds(delay_before_ms);
    delay_after_ = std::chrono::milliseconds(delay_after_ms);
}

bool KeyboardShortcutHandler::is_key_held(int key_code) const {
    auto it = held_keys_.find(key_code);
    return it != held_keys_.end() && it->second;
}

std::vector<int> KeyboardShortcutHandler::get_held_modifiers() const {
    return held_modifiers_;
}

void KeyboardShortcutHandler::clear_all_held_keys() {
    for (auto& pair : held_keys_) {
        if (pair.second) {
            simulator_->send_key_release(pair.first);
            pair.second = false;
        }
    }
    held_modifiers_.clear();
}

int KeyboardShortcutHandler::parse_key(const std::string& key_string) {
    // Convert string to uppercase for case-insensitive matching
    std::string key_upper = key_string;
    std::transform(key_upper.begin(), key_upper.end(), key_upper.begin(), ::toupper);

    // Remove KEY_ prefix if present
    if (key_upper.substr(0, 4) == "KEY_") {
        key_upper = key_upper.substr(4);
    }

    // Map key names to Linux key codes
    static const std::map<std::string, int> key_map = {
        // Modifier keys
        {"LEFTCTRL", KEY_LEFTCTRL}, {"RIGHTCTRL", KEY_RIGHTCTRL},
        {"LEFTALT", KEY_LEFTALT}, {"RIGHTALT", KEY_RIGHTALT},
        {"LEFTSHIFT", KEY_LEFTSHIFT}, {"RIGHTSHIFT", KEY_RIGHTSHIFT},
        {"LEFTMETA", KEY_LEFTMETA}, {"RIGHTMETA", KEY_RIGHTMETA},
        
        // Function keys
        {"F1", KEY_F1}, {"F2", KEY_F2}, {"F3", KEY_F3}, {"F4", KEY_F4},
        {"F5", KEY_F5}, {"F6", KEY_F6}, {"F7", KEY_F7}, {"F8", KEY_F8},
        {"F9", KEY_F9}, {"F10", KEY_F10}, {"F11", KEY_F11}, {"F12", KEY_F12},
        
        // Special keys
        {"ESC", KEY_ESC}, {"TAB", KEY_TAB}, {"SPACE", KEY_SPACE},
        {"ENTER", KEY_ENTER}, {"RETURN", KEY_ENTER},
        {"BACKSPACE", KEY_BACKSPACE}, {"DELETE", KEY_DELETE},
        {"INSERT", KEY_INSERT}, {"HOME", KEY_HOME}, {"END", KEY_END},
        {"PAGEUP", KEY_PAGEUP}, {"PAGEDOWN", KEY_PAGEDOWN},
        {"PRINT", KEY_PRINT}, {"SCROLLLOCK", KEY_SCROLLLOCK},
        {"PAUSE", KEY_PAUSE}, {"NUMLOCK", KEY_NUMLOCK},
        {"CAPSLOCK", KEY_CAPSLOCK},
        
        // Arrow keys
        {"UP", KEY_UP}, {"DOWN", KEY_DOWN}, {"LEFT", KEY_LEFT}, {"RIGHT", KEY_RIGHT},
        
        // Number keys
        {"1", KEY_1}, {"2", KEY_2}, {"3", KEY_3}, {"4", KEY_4}, {"5", KEY_5},
        {"6", KEY_6}, {"7", KEY_7}, {"8", KEY_8}, {"9", KEY_9}, {"0", KEY_0},
        
        // Letter keys
        {"A", KEY_A}, {"B", KEY_B}, {"C", KEY_C}, {"D", KEY_D}, {"E", KEY_E},
        {"F", KEY_F}, {"G", KEY_G}, {"H", KEY_H}, {"I", KEY_I}, {"J", KEY_J},
        {"K", KEY_K}, {"L", KEY_L}, {"M", KEY_M}, {"N", KEY_N}, {"O", KEY_O},
        {"P", KEY_P}, {"Q", KEY_Q}, {"R", KEY_R}, {"S", KEY_S}, {"T", KEY_T},
        {"U", KEY_U}, {"V", KEY_V}, {"W", KEY_W}, {"X", KEY_X}, {"Y", KEY_Y}, {"Z", KEY_Z}
    };

    auto it = key_map.find(key_upper);
    return (it != key_map.end()) ? it->second : 0;
}

std::vector<std::string> KeyboardShortcutHandler::split_shortcut(const std::string& shortcut) {
    std::vector<std::string> keys;
    std::stringstream ss(shortcut);
    std::string key;
    
    while (std::getline(ss, key, '+')) {
        // Trim whitespace
        key.erase(0, key.find_first_not_of(" \t"));
        key.erase(key.find_last_not_of(" \t") + 1);
        if (!key.empty()) {
            keys.push_back(key);
        }
    }
    
    return keys;
}

bool KeyboardShortcutHandler::is_modifier_key(int key_code) const {
    return key_code == KEY_LEFTCTRL || key_code == KEY_RIGHTCTRL ||
           key_code == KEY_LEFTALT || key_code == KEY_RIGHTALT ||
           key_code == KEY_LEFTSHIFT || key_code == KEY_RIGHTSHIFT ||
           key_code == KEY_LEFTMETA || key_code == KEY_RIGHTMETA;
}

void KeyboardShortcutHandler::delay(std::chrono::milliseconds duration) {
    if (duration.count() > 0) {
        std::this_thread::sleep_for(duration);
    }
}

// Enhanced input simulator implementation
EnhancedInputSimulator::EnhancedInputSimulator(std::shared_ptr<InputSimulator> base_simulator)
    : base_simulator_(base_simulator) {
    shortcut_handler_ = std::make_unique<KeyboardShortcutHandler>(base_simulator_);
}

bool EnhancedInputSimulator::initialize() {
    return base_simulator_->initialize();
}

void EnhancedInputSimulator::cleanup() {
    base_simulator_->cleanup();
}

void EnhancedInputSimulator::send_key_press(int key_code) {
    base_simulator_->send_key_press(key_code);
}

void EnhancedInputSimulator::send_key_release(int key_code) {
    base_simulator_->send_key_release(key_code);
}

void EnhancedInputSimulator::send_mouse_click(MouseButton button) {
    base_simulator_->send_mouse_click(button);
}

void EnhancedInputSimulator::send_mouse_move(float delta_x, float delta_y) {
    base_simulator_->send_mouse_move(delta_x, delta_y);
}

void EnhancedInputSimulator::send_mouse_scroll(int delta) {
    base_simulator_->send_mouse_scroll(delta);
}

bool EnhancedInputSimulator::send_key_combination(const std::string& combination) {
    return shortcut_handler_->execute_shortcut(combination);
}

bool EnhancedInputSimulator::send_key_combination(const KeyCombination& combination) {
    return shortcut_handler_->execute_shortcut(combination);
}

void EnhancedInputSimulator::hold_modifier(int modifier_key) {
    shortcut_handler_->hold_modifiers({modifier_key});
}

void EnhancedInputSimulator::release_modifier(int modifier_key) {
    shortcut_handler_->release_modifiers({modifier_key});
}

void EnhancedInputSimulator::release_all_modifiers() {
    shortcut_handler_->clear_all_held_keys();
}

} // namespace gamepad_mapper
