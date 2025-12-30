# SpareTools Conan Profiles

Standardized Conan profiles for consistent cross-platform builds across the SpareTools ecosystem.

## Overview

These profiles ensure that all SpareTools packages use the same tool requirements and build configurations, providing consistent development and CI/CD experiences across different platforms.

## Available Profiles

### Linux (x86_64)
- **Profile**: `linux-x86_64`
- **Target**: Linux desktop/server development
- **Compiler**: GCC 11 with libstdc++11
- **Build System**: Ninja

### ESP32 (Xtensa)
- **Profile**: `esp32-xtensa`
- **Target**: ESP32 embedded development
- **Compiler**: GCC 8 cross-compiler
- **Build System**: Ninja
- **Notes**: Configured for ESP32 Xtensa LX6/LX7 cores

### Android (ARMv8)
- **Profile**: `android-armv8`
- **Target**: Android mobile development
- **Compiler**: Clang 12 with libc++
- **Build System**: Ninja
- **API Level**: 28 (Android 9.0)

### macOS (x86_64)
- **Profile**: `macos-x86_64`
- **Target**: macOS Intel development
- **Compiler**: Apple Clang 14 with libc++
- **Build System**: Ninja

### macOS (ARM64)
- **Profile**: `macos-armv8`
- **Target**: macOS Apple Silicon development
- **Compiler**: Apple Clang 14 with libc++
- **Build System**: Ninja

## Tool Requirements

All profiles include these standardized tool requirements:

- **sparetools-cpython/3.12.7**: Bundled Python runtime
- **sparetools-flatbuffers/24.3.25**: FlatBuffers compiler and runtime
- **cmake/[>=3.25]**: Build system generator
- **ninja/[>=1.11]**: Fast build tool

Platform-specific profiles include additional tools:
- **android-ndk/r26d**: Android Native Development Kit (Android profiles only)

## Usage

### Command Line

```bash
# Build package for Linux
conan create . --profile=profiles/linux-x86_64

# Build for ESP32
conan create . --profile=profiles/esp32-xtensa

# Install dependencies for Android
conan install . --profile=profiles/android-armv8
```

### CI/CD Integration

In GitHub Actions workflows:

```yaml
- name: Build with profile
  run: |
    conan create . --profile=profiles/${{ matrix.profile }}
```

### Profile Detection

For automatic profile detection in development:

```bash
# Detect and use appropriate profile
conan profile detect --name=default
# Then customize default profile to match SpareTools standards
```

## Customization

### Adding New Platforms

1. Create new profile file: `profiles/<platform>-<arch>`
2. Include required tool requirements
3. Set appropriate compiler and settings
4. Test cross-compilation

### Updating Tool Versions

Update versions in `versions.yaml` and regenerate profiles:

```yaml
foundation:
  cpython: 3.12.7      # Update this
  flatbuffers: 24.3.25 # Update this
```

## Best Practices

### Tool Requirements vs Package Requirements

- **tool_requires**: Development tools (compilers, generators)
- **requires**: Runtime dependencies (libraries, headers)
- Keep tool_requires in profiles for consistency
- Use requires in conanfile.py for package dependencies

### Profile Selection

- Use specific profiles for CI/CD (explicit platform targeting)
- Use `conan profile detect` for local development
- Document required profile for each package

### Cross-Compilation

- Test profiles on actual target hardware when possible
- Use emulators/simulators for initial validation
- Include platform-specific settings in profile [conf] section

## Troubleshooting

### Profile Not Found
```bash
# List available profiles
conan profile list

# Path to profiles directory
conan create . --profile=./profiles/linux-x86_64
```

### Tool Requirements Issues
```bash
# Check tool availability
conan info <package> --profile=<profile>

# Clean and rebuild tools
conan remove "*" --build --force
conan create . --profile=<profile> --build=missing
```

### Cross-Compilation Problems
```bash
# Validate profile settings
conan profile show <profile>

# Test basic compilation
conan create . --profile=<profile> --build=missing
```