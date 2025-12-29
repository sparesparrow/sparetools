# SpareTools ESP32 BPM Detector Consumer

Real-time beat detection firmware for ESP32 microcontrollers, integrated into the SpareTools ecosystem.

## Overview

This consumer package provides the ESP32 BPM Detector firmware as part of the SpareTools monorepo. Following the OMS repository separation pattern, this package focuses on application-specific code while leveraging shared components from SpareTools foundation packages.

## Architecture

```
sparetools-bpm-detector (consumer)
├── Dependencies from SpareTools:
│   ├── sparesparrow-protocols/1.0.0 (FlatBuffers schemas)
│   ├── sparetools-hal-sunton/1.0.0 (Display HAL)
│   ├── sparetools-test-harness/2.0.0 (Testing infrastructure)
│   └── sparetools-shared-dev-tools/2.0.0 (Build tools)
├── Application Code:
│   ├── src/ - ESP32 firmware source
│   ├── include/ - Headers
│   └── platformio.ini - PlatformIO configuration
└── Testing:
    ├── CMakeLists.txt - Host-based unit tests
    ├── test/ - Test files
    └── scripts/ - Test utilities
```

## Features

- **Real-time BPM Detection**: Digital signal processing for accurate beat detection
- **Audio Input**: I2S microphone interface support
- **Multiple Displays**: OLED SSD1306 and 7-segment TM1637 support
- **Networking**: HTTP REST API, WebSocket streaming, UDP multicast
- **FlatBuffers Protocol**: Efficient binary serialization using SpareTools schemas
- **Audio Calibration**: Signal quality monitoring and calibration

## Building

### ESP32 Firmware (PlatformIO)

```bash
# Install dependencies via SpareTools
conan install . --profile=esp32_sunton_v3.prof

# Build with PlatformIO
pio run -e esp32-s3
pio run -e esp32-s3-debug
pio run -e esp32-s3-release
```

### Host-based Unit Tests (CMake)

```bash
# Configure and build tests
conan install . --profile=linux-release
conan build .

# Run tests
ctest --output-on-failure
```

## Dependencies

### Required SpareTools Packages

- `sparesparrow-protocols/1.0.0` - FlatBuffers schemas for BPM protocol
- `sparetools-hal-sunton/1.0.0` - Hardware abstraction layer for displays
- `sparetools-test-harness/2.0.0` - Testing infrastructure
- `sparetools-shared-dev-tools/2.0.0` - Build and development tools

### PlatformIO Libraries

- `arduinoFFT` - Audio frequency analysis
- `ArduinoJson` - JSON serialization for REST API
- `flatbuffers` - Runtime FlatBuffers library

## Configuration

The package supports multiple build configurations:

- `esp32-s3` - Standard release build
- `esp32-s3-debug` - Debug build with logging
- `esp32-s3-release` - Optimized production build
- `esp32-s3-ci` - CI/CD build configuration

## Testing

### Unit Tests

Host-based unit tests use mock implementations for ESP32-specific hardware:

```bash
# Run unit tests
conan install . --profile=linux-release
conan build .
ctest
```

### Integration Tests

Integration tests run on actual ESP32 hardware:

```bash
# Flash firmware and run integration tests
pio run -e esp32-s3 -t upload
python scripts/run_integration_tests.py
```

## API

The BPM detector exposes multiple interfaces:

### HTTP REST API
```
GET  /api/status      - Current BPM and status
POST /api/config      - Update configuration
POST /api/calibrate   - Start audio calibration
POST /api/reset       - Reset device
```

### WebSocket Streaming
- Real-time BPM updates
- Status change notifications
- Audio quality metrics

### UDP Multicast
- BPM data broadcast to multiple clients
- Status updates

## Development

### Adding New Features

1. Define protocol changes in `sparesparrow-protocols` schemas
2. Update consumer package to use new schemas
3. Implement feature in ESP32 firmware
4. Add unit tests with mocks
5. Update integration tests

### Schema Updates

When schemas are updated in `sparesparrow-protocols`:

```bash
# Rebuild to get latest headers
conan install . --build=missing
pio run -e esp32-s3
```

## CI/CD Integration

This package integrates with SpareTools CI/CD workflows:

- **esp32-build**: Firmware compilation and basic tests
- **esp32-testing**: Comprehensive test suite
- **esp32-quality**: Code quality checks
- **esp32-security**: Security scanning

## Migration from Standalone Repository

This consumer package replaces the standalone `esp32-bpm-detector` repository, providing:

- **Unified Dependency Management**: All dependencies managed via SpareTools
- **Shared Schemas**: FlatBuffers schemas centralized in `sparesparrow-protocols`
- **Consistent Tooling**: Build, test, and CI/CD tools shared across projects
- **Better Testing**: Host-based unit tests with hardware mocks

## Contributing

Follow the SpareTools contribution guidelines:

1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation
4. Submit pull request
5. CI/CD will validate changes across the ecosystem