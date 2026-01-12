# SpareTools Protocols

Consolidated FlatBuffers protocol schemas for the SpareTools ecosystem.

## Overview

This package provides a centralized repository of FlatBuffers schemas used across the SpareTools ecosystem. All protocol definitions are organized by domain and automatically generate C++ headers and Python bindings during the build process.

## Schema Organization

### Directory Structure

```
schemas/
├── common/           # Shared types and utilities
│   └── common.fbs
├── iot/              # IoT and sensor protocols
│   ├── BPM.fbs
│   ├── VEHICLE.fbs
│   └── bpm_protocol.fbs
├── medical/          # Medical device protocols
│   └── MIA.fbs
├── mcp/              # Model Context Protocol
│   └── MCP.fbs
└── embedded/         # Embedded system protocols
    ├── hardware.fbs
    ├── audio.fbs
    ├── rf.fbs
    ├── obd.fbs
    └── nucleus_protocol.fbs
```

### Schema Domains

#### Common (`common/`)
Shared types, enumerations, and utilities used across all protocols:
- `Status` enum for operation results
- `Response` envelope structure
- `Timestamp` and `Version` utilities
- `DeviceId` for device identification

#### IoT (`iot/`)
Protocols for IoT sensors and data collection:
- **BPM.fbs**: Comprehensive beat detection protocol with real-time streaming
- **VEHICLE.fbs**: Vehicle telemetry and sensor data
- **bpm_protocol.fbs**: BPM-specific protocol definitions

#### Medical (`medical/`)
Healthcare and medical device protocols:
- **MIA.fbs**: Medical Interface Architecture for device control and telemetry

#### MCP (`mcp/`)
Model Context Protocol for AI agent communication:
- **MCP.fbs**: Hardware control, GPIO, serial telemetry, and system management

#### Embedded (`embedded/`)
Low-level embedded system protocols:
- **hardware.fbs**: Hardware abstraction layer schemas
- **audio.fbs**: Audio processing and capture protocols
- **rf.fbs**: Radio frequency communication schemas
- **obd.fbs**: On-board diagnostics protocols
- **nucleus_protocol.fbs**: ESP32 Nucleus device protocol

## Usage

### As a Library Dependency

Add to your `conanfile.py`:

```python
def requirements(self):
    # Include protocol schemas and generated headers
    self.requires("sparetools-protocols/1.0.1")

def build_requirements(self):
    # Include FlatBuffers compiler for code generation
    self.tool_requires("sparetools-flatbuffers/24.3.25")
```

### Including Generated Headers

```cpp
// Include common types
#include <sparetools-protocols/common/common_generated.h>

// Include domain-specific protocols
#include <sparetools-protocols/iot/BPM_generated.h>
#include <sparetools-protocols/mcp/MCP_generated.h>

// Use in your code
auto builder = flatbuffers::FlatBufferBuilder();
auto bpm_update = CreateBPMUpdate(builder, /* ... */);
builder.Finish(bpm_update);
```

### Component-Based Inclusion

For minimal dependencies, use specific components:

```python
# In package_info()
self.cpp_info.requires = ["sparetools-protocols::iot"]  # Only IoT protocols
# or
self.cpp_info.requires = ["sparetools-protocols::mcp"]  # Only MCP protocols
```

### Accessing Schema Files

Schema files are available as resources for code generation:

```python
def generate(self):
    # Get schema directory
    deps = self.dependencies
    schemas_dir = deps["sparetools-protocols"].cpp_info.resdirs[0]

    # Generate code from specific schemas
    self.run(f"flatc --cpp {schemas_dir}/iot/BPM.fbs")
```

## Code Generation

The package automatically generates:

- **C++ Headers**: Scoped enums, mutable objects, and object API
- **Python Bindings**: Cross-platform testing and scripting
- **Multiple Targets**: Support for various FlatBuffers features

### Generated Files

```
include/sparetools-protocols/
├── common/common_generated.h
├── iot/
│   ├── BPM_generated.h
│   ├── VEHICLE_generated.h
│   └── bpm_protocol_generated.h
├── medical/MIA_generated.h
├── mcp/MCP_generated.h
└── embedded/
    ├── hardware_generated.h
    ├── audio_generated.h
    └── ...
```

## Development Workflow

### Adding New Schemas

1. **Choose domain** or create new domain directory
2. **Add .fbs file** following FlatBuffers syntax
3. **Include common.fbs** for shared types: `include "common.fbs";`
4. **Use proper namespace**: `namespace sparesparrow.<domain>;`
5. **Update CMakeLists.txt** to include new schema
6. **Test generation**: `conan build .`

### Schema Best Practices

- **Include common.fbs** for shared types
- **Use scoped enums** for type safety
- **Version root types** for API evolution
- **Document protocols** with comments
- **Test compatibility** across platforms

### Example Schema

```flatbuffers
include "common.fbs";

namespace sparesparrow.mcp;

// GPIO control message
table GPIOCommand {
  pin:int;
  state:bool;
  timestamp:uint64;
}

root_type GPIOCommand;
```

## Cross-Platform Compatibility

- **ESP32**: Full C++ support for embedded firmware
- **Android**: NDK compatibility for mobile apps
- **Linux/macOS**: Native development and testing
- **Python**: Cross-platform testing and utilities

## Integration Examples

### ESP32 BPM Detector

```cpp
#include <sparetools-protocols/iot/BPM_generated.h>

// Create BPM update message
auto builder = flatbuffers::FlatBufferBuilder();
auto bpm_data = CreateBPMUpdate(builder,
    /* bpm */ 72.5f,
    /* confidence */ 0.95f,
    /* timestamp */ millis()
);
builder.Finish(bpm_data);

// Send over WebSocket/serial
webSocket.sendBIN(builder.GetBufferPointer(), builder.GetSize());
```

### Android App Integration

```java
// Include generated Java classes
import com.sparesparrow.mcp.GPIOCommand;

// Use FlatBuffers in Android
FlatBufferBuilder builder = new FlatBufferBuilder();
int gpioCmd = GPIOCommand.createGPIOCommand(builder,
    /* pin */ 2,
    /* state */ true,
    /* timestamp */ System.currentTimeMillis()
);
builder.finish(gpioCmd);
```

### MCP Server Integration

```python
# Use Python bindings for testing
import sparetools_protocols.mcp_generated as mcp

# Parse binary message
message = mcp.GPIOCommand.GetRootAsGPIOCommand(buffer)
print(f"GPIO Pin {message.Pin()} set to {message.State()}")
```

## Building

```bash
# Build with all code generation
conan create . --build=missing

# Build with Python bindings
conan create . -o generate_python_bindings=True

# Cross-compile for different platforms
conan create . --profile=esp32-xtensa
conan create . --profile=android-armv8
```

## Dependencies

- `flatbuffers/24.3.25`: Runtime library
- `sparetools-flatbuffers/24.3.25`: Compiler tool
- `sparetools-base/2.0.3`: Foundation utilities

## Version Compatibility

- **Semantic versioning** for API stability
- **Backward compatibility** maintained within major versions
- **Breaking changes** require major version bumps
- **Schema evolution** supported through FlatBuffers features