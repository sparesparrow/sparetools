#include "hid_parser.h"
#include <iostream>
#include <cstring>
#include <linux/input.h>

namespace gamepad_mapper {

HIDParser::HIDParser() : vendor_id_(0), product_id_(0) {
    setup_generic_layout();
}

HIDParser::~HIDParser() {
}

void HIDParser::configure_for_device(uint16_t vendor_id, uint16_t product_id) {
    vendor_id_ = vendor_id;
    product_id_ = product_id;

    // Configure layout based on vendor/product ID
    if (vendor_id == 0x045e) { // Microsoft
        setup_xbox_layout();
    } else if (vendor_id == 0x054c) { // Sony
        setup_playstation_layout();
    } else {
        setup_generic_layout();
    }
}

void HIDParser::setup_xbox_layout() {
    layout_.button_offset = 10;
    layout_.button_count = 11; // A, B, X, Y, LB, RB, LT, RT, Start, Back, Guide
    layout_.axis_offset = 0;
    layout_.axis_count = 6; // Left X/Y, Right X/Y, LT, RT
    layout_.has_dpad = true;
}

void HIDParser::setup_playstation_layout() {
    layout_.button_offset = 5;
    layout_.button_count = 14; // Cross, Circle, Square, Triangle, L1, R1, L2, R2, Share, Options, L3, R3, PS, Touchpad
    layout_.axis_offset = 0;
    layout_.axis_count = 6; // Left X/Y, Right X/Y, L2, R2
    layout_.has_dpad = true;
}

void HIDParser::setup_generic_layout() {
    layout_.button_offset = 0;
    layout_.button_count = 16;
    layout_.axis_offset = 0;
    layout_.axis_count = 8;
    layout_.has_dpad = true;
}

bool HIDParser::parse_descriptor(const std::vector<uint8_t>& descriptor) {
    // Basic HID descriptor parsing
    // For now, we assume standard gamepad descriptors
    // A full implementation would parse the HID descriptor tree

    if (descriptor.empty()) {
        return false;
    }

    // Look for basic gamepad indicators in the descriptor
    // This is a simplified implementation
    return true;
}

bool HIDParser::parse_report(const std::vector<uint8_t>& report, GamepadEvent& event) {
    if (report.empty()) {
        return false;
    }

    // Parse based on report type (button or axis report)
    uint8_t report_id = report[0];

    // Simple heuristic: if report has many zero bytes at the beginning,
    // it might be an axis report. Otherwise, button report.
    bool is_button_report = true;
    for (size_t i = 1; i < std::min(size_t(4), report.size()); ++i) {
        if (report[i] != 0) {
            is_button_report = false;
            break;
        }
    }

    if (is_button_report) {
        return parse_button_report(report, event);
    } else {
        return parse_axis_report(report, event);
    }
}

bool HIDParser::parse_button_report(const std::vector<uint8_t>& report, GamepadEvent& event) {
    if (report.size() < 3) {
        return false;
    }

    // Parse button presses
    // This is a simplified implementation for common gamepads

    // D-pad buttons (hat switch)
    uint8_t dpad = report[1] & 0x0F;
    switch (dpad) {
        case 0: event.type = GamepadEvent::BUTTON; event.button.code = BTN_DPAD_UP; event.button.pressed = true; return true;
        case 1: event.type = GamepadEvent::BUTTON; event.button.code = BTN_DPAD_UP | BTN_DPAD_RIGHT; event.button.pressed = true; return true;
        case 2: event.type = GamepadEvent::BUTTON; event.button.code = BTN_DPAD_RIGHT; event.button.pressed = true; return true;
        case 3: event.type = GamepadEvent::BUTTON; event.button.code = BTN_DPAD_DOWN | BTN_DPAD_RIGHT; event.button.pressed = true; return true;
        case 4: event.type = GamepadEvent::BUTTON; event.button.code = BTN_DPAD_DOWN; event.button.pressed = true; return true;
        case 5: event.type = GamepadEvent::BUTTON; event.button.code = BTN_DPAD_DOWN | BTN_DPAD_LEFT; event.button.pressed = true; return true;
        case 6: event.type = GamepadEvent::BUTTON; event.button.code = BTN_DPAD_LEFT; event.button.pressed = true; return true;
        case 7: event.type = GamepadEvent::BUTTON; event.button.code = BTN_DPAD_UP | BTN_DPAD_LEFT; event.button.pressed = true; return true;
        default: break; // Centered
    }

    // Face buttons (A, B, X, Y)
    uint8_t face_buttons = (report[1] >> 4) & 0x0F;
    if (face_buttons & 0x01) { event.type = GamepadEvent::BUTTON; event.button.code = BTN_A; event.button.pressed = true; return true; }
    if (face_buttons & 0x02) { event.type = GamepadEvent::BUTTON; event.button.code = BTN_B; event.button.pressed = true; return true; }
    if (face_buttons & 0x04) { event.type = GamepadEvent::BUTTON; event.button.code = BTN_X; event.button.pressed = true; return true; }
    if (face_buttons & 0x08) { event.type = GamepadEvent::BUTTON; event.button.code = BTN_Y; event.button.pressed = true; return true; }

    // Shoulder buttons
    if (report.size() >= 3) {
        uint8_t shoulder_buttons = report[2];
        if (shoulder_buttons & 0x01) { event.type = GamepadEvent::BUTTON; event.button.code = BTN_TL; event.button.pressed = true; return true; }
        if (shoulder_buttons & 0x02) { event.type = GamepadEvent::BUTTON; event.button.code = BTN_TR; event.button.pressed = true; return true; }
        if (shoulder_buttons & 0x04) { event.type = GamepadEvent::BUTTON; event.button.code = BTN_TL2; event.button.pressed = true; return true; }
        if (shoulder_buttons & 0x08) { event.type = GamepadEvent::BUTTON; event.button.code = BTN_TR2; event.button.pressed = true; return true; }

        // Menu buttons
        if (shoulder_buttons & 0x10) { event.type = GamepadEvent::BUTTON; event.button.code = BTN_SELECT; event.button.pressed = true; return true; }
        if (shoulder_buttons & 0x20) { event.type = GamepadEvent::BUTTON; event.button.code = BTN_START; event.button.pressed = true; return true; }
    }

    return false; // No button pressed
}

bool HIDParser::parse_axis_report(const std::vector<uint8_t>& report, GamepadEvent& event) {
    if (report.size() < 12) { // Minimum size for standard gamepad axes
        return false;
    }

    // Parse analog sticks and triggers
    // Assuming little-endian 16-bit values

    // Left stick X/Y
    int16_t left_x = static_cast<int16_t>(report[1] | (report[2] << 8));
    int16_t left_y = static_cast<int16_t>(report[3] | (report[4] << 8));

    // Right stick X/Y
    int16_t right_x = static_cast<int16_t>(report[5] | (report[6] << 8));
    int16_t right_y = static_cast<int16_t>(report[7] | (report[8] << 8));

    // Triggers
    uint8_t left_trigger = report[9];
    uint8_t right_trigger = report[10];

    // Convert to appropriate ranges and set events
    // For now, just return the first non-zero axis
    if (left_x != 0) {
        event.type = GamepadEvent::AXIS;
        event.axis.code = ABS_X;
        event.axis.value = left_x;
        return true;
    }

    if (left_y != 0) {
        event.type = GamepadEvent::AXIS;
        event.axis.code = ABS_Y;
        event.axis.value = left_y;
        return true;
    }

    if (right_x != 0) {
        event.type = GamepadEvent::AXIS;
        event.axis.code = ABS_RX;
        event.axis.value = right_x;
        return true;
    }

    if (right_y != 0) {
        event.type = GamepadEvent::AXIS;
        event.axis.code = ABS_RY;
        event.axis.value = right_y;
        return true;
    }

    if (left_trigger != 0) {
        event.type = GamepadEvent::AXIS;
        event.axis.code = ABS_Z;
        event.axis.value = left_trigger * 128; // Scale to 16-bit range
        return true;
    }

    if (right_trigger != 0) {
        event.type = GamepadEvent::AXIS;
        event.axis.code = ABS_RZ;
        event.axis.value = right_trigger * 128; // Scale to 16-bit range
        return true;
    }

    return false;
}

} // namespace gamepad_mapper