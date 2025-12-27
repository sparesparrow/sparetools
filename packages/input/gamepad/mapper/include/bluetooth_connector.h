#pragma once

#include "bluetooth_types.h"
#include "hid_parser.h"
#include <string>
#include <vector>
#include <memory>
#include <thread>
#include <atomic>

namespace gamepad_mapper {

class BluetoothConnector {
public:
    BluetoothConnector();
    ~BluetoothConnector();

    // Initialize the connector
    bool initialize();

    // Connect to a Bluetooth HID device
    bool connect_device(const std::string& mac_address);

    // Disconnect from current device
    void disconnect_device();

    // Check if connected to a device
    bool is_connected() const;

    // Read HID report from connected device
    bool read_hid_report(HIDReport& report);

    // Get connected device info
    BluetoothDevice get_connected_device() const;

    // Set HID parser for report processing
    void set_hid_parser(std::shared_ptr<HIDParser> parser);

private:
    // L2CAP socket for HID communication
    int l2cap_socket_;

    // Connected device information
    BluetoothDevice connected_device_;
    std::atomic<bool> connected_;

    // HID parser for processing reports
    std::shared_ptr<HIDParser> hid_parser_;

    // Connection thread for background reading
    std::thread connection_thread_;
    std::atomic<bool> running_;

    // Helper methods
    bool create_l2cap_socket();
    void close_l2cap_socket();

    // HID protocol control channel (PSM 0x11)
    bool connect_control_channel(const std::string& mac_address);

    // HID protocol interrupt channel (PSM 0x13)
    bool connect_interrupt_channel(const std::string& mac_address);

    // Send HID command
    bool send_hid_command(uint8_t type, const std::vector<uint8_t>& data);

    // Receive HID response
    bool receive_hid_response(std::vector<uint8_t>& response, int timeout_ms = 1000);

    // Background connection monitoring
    void connection_monitor();

    // Parse incoming HID data
    void process_hid_data(const std::vector<uint8_t>& data);
};

} // namespace gamepad_mapper