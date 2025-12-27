#include "bluetooth_connector.h"
#include <iostream>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/l2cap.h>
#include <bluetooth/hidp.h>
#include <errno.h>
#include <fcntl.h>

namespace gamepad_mapper {

BluetoothConnector::BluetoothConnector()
    : l2cap_socket_(-1), connected_(false), running_(false) {
}

BluetoothConnector::~BluetoothConnector() {
    disconnect_device();
}

bool BluetoothConnector::initialize() {
    return create_l2cap_socket();
}

bool BluetoothConnector::create_l2cap_socket() {
    l2cap_socket_ = socket(AF_BLUETOOTH, SOCK_SEQPACKET, BTPROTO_L2CAP);
    if (l2cap_socket_ < 0) {
        std::cerr << "Failed to create L2CAP socket: " << strerror(errno) << std::endl;
        return false;
    }

    // Set socket to non-blocking mode
    int flags = fcntl(l2cap_socket_, F_GETFL, 0);
    if (flags < 0) {
        std::cerr << "Failed to get socket flags" << std::endl;
        return false;
    }

    if (fcntl(l2cap_socket_, F_SETFL, flags | O_NONBLOCK) < 0) {
        std::cerr << "Failed to set non-blocking mode" << std::endl;
        return false;
    }

    return true;
}

void BluetoothConnector::close_l2cap_socket() {
    if (l2cap_socket_ >= 0) {
        close(l2cap_socket_);
        l2cap_socket_ = -1;
    }
}

bool BluetoothConnector::connect_device(const std::string& mac_address) {
    if (connected_) {
        disconnect_device();
    }

    std::cout << "Connecting to Bluetooth device: " << mac_address << std::endl;

    // Store device info
    connected_device_.mac_address = mac_address;
    connected_device_.connected = false;

    // Connect to HID interrupt channel (PSM 0x13)
    if (!connect_interrupt_channel(mac_address)) {
        std::cerr << "Failed to connect to HID interrupt channel" << std::endl;
        return false;
    }

    // Try to connect to control channel (PSM 0x11) for device control
    connect_control_channel(mac_address); // Optional, continue even if it fails

    connected_ = true;
    connected_device_.connected = true;

    // Start connection monitoring thread
    running_ = true;
    connection_thread_ = std::thread(&BluetoothConnector::connection_monitor, this);

    std::cout << "Successfully connected to Bluetooth device" << std::endl;
    return true;
}

void BluetoothConnector::disconnect_device() {
    if (!connected_) {
        return;
    }

    running_ = false;

    if (connection_thread_.joinable()) {
        connection_thread_.join();
    }

    close_l2cap_socket();
    connected_ = false;
    connected_device_.connected = false;

    std::cout << "Disconnected from Bluetooth device" << std::endl;
}

bool BluetoothConnector::is_connected() const {
    return connected_;
}

bool BluetoothConnector::connect_interrupt_channel(const std::string& mac_address) {
    struct sockaddr_l2 addr;
    memset(&addr, 0, sizeof(addr));

    addr.l2_family = AF_BLUETOOTH;
    addr.l2_psm = htobs(0x13); // HID interrupt PSM
    str2ba(mac_address.c_str(), &addr.l2_bdaddr);

    if (connect(l2cap_socket_, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        std::cerr << "Failed to connect to interrupt channel: " << strerror(errno) << std::endl;
        return false;
    }

    return true;
}

bool BluetoothConnector::connect_control_channel(const std::string& mac_address) {
    // Create separate socket for control channel
    int control_socket = socket(AF_BLUETOOTH, SOCK_SEQPACKET, BTPROTO_L2CAP);
    if (control_socket < 0) {
        std::cerr << "Failed to create control socket" << std::endl;
        return false;
    }

    struct sockaddr_l2 addr;
    memset(&addr, 0, sizeof(addr));

    addr.l2_family = AF_BLUETOOTH;
    addr.l2_psm = htobs(0x11); // HID control PSM
    str2ba(mac_address.c_str(), &addr.l2_bdaddr);

    if (connect(control_socket, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        std::cerr << "Failed to connect to control channel: " << strerror(errno) << std::endl;
        close(control_socket);
        return false;
    }

    // Send SET_PROTOCOL command to switch to report protocol
    std::vector<uint8_t> set_protocol_cmd = {0xA0, 0x01}; // HIDP_TRANS_SET_PROTOCOL, HIDP_PROTO_REPORT
    if (send(control_socket, set_protocol_cmd.data(), set_protocol_cmd.size(), 0) < 0) {
        std::cerr << "Failed to send SET_PROTOCOL command" << std::endl;
        close(control_socket);
        return false;
    }

    close(control_socket); // Close control socket after setup
    return true;
}

bool BluetoothConnector::read_hid_report(HIDReport& report) {
    if (!connected_ || l2cap_socket_ < 0) {
        return false;
    }

    uint8_t buffer[1024];
    ssize_t bytes_read = recv(l2cap_socket_, buffer, sizeof(buffer), 0);

    if (bytes_read < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            // No data available
            return false;
        }
        std::cerr << "Failed to read HID report: " << strerror(errno) << std::endl;
        return false;
    }

    if (bytes_read == 0) {
        // Connection closed
        disconnect_device();
        return false;
    }

    // Parse HID report
    report.data.assign(buffer, buffer + bytes_read);
    if (bytes_read > 0) {
        report.report_id = buffer[0];
    }

    return true;
}

BluetoothDevice BluetoothConnector::get_connected_device() const {
    return connected_device_;
}

void BluetoothConnector::set_hid_parser(std::shared_ptr<HIDParser> parser) {
    hid_parser_ = parser;
}

void BluetoothConnector::connection_monitor() {
    while (running_ && connected_) {
        // Check connection status by attempting to read
        uint8_t test_byte;
        ssize_t result = recv(l2cap_socket_, &test_byte, 1, MSG_PEEK | MSG_DONTWAIT);

        if (result == 0) {
            // Connection closed by peer
            std::cerr << "Bluetooth connection lost" << std::endl;
            connected_ = false;
            break;
        } else if (result < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
            // Other error
            std::cerr << "Bluetooth connection error: " << strerror(errno) << std::endl;
            connected_ = false;
            break;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

void BluetoothConnector::process_hid_data(const std::vector<uint8_t>& data) {
    if (!hid_parser_) {
        return;
    }

    // Process HID data through parser
    // This would typically be called from the main event loop
}

} // namespace gamepad_mapper