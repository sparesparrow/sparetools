# ESP32-Bus-Pirate Conan Package

A Conan package for the ESP32 Bus Pirate firmware - a multi-protocol hacker's tool that turns your ESP32 device into a versatile protocol analyzer and communication tool.

## Overview

This package provides both the source code and pre-built firmware binaries for the ESP32 Bus Pirate, making it easy to integrate into projects that need protocol analysis capabilities or want to provide Bus Pirate functionality alongside their own ESP32 firmware.

## Features

- **Multi-Protocol Support**: I2C, SPI, UART, 1-Wire, CAN, Infrared, Bluetooth, Wi-Fi, Sub-GHz, RFID, JTAG, and more
- **Multiple Board Variants**: Support for ESP32-S3 DevKit, M5 Cardputer, M5 Stick C, LILYGO T-Embed, and other ESP32-S3 boards
- **Source Code Access**: Full source code included for modification and learning
- **Pre-built Binaries**: Ready-to-flash firmware binaries for each supported board
- **PlatformIO Integration**: Built using PlatformIO for consistent development experience

## Package Contents

### Source Code
- Complete ESP32 Bus Pirate source code
- PlatformIO configuration files
- Build scripts and documentation

### Firmware Binaries
- Pre-built `.bin` files for each supported board variant
- Partition table files where applicable
- Firmware flashing instructions

## Supported Boards

| Board | Environment | Description |
|-------|-------------|-------------|
| ESP32-S3 DevKit | `s3-devkit`, `s3-devkit-n16-r8` | Generic ESP32-S3 DevKit with Octal SPIRAM support |
| M5 Cardputer | `cardputer` | M5 Cardputer with screen, keyboard, and peripherals |
| M5 Cardputer ADV | `cardputer-adv` | Advanced Cardputer with additional GPIO pins |
| M5 Stick C Plus 2 | `m5stick` | M5 Stick C with IMU and peripherals |
| LILYGO T-Embed | `t-embed-s3`, `t-embed-s3-cc1101` | T-Embed with/without CC1101 Sub-GHz module |
| M5 Atom S3 Lite | `atom-lite-s3` | Compact Atom S3 board |
| Seeed Studio Xiao S3 | `xiao-esp32s3` | Xiao ESP32-S3 with exposed pins |
| M5 Stamp S3 | `m5stack-stamps3` | Stamp S3 compact board |

## Usage

### As a Conan Dependency

Add to your `conanfile.txt`:

```ini
[requires]
esp32-bus-pirate/1.0.0

[options]
esp32-bus-pirate/*:board=s3-devkit
esp32-bus-pirate/*:build_firmware=True
```

### Building the Package

```bash
# Build for a specific board
conan create . --name esp32-bus-pirate --version 1.0.0 \
  -o board=s3-devkit -o build_firmware=True

# Build for all supported boards
conan create . --name esp32-bus-pirate --version 1.0.0 \
  -o board=all -o build_firmware=True
```

### Accessing Firmware Binaries

After installation, firmware binaries are available in the package's `firmware/` directory:

```python
# In your consuming ConanFile
def package_info(self):
    firmware_dir = self.deps_env_info["esp32-bus-pirate"].ESP32_BUS_PIRATE_FIRMWARE_DIR
    # firmware_dir now points to the firmware binaries
```

### Flashing Firmware

Use the included firmware binaries with your preferred flashing tool:

```bash
# Using esptool.py
esptool.py --chip esp32s3 --port /dev/ttyUSB0 --baud 921600 \
  --before default_reset --after hard_reset write_flash \
  0x0 firmware/esp32-bus-pirate-s3-devkit.bin \
  0x8000 firmware/esp32-bus-pirate-s3-devkit-partitions.bin

# Using PlatformIO
pio run -e s3-devkit --target upload
```

## Package Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `board` | `s3-devkit`, `cardputer`, `m5stick`, `cardputer-adv`, `t-embed-s3`, `atom-lite-s3`, `xiao-esp32s3`, `m5stack-stamps3`, `all` | `s3-devkit` | Target board(s) to build firmware for |
| `build_firmware` | `True`, `False` | `True` | Whether to build firmware binaries |
| `with_libs` | `True`, `False` | `True` | Include PlatformIO library dependencies |

## Development

### Building from Source

1. Clone the ESP32-Bus-Pirate repository:
   ```bash
   git clone https://github.com/geo-tp/ESP32-Bus-Pirate.git
   cd ESP32-Bus-Pirate
   ```

2. Install PlatformIO and build:
   ```bash
   pio run -e s3-devkit  # Build for ESP32-S3 DevKit
   pio run -e cardputer  # Build for M5 Cardputer
   ```

3. Flash the firmware:
   ```bash
   pio run -e s3-devkit --target upload
   ```

### Modifying the Firmware

The source code is included in the package. You can:

1. Extract the source code from the Conan package
2. Modify the code as needed
3. Rebuild using PlatformIO
4. Create a custom firmware variant

## Integration Examples

### ESP32 BPM Detector Integration

The ESP32 BPM Detector project can use this package to provide Bus Pirate functionality alongside BPM detection:

```ini
# conanfile.txt
[requires]
esp32-bus-pirate/1.0.0
sparetools-protocols/1.0.1

[options]
esp32-bus-pirate/*:board=s3-devkit
esp32-bus-pirate/*:build_firmware=False  # Only need source/reference
```

### Custom Firmware Project

Create a project that combines your functionality with Bus Pirate features:

```python
# conanfile.py
from conans import ConanFile

class MyFirmwareConan(ConanFile):
    requires = "esp32-bus-pirate/1.0.0"

    def package_info(self):
        # Access Bus Pirate source for reference
        bp_source = self.deps_env_info["esp32-bus-pirate"].package_dir
        # Access firmware binaries
        bp_firmware = self.deps_env_info["esp32-bus-pirate"].ESP32_BUS_PIRATE_FIRMWARE_DIR
```

## Protocol Support

The ESP32 Bus Pirate supports numerous protocols:

### Digital Protocols
- **I2C** - Scan, sniff, slave mode, EEPROM dump
- **SPI** - EEPROM, Flash, SD card, slave mode
- **UART** - Bridge, read/write with auto-baud detection
- **1-Wire** - iButton, EEPROM support
- **CAN** - Sniff, send/receive CAN frames

### Wireless Protocols
- **Bluetooth** - BLE scanning, spoofing, sniffing
- **Wi-Fi** - Sniffing, deauth attacks, network scanning
- **Sub-GHz** - Radio signal analysis (with CC1101)
- **Infrared** - Universal remote control
- **RFID** - Read/write/clone RFID tags

### Other Features
- **JTAG** - Pinout scanning, SWD support
- **DIO** - Digital I/O manipulation
- **PWM** - Servo control, signal generation
- **LED** - Addressable LED control (50+ protocols)
- **I2S** - Audio playback and recording

## License

This package contains the ESP32 Bus Pirate firmware, which is licensed under the MIT License.

## Links

- [ESP32 Bus Pirate GitHub Repository](https://github.com/geo-tp/ESP32-Bus-Pirate)
- [ESP32 Bus Pirate Wiki](https://github.com/geo-tp/ESP32-Bus-Pirate/wiki)
- [PlatformIO Documentation](https://docs.platformio.org/)
- [Conan Package Manager](https://conan.io/)




