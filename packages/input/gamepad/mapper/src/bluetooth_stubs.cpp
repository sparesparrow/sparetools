// Stub implementations for Bluetooth classes when Bluetooth support is disabled
#include <iostream>
#include <vector>
#include <memory>
#include <cstdint>
#include <string>

namespace gamepad_mapper {

struct BluetoothDevice {
    std::string name;
    std::string mac_address;
    uint16_t vendor_id;
    uint16_t product_id;
};

struct HIDReport {
    // Empty struct for stub
};

struct GamepadEvent {
    // Empty struct for stub
};

class BluetoothScanner {
public:
    BluetoothScanner() = default;
    ~BluetoothScanner() = default;
    bool initialize() { return false; }
    std::vector<BluetoothDevice> scan_devices(int) { return {}; }
};

class BluetoothConnector {
public:
    BluetoothConnector() = default;
    ~BluetoothConnector() = default;
    bool initialize() { return false; }
    void set_hid_parser(std::shared_ptr<class HIDParser>) {}
    bool is_connected() const { return false; }
    bool read_hid_report(HIDReport&) { return false; }
    bool connect_device(const std::string&) { return false; }
    std::string get_connected_device() const { return ""; }
};

class HIDParser {
public:
    HIDParser() = default;
    ~HIDParser() = default;
    void configure_for_device(uint16_t, uint16_t) {}
    bool parse_report(const std::vector<unsigned char>&, GamepadEvent&) { return false; }
};

} // namespace gamepad_mapper
