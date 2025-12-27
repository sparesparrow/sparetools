# Repository Structure & Separation Plan

## Overview

This document outlines the plan for separating the monolithic `gamepad-mapper` project into a modular ecosystem of repositories that integrate with the existing `sparesparrow` MCP ecosystem.

## Current Project Analysis

The current `gamepad-mapper` project is a monolithic application containing:

- **Core Gamepad Logic**: Input mapping and device management
- **Multi-Backend Input Simulation**: X11, Wayland, KDE, SDL2, UInput backends
- **MCP Server Integration**: TinyMCP-based server with JSON-RPC API
- **Bluetooth HID Support**: Device discovery and connection
- **Audio Backend**: ALSA/PulseAudio integration with voice alerts
- **Configuration Management**: JSON-based mapping presets
- **KDE Integration**: Cross-device communication

## Proposed Repository Structure

### 1. `gamepad-core` - Core Gamepad Mapping Logic
**Purpose**: Fundamental gamepad-to-input mapping functionality

**Contents**:
- Gamepad event processing and mapping engine
- Controller manager and device detection
- Multi-controller coordination
- Core data structures and APIs

**Dependencies**:
- None (pure core logic)

**Repository Structure**:
```
gamepad-core/
├── CMakeLists.txt
├── conanfile.py
├── include/
│   ├── gamepad_mapper.h
│   ├── controller_manager.h
│   ├── multi_controller_manager.h
│   └── gamepad_events.h
├── src/
│   ├── gamepad_mapper.cpp
│   ├── controller_manager.cpp
│   └── multi_controller_manager.cpp
└── tests/
    └── unit_tests.cpp
```

### 2. `input-backends` - Multi-Platform Input Simulation
**Purpose**: Platform-specific input simulation with fallback support

**Contents**:
- X11 input simulation
- Wayland input simulation
- KDE input simulation
- SDL2 input simulation
- UInput fallback simulation
- Abstract input simulator interface

**Dependencies**:
- `gamepad-core`
- System libraries (X11, Wayland, SDL2, etc.)

**Repository Structure**:
```
input-backends/
├── CMakeLists.txt
├── conanfile.py
├── include/
│   ├── backends/
│   │   ├── input_simulator.h
│   │   ├── x11_simulator.h
│   │   ├── wayland_simulator.h
│   │   ├── kde_simulator.h
│   │   ├── sdl2_simulator.h
│   │   └── uinput_simulator.h
│   └── input_backend_manager.h
├── src/
│   ├── input_backend_manager.cpp
│   └── backends/
│       ├── x11_simulator.cpp
│       ├── wayland_simulator.cpp
│       ├── kde_simulator.cpp
│       ├── sdl2_simulator.cpp
│       └── uinput_simulator.cpp
└── tests/
    └── backend_tests.cpp
```

### 3. `gamepad-mcp-server` - MCP Integration Server
**Purpose**: MCP server for gamepad control and integration

**Contents**:
- MCP server implementation using TinyMCP
- Gamepad control tools and resources
- Prompt templates for gamepad operations
- MCP protocol handling

**Dependencies**:
- `gamepad-core`
- `input-backends`
- TinyMCP (from existing external/TinyMCP)
- nlohmann_json, jsoncpp

**Repository Structure**:
```
gamepad-mcp-server/
├── CMakeLists.txt
├── conanfile.py
├── mcp-config.json
├── include/
│   ├── mcp_server.h
│   ├── gamepad_server.h
│   └── mcp_prompts_client.h
├── src/
│   ├── mcp_server.cpp
│   ├── gamepad_server.cpp
│   └── mcp_prompts_client.cpp
├── external/
│   └── TinyMCP/ (copied from current project)
└── tests/
    └── mcp_integration_tests.cpp
```

### 4. `gamepad-bluetooth` - Bluetooth HID Device Support
**Purpose**: Wireless gamepad connectivity via Bluetooth

**Contents**:
- Bluetooth device scanning and discovery
- HID device connection and management
- Protocol parsing for gamepad data
- Bluetooth type definitions

**Dependencies**:
- `gamepad-core`
- BlueZ libraries
- System Bluetooth libraries

**Repository Structure**:
```
gamepad-bluetooth/
├── CMakeLists.txt
├── conanfile.py
├── include/
│   ├── bluetooth_scanner.h
│   ├── bluetooth_connector.h
│   ├── bluetooth_types.h
│   └── hid_parser.h
├── src/
│   ├── bluetooth_scanner.cpp
│   ├── bluetooth_connector.cpp
│   ├── hid_parser.cpp
│   └── bluetooth_stubs.cpp
└── tests/
    └── bluetooth_tests.cpp
```

### 5. `gamepad-audio` - Audio Backend & Voice Alerts
**Purpose**: Audio feedback and voice alert system

**Contents**:
- Audio backend implementation (ALSA/PulseAudio)
- Voice alert synthesis using espeak
- Audio configuration and management
- Sound effect management

**Dependencies**:
- ALSA/PulseAudio system libraries
- espeak for voice synthesis

**Repository Structure**:
```
gamepad-audio/
├── CMakeLists.txt
├── conanfile.py
├── include/
│   ├── audio_backend.h
│   └── voice_alerts.h
├── src/
│   ├── audio_backend.cpp
│   └── voice_alerts.cpp
└── tests/
    └── audio_tests.cpp
```

### 6. `gamepad-config` - Configuration Management
**Purpose**: Centralized configuration and preset management

**Contents**:
- JSON configuration file management
- Mapping preset loading and validation
- Configuration schema definitions
- Preset categories (gaming, accessibility, etc.)

**Dependencies**:
- nlohmann_json
- Standard filesystem libraries

**Repository Structure**:
```
gamepad-config/
├── CMakeLists.txt
├── conanfile.py
├── include/
│   ├── config_manager.h
│   └── preset_manager.h
├── src/
│   ├── config_manager.cpp
│   └── preset_manager.cpp
├── config/
│   ├── default_mappings.json
│   ├── gaming_mappings.json
│   ├── accessibility_mappings.json
│   └── ... (all preset files)
└── tests/
    └── config_tests.cpp
```

### 7. `gamepad-kde-integration` - KDE Desktop Integration
**Purpose**: KDE-specific features and cross-device communication

**Contents**:
- KDE Connect client for cross-device sync
- KDE-specific input handling
- Desktop environment integration
- Clipboard monitoring (GTK-based)

**Dependencies**:
- `gamepad-core`
- KDE libraries
- GTK libraries
- KDE Connect

**Repository Structure**:
```
gamepad-kde-integration/
├── CMakeLists.txt
├── conanfile.py
├── include/
│   ├── kde_connect_client.h
│   ├── clipboard_monitor.h
│   └── kde_simulator.h
├── src/
│   ├── kde_connect_client.cpp
│   ├── clipboard_monitor.cpp
│   └── kde_simulator.cpp
└── tests/
    └── kde_integration_tests.cpp
```

### 8. `gamepad-mapper` - Main Orchestrator (Updated)
**Purpose**: Main application that coordinates all modules

**Contents**:
- Main application entry points
- Module coordination and initialization
- High-level configuration management
- Cross-module communication

**Dependencies**:
- All gamepad-* repositories
- MCP client integration

**Repository Structure**:
```
gamepad-mapper/ (updated)
├── CMakeLists.txt
├── conanfile.py
├── README.md
├── BUILDING-CONAN.md
├── MAPPING_GUIDE.md
├── scripts/
│   ├── build-*.sh
│   └── setup scripts
├── src/
│   ├── main.cpp
│   ├── advanced_main.cpp
│   └── orchestrator.cpp (new)
├── include/
│   └── orchestrator.h (new)
├── tools/
│   └── mcp_gamepad_tool.py
└── docs/
    └── integration_guide.md (new)
```

## Integration Strategy

### MCP-Based Communication

All repositories will communicate through MCP servers:

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

### Build System Consistency

- **CMake**: All repositories use CMake for build configuration
- **Conan**: Dependency management across all repositories
- **C++20**: Consistent language standard
- **PkgConfig**: System library detection

### Shared Infrastructure

- **Common CMake Modules**: Shared CMake helper functions
- **Testing Framework**: GTest-based unit testing
- **Documentation**: Doxygen for API documentation
- **CI/CD**: GitHub Actions for automated testing and releases

## Implementation Phases

### Phase 1: Core Extraction
1. Extract `gamepad-core` from current codebase
2. Create minimal repository with core functionality
3. Establish testing infrastructure

### Phase 2: Backend Separation
1. Create `input-backends` repository
2. Extract all input simulator implementations
3. Implement abstract backend interface

### Phase 3: MCP Integration
1. Create `gamepad-mcp-server` repository
2. Integrate with existing MCP ecosystem
3. Establish cross-repository communication

### Phase 4: Feature Modules
1. Extract `gamepad-bluetooth`, `gamepad-audio`, `gamepad-config`
2. Create `gamepad-kde-integration` repository
3. Implement module-specific testing

### Phase 5: Orchestration & Documentation
1. Update main `gamepad-mapper` repository
2. Create integration documentation
3. Establish release coordination

## Benefits of This Architecture

1. **Modular Development**: Independent development and testing of components
2. **Selective Deployment**: Deploy only required functionality
3. **Easier Maintenance**: Focused responsibilities reduce complexity
4. **Enhanced Testing**: Component-level testing improves reliability
5. **Better Reusability**: Components can be used in other projects
6. **MCP Integration**: Seamless integration with AI and automation tools
7. **Cross-Platform**: Consistent behavior across different platforms

## Migration Strategy

1. **Source Code Migration**: Copy relevant source files to new repositories
2. **Dependency Management**: Update conanfile.py files for each repository
3. **Build System Updates**: Create CMakeLists.txt for each module
4. **Configuration Handling**: Distribute configuration files appropriately
5. **Testing Migration**: Move and adapt existing tests

## Repository URLs

Assuming GitHub organization `sparesparrow`:

- `https://github.com/sparesparrow/gamepad-core`
- `https://github.com/sparesparrow/input-backends`
- `https://github.com/sparesparrow/gamepad-mcp-server`
- `https://github.com/sparesparrow/gamepad-bluetooth`
- `https://github.com/sparesparrow/gamepad-audio`
- `https://github.com/sparesparrow/gamepad-config`
- `https://github.com/sparesparrow/gamepad-kde-integration`

This structure transforms the monolithic `gamepad-mapper` into a modular, MCP-enabled ecosystem that integrates seamlessly with the existing `sparesparrow` project portfolio.