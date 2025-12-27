# Flipper Zero Integration Guide

## Overview

This workspace now includes integration with the Flipper Zero DIY project, enabling advanced WiFi sensing and wardriving capabilities. The Flipper Zero is a portable multi-tool that can be used for various wireless protocols, including WiFi scanning and analysis.

## What is Flipper Zero?

The Flipper Zero is an open-source, portable multi-tool for pentesters and geeks. The "Fucking Cheap Flipper Zero" project provides a cheaper alternative using off-the-shelf components instead of the proprietary Flipper Devices hardware.

### Key Features
- **Multi-protocol support**: RFID, NFC, Sub-GHz, Infrared
- **WiFi capabilities**: Through optional ESP32-S2 development board
- **Extensible firmware**: OpenFlipper firmware with custom applications
- **Hardware hacking**: GPIO access, custom modules

## Integration Components

### 1. Repository Structure
```
research/repositories/flipper_zero/
├── wifi_sensing_integration/     # Integration components
│   ├── scripts/                   # Build and deployment scripts
│   ├── apps/                      # Custom Flipper apps
│   ├── docs/                      # Documentation
│   └── tools/                     # Integration utilities
├── applications/                  # Flipper firmware source
├── firmware.scons                 # Build configuration
└── fbt                            # Build tool
```

### 2. WiFi Sensing Capabilities
- **ESP32-S2 WiFi Dev Board**: For development and debugging
- **Wardriving Integration**: Combined with ESP8266 wardriving tools
- **Data Analysis**: Integration with WiGLE tools for visualization
- **CSI Potential**: Hardware could support Channel State Information extraction

### 3. Unified Build System
The integration provides unified build scripts that combine:
- Flipper Zero firmware compilation
- ESP8266 wardriving device preparation
- WiGLE analysis tools integration

## Quick Start

### 1. Clone and Setup
```bash
# The repository is already cloned
cd research/repositories/flipper_zero

# Run the analysis script
python3 scripts/clone_flipper_zero.py
```

### 2. Build Integration
```bash
# Build everything (skip Flipper if issues)
python3 wifi_sensing_integration/scripts/unified_build.py --skip-flipper

# Or build individual components
bash wifi_sensing_integration/scripts/build_integration.sh
```

### 3. Run Integration
```bash
# Use the integration runner
bash wifi_sensing_integration/build_output/scripts/run_integration.sh
```

## Hardware Setup

### Flipper Zero DIY Bill of Materials
- STM32WB55CGU6 evaluation board (WeAct Studio)
- CC1101 module for Sub-GHz
- ST25R3916 module for NFC
- ST756x 128x64 SPI LCD
- SD card module
- Push buttons and basic electronics

### Optional WiFi Components
- ESP32-S2 development board for WiFi connectivity
- External antennas for better reception

### Wardriving Hardware
- ESP8266 board (D1 Mini)
- GPS module (NEO-6M)
- SD card reader
- OLED display (optional)
- LiPo battery (optional)

## Software Architecture

### Build System
- **FBT (Flipper Build Tool)**: SCons-based build system
- **PlatformIO**: For ESP8266 wardriving firmware
- **Python Scripts**: For integration and automation

### Key Scripts
- `clone_flipper_zero.py`: Repository management and analysis
- `unified_build.py`: Complete integration build system
- `build_integration.sh`: Shell-based build automation

### Integration Points
1. **WiFi Scanning**: Unified scanning across Flipper Zero and ESP8266
2. **Data Storage**: SD card + database integration
3. **Visualization**: Combined data views with WiGLE tools
4. **Automation**: Scheduled scanning and data collection

## Development Workflow

### Building Firmware
```bash
cd research/repositories/flipper_zero
./fbt fw_dist  # Build firmware distribution
```

### Adding Custom Apps
1. Create app in `applications/main/your_app/`
2. Add to `applications/application.fam`
3. Build with `./fbt`

### Testing Integration
1. Build integration suite
2. Flash firmware to hardware
3. Test WiFi scanning capabilities
4. Validate data collection and analysis

## WiFi Sensing Applications

### Current Capabilities
- **WiFi Network Discovery**: Scan and catalog WiFi networks
- **Signal Strength Mapping**: RSSI measurement and mapping
- **Wardriving**: Mobile WiFi mapping with GPS
- **Data Analysis**: Post-processing with WiGLE tools

### Future Enhancements
- **CSI Extraction**: Channel State Information analysis
- **Protocol Analysis**: Deep packet inspection
- **Security Testing**: WiFi vulnerability assessment
- **Mesh Network Analysis**: Multi-device coordination

## Troubleshooting

### Common Issues

#### Build Failures
- Ensure Python 3.8+ is installed
- Check for missing submodules: `git submodule update --init`
- Verify toolchain download

#### Hardware Issues
- Check USB connectivity for Flipper Zero
- Verify ESP32-S2 board connections
- Test GPS module serial communication

#### Integration Issues
- Confirm all repositories are cloned
- Check Python dependencies
- Validate file paths in scripts

### Debug Commands
```bash
# Check Flipper build status
cd research/repositories/flipper_zero
./fbt --help

# Test Python integration
python3 wifi_sensing_integration/scripts/unified_build.py --help

# Check hardware
lsusb | grep flipper
ls /dev/ttyUSB*
```

## Contributing

### Adding New Features
1. Create feature branch in integration directory
2. Implement changes
3. Update documentation
4. Test across all components
5. Submit pull request

### Code Standards
- Follow existing Python code style
- Use descriptive commit messages
- Include documentation for new features
- Test hardware compatibility

## Related Documentation

- [Flipper Zero Official Documentation](https://docs.flipperzero.one/)
- [OpenFlipper Firmware](https://github.com/RogueMaster/flipperzero-firmware-wPlugins)
- [ESP8266 Wardriving](research/repositories/wigle/ESP8266-Wardriving/)
- [WiGLE Tools](research/repositories/wigle/)

## Support

- **Flipper Zero Community**: Discord and forums
- **ESP8266 Wardriving**: Check individual tool documentation
- **WiFi Sensing**: Refer to main workspace documentation

## License

This integration combines multiple open-source projects. Individual components maintain their respective licenses:

- Flipper Zero DIY: Custom open-source license
- ESP8266 Wardriving tools: MIT/BSD licenses
- WiGLE tools: Various open-source licenses

---

*This integration is part of the WiFi Sensing Workspace and is continuously evolving. Check for updates and new features regularly.*