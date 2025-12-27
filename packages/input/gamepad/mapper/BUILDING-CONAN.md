# Building Gamepad Mapper with Conan

This document provides detailed instructions for building the Gamepad Mapper project using Conan package manager.

## Prerequisites

### System Requirements
- Linux operating system
- CMake 3.20 or higher
- Conan 2.0 or higher
- C++17 compatible compiler (GCC 7+, Clang 5+)
- Bluetooth adapter (for Bluetooth HID support)

### System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential cmake pkg-config libbluetooth-dev libudev-dev

# Fedora/CentOS
sudo dnf install gcc gcc-c++ cmake pkgconfig bluez-libs-devel systemd-devel

# Arch Linux
sudo pacman -S base-devel cmake bluez-libs systemd-libs
```

## Conan Setup

### Install Conan
```bash
# Install Conan (if not already installed)
pip install conan

# Configure Conan profile
conan profile detect --force

# Optional: Create a custom profile for this project
conan profile show > gamepad_mapper_profile
# Edit gamepad_mapper_profile as needed
```

## Building with Bluetooth Support

### Bluetooth HID Device Support

The project includes optional Bluetooth HID device support for connecting wireless gamepads directly via Bluetooth. This feature requires:

#### System Bluetooth Setup
```bash
# Install Bluetooth utilities
sudo apt-get install bluetooth bluez-tools

# Start Bluetooth service
sudo systemctl start bluetooth
sudo systemctl enable bluetooth

# Verify Bluetooth adapter
bluetoothctl list
bluetoothctl show
```

#### Build with Bluetooth Support
```bash
# Clone and enter the project directory
cd .cursor/gamepad-mapper

# Install dependencies with Bluetooth support (default enabled)
conan install . --build=missing

# Build the project
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DWITH_BLUETOOTH=ON
make -j$(nproc)

# Alternative: Use the provided build script
cd ..
chmod +x scripts/build-dev.sh
./scripts/build-dev.sh
```

#### Bluetooth Configuration

Create or modify the Bluetooth configuration file:

```bash
# Edit Bluetooth device mappings
nano config/bluetooth_mappings.json
```

Example Bluetooth configuration:
```json
{
  "scan_timeout": 10,
  "auto_connect": true,
  "devices": {
    "Xbox Wireless Controller": {
      "vendor_id": "045e",
      "product_id": "02fd",
      "mappings": {
        "A": "KEY_ENTER",
        "B": "KEY_ESC",
        "X": "KEY_SPACE",
        "Y": "KEY_LEFTCTRL",
        "DPAD_UP": "KEY_UP",
        "DPAD_DOWN": "KEY_DOWN",
        "DPAD_LEFT": "KEY_LEFT",
        "DPAD_RIGHT": "KEY_RIGHT"
      },
      "analog_mappings": {
        "LEFT_X": "MOUSE_MOVE_X",
        "LEFT_Y": "MOUSE_MOVE_Y"
      }
    }
  }
}
```

### Building without Bluetooth Support

If you don't need Bluetooth support or want to reduce dependencies:

```bash
# Build without Bluetooth
cmake .. -DCMAKE_BUILD_TYPE=Release -DWITH_BLUETOOTH=OFF
make -j$(nproc)
```

## Backend-Specific Builds

### X11 Backend
```bash
sudo apt-get install libx11-dev libxtst-dev
cmake .. -DWITH_X11=ON
```

### Wayland Backend
```bash
sudo apt-get install libwayland-dev wayland-protocols
cmake .. -DWITH_WAYLAND=ON
```

### SDL2 Backend
```bash
sudo apt-get install libsdl2-dev
cmake .. -DWITH_SDL2=ON
```

### KDE Backend
```bash
# KDE backend uses DBus, typically available in KDE environments
cmake .. -DWITH_KDE=ON
```

### UInput Backend
```bash
# UInput is part of the Linux kernel input subsystem
cmake .. -DWITH_UINPUT=ON
```

## Testing Bluetooth Integration

### Verify Bluetooth Setup
```bash
# Check Bluetooth service status
sudo systemctl status bluetooth

# Test Bluetooth device discovery
bluetoothctl scan on
# Wait for devices to appear, then Ctrl+C

# Test with btscanner (if available)
./btscanner
```

### Test Gamepad Mapper with Bluetooth
```bash
# Start the mapper (will automatically detect Bluetooth devices)
./build/gamepad_mapper_app

# The application will:
# 1. Scan for Bluetooth HID devices
# 2. Attempt to connect to discovered gamepads
# 3. Load appropriate device mappings
# 4. Start processing input events
```

### Troubleshooting Bluetooth Issues

#### Common Problems

1. **Bluetooth adapter not found**
   ```bash
   # Check if Bluetooth is blocked
   rfkill list bluetooth

   # Unblock if necessary
   sudo rfkill unblock bluetooth
   ```

2. **Permission denied**
   ```bash
   # Add user to bluetooth group
   sudo usermod -a -G bluetooth $USER

   # Restart session or run:
   newgrp bluetooth
   ```

3. **Device pairing issues**
   ```bash
   # Use bluetoothctl for manual pairing
   bluetoothctl
   # agent on
   # default-agent
   # scan on
   # pair <MAC_ADDRESS>
   # trust <MAC_ADDRESS>
   # connect <MAC_ADDRESS>
   ```

4. **HID service not found**
   - Ensure the Bluetooth device supports HID profile
   - Some devices may require specific pairing procedures
   - Check device compatibility with Linux Bluetooth stack

#### Debug Output
```bash
# Enable verbose Bluetooth logging
sudo btmon

# Check system logs
journalctl -u bluetooth -f
```

## Development Build

For development with additional debugging:

```bash
# Build with debug symbols and all features
mkdir build-dev && cd build-dev
cmake .. \
    -DCMAKE_BUILD_TYPE=Debug \
    -DWITH_BLUETOOTH=ON \
    -DWITH_X11=ON \
    -DWITH_WAYLAND=ON \
    -DWITH_KDE=ON \
    -DWITH_SDL2=ON \
    -DWITH_UINPUT=ON \
    -DWITH_MCP=ON

make -j$(nproc)

# Run with debug output
./gamepad_mapper_app -v
```

## Conan Package Creation

To create a Conan package for redistribution:

```bash
# Create package
conan create . --build=missing

# Upload to Conan remote (if configured)
conan upload "gamepad-mapper/1.0.0" -c
```

## Cross-Compilation

For cross-compiling to different architectures:

```bash
# Example for ARM64
conan install . --profile:build default --profile:host arm64_profile
cmake .. --toolchain conan_toolchain.cmake
make -j$(nproc)
```

## Performance Optimization

For production builds with optimizations:

```bash
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_FLAGS="-O3 -march=native" \
    -DWITH_BLUETOOTH=ON

make -j$(nproc)

# Optional: Use LTO (Link Time Optimization)
cmake .. -DCMAKE_CXX_FLAGS="-O3 -march=native -flto"
```

## Integration with IDEs

### CLion/CLion Nova
- Import project as CMake project
- Set build directory to `build-dev`
- Use Conan toolchain file

### Visual Studio Code
- Install CMake Tools extension
- Configure with Conan toolchain
- Use provided build scripts

### Vim/Neovim
- Use CMake integration plugins
- Run build scripts manually
- Configure compile_commands.json for LSP