# SpareTools BPM Schemas

FlatBuffers schema definitions for the ESP32 BPM Detector protocol within the SpareTools ecosystem.

## Overview

This package contains the centralized schema definitions for the BPM detection protocol, used by:

- **sparetools-bpm-detector**: ESP32 firmware (C++)
- Future BPM-related consumers and providers

## Schema Files

- `schemas/bpm_protocol.fbs`: Main FlatBuffers schema defining all message types, requests, responses, and data structures

## Generated Code

The package automatically generates:

- **C++ headers**: `generated/cpp/bpm_protocol_generated.h`
- **Python bindings**: `generated/python/bpm_protocol_generated.py` (if enabled)

## Usage

### In SpareTools Consumer Packages

```python
# In conanfile.py
def requirements(self):
    self.requires("sparetools-bpm-schemas/2.0.0")
```

### C++ (ESP32/Arduino)

```cpp
#include "bpm_protocol_generated.h"

using namespace sparesparrow::bpm;

// Create a BPM update message
flatbuffers::FlatBufferBuilder builder;
auto bpm_update = CreateBPMUpdate(
    builder,
    128.5f,  // bpm
    0.87f,   // confidence
    0.72f,   // signal_level
    DetectionStatus_DETECTING,
    // ... other fields
    1234567890ULL  // timestamp
);
builder.Finish(bpm_update);
```

### Python

```python
import bpm_protocol_generated as bpm

# Create a BPM update message
builder = flatbuffers.Builder(1024)
bpm.BPMUpdateStart(builder)
bpm.BPMUpdateAddBpm(builder, 128.5)
bpm.BPMUpdateAddConfidence(builder, 0.87)
# ... set other fields
bpm_update = bpm.BPMUpdateEnd(builder)
builder.Finish(bpm_update)
```

## Protocol Features

- **Request/Response Pattern**: Type-safe client-server communication
- **Streaming Updates**: Real-time BPM detection data
- **Configuration Management**: Runtime parameter adjustment
- **Error Handling**: Comprehensive error codes and reporting
- **Status Monitoring**: Device health and performance metrics

## Dependencies

- FlatBuffers 24.3.25 (via Conan tool requirement)
- CMake 3.15+ (for code generation)

## Integration

This package is part of the SpareTools foundation and integrates with:

- `sparesparrow-protocols`: General protocol schemas
- `sparetools-bpm-detector`: ESP32 BPM detector implementation
- `sparetools-hal-sunton`: ESP32 hardware abstraction

## Versioning

Follows SpareTools semantic versioning:

- **MAJOR**: Breaking protocol changes
- **MINOR**: Backward-compatible additions
- **PATCH**: Bug fixes and optimizations

## License

MIT License - See SpareTools main repository LICENSE file.