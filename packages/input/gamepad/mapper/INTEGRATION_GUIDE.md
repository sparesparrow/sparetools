# Gamepad-Mapper Ecosystem Integration Guide

## Overview

This document provides comprehensive integration guidance for the modular `gamepad-mapper` ecosystem. The monolithic project has been separated into focused repositories that communicate through the Model Context Protocol (MCP), enabling better maintainability, reusability, and integration with AI tools.

## Architecture Overview

The gamepad-mapper ecosystem consists of 8 repositories working together through MCP:

```
┌─────────────────┐    ┌──────────────────┐
│   gamepad-core  │◄──►│ gamepad-mcp-server│
│                 │    │                  │
│ • Mapping logic │    │ • MCP tools      │
│ • Device mgmt   │    │ • AI integration │
│ • Event proc.   │    │ • Remote control │
└─────────────────┘    └──────────────────┘
         │                       │
         ├───────────────────────┼─────────────────────── MCP Protocol
         │                       │
┌────────▼────────┐    ┌─────────▼──────────┐
│ input-backends  │    │ gamepad-bluetooth  │
│                 │    │                    │
│ • X11/Wayland   │    │ • BT device scan   │
│ • KDE/SDL2      │    │ • HID connection   │
│ • UInput        │    │ • Wireless gaming  │
└─────────────────┘    └────────────────────┘
         │                       │
┌────────▼────────┐    ┌─────────▼──────────┐
│ gamepad-audio   │    │ gamepad-config     │
│                 │    │                    │
│ • ALSA/Pulse    │    │ • JSON presets     │
│ • Voice alerts  │    │ • Config mgmt      │
│ • Sound fx      │    │ • Validation       │
└─────────────────┘    └────────────────────┘
         │
┌────────▼────────┐
│  kde-integration│
│                 │
│ • KDE Connect   │
│ • Clipboard mon │
│ • Desktop sync  │
└─────────────────┘
```

## Repository Descriptions

### gamepad-core
**Location**: `https://github.com/sparesparrow/gamepad-core`
**Purpose**: Core gamepad mapping and device management logic

**Key APIs**:
```cpp
class GamepadMapper {
public:
    bool load_mapping(const std::string& config_path);
    bool process_event(const GamepadEvent& event);
    std::vector<GamepadDevice> get_connected_devices();
};

class ControllerManager {
public:
    bool initialize();
    void scan_devices();
    ControllerState get_controller_state(int device_id);
};
```

**MCP Integration**: Provides core functionality consumed by MCP server

### input-backends
**Location**: `https://github.com/sparesparrow/input-backends`
**Purpose**: Multi-platform input simulation with fallback support

**Backend Interface**:
```cpp
class InputSimulator {
public:
    virtual bool initialize() = 0;
    virtual bool simulate_key_press(int key_code) = 0;
    virtual bool simulate_mouse_move(int x, int y) = 0;
    virtual ~InputSimulator() = default;
};

// Available backends
std::unique_ptr<InputSimulator> create_x11_simulator();
std::unique_ptr<InputSimulator> create_wayland_simulator();
std::unique_ptr<InputSimulator> create_kde_simulator();
std::unique_ptr<InputSimulator> create_sdl2_simulator();
std::unique_ptr<InputSimulator> create_uinput_simulator();
```

**System Dependencies**:
- X11: `libx11-dev`, `libxtst-dev`
- Wayland: `libwayland-dev`, `wayland-protocols`
- SDL2: `libsdl2-dev`
- KDE: KDE development libraries

### gamepad-mcp-server
**Location**: `https://github.com/sparesparrow/gamepad-mcp-server`
**Purpose**: MCP server providing AI-accessible gamepad control

**MCP Tools Provided**:
```json
{
  "tools": [
    {
      "name": "gamepad_list_devices",
      "description": "List all connected gamepad devices"
    },
    {
      "name": "gamepad_load_mapping",
      "description": "Load a gamepad mapping configuration"
    },
    {
      "name": "gamepad_get_mapping",
      "description": "Get current mapping configuration"
    },
    {
      "name": "gamepad_remap_button",
      "description": "Remap a gamepad button to keyboard/mouse input"
    },
    {
      "name": "gamepad_start_voice_alerts",
      "description": "Enable voice alerts for gamepad events"
    },
    {
      "name": "gamepad_connect_bluetooth",
      "description": "Connect to a Bluetooth gamepad device"
    }
  ]
}
```

**MCP Resources**:
- `gamepad://devices` - Connected device information
- `gamepad://mappings` - Available mapping presets
- `gamepad://status` - Current system status

### gamepad-bluetooth
**Location**: `https://github.com/sparesparrow/gamepad-bluetooth`
**Purpose**: Bluetooth HID device discovery and connection

**Key Classes**:
```cpp
class BluetoothScanner {
public:
    std::vector<BluetoothDevice> scan_devices();
    bool start_scan();
    void stop_scan();
};

class BluetoothConnector {
public:
    bool connect(const BluetoothDevice& device);
    bool disconnect();
    BluetoothConnectionStatus get_status();
};

class HIDParser {
public:
    GamepadEvent parse_hid_report(const std::vector<uint8_t>& report);
    bool validate_device(const BluetoothDevice& device);
};
```

**System Dependencies**:
- BlueZ: `libbluetooth-dev`
- BlueZ Utils: `bluez-utils`

### gamepad-audio
**Location**: `https://github.com/sparesparrow/gamepad-audio`
**Purpose**: Audio backend and voice alert system

**Audio Interface**:
```cpp
class AudioBackend {
public:
    virtual bool initialize() = 0;
    virtual bool play_sound(const std::string& sound_file) = 0;
    virtual bool set_volume(float volume) = 0;
    virtual ~AudioBackend() = default;
};

// Voice alerts system
class VoiceAlerts {
public:
    bool initialize();
    bool speak_text(const std::string& text);
    bool play_alert(GamepadEventType event_type);
    void set_voice_parameters(int pitch, int speed);
};
```

**System Dependencies**:
- ALSA: `libasound2-dev`
- PulseAudio: `libpulse-dev`
- eSpeak: `libespeak-dev`

### gamepad-config
**Location**: `https://github.com/sparesparrow/gamepad-config`
**Purpose**: Configuration management and preset system

**Configuration API**:
```cpp
class ConfigManager {
public:
    bool load_config(const std::string& config_path);
    bool save_config(const std::string& config_path);
    nlohmann::json get_mapping(const std::string& preset_name);
    std::vector<std::string> list_presets();
    bool validate_config(const nlohmann::json& config);
};

class PresetManager {
public:
    bool load_preset_directory(const std::string& dir_path);
    std::vector<PresetInfo> get_available_presets();
    bool apply_preset(const std::string& preset_name);
};
```

**Configuration Schema**:
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
  },
  "audio": {
    "voice_alerts": true,
    "sound_effects": true
  }
}
```

### gamepad-kde-integration
**Location**: `https://github.com/sparesparrow/gamepad-kde-integration`
**Purpose**: KDE-specific features and cross-device communication

**Key Components**:
```cpp
class KDEConnectClient {
public:
    bool initialize();
    bool pair_device(const std::string& device_id);
    bool send_mapping(const std::string& mapping_json);
    std::vector<KDEDevice> get_paired_devices();
};

class ClipboardMonitor {
public:
    bool start_monitoring();
    void stop_monitoring();
    std::string get_clipboard_content();
    void set_clipboard_content(const std::string& content);
};
```

**System Dependencies**:
- GTK: `libgtk-3-dev`
- KDE Frameworks: `libkf5*` packages

## MCP Integration Details

### Server Configuration

Each MCP server in the ecosystem can be configured independently:

```json
{
  "mcpServers": {
    "gamepad-control": {
      "command": "gamepad-mcp-server",
      "args": ["--config", "/etc/gamepad-mcp/config.json"]
    },
    "gamepad-bluetooth": {
      "command": "gamepad-bluetooth-mcp",
      "args": ["--scan-interval", "30"]
    }
  }
}
```

### Cross-Repository Communication

Components communicate through MCP protocol:

1. **gamepad-mcp-server** acts as the central hub
2. Other repositories expose MCP servers for specific functionality
3. The main orchestrator coordinates between MCP servers

### AI Integration Examples

**Claude Desktop Configuration**:
```json
{
  "mcpServers": {
    "gamepad": {
      "command": "uvx",
      "args": ["gamepad-mcp-server"]
    }
  }
}
```

**Available AI Commands**:
- "List all connected gamepads"
- "Load the gaming mapping preset"
- "Remap A button to spacebar"
- "Connect to Bluetooth gamepad 'Xbox Controller'"
- "Enable voice alerts for button presses"

## Build and Installation

### Prerequisites

```bash
# System dependencies
sudo apt-get install build-essential cmake libx11-dev libxtst-dev \
                     libwayland-dev wayland-protocols libsdl2-dev \
                     libbluetooth-dev libasound2-dev libpulse-dev \
                     libespeak-dev libgtk-3-dev

# Conan package manager
pip install conan

# Rust (for some components)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### Building Individual Repositories

```bash
# Clone and build each repository
for repo in gamepad-core input-backends gamepad-mcp-server \
           gamepad-bluetooth gamepad-audio gamepad-config \
           gamepad-kde-integration; do
    git clone https://github.com/sparesparrow/$repo.git
    cd $repo
    mkdir build && cd build
    conan install .. --build missing
    cmake .. -DCMAKE_BUILD_TYPE=Release
    make -j$(nproc)
    sudo make install
    cd ../..
done
```

### Building Main Orchestrator

```bash
git clone https://github.com/sparesparrow/gamepad-mapper.git
cd gamepad-mapper
mkdir build && cd build
conan install .. --build missing
cmake .. -DWITH_MCP=ON -DWITH_BLUETOOTH=ON -DWITH_ALSA=ON
make -j$(nproc)
sudo make install
```

## Configuration

### Global Configuration

```json
{
  "ecosystem": {
    "mcp_servers": {
      "gamepad-control": "http://localhost:3001",
      "gamepad-bluetooth": "http://localhost:3002",
      "gamepad-audio": "http://localhost:3003"
    },
    "repositories": {
      "config_dir": "/usr/share/gamepad-mapper/config",
      "preset_dir": "/usr/share/gamepad-mapper/presets"
    }
  }
}
```

### MCP Server Configuration

```json
{
  "server": {
    "host": "localhost",
    "port": 3001,
    "cors": {
      "enabled": true,
      "origins": ["http://localhost:3000"]
    }
  },
  "gamepad": {
    "auto_scan": true,
    "scan_interval": 5,
    "default_mapping": "gaming"
  },
  "logging": {
    "level": "info",
    "file": "/var/log/gamepad-mcp.log"
  }
}
```

## Testing

### Unit Testing

Each repository includes comprehensive unit tests:

```bash
# Run tests for a specific repository
cd gamepad-core
mkdir build && cd build
cmake .. -DBUILD_TESTS=ON
make test

# Run integration tests
cd gamepad-mcp-server
mkdir build && cd build
cmake .. -DBUILD_TESTS=ON
ctest --output-on-failure
```

### Integration Testing

```bash
# Test MCP communication between components
cd gamepad-mapper/tests
python integration_test.py

# Test Bluetooth functionality
cd gamepad-bluetooth/tests
./bluetooth_integration_test
```

## Troubleshooting

### Common Issues

1. **MCP Server Connection Failed**
   ```bash
   # Check if MCP servers are running
   netstat -tlnp | grep 3001

   # Verify configuration
   cat ~/.config/claude-desktop/config.json
   ```

2. **Bluetooth Device Not Found**
   ```bash
   # Check Bluetooth service
   systemctl status bluetooth

   # Scan for devices
   bluetoothctl scan on
   ```

3. **Audio Backend Not Working**
   ```bash
   # Check audio services
   systemctl status alsa-restore
   systemctl status pulseaudio

   # Test audio output
   speaker-test -c 2 -t wav
   ```

### Debug Mode

Enable debug logging across all components:

```bash
export GAMEPAD_DEBUG=1
export MCP_DEBUG=1
./gamepad-mcp-server --log-level debug
```

## Development

### Contributing

1. Fork the relevant repository
2. Create a feature branch
3. Make changes with comprehensive tests
4. Submit a pull request

### Code Standards

- C++20 standard
- CMake build system
- Conan for dependency management
- Google Test for unit testing
- Doxygen for documentation

### Repository Maintenance

Each repository should maintain:
- Comprehensive README.md
- API documentation
- Build and test CI/CD
- Semantic versioning
- Changelog

## Performance Considerations

### Optimization Tips

1. **Input Latency**: Use UInput backend for lowest latency
2. **Memory Usage**: Configure appropriate buffer sizes
3. **CPU Usage**: Enable multi-threading for concurrent processing
4. **Network**: Use local MCP communication for best performance

### Monitoring

```bash
# Monitor MCP server performance
curl http://localhost:3001/metrics

# Check system resource usage
top -p $(pgrep gamepad)

# Monitor Bluetooth connections
bluetoothctl devices
```

## Future Enhancements

### Planned Features

1. **Web Interface**: Browser-based configuration and monitoring
2. **Plugin System**: Dynamic loading of custom backends
3. **Cloud Sync**: Cross-device mapping synchronization
4. **AI Training**: Machine learning for optimal mappings
5. **VR Support**: Virtual reality gamepad integration

### Ecosystem Expansion

1. **Mobile Apps**: iOS/Android companion apps
2. **Hardware Integration**: Custom gamepad firmware
3. **Cloud Services**: Remote configuration and monitoring
4. **Analytics**: Usage statistics and optimization insights

---

This integration guide provides the foundation for working with the modular gamepad-mapper ecosystem. Each repository is designed to be independently useful while working seamlessly together through MCP for comprehensive gamepad control and integration.