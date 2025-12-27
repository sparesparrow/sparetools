# Gamepad Core

Core gamepad mapping and device management functionality for the gamepad-mapper ecosystem.

## Overview

Gamepad Core provides the fundamental functionality for:
- Gamepad device detection and management
- Input event processing and mapping
- Multi-controller coordination
- Cross-platform device abstraction

## Features

- **Device Management**: Automatic detection and management of connected gamepad devices
- **Event Processing**: High-performance input event processing with customizable mappings
- **Multi-Controller Support**: Coordinate multiple gamepads simultaneously
- **Platform Agnostic**: Abstract interface that works across different platforms
- **Thread Safe**: Designed for concurrent access and processing

## Dependencies

- **nlohmann_json**: JSON configuration and data serialization
- **C++17**: Modern C++ standard required

## Building

### Using Conan

```bash
# Install dependencies
conan install . --build missing

# Build with CMake
cmake --preset conan-release
cmake --build build --config Release

# Install
cmake --install build
```

### Manual Build

```bash
# Install dependencies manually
# nlohmann_json, etc.

# Build
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
```

## Usage

### Basic Usage

```cpp
#include <gamepad_mapper.h>
#include <controller_manager.h>

// Initialize core components
ControllerManager controller_mgr;
GamepadMapper mapper;

// Scan for devices
controller_mgr.scan_devices();

// Load mapping configuration
mapper.load_mapping("config/default.json");

// Start processing
mapper.start_mapping();

// Process events (in event loop)
while (mapper.is_running()) {
    // Events are processed automatically
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
}
```

### Advanced Usage

```cpp
// Multi-controller setup
MultiControllerManager multi_mgr;

// Set up multiple controllers
multi_mgr.add_controller(0); // Primary controller
multi_mgr.add_controller(1); // Secondary controller

// Configure different mappings for each
multi_mgr.load_mapping_for_controller(0, "gaming.json");
multi_mgr.load_mapping_for_controller(1, "accessibility.json");

// Coordinate between controllers
multi_mgr.set_coordination_mode(CoordinationMode::MASTER_SLAVE);
```

## API Reference

### GamepadMapper

Main class for gamepad input mapping and processing.

```cpp
class GamepadMapper {
public:
    bool load_mapping(const std::string& config_path);
    bool process_event(const GamepadEvent& event);
    std::vector<GamepadDevice> get_connected_devices();
    // ... more methods
};
```

### ControllerManager

Manages gamepad device connections and state.

```cpp
class ControllerManager {
public:
    bool scan_devices();
    ControllerState get_device_state(int device_id);
    bool connect_device(int device_id);
    // ... more methods
};
```

## Configuration

Gamepad Core uses JSON configuration files for mapping definitions:

```json
{
  "mappings": {
    "A": {"type": "keyboard", "key": "space"},
    "B": {"type": "mouse", "button": "left"},
    "X": {"type": "keyboard", "key": "ctrl"},
    "Y": {"type": "keyboard", "key": "shift"}
  },
  "sensitivity": {
    "stick_deadzone": 0.1,
    "trigger_threshold": 0.5
  }
}
```

## Testing

```bash
# Build with tests
cmake -DBUILD_TESTS=ON ..
make

# Run tests
ctest --output-on-failure
```

## Integration

Gamepad Core is designed to integrate with other components in the gamepad-mapper ecosystem:

- **input-backends**: Provides platform-specific input simulation
- **gamepad-mcp-server**: Exposes functionality through MCP protocol
- **gamepad-config**: Manages configuration presets
- **gamepad-bluetooth**: Adds wireless device support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Related Projects

- [gamepad-mapper](https://github.com/sparesparrow/gamepad-mapper) - Main orchestrator
- [input-backends](https://github.com/sparesparrow/input-backends) - Input simulation backends
- [gamepad-mcp-server](https://github.com/sparesparrow/gamepad-mcp-server) - MCP integration