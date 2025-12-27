#pragma once

#include "bluetooth_types.h"
#include "gamepad_mapper.h"
#include <vector>
#include <cstdint>

namespace gamepad_mapper {

class HIDParser {
public:
    HIDParser();
    ~HIDParser();

    // Parse HID descriptor (basic implementation for gamepads)
    bool parse_descriptor(const std::vector<uint8_t>& descriptor);

    // Parse HID report and convert to GamepadEvent
    bool parse_report(const std::vector<uint8_t>& report, GamepadEvent& event);

    // Configure parser for specific device type
    void configure_for_device(uint16_t vendor_id, uint16_t product_id);

private:
    // Device-specific configuration
    uint16_t vendor_id_;
    uint16_t product_id_;

    // Report parsing helpers
    bool parse_button_report(const std::vector<uint8_t>& report, GamepadEvent& event);
    bool parse_axis_report(const std::vector<uint8_t>& report, GamepadEvent& event);

    // Common gamepad layouts
    struct GamepadLayout {
        int button_offset;
        int button_count;
        int axis_offset;
        int axis_count;
        bool has_dpad;
    };

    GamepadLayout layout_;

    // Button and axis mappings for different devices
    void setup_xbox_layout();
    void setup_playstation_layout();
    void setup_generic_layout();
};

} // namespace gamepad_mapper