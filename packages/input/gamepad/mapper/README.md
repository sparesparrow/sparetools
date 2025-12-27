# Gamepad Mapper

A comprehensive multi-backend gamepad to keyboard/mouse input mapper with MCP (Model Control Protocol) support for dynamic remapping.

## Features

### Multi-Backend Input Simulation
- **X11 Backend**: Primary backend for Xorg desktop environments
- **Wayland Backend**: Support for modern Wayland compositors (detection only - limited functionality)
- **KDE Backend**: Native KDE Plasma integration with DBus and KWin
- **SDL2 Backend**: Cross-platform fallback with event injection
- **UInput Backend**: Kernel-level input injection for maximum compatibility

### Intelligent Backend Detection
- Automatic detection of available display servers and desktop environments
- Graceful fallback when primary backends are unavailable
- Priority-based backend selection (KDE > Wayland > X11 > SDL2 > UInput)

### MCP Protocol Support
- Full MCP server implementation using TinyMCP SDK
- Dynamic configuration and remapping via JSON-RPC 2.0
- Tool-based interface for AI assistants and automation
- Stdio transport for seamless integration

### Pre-configured Mappings
- **Default mappings**: General purpose keyboard and mouse controls
- **Browser mappings**: Optimized for web browsing (tabs, scrolling, copy/paste)
- **Cursor IDE mappings**: Tailored for Cursor IDE development workflow

## Requirements

### System Requirements
- Linux (primary target platform)
- C++17 compatible compiler (GCC 7+, Clang 5+)
- CMake 3.20+
- Conan package manager

### Dependencies
- nlohmann_json (header-only JSON library)
- X11 libraries (for X11 backend)
- SDL2 (for SDL2 backend)
- TinyMCP (for MCP support)

## Installation

### Quick Start with Conan

```bash
# Clone the repository
cd .cursor/gamepad-mapper

# Make scripts executable
chmod +x scripts/build-dev.sh scripts/build-clean.sh

# Build the project
./scripts/build-dev.sh

# The binary will be available at: build-dev/gamepad_mapper_app
```

### Manual Build

```bash
# Install dependencies via package manager
sudo apt-get install build-essential cmake libx11-dev libxtst-dev libsdl2-dev libudev-dev

# Configure Conan profile
conan profile detect --force

# Install dependencies
conan install . --build=missing

# Build
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

## Usage

### Basic Usage

```bash
# Start with default mappings
./gamepad_mapper_app

# Use specific configuration
./gamepad_mapper_app -c config/browser_mappings.json

# Start as MCP server
./gamepad_mapper_app -m
```

### Command Line Options

```
Usage: gamepad_mapper_app [OPTIONS]

Options:
  -c, --config FILE     Load configuration file (default: config/default_mappings.json)
  -m, --mcp            Enable MCP server mode (stdio transport)
  -h, --help           Show this help message
  -v, --version        Show version information

Examples:
  ./gamepad_mapper_app                                    # Start with default config
  ./gamepad_mapper_app -c config/browser_mappings.json    # Use browser mappings
  ./gamepad_mapper_app -m                                 # Start as MCP server
```

### MCP Server Mode

When started with the `-m` flag, the application runs as an MCP server that can be controlled by MCP clients:

```bash
# Available MCP tools:
# - add_mapping: Add a new gamepad to keyboard/mouse mapping
# - remove_mapping: Remove an existing gamepad mapping
# - load_config: Load mappings from a configuration file
# - get_status: Get current status of the gamepad mapper
```

### Configuration Files

The mapper uses JSON configuration files to define gamepad mappings. Each mapping consists of an input (gamepad button/axis) and an output (keyboard key or mouse action).

#### Example Configuration

```json
{
  "description": "Browser optimized mappings",
  "mappings": {
    "A": "KEY_ENTER",
    "B": "KEY_ESC",
    "X": "KEY_TAB",
    "Y": "KEY_LEFTCTRL+KEY_T",
    "LB": "KEY_LEFTALT+KEY_LEFT",
    "RB": "KEY_LEFTALT+KEY_RIGHT",
    "SELECT": "KEY_LEFTCTRL+KEY_W",
    "START": "KEY_F12",
    "DPAD_UP": "KEY_UP",
    "DPAD_DOWN": "KEY_DOWN",
    "DPAD_LEFT": "KEY_LEFT",
    "DPAD_RIGHT": "KEY_RIGHT",
    "LEFT_TRIGGER": "MOUSE_LEFT_CLICK",
    "RIGHT_TRIGGER": "MOUSE_RIGHT_CLICK"
  },
  "analog_mappings": {
    "LEFT_X": "MOUSE_MOVE_X",
    "LEFT_Y": "MOUSE_MOVE_Y"
  },
  "sensitivity": {
    "mouse_speed": 3.0,
    "analog_threshold": 0.15
  }
}
```

#### Gamepad Inputs

| Input | Description |
|-------|-------------|
| `A`, `B`, `X`, `Y` | Face buttons |
| `LB`, `RB` | Left/Right bumpers |
| `LT`, `RT` | Left/Right triggers |
| `SELECT`, `START` | Menu buttons |
| `LS`, `RS` | Left/Right stick clicks |
| `DPAD_UP/DOWN/LEFT/RIGHT` | D-pad directions |
| `LEFT_X`, `LEFT_Y` | Left analog stick axes |
| `RIGHT_X`, `RIGHT_Y` | Right analog stick axes |
| `LEFT_TRIGGER`, `RIGHT_TRIGGER` | Trigger axes |

#### Output Actions

| Action Type | Format | Examples |
|-------------|--------|----------|
| Keyboard | `KEY_NAME` | `KEY_ENTER`, `KEY_ESC`, `KEY_A` |
| Modifiers | `KEY_MOD+KEY_NAME` | `KEY_LEFTCTRL+KEY_C`, `KEY_LEFTALT+KEY_TAB` |
| Mouse | `MOUSE_ACTION` | `MOUSE_LEFT_CLICK`, `MOUSE_RIGHT_CLICK` |
| Mouse Move | `MOUSE_MOVE_X`, `MOUSE_MOVE_Y` | Analog stick to mouse movement |

## UDEV Rules Setup

For proper gamepad access without root privileges, install the UDEV rules:

```bash
# Copy rules to system location
sudo cp scripts/99-gamepad-mapper.rules /etc/udev/rules.d/

# Reload UDEV rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Alternatively, add your user to the 'input' group
sudo usermod -a -G input $USER
```

## Architecture

### Backend System

The mapper uses a priority-based backend system for maximum compatibility:

1. **KDE Backend** (Priority 100): Uses DBus/KWin for native Plasma integration
2. **Wayland Backend** (Priority 80): Wayland protocol support (limited)
3. **X11 Backend** (Priority 60): XTest extension for Xorg environments
4. **SDL2 Backend** (Priority 40): Cross-platform event injection
5. **UInput Backend** (Priority 20): Kernel-level virtual device creation

### MCP Integration

The TinyMCP-based server provides:
- JSON-RPC 2.0 compliant communication
- Tool-based API for dynamic configuration
- Stdio transport for easy integration
- Comprehensive error handling and logging

### Threading Model

- Main thread: Event polling and processing
- Backend threads: Input simulation (as needed)
- MCP server: Asynchronous request handling

## Development

### Building for Development

```bash
# Build with debug symbols and all backends enabled
./scripts/build-dev.sh

# Clean build artifacts
./scripts/build-clean.sh
```

### Testing

```bash
# Run unit tests (if implemented)
cd build-dev
make test
```

### Code Structure

```
.cursor/gamepad-mapper/
├── CMakeLists.txt           # Build configuration
├── conanfile.py            # Dependency management
├── src/
│   ├── main.cpp            # Application entry point
│   ├── gamepad_mapper.cpp  # Core mapping logic
│   ├── gamepad_server.cpp # MCP server implementation
│   └── input_backends/     # Backend implementations
│       ├── x11_simulator.cpp
│       ├── wayland_simulator.cpp
│       ├── kde_simulator.cpp
│       ├── sdl2_simulator.cpp
│       └── uinput_simulator.cpp
├── include/
│   ├── gamepad_mapper.h    # Public API
│   ├── gamepad_server.h   # MCP server interface
│   └── backends/           # Backend interfaces
├── config/                 # Configuration files
├── scripts/               # Build and utility scripts
└── external/TinyMCP/      # MCP SDK dependency
```

## Troubleshooting

### Common Issues

1. **Permission denied on gamepad access**
   - Install UDEV rules or add user to 'input' group
   - Check device permissions: `ls -la /dev/input/event*`

2. **Backend detection fails**
   - Verify display server: `echo $DISPLAY` (X11) or `echo $WAYLAND_DISPLAY` (Wayland)
   - Check desktop environment: `echo $XDG_CURRENT_DESKTOP`

3. **UInput backend not working**
   - Ensure uinput kernel module: `lsmod | grep uinput`
   - Load module if needed: `sudo modprobe uinput`

4. **MCP server connection issues**
   - Verify stdio transport is being used correctly
   - Check MCP client configuration

### Debug Output

Enable verbose logging by modifying the source code or adding debug flags during compilation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- TinyMCP SDK for MCP protocol implementation
- nlohmann/json for JSON handling
- SDL2 project for cross-platform input handling
- Linux kernel uinput subsystem for virtual device support