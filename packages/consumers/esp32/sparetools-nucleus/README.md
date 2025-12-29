# SpareTools NucleusESP32 Consumer

Multi-tool ESP32 firmware integrated into the SpareTools ecosystem.

## Overview

This consumer package provides the NucleusESP32 firmware as part of the SpareTools monorepo. Following the OMS repository separation pattern, this package focuses on application-specific code while leveraging shared components from SpareTools foundation packages.

## Features

- **RF Communication**: Sub-GHz radio frequency analysis and transmission
- **NFC/RFID**: Contactless card reading and emulation
- **IR Communication**: Infrared signal analysis and generation
- **Display Support**: LVGL-based graphical user interface
- **Cryptography**: Hardware-accelerated security features
- **WiFi/Bluetooth**: Network connectivity options

## Architecture

```
sparetools-nucleus (consumer)
├── Dependencies from SpareTools:
│   ├── sparetools-hal-sunton/1.0.0 (Display HAL)
│   ├── sparetools-crypto-suite/1.0.0 (Security)
│   ├── sparetools-test-harness/2.0.0 (Testing)
│   └── sparetools-shared-dev-tools/2.0.0 (Build tools)
├── Application Code:
│   ├── src/ - ESP32 firmware source
│   ├── include/ - Headers
│   └── platformio.ini - PlatformIO configuration
└── Testing:
    ├── test/ - Unit tests
    └── test_harness/ - Integration tests
```

## Building

### ESP32 Firmware (PlatformIO)

```bash
# Install dependencies via SpareTools
conan install . --profile=esp32_sunton_v3.prof

# Build with PlatformIO
pio run -e esp32s3
pio run -e esp32s3-debug
```

### Host-based Unit Tests (CMake)

```bash
# Configure and build tests
conan install . --profile linux-release
conan build .
ctest
```

## Dependencies

### Required SpareTools Packages

- `sparetools-hal-sunton/1.0.0` - Hardware abstraction layer
- `sparetools-crypto-suite/1.0.0` - Cryptography components
- `sparetools-test-harness/2.0.0` - Testing infrastructure
- `sparetools-shared-dev-tools/2.0.0` - Build and development tools

### PlatformIO Libraries

- `lvgl` - Graphics library for displays
- `ELECHOUSE_CC1101_SRC_DRV` - CC1101 radio transceiver
- `MFRC522` - NFC/RFID reader
- `IRremoteESP8266` - Infrared communication

## Configuration

The package supports multiple build configurations:

- `esp32s3` - Standard release build with display
- `esp32s3-debug` - Debug build with logging
- `esp32` - Basic ESP32 support

## Testing

### Unit Tests

Host-based unit tests for core functionality:

```bash
# Run unit tests
conan install . --profile=linux-release
conan build .
ctest
```

### Integration Tests

Hardware integration tests with actual ESP32:

```bash
# Run hardware tests
python test_harness/run_nucleus_unit_tests.py
```

## Development Workflow

1. **Make Code Changes**: Edit files in consumer package
2. **Run Tests**: Use SpareTools testing infrastructure
3. **Build Firmware**: Use PlatformIO with Conan dependencies
4. **Version Updates**: Update versions in SpareTools central configuration

## Migration from Standalone Repository

This consumer package replaces the standalone `nucleus-esp32` repository, providing:

- **Dependency Management**: Uses SpareTools foundation packages
- **Shared Components**: Hardware abstraction layers, crypto suites
- **CI/CD Integration**: Reusable workflows and templates
- **Consistency**: Follows OMS patterns across all projects