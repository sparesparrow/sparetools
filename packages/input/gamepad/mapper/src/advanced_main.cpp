#include "multi_controller_manager.h"
#include "gamepad_mapper.h"
#include <iostream>
#include <signal.h>
#include <unistd.h>
#include <getopt.h>
#include <fstream>
#include <chrono>
#include <thread>
#include <nlohmann/json.hpp>

using namespace gamepad_mapper;

// Global variables for signal handling
std::atomic<bool> g_running{true};
MultiControllerManager* g_manager = nullptr;

// Signal handler
void signal_handler(int signal) {
    std::cout << "\nReceived signal " << signal << ". Shutting down gracefully...\n";
    g_running = false;
    if (g_manager) {
        g_manager->stop_event_processing();
        g_manager->stop_auto_detection();
    }
}

// Print usage information
void print_usage(const char* program_name) {
    std::cout << "Advanced Multi-Controller Gamepad Mapper\n";
    std::cout << "Usage: " << program_name << " [OPTIONS]\n\n";
    std::cout << "Options:\n";
    std::cout << "  -c, --config FILE     Load configuration from FILE\n";
    std::cout << "  -p, --profile NAME    Load profile by name (professional, gaming, accessibility)\n";
    std::cout << "  -v, --voice           Enable voice alerts\n";
    std::cout << "  -s, --scan            Run device scan and exit\n";
    std::cout << "  -r, --remote HOST     Enable remote control to HOST\n";
    std::cout << "  -k, --kde             Enable KDE Connect integration\n";
    std::cout << "  -t, --tasker          Enable Tasker/Join integration\n";
    std::cout << "  -b, --bluetooth       Enable Bluetooth scanning\n";
    std::cout << "  -n, --network         Enable network device discovery\n";
    std::cout << "  -a, --auto            Enable auto-detection\n";
    std::cout << "  -d, --daemon          Run as daemon\n";
    std::cout << "  -l, --log FILE        Log to FILE\n";
    std::cout << "  -h, --help            Show this help\n";
    std::cout << "\nExamples:\n";
    std::cout << "  " << program_name << " --profile professional --voice --remote studio.local\n";
    std::cout << "  " << program_name << " --config custom.json --kde --tasker\n";
    std::cout << "  " << program_name << " --scan --bluetooth --network\n";
}

// Load profile configuration
bool load_profile(MultiControllerManager& manager, const std::string& profile_name) {
    std::string profile_file = "config/" + profile_name + "_mappings.json";
    
    std::ifstream file(profile_file);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open profile file: " << profile_file << std::endl;
        return false;
    }
    
    // Parse JSON configuration
    nlohmann::json config;
    file >> config;
    
    // Load voice alerts configuration
    if (config.contains("voice_alerts") && config["voice_alerts"]["enabled"]) {
        manager.enable_voice_alerts(true);
    }
    
    // Load network control configuration
    if (config.contains("network_control") && config["network_control"]["enabled"]) {
        // Enable network control for specified targets
        auto targets = config["network_control"]["targets"];
        for (auto& target : targets.items()) {
            std::string host = target.key();
            if (target.value().contains("ip")) {
                host = target.value()["ip"];
            }
            std::cout << "Enabling remote control to: " << host << std::endl;
        }
    }
    
    // Load controller configurations
    if (config.contains("controllers")) {
        for (auto& controller : config["controllers"].items()) {
            std::string device_id = controller.value()["device_id"];
            std::string name = controller.value()["name"];
            std::string connection_type = controller.value()["connection_type"];
            
            // Create controller device
            ControllerDevice device;
            device.device_id = device_id;
            device.name = name;
            device.connection_type = (connection_type == "USB") ? ConnectionType::USB : 
                                   (connection_type == "BLUETOOTH") ? ConnectionType::BLUETOOTH :
                                   ConnectionType::UNKNOWN;
            device.is_connected = false;
            device.is_active = false;
            device.last_seen = std::chrono::steady_clock::now();
            
            // Add controller to manager
            manager.add_controller(device);
            
            // Load mappings if available
            if (controller.value().contains("mappings")) {
                std::string mapping_file = "config/" + name + "_mappings.json";
                manager.load_controller_mapping(device_id, mapping_file);
            }
        }
    }
    
    return true;
}

// Run device scan
void run_device_scan(bool bluetooth, bool network, bool usb) {
    AdvancedDeviceScanner scanner;
    if (!scanner.initialize()) {
        std::cerr << "Error: Failed to initialize device scanner" << std::endl;
        return;
    }
    
    std::cout << "Starting device scan...\n";
    
    if (usb) {
        std::cout << "\n=== USB Devices ===\n";
        auto usb_devices = scanner.scan_usb_devices();
        for (const auto& device : usb_devices) {
            std::cout << "USB Device: " << device.name << " (" << device.device_id << ")\n";
        }
    }
    
    if (bluetooth) {
        std::cout << "\n=== Bluetooth Devices ===\n";
        auto bluetooth_devices = scanner.scan_bluetooth_devices();
        for (const auto& device : bluetooth_devices) {
            std::cout << "Bluetooth Device: " << device.name << " (" << device.device_id << ")\n";
        }
        
        // Run advanced Bluetooth scan
        std::cout << "\nRunning advanced Bluetooth scan...\n";
        scanner.run_btscanner_scan("advanced_scan.log");
        std::cout << "Advanced scan results saved to advanced_scan.log\n";
    }
    
    if (network) {
        std::cout << "\n=== Network Devices ===\n";
        auto network_devices = scanner.scan_network_devices("192.168.1.0/24");
        for (const auto& device : network_devices) {
            std::cout << "Network Device: " << device.ip_address << " (" << device.device_id << ")\n";
        }
    }
    
    scanner.cleanup();
}

// Main application
int main(int argc, char* argv[]) {
    // Set up signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Command line options
    static struct option long_options[] = {
        {"config", required_argument, 0, 'c'},
        {"profile", required_argument, 0, 'p'},
        {"voice", no_argument, 0, 'v'},
        {"scan", no_argument, 0, 's'},
        {"remote", required_argument, 0, 'r'},
        {"kde", no_argument, 0, 'k'},
        {"tasker", no_argument, 0, 't'},
        {"bluetooth", no_argument, 0, 'b'},
        {"network", no_argument, 0, 'n'},
        {"auto", no_argument, 0, 'a'},
        {"daemon", no_argument, 0, 'd'},
        {"log", required_argument, 0, 'l'},
        {"help", no_argument, 0, 'h'},
        {0, 0, 0, 0}
    };
    
    // Parse command line arguments
    std::string config_file;
    std::string profile_name;
    bool enable_voice = false;
    bool scan_only = false;
    std::string remote_host;
    bool enable_kde = false;
    bool enable_tasker = false;
    bool enable_bluetooth = false;
    bool enable_network = false;
    bool enable_auto = false;
    bool daemon_mode = false;
    std::string log_file;
    
    int opt;
    int option_index = 0;
    while ((opt = getopt_long(argc, argv, "c:p:vsr:ktbnal:dh", long_options, &option_index)) != -1) {
        switch (opt) {
            case 'c':
                config_file = optarg;
                break;
            case 'p':
                profile_name = optarg;
                break;
            case 'v':
                enable_voice = true;
                break;
            case 's':
                scan_only = true;
                break;
            case 'r':
                remote_host = optarg;
                break;
            case 'k':
                enable_kde = true;
                break;
            case 't':
                enable_tasker = true;
                break;
            case 'b':
                enable_bluetooth = true;
                break;
            case 'n':
                enable_network = true;
                break;
            case 'a':
                enable_auto = true;
                break;
            case 'd':
                daemon_mode = true;
                break;
            case 'l':
                log_file = optarg;
                break;
            case 'h':
                print_usage(argv[0]);
                return 0;
            default:
                print_usage(argv[0]);
                return 1;
        }
    }
    
    // If scan only, run scan and exit
    if (scan_only) {
        run_device_scan(enable_bluetooth, enable_network, true);
        return 0;
    }
    
    // Initialize multi-controller manager
    MultiControllerManager manager;
    g_manager = &manager;
    
    if (!manager.initialize()) {
        std::cerr << "Error: Failed to initialize multi-controller manager" << std::endl;
        return 1;
    }
    
    // Enable voice alerts if requested
    if (enable_voice) {
        manager.enable_voice_alerts(true);
    }
    
    // Load configuration
    if (!config_file.empty()) {
        // Load custom configuration file
        std::cout << "Loading configuration from: " << config_file << std::endl;
        // TODO: Implement custom configuration loading
    } else if (!profile_name.empty()) {
        // Load profile
        std::cout << "Loading profile: " << profile_name << std::endl;
        if (!load_profile(manager, profile_name)) {
            std::cerr << "Error: Failed to load profile" << std::endl;
            return 1;
        }
    } else {
        // Load default profile
        std::cout << "Loading default profile" << std::endl;
        if (!load_profile(manager, "professional")) {
            std::cerr << "Error: Failed to load default profile" << std::endl;
            return 1;
        }
    }
    
    // Enable remote control if requested
    if (!remote_host.empty()) {
        std::cout << "Enabling remote control to: " << remote_host << std::endl;
        // TODO: Implement remote control setup
    }
    
    // Enable KDE Connect if requested
    if (enable_kde) {
        std::cout << "Enabling KDE Connect integration" << std::endl;
        // TODO: Implement KDE Connect setup
    }
    
    // Enable Tasker/Join if requested
    if (enable_tasker) {
        std::cout << "Enabling Tasker/Join integration" << std::endl;
        // TODO: Implement Tasker/Join setup
    }
    
    // Enable auto-detection if requested
    if (enable_auto) {
        std::cout << "Enabling auto-detection" << std::endl;
        manager.start_auto_detection();
    }
    
    // Set up event callbacks
    manager.set_event_callback([](const MultiControllerEvent& event) {
        std::cout << "Event from " << event.controller_name << ": ";
        // Define enum type for switch statement
        enum EventType { BUTTON, AXIS, CONNECTION, DISCONNECTION };

        switch (event.event.type) {
            case BUTTON:
                std::cout << "Button " << event.event.button.code << " "
                         << (event.event.button.pressed ? "pressed" : "released") << std::endl;
                break;
            case AXIS:
                std::cout << "Axis " << event.event.axis.code << " = "
                         << event.event.axis.value << std::endl;
                break;
            case CONNECTION:
                std::cout << "Controller " << (event.event.connection.connected ? "connected" : "disconnected") << std::endl;
                break;
        }
    });
    
    manager.set_connection_callback([](const std::string& device_id, bool connected) {
        std::cout << "Controller " << device_id << " " 
                 << (connected ? "connected" : "disconnected") << std::endl;
    });
    
    // Start event processing
    manager.start_event_processing();
    
    // Print status
    std::cout << "\n=== Multi-Controller Gamepad Mapper Started ===\n";
    std::cout << "Voice alerts: " << (enable_voice ? "enabled" : "disabled") << std::endl;
    std::cout << "Auto-detection: " << (enable_auto ? "enabled" : "disabled") << std::endl;
    std::cout << "Remote control: " << (remote_host.empty() ? "disabled" : "enabled") << std::endl;
    std::cout << "KDE Connect: " << (enable_kde ? "enabled" : "disabled") << std::endl;
    std::cout << "Tasker/Join: " << (enable_tasker ? "enabled" : "disabled") << std::endl;
    std::cout << "\nPress Ctrl+C to stop\n\n";
    
    // Main loop
    while (g_running) {
        // Get controller statistics
        auto stats = manager.get_controller_statistics();
        std::cout << "Controllers: " << stats["total_controllers"] 
                 << " total, " << stats["connected_controllers"] 
                 << " connected, " << stats["active_controllers"] << " active\n";
        
        // Sleep for a bit
        std::this_thread::sleep_for(std::chrono::seconds(5));
    }
    
    // Cleanup
    std::cout << "\nShutting down...\n";
    manager.cleanup();
    
    return 0;
}