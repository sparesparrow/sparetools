#include "gamepad_mapper.h"
#ifdef WITH_MCP
#include "gamepad_server.h"
#endif
#include <iostream>
#include <csignal>
#include <atomic>
#include <thread>
#include <getopt.h>

std::atomic<bool> running{true};

void signal_handler(int signal) {
    std::cout << "\nReceived signal " << signal << ", shutting down..." << std::endl;
    running = false;
}

void print_usage(const char* program_name) {
    std::cout << "Gamepad Mapper - Multi-backend gamepad to keyboard/mouse input mapper\n\n";
    std::cout << "Usage: " << program_name << " [OPTIONS]\n\n";
    std::cout << "Options:\n";
    std::cout << "  -c, --config FILE     Load configuration file (default: config/default_mappings.json)\n";
    std::cout << "  -m, --mcp             Enable MCP server mode (stdio transport)\n";
    std::cout << "  -h, --help           Show this help message\n";
    std::cout << "  -v, --version        Show version information\n\n";
    std::cout << "Examples:\n";
    std::cout << "  " << program_name << "                                    # Start with default config\n";
    std::cout << "  " << program_name << " -c config/browser_mappings.json   # Use browser mappings\n";
    std::cout << "  " << program_name << " -m                               # Start as MCP server\n";
}

void print_version() {
    std::cout << "Gamepad Mapper v1.0.0\n";
    std::cout << "Multi-backend input simulation system\n";
}

int main(int argc, char* argv[]) {
    // Register signal handlers
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    // Default configuration
    std::string config_file = "config/default_mappings.json";
    bool enable_mcp = false; // MCP enabled/disabled

    // Parse command line options
    static struct option long_options[] = {
        {"config", required_argument, 0, 'c'},
        {"mcp", no_argument, 0, 'm'},
        {"help", no_argument, 0, 'h'},
        {"version", no_argument, 0, 'v'},
        {0, 0, 0, 0}
    };

    int option_index = 0;
    int c;

    while ((c = getopt_long(argc, argv, "c:mhv", long_options, &option_index)) != -1) {
        switch (c) {
            case 'c':
                config_file = optarg;
                break;
            case 'm':
                enable_mcp = true;
                break;
            case 'h':
                print_usage(argv[0]);
                return 0;
            case 'v':
                print_version();
                return 0;
            case '?':
                print_usage(argv[0]);
                return 1;
            default:
                return 1;
        }
    }

    // MCP server mode vs regular mapper mode
    if (enable_mcp) {
        std::cout << "Starting in MCP server mode" << std::endl;
    } else {
        std::cout << "Starting in gamepad mapper mode" << std::endl;
    }

    try {
        // Create gamepad mapper
        auto mapper = std::make_shared<gamepad_mapper::GamepadMapper>();

        if (enable_mcp) {
#ifdef WITH_MCP
            // MCP Server Mode
            std::cout << "Initializing MCP server..." << std::endl;

            // Initialize the MCP server with the mapper
            auto& server = gamepad_mapper::GamepadServer::GetInstance();
            int init_result = server.Initialize(mapper);
            if (init_result != MCP::ERRNO_OK) {
                std::cerr << "Failed to initialize MCP server" << std::endl;
                return 1;
            }

            // Start the MCP server
            int start_result = server.Start();
            if (start_result != MCP::ERRNO_OK) {
                std::cerr << "Failed to start MCP server" << std::endl;
                return 1;
            }

            std::cout << "MCP server started. Press Ctrl+C to stop." << std::endl;

            // Wait for shutdown signal
            while (running) {
                std::this_thread::sleep_for(std::chrono::seconds(1));
            }
#else
            std::cerr << "MCP support not compiled in this build" << std::endl;
            return 1;
#endif
        } else {
            // Regular Gamepad Mapper Mode
            std::cout << "Initializing gamepad mapper..." << std::endl;

            // Initialize mapper
            if (!mapper->initialize()) {
                std::cerr << "Failed to initialize gamepad mapper" << std::endl;
                return 1;
            }

            // Load configuration
            if (!mapper->load_mappings(config_file)) {
                std::cout << "Warning: Could not load config file '" << config_file
                          << "', using empty configuration" << std::endl;
            } else {
                std::cout << "Loaded configuration from '" << config_file << "'" << std::endl;
            }

            // Start mapper
            mapper->start();
            std::cout << "Gamepad mapper started. Press Ctrl+C to stop." << std::endl;

            // Main loop
            while (running) {
                std::this_thread::sleep_for(std::chrono::seconds(1));
            }

            // Stop mapper
            mapper->stop();
            std::cout << "Gamepad mapper stopped" << std::endl;
        }

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}