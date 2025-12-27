# Gamepad-Mapper Module Analysis & Separation Plan

## Current Project Structure Analysis

### Core Components Identified

Based on the analysis of the current `gamepad-mapper` project, the following separable modules have been identified:

### 1. Gamepad Core (`gamepad-core`)
**Location**: Core mapping logic and controller management
**Files**:
- `src/gamepad_mapper.cpp` - Main mapping engine
- `src/controller_manager.cpp` - Gamepad device management
- `src/multi_controller_manager.cpp` - Multi-device coordination
- `include/gamepad_mapper.h` - Core API
- `include/controller_manager.h` - Controller management API
- `include/multi_controller_manager.h` - Multi-controller API
- `include/gamepad_events.h` - Event definitions

**Dependencies**: None (pure core logic)
**Purpose**: Core gamepad-to-input mapping functionality

### 2. Input Backend System (`input-backends`)
**Location**: Multi-platform input simulation backends
**Files**:
- `src/input_backends/x11_simulator.cpp`
- `src/input_backends/wayland_simulator.cpp`
- `src/input_backends/kde_simulator.cpp`
- `src/input_backends/sdl2_simulator.cpp`
- `src/input_backends/uinput_simulator.cpp`
- `include/backends/input_simulator.h` (base class)
- `include/backends/x11_simulator.h`
- `include/backends/wayland_simulator.h`
- `include/backends/kde_simulator.h`
- `include/backends/sdl2_simulator.h`
- `include/backends/uinput_simulator.h`

**System Dependencies**: X11, Wayland, KDE, SDL2, UInput
**Purpose**: Platform-specific input simulation with fallback support

### 3. MCP Server Integration (`gamepad-mcp-server`)
**Location**: Model Context Protocol server implementation
**Files**:
- `src/mcp_server.cpp` - MCP server implementation
- `src/gamepad_server.cpp` - Gamepad-specific MCP server
- `src/mcp_prompts_client.cpp` - MCP prompts integration
- `include/mcp_server.h` - MCP server API
- `include/gamepad_server.h` - Gamepad server API
- `include/mcp_prompts_client.h` - MCP prompts API
- `external/TinyMCP/` - TinyMCP dependency

**Dependencies**: TinyMCP, nlohmann_json, jsoncpp, boost, openssl
**Purpose**: MCP-based remote control and AI integration

### 4. Bluetooth HID Support (`gamepad-bluetooth`)
**Location**: Bluetooth device discovery and connection
**Files**:
- `src/bluetooth_scanner.cpp` - Device scanning
- `src/bluetooth_connector.cpp` - Device connection
- `src/hid_parser.cpp` - HID protocol parsing
- `src/bluetooth_stubs.cpp` - Stub implementations
- `include/bluetooth_scanner.h` - Scanner API
- `include/bluetooth_connector.h` - Connector API
- `include/bluetooth_types.h` - Bluetooth type definitions
- `include/hid_parser.h` - HID parser API

**System Dependencies**: BlueZ (bluetooth)
**Purpose**: Bluetooth HID device support and wireless connectivity

### 5. Audio Backend System (`gamepad-audio`)
**Location**: Audio output and voice alerts
**Files**:
- `src/audio_backend.cpp` - Audio backend implementation
- `src/voice_alerts.cpp` - Voice alert system
- `include/audio_backend.h` - Audio backend API
- `include/voice_alerts.h` - Voice alerts API

**System Dependencies**: ALSA, PulseAudio, espeak
**Purpose**: Audio feedback and voice alert functionality

### 6. Configuration Management (`gamepad-config`)
**Location**: Configuration loading and preset management
**Files**:
- `config/*.json` - All mapping configuration files
- Configuration loading logic (extracted from core)

**Dependencies**: nlohmann_json
**Purpose**: JSON-based mapping configurations and presets

### 7. KDE Integration (`gamepad-kde-integration`)
**Location**: KDE-specific features and cross-device communication
**Files**:
- `src/kde_connect_client.cpp` - KDE Connect integration
- `include/kde_connect_client.h` - KDE Connect API
- KDE-specific simulator components

**System Dependencies**: KDE libraries
**Purpose**: KDE desktop environment integration and device sync

### 8. Additional Components

#### Clipboard Monitor (`clipboard-monitor`)
**Files**:
- `src/clipboard_monitor.cpp`
- `include/clipboard_monitor.h`

**System Dependencies**: GTK
**Purpose**: Clipboard content monitoring

## Integration Architecture

### MCP as Central Communication Protocol

All components will communicate through MCP (Model Context Protocol) servers:

```
┌─────────────────┐    ┌──────────────────┐
│   gamepad-core  │◄──►│ gamepad-mcp-server│
└─────────────────┘    └──────────────────┘
         │                       │
         ├───────────────────────┼─────────────────────── MCP
         │                       │
┌────────▼────────┐    ┌─────────▼──────────┐
│ input-backends  │    │ gamepad-bluetooth  │
└─────────────────┘    └────────────────────┘
         │                       │
┌────────▼────────┐    ┌─────────▼──────────┐
│ gamepad-audio   │    │ gamepad-config     │
└─────────────────┘    └────────────────────┘
         │
┌────────▼────────┐
│  kde-integration│
└─────────────────┘
```

### Repository Structure Plan

```
sparesparrow/
├── gamepad-core/           # Core mapping logic
├── input-backends/         # Multi-platform input simulation
├── gamepad-mcp-server/     # MCP integration
├── gamepad-bluetooth/      # Bluetooth HID support
├── gamepad-audio/          # Audio backend & voice alerts
├── gamepad-config/         # Configuration management
├── gamepad-kde-integration/# KDE-specific features
└── gamepad-mapper/         # Main orchestrator (uses all above)
```

### Shared Dependencies

- **nlohmann_json**: JSON parsing across all components
- **CMake**: Build system consistency
- **Conan**: Dependency management
- **MCP Protocol**: Communication between components

### Build System Strategy

Each repository will have:
- Independent CMakeLists.txt
- Conan package definition
- Modular build options
- Cross-repository dependency management

This separation enables:
1. **Independent development** of each component
2. **Selective deployment** of required features
3. **Easier testing** of individual modules
4. **Better maintainability** through focused responsibilities
5. **Enhanced reusability** across different projects