#pragma once

#include <string>
#include <vector>
#include <cstdint>

namespace gamepad_mapper {

// Bluetooth service UUIDs
const std::string HID_SERVICE_UUID = "00001124-0000-1000-8000-00805f9b34fb";
const std::string PNP_SERVICE_UUID = "00001200-0000-1000-8000-00805f9b34fb";

// Bluetooth device information
struct BluetoothDevice {
    std::string mac_address;
    std::string name;
    uint16_t vendor_id;
    uint16_t product_id;
    std::vector<uint8_t> hid_descriptor;
    bool connected;
};

// HID report data
struct HIDReport {
    std::vector<uint8_t> data;
    uint8_t report_id;
};

// HID descriptor parsing
struct HIDDescriptor {
    std::vector<uint8_t> raw_descriptor;
    // Parsed descriptor information would go here
    // For now, we'll focus on basic gamepad mapping
};

// Gamepad event from Bluetooth HID
struct BluetoothGamepadEvent {
    enum Type { BUTTON, AXIS } type;
    union {
        struct {
            int code;
            bool pressed;
        } button;
        struct {
            int code;
            int32_t value;
        } axis;
    };
};

} // namespace gamepad_mapper