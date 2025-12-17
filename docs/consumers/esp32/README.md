# ESP32 Consumer Documentation

## Overview

The ESP32 consumer provides a complete development environment for ESP32-based embedded projects within the SpareTools ecosystem. This consumer includes templates, workflows, and tooling specifically designed for ESP32 microcontroller development.

## Features

- **PlatformIO Integration**: Automated PlatformIO setup and configuration
- **Hardware Simulation**: ESP32 hardware simulation for testing without physical devices
- **Comprehensive Testing**: Unit tests, integration tests, and hardware simulation
- **CI/CD Workflows**: Reusable GitHub Actions workflows for ESP32 projects
- **Package Management**: Conan-based dependency management
- **Bootstrap Automation**: One-command development environment setup

## Supported ESP32 Variants

- ESP32 (original)
- ESP32-S2
- ESP32-S3
- ESP32-C3 (RISC-V)
- ESP32-C6 (RISC-V)

## Project Structure

ESP32 consumer projects follow this structure:

```
esp32-project/
├── .sparetools/           # SpareTools submodule
├── src/                   # ESP32 firmware source code
├── include/               # Header files
├── test/                  # Unit and integration tests
├── test_harness/          # Hardware simulation components
├── scripts/               # Build and development scripts
├── .github/workflows/     # CI/CD workflows
├── platformio.ini         # PlatformIO configuration
├── CMakeLists.txt         # CMake build configuration
├── conanfile.py           # Conan package definition
├── pyproject.toml         # Python project configuration
└── requirements-dev.txt   # Development dependencies
```

## Getting Started

### 1. Bootstrap Development Environment

```bash
python scripts/bootstrap.py
```

This command will:
- Set up Python virtual environment
- Install PlatformIO and ESP32 platform
- Configure development tools
- Initialize test harness

### 2. Build ESP32 Firmware

```bash
# Build for default board
pio run -e esp32dev

# Build for specific board
pio run -e esp32-s3-devkitc-1
```

### 3. Run Tests

```bash
# Run all tests
python scripts/test_runner.py

# Run specific test types
python scripts/test_runner.py --unit-only
python scripts/test_runner.py --integration-only
```

## Configuration

### PlatformIO Configuration

The `platformio.ini` file includes configurations for multiple ESP32 boards:

```ini
[env:esp32dev]
board = esp32dev
build_flags =
    -Ofast
    -D BOARD_NAME="esp32dev"

[env:esp32-s3-devkitc-1]
board = esp32-s3-devkitc-1
build_flags =
    -Ofast
    -D BOARD_NAME="esp32-s3-devkitc-1"
```

### Hardware Simulation

ESP32 projects include hardware simulation for testing:

```python
from sparetools_test_harness import ESP32TestHarness

harness = ESP32TestHarness()
result = harness.verify_nfc_communication(expected_data, actual_data)
```

## CI/CD Integration

ESP32 consumer projects include reusable GitHub Actions workflows:

- **esp32-quality.yml**: Code quality checks (linting, formatting)
- **esp32-testing.yml**: Unit and integration testing
- **esp32-build.yml**: ESP32 firmware builds
- **esp32-security.yml**: Security scanning and SBOM generation

## Available Packages

- **sparetools-nucleus**: NucleusESP32 reference implementation
- Additional ESP32 packages coming soon

## Development Tools

### Bootstrap
```bash
sparetools-cli bootstrap esp32
```

### Testing
```bash
sparetools-cli test esp32
```

### Package Management
```bash
conan install . --build=missing
conan build .
```

## Troubleshooting

### PlatformIO Issues
- Ensure PlatformIO is installed: `pip install platformio`
- Update ESP32 platform: `pio platform update espressif32`

### Hardware Simulation
- Hardware simulation requires Python test harness
- Physical hardware testing requires connected ESP32 device

### Build Issues
- Check ESP32 board configuration in `platformio.ini`
- Verify all dependencies are installed via Conan

## Contributing

When contributing to ESP32 consumer projects:

1. Follow the established project structure
2. Include comprehensive tests with hardware simulation
3. Update documentation for any new features
4. Ensure CI/CD workflows pass for all supported boards

## Reference Implementations

- **NucleusESP32**: Multi-tool device firmware with NFC, RF, and IR capabilities
- More reference implementations coming soon