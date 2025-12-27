#pragma once

#include "bluetooth_types.h"
#include <vector>
#include <string>
#include <memory>

namespace gamepad_mapper {

class BluetoothScanner {
public:
    BluetoothScanner();
    ~BluetoothScanner();

    // Initialize the scanner
    bool initialize();

    // Scan for Bluetooth devices
    std::vector<BluetoothDevice> scan_devices(int timeout_seconds = 10);

    // Check if a device supports HID service
    bool has_hid_service(const std::string& mac_address);

    // Get device name
    std::string get_device_name(const std::string& mac_address);

    // Read PnP information from device
    bool read_pnp_info(const std::string& mac_address, uint16_t& vendor_id, uint16_t& product_id);

    // Read HID descriptor from device
    bool read_hid_descriptor(const std::string& mac_address, std::vector<uint8_t>& descriptor);

private:
    // HCI socket for Bluetooth communication
    int hci_socket_;

    // Helper methods
    bool open_hci_socket();
    void close_hci_socket();

    // Device inquiry using HCI
    std::vector<std::string> perform_inquiry(int timeout_seconds);

    // Parse btscanner log (fallback method)
    std::vector<BluetoothDevice> parse_btscanner_log();

    // BlueZ SDP browsing for services
    bool browse_services(const std::string& mac_address);
};

} // namespace gamepad_mapper