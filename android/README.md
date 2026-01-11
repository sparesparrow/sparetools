# Android Tools

This directory contains tools for Android device interaction, payload management, and mobile testing.

## Directory Structure

```
android/
├── payloads/         # Payload files
├── scripts/          # Control scripts
│   ├── android_targeting_suite.py
│   ├── wifi_motion_demo.py
│   └── wifi_sensing_scanner.py
├── config/           # Configuration files
│   ├── demo_listener.rc
│   ├── wifi_meterpreter_listener.rc
│   ├── wifi_shell_listener.rc
│   └── working_listener.rc
├── reports/          # Test reports
│   └── wifi_targeting_report.json
└── README.md
```

## Components

### Targeting Suite
- **Android Targeting**: Comprehensive Android exploitation tools
- **WiFi Motion Demo**: Motion detection using WiFi signals
- **WiFi Sensing Scanner**: Network scanning and analysis

### Payloads
- APK files for Android deployment
- Raw payload binaries
- Configuration files for listeners

### Configuration
- Metasploit listener configurations
- Network settings
- Device profiles

## Usage

### Run Targeting Suite
```bash
python3 scripts/android_targeting_suite.py --scan
```

### WiFi Motion Detection
```bash
python3 scripts/wifi_motion_demo.py --interface wlan0
```

### WiFi Scanning
```bash
python3 scripts/wifi_sensing_scanner.py --band 2.4GHz
```

## Supported Features

- Device discovery and enumeration
- Payload deployment
- Remote shell access
- WiFi-based sensing
- Motion detection
- Network analysis

## Requirements

- Android device with ADB access
- Metasploit Framework
- Python libraries (scapy, numpy)
- WiFi adapter supporting monitor mode

## Target Devices

- Android smartphones and tablets
- IoT devices
- WiFi-enabled embedded systems

## Security Note

These tools are for authorized testing and research purposes only.