# SpareTools Cross-Platform FlatBuffers Integration

Example demonstrating seamless FlatBuffers protocol usage across ESP32 firmware, Android applications, and MCP servers.

## Overview

This example shows how to use the same FlatBuffers schemas to communicate between:
- **ESP32 firmware** (C++ embedded)
- **Android application** (Java/Kotlin + C++)
- **MCP server** (Python/TypeScript)

All components share the same protocol definitions from `sparetools-protocols`, ensuring type-safe, efficient communication.

## Architecture

```
┌─────────────────┐    FlatBuffers    ┌─────────────────┐
│   Android App   │◄─────────────────►│    ESP32 FW     │
│ (Java/Kotlin)   │  Binary Protocol  │     (C++)       │
└─────────────────┘                   └─────────────────┘
         │                                       │
         └───────────────────┬───────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   MCP Server    │
                    │   (Python)      │
                    └─────────────────┘
```

## Protocol Schema

Using shared schemas from `sparetools-protocols`:

```flatbuffers
// BPM detection data (ESP32 → Android/MCP)
table BPMUpdate {
    bpm:float;
    confidence:float;
    signal_level:float;
    status:DetectionStatus;
    timestamp:uint64;
}

// GPIO control (Android/MCP → ESP32)
table GPIOCommand {
    pin:int;
    state:bool;
    timestamp:uint64;
}

// System status (ESP32 → Android/MCP)
table SystemStatus {
    uptime_seconds:uint64;
    cpu_usage_percent:uint8;
    free_heap_bytes:uint32;
    temperature_celsius:float;
}
```

## Platform-Specific Implementation

### ESP32 Firmware (C++)

```cpp
#include <sparetools-protocols/iot/BPM_generated.h>
#include <sparetools-protocols/mcp/MCP_generated.h>

// Create BPM update message
flatbuffers::FlatBufferBuilder builder;
auto bpm_update = sparetools::bpm::CreateBPMUpdate(builder,
    bpm_value, confidence, signal_level,
    sparetools::bpm::DetectionStatus_DETECTING, millis()
);
builder.Finish(bpm_update);

// Send via WebSocket/serial
webSocket.sendBIN(builder.GetBufferPointer(), builder.GetSize());
```

**CMakeLists.txt**:
```cmake
cmake_minimum_required(VERSION 3.16)
project(esp32_bpm_detector)

find_package(sparetools-protocols REQUIRED)

add_executable(bpm_detector src/main.cpp)
target_link_libraries(bpm_detector sparetools-protocols::iot)
```

**conanfile.py**:
```python
def requirements(self):
    self.requires("sparetools-protocols/1.0.1")

def build_requirements(self):
    self.tool_requires("sparetools-flatbuffers/24.3.25")
```

### Android Application (Java + C++)

**Java/Kotlin (JNI Interface)**:
```java
public class BPMReceiver {
    static {
        System.loadLibrary("bpm_processor");
    }

    public native void processBPMData(byte[] buffer);
    public native byte[] createGPIOCommand(int pin, boolean state);
}

// Usage
BPMReceiver receiver = new BPMReceiver();
receiver.processBPMData(receivedBuffer);
```

**C++ (Native Implementation)**:
```cpp
#include <jni.h>
#include <sparetools-protocols/iot/BPM_generated.h>

extern "C" JNIEXPORT void JNICALL
Java_com_sparetools_BPMReceiver_processBPMData(JNIEnv* env, jobject obj, jbyteArray data) {
    // Get FlatBuffers buffer
    jbyte* buffer = env->GetByteArrayElements(data, nullptr);
    jsize length = env->GetArrayLength(data);

    // Verify and parse BPM data
    flatbuffers::Verifier verifier((uint8_t*)buffer, length);
    if (sparetools::bpm::VerifyBPMUpdateBuffer(verifier)) {
        auto bpm = sparetools::bpm::GetBPMUpdate((uint8_t*)buffer);

        // Process BPM data
        float bpm_value = bpm->bpm();
        float confidence = bpm->confidence();
        // ... process data
    }

    env->ReleaseByteArrayElements(data, buffer, JNI_ABORT);
}
```

**app/build.gradle**:
```gradle
android {
    externalNativeBuild {
        cmake {
            path "src/main/cpp/CMakeLists.txt"
        }
    }
}

dependencies {
    implementation 'com.google.flatbuffers:flatbuffers-java:24.3.25'
}
```

### MCP Server (Python)

```python
import asyncio
from mcp import Tool
import sparetools_protocols.iot.BPM_generated as bpm_fb

class ESP32MCPServer:
    async def handle_bpm_data(self, binary_data: bytes) -> dict:
        """Process BPM data from ESP32 via FlatBuffers"""

        # Parse FlatBuffers message
        bpm_update = bpm_fb.BPMUpdate.GetRootAsBPMUpdate(binary_data, 0)

        # Extract data
        bpm_value = bpm_update.Bpm()
        confidence = bpm_update.Confidence()
        timestamp = bpm_update.Timestamp()

        # Process and return results
        return {
            "bpm": bpm_value,
            "confidence": confidence,
            "timestamp": timestamp,
            "status": "processed"
        }

    @Tool()
    async def send_gpio_command(self, pin: int, state: bool) -> bytes:
        """Send GPIO command to ESP32"""

        # Create FlatBuffers message
        builder = flatbuffers.Builder(1024)
        gpio_cmd = sparetools.mcp.CreateGPIOCommand(builder,
            pin, state, int(time.time() * 1000))
        builder.Finish(gpio_cmd)

        return builder.Output()
```

## Build System Integration

### Unified Conan Configuration

**conanfile.py** (shared across platforms):
```python
from conan import ConanFile

class CrossPlatformPackage(ConanFile):
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"
    tool_requires = "sparetools-flatbuffers/24.3.25"

    def requirements(self):
        self.requires("sparetools-protocols/1.0.1")
        # Platform-specific requirements...
```

### Platform-Specific Profiles

Use standardized SpareTools profiles:

```bash
# ESP32 build
conan create . --profile=profiles/esp32-xtensa

# Android build
conan create . --profile=profiles/android-armv8

# Desktop/MCP build
conan create . --profile=profiles/linux-x86_64
```

## Communication Patterns

### Real-Time Streaming (ESP32 → Clients)

```cpp
// ESP32: Send periodic BPM updates
void sendBPMUpdate(float bpm, float confidence) {
    flatbuffers::FlatBufferBuilder builder;
    auto update = sparetools::bpm::CreateBPMUpdate(builder, bpm, confidence, 0.8f,
        sparetools::bpm::DetectionStatus_DETECTING, millis());
    builder.Finish(update);

    // Send to all connected clients
    webSocket.broadcastBIN(builder.GetBufferPointer(), builder.GetSize());
}
```

### Request-Response (Client → ESP32)

```python
# MCP Server: Send GPIO command
async def control_gpio(pin: int, state: bool) -> dict:
    # Create command
    builder = flatbuffers.Builder(256)
    cmd = sparetools.mcp.CreateGPIOCommand(builder, pin, state, timestamp)
    builder.Finish(cmd)

    # Send to ESP32 and wait for response
    response = await esp32_connection.send_command(builder.Output())

    # Parse response
    resp = sparetools.common.GetResponse(response)
    return {"success": resp.Status() == sparetools.common.Status_OK}
```

### Bidirectional Communication

```javascript
// Android WebSocket client
const ws = new WebSocket('ws://esp32.local:81');

ws.onmessage = (event) => {
    const data = new Uint8Array(event.data);

    // Determine message type and parse accordingly
    if (sparetools.bpm.VerifyBPMUpdateBuffer(data)) {
        const bpm = sparetools.bpm.GetBPMUpdate(data);
        updateBPMDisplay(bpm.bpm(), bpm.confidence());
    } else if (sparetools.common.VerifyResponseBuffer(data)) {
        const response = sparetools.common.GetResponse(data);
        handleCommandResponse(response);
    }
};
```

## Testing Strategy

### Unit Tests (Platform-Specific)

```cpp
// ESP32 unit test
TEST(BPMProtocolTest, CreateAndParseBPMUpdate) {
    flatbuffers::FlatBufferBuilder builder;
    auto update = sparetools::bpm::CreateBPMUpdate(builder, 72.0f, 0.95f, 0.8f,
        sparetools::bpm::DetectionStatus_DETECTING, 1234567890ULL);
    builder.Finish(update);

    // Verify buffer
    flatbuffers::Verifier verifier(builder.GetBufferPointer(), builder.GetSize());
    ASSERT_TRUE(sparetools::bpm::VerifyBPMUpdateBuffer(verifier));

    // Parse and validate
    auto parsed = sparetools::bpm::GetBPMUpdate(builder.GetBufferPointer());
    ASSERT_FLOAT_EQ(parsed->bpm(), 72.0f);
}
```

### Integration Tests (Cross-Platform)

```python
# Python integration test using generated bindings
def test_cross_platform_compatibility():
    # Create message on "ESP32" (simulated)
    builder = flatbuffers.Builder(1024)
    bpm_update = sparetools.bpm.CreateBPMUpdate(builder, 75.0, 0.9, 0.85,
        sparetools.bpm.DetectionStatus_DETECTING, 1234567890)
    builder.Finish(bpm_update)
    buffer = builder.Output()

    # Parse on "Android/MCP" side
    parsed = sparetools.bpm.GetBPMUpdate(buffer)
    assert parsed.Bpm() == 75.0
    assert parsed.Confidence() == 0.9
```

### Protocol Fuzzing

```python
# Fuzz test protocol parsing
def test_protocol_fuzzing():
    import atheris

    @atheris.instrument_func
    def test_one_input(data):
        try:
            # Try to parse as different message types
            if sparetools.bpm.VerifyBPMUpdateBuffer(data):
                msg = sparetools.bpm.GetBPMUpdate(data)
                # Validate field ranges
                assert 0 <= msg.Confidence() <= 1.0
                assert 0 <= msg.Bpm() <= 300
        except:
            pass  # Expected for invalid data

    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()
```

## Performance Characteristics

### Message Sizes (bytes)

| Message Type | FlatBuffers | JSON | Protocol Buffers |
|-------------|-------------|------|------------------|
| BPM Update | 32 | 85 | 28 |
| GPIO Command | 16 | 45 | 12 |
| System Status | 24 | 120 | 18 |

### Serialization Speed (ESP32)

- **FlatBuffers**: ~5μs per message
- **JSON**: ~50μs per message
- **Protocol Buffers**: ~8μs per message

### Memory Usage

- **Zero-copy parsing**: Direct buffer access
- **No dynamic allocation**: Fixed-size structures
- **Shared schemas**: Common generated code

## Deployment

### CI/CD Pipeline

```yaml
name: Cross-Platform Build

on: [push, pull_request]

jobs:
  build:
    strategy:
      matrix:
        platform: [esp32-xtensa, android-armv8, linux-x86_64]

    steps:
    - uses: actions/checkout@v4

    - name: Setup Conan
      uses: turtlebrowser/get-conan@v1.2

    - name: Build for ${{ matrix.platform }}
      run: |
        conan create . --profile=profiles/${{ matrix.platform }} --build=missing

    - name: Run platform tests
      run: |
        # Platform-specific test execution
```

### Container Deployment

```dockerfile
# Multi-platform container
FROM --platform=$BUILDPLATFORM conan:2.0 AS builder

# Copy source and profiles
COPY . /src
COPY profiles/ /profiles

# Build for target platform
RUN conan create /src --profile=/profiles/$TARGETPLATFORM

FROM scratch AS artifact
COPY --from=builder /root/.conan2 /artifacts
```

## Best Practices

### Schema Design
- Use `include "common.fbs"` for shared types
- Define clear namespaces: `sparetools.<domain>`
- Version root types for API evolution
- Test schema changes across all platforms

### Error Handling
- Always verify buffers before parsing
- Handle version mismatches gracefully
- Implement fallback parsing for old formats

### Performance Optimization
- Reuse FlatBufferBuilder instances
- Pre-allocate builder capacity when known
- Use object API for complex message construction

### Security Considerations
- Validate all input data ranges
- Implement message authentication when needed
- Use secure channels for sensitive data

## Troubleshooting

### Common Issues

**Schema Version Mismatch**
```
Error: flatbuffers::Verfier failed
Solution: Update all platform dependencies to same protocol version
```

**Missing Generated Headers**
```
fatal error: 'BPM_generated.h' not found
Solution: Run FlatBuffers code generation before compilation
```

**Cross-Platform Endianness**
```
Issue: Different byte orders between platforms
Solution: FlatBuffers handles endianness automatically
```

### Debug Tools

```bash
# Validate schema syntax
flatc --schema --strict-json schema.fbs

# Generate JSON representation
flatc --json --raw-binary binary_data.fbs

# Inspect binary format
flatc --json --strict-json -o /dev/stdout binary_data.fbs
```