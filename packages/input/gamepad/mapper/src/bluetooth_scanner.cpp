#include "bluetooth_scanner.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <bluetooth/bluetooth.h>
#include <bluetooth/hci.h>
#include <bluetooth/hci_lib.h>
#include <bluetooth/sdp.h>
#include <bluetooth/sdp_lib.h>
#include <fcntl.h>

namespace gamepad_mapper {

BluetoothScanner::BluetoothScanner() : hci_socket_(-1) {
}

BluetoothScanner::~BluetoothScanner() {
    close_hci_socket();
}

bool BluetoothScanner::initialize() {
    return open_hci_socket();
}

bool BluetoothScanner::open_hci_socket() {
    // Find the first available HCI device
    int dev_id = hci_get_route(nullptr);
    if (dev_id < 0) {
        std::cerr << "No Bluetooth adapter found" << std::endl;
        return false;
    }

    // Open HCI socket
    hci_socket_ = hci_open_dev(dev_id);
    if (hci_socket_ < 0) {
        std::cerr << "Failed to open HCI socket" << std::endl;
        return false;
    }

    return true;
}

void BluetoothScanner::close_hci_socket() {
    if (hci_socket_ >= 0) {
        close(hci_socket_);
        hci_socket_ = -1;
    }
}

std::vector<BluetoothDevice> BluetoothScanner::scan_devices(int timeout_seconds) {
    std::vector<BluetoothDevice> devices;

    // Try btscanner log first (if available)
    devices = parse_btscanner_log();
    if (!devices.empty()) {
        return devices;
    }

    // Fall back to HCI inquiry
    std::vector<std::string> mac_addresses = perform_inquiry(timeout_seconds);

    for (const auto& mac : mac_addresses) {
        if (has_hid_service(mac)) {
            BluetoothDevice device;
            device.mac_address = mac;
            device.name = get_device_name(mac);
            device.connected = false;

            // Try to read PnP info
            read_pnp_info(mac, device.vendor_id, device.product_id);

            // Try to read HID descriptor
            read_hid_descriptor(mac, device.hid_descriptor);

            devices.push_back(device);
        }
    }

    return devices;
}

std::vector<std::string> BluetoothScanner::perform_inquiry(int timeout_seconds) {
    std::vector<std::string> mac_addresses;

    if (hci_socket_ < 0) {
        return mac_addresses;
    }

    // Set inquiry parameters
    inquiry_info* inquiry_results = nullptr;
    int num_devices = 0;
    int max_devices = 255;

    // Perform inquiry
    num_devices = hci_inquiry(hci_socket_, timeout_seconds, max_devices,
                            nullptr, &inquiry_results, IREQ_CACHE_FLUSH);

    if (num_devices < 0) {
        std::cerr << "HCI inquiry failed" << std::endl;
        return mac_addresses;
    }

    // Process results
    for (int i = 0; i < num_devices; ++i) {
        char mac_str[18];
        ba2str(&inquiry_results[i].bdaddr, mac_str);
        mac_addresses.push_back(mac_str);
    }

    // Clean up
    if (inquiry_results) {
        free(inquiry_results);
    }

    return mac_addresses;
}

std::vector<BluetoothDevice> BluetoothScanner::parse_btscanner_log() {
    std::vector<BluetoothDevice> devices;

    std::ifstream log_file("btscanner.log");
    if (!log_file.is_open()) {
        return devices;
    }

    std::string line;
    while (std::getline(log_file, line)) {
        // Parse btscanner log format
        // This is a simplified parser - you'd need to adapt to actual btscanner output format
        if (line.find("Device found") != std::string::npos) {
            // Extract MAC address and device info
            // This would need to be adapted to the actual btscanner log format
            BluetoothDevice device;
            device.mac_address = "00:00:00:00:00:00"; // Placeholder
            device.name = "Unknown Device"; // Placeholder
            device.connected = false;
            devices.push_back(device);
        }
    }

    return devices;
}

bool BluetoothScanner::has_hid_service(const std::string& mac_address) {
    bdaddr_t bdaddr;
    str2ba(mac_address.c_str(), &bdaddr);

    // Connect to SDP server
    sdp_session_t* session = sdp_connect(BDADDR_ANY, &bdaddr, SDP_RETRY_IF_BUSY);
    if (!session) {
        return false;
    }

    // Search for HID service
    uuid_t hid_uuid;
    sdp_uuid16_create(&hid_uuid, HID_SVCLASS_ID);

    sdp_list_t* search_list = sdp_list_append(nullptr, &hid_uuid);
    sdp_list_t* attr_list = sdp_list_append(nullptr, &public_browse_group);

    uint32_t range = 0x0000ffff;
    sdp_list_t* attr_range = sdp_list_append(nullptr, &range);

    sdp_list_t* response_list = nullptr;

    int result = sdp_service_search_attr_req(session, search_list, SDP_ATTR_REQ_RANGE,
                                           attr_list, &response_list);

    sdp_list_free(search_list, nullptr);
    sdp_list_free(attr_list, nullptr);
    sdp_list_free(attr_range, nullptr);

    bool has_hid = (result == 0 && response_list != nullptr);

    if (response_list) {
        sdp_list_free(response_list, free);
    }

    sdp_close(session);

    return has_hid;
}

std::string BluetoothScanner::get_device_name(const std::string& mac_address) {
    if (hci_socket_ < 0) {
        return "Unknown";
    }

    bdaddr_t bdaddr;
    str2ba(mac_address.c_str(), &bdaddr);

    char name[248] = {0};
    if (hci_read_remote_name(hci_socket_, &bdaddr, sizeof(name), name, 5000) < 0) {
        return "Unknown";
    }

    return std::string(name);
}

bool BluetoothScanner::read_pnp_info(const std::string& mac_address,
                                   uint16_t& vendor_id, uint16_t& product_id) {
    bdaddr_t bdaddr;
    str2ba(mac_address.c_str(), &bdaddr);

    // Connect to SDP server
    sdp_session_t* session = sdp_connect(BDADDR_ANY, &bdaddr, SDP_RETRY_IF_BUSY);
    if (!session) {
        return false;
    }

    // Search for PnP service
    uuid_t pnp_uuid;
    sdp_uuid16_create(&pnp_uuid, PNPINFO_SVCLASS_ID);

    sdp_list_t* search_list = sdp_list_append(nullptr, &pnp_uuid);
    uint32_t range = 0x0000ffff;
    sdp_list_t* attr_range = sdp_list_append(nullptr, &range);

    sdp_list_t* response_list = nullptr;

    int result = sdp_service_search_attr_req(session, search_list, SDP_ATTR_REQ_RANGE,
                                           attr_range, &response_list);

    if (result == 0 && response_list) {
        sdp_record_t* rec = (sdp_record_t*)response_list->data;

        // Extract vendor and product ID from PnP record
        // This is a simplified implementation
        vendor_id = 0;
        product_id = 0;

        // In a full implementation, you'd parse the SDP record attributes
        // to extract the actual vendor_id and product_id values
    }

    sdp_list_free(search_list, nullptr);
    sdp_list_free(attr_range, nullptr);

    if (response_list) {
        sdp_list_free(response_list, free);
    }

    sdp_close(session);

    return (vendor_id != 0 && product_id != 0);
}

bool BluetoothScanner::read_hid_descriptor(const std::string& mac_address,
                                         std::vector<uint8_t>& descriptor) {
    bdaddr_t bdaddr;
    str2ba(mac_address.c_str(), &bdaddr);

    // Connect to SDP server
    sdp_session_t* session = sdp_connect(BDADDR_ANY, &bdaddr, SDP_RETRY_IF_BUSY);
    if (!session) {
        return false;
    }

    // Search for HID service and request descriptor
    uuid_t hid_uuid;
    sdp_uuid16_create(&hid_uuid, HID_SVCLASS_ID);

    sdp_list_t* search_list = sdp_list_append(nullptr, &hid_uuid);

    // Request HID descriptor attribute
    uint16_t attr_id = 0x0206; // HIDDescriptorList
    sdp_list_t* attr_list = sdp_list_append(nullptr, &attr_id);

    sdp_list_t* response_list = nullptr;

    int result = sdp_service_search_attr_req(session, search_list, SDP_ATTR_REQ_INDIVIDUAL,
                                           attr_list, &response_list);

    if (result == 0 && response_list) {
        // Extract HID descriptor from SDP record
        // This is a simplified implementation - actual parsing would be more complex
        descriptor.clear();
        // In practice, you'd parse the SDP data element sequence
    }

    sdp_list_free(search_list, nullptr);
    sdp_list_free(attr_list, nullptr);

    if (response_list) {
        sdp_list_free(response_list, free);
    }

    sdp_close(session);

    return !descriptor.empty();
}

} // namespace gamepad_mapper