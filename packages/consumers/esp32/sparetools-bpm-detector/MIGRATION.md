# ESP32 BPM Detector Migration to SpareTools

## Overview

The ESP32 BPM Detector has been migrated to the SpareTools consumer package structure following OMS repository separation patterns.

## What Changed

### Before (Standalone Repository)
```
esp32-bpm-detector/
├── src/           # Application code
├── include/       # Headers
├── tests/         # Test files
├── scripts/       # Build scripts
├── conanfile.txt  # Direct dependencies
└── platformio.ini # Build configuration
```

### After (Consumer Package Structure)
```
sparetools/packages/consumers/esp32/sparetools-bpm-detector/
├── conanfile.py       # Consumer package definition
├── CMakeLists.txt     # Host testing configuration
├── platformio.ini     # ESP32 build configuration
├── src/              # Application code (migrated)
├── include/          # Headers (migrated)
├── test/             # Test files (migrated)
└── scripts/          # Build scripts (migrated)

esp32-bpm-detector/ (original repo)
└── conanfile.txt     # Now references consumer package
```

## Benefits

1. **Dependency Management**: Uses SpareTools foundation packages
2. **Shared Schemas**: FlatBuffers schemas from sparetools-protocols
3. **CI/CD Integration**: Reusable workflows and templates
4. **Consistency**: Follows OMS patterns across all projects

## Building

### Option 1: Use Consumer Package Directly
```bash
# From SpareTools root
cd packages/consumers/esp32/sparetools-bpm-detector
conan install . --profile=esp32_sunton_v3.prof
platformio run -e esp32-s3
```

### Option 2: Use Original Repository (References Consumer)
```bash
# From esp32-bpm-detector directory
conan install . --profile=esp32_sunton_v3.prof
# This will pull in the consumer package and its dependencies
platformio run -e esp32-s3
```

## Development Workflow

1. **Make Code Changes**: Edit files in consumer package
2. **Run Tests**: Use SpareTools testing infrastructure
3. **Build Firmware**: Use PlatformIO with Conan dependencies
4. **Version Updates**: Update versions in SpareTools central configuration

## Dependencies

- `sparetools-protocols/1.0.1` - FlatBuffers schemas
- `sparetools-hal-sunton/1.0.0` - Hardware abstraction layer
- `sparetools-test-harness/2.0.0` - Testing infrastructure
- `sparetools-shared-dev-tools/2.0.0` - Build tools
