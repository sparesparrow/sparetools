# Gamepad/Input Tools

This directory contains tools for gamepad input handling, mapping, and device management.

## Directory Structure

```
gamepad/
├── scripts/          # Control scripts
│   ├── gamepad_mapper.py
│   ├── simple_gamepad_mapper.py
│   └── gamepad_monitor.sh
├── services/         # System services
│   └── gamepad-monitor.service
├── config/           # Configuration files
│   └── dualsense_mappings.json
└── README.md
```

## Components

### Mapping Tools
- **Gamepad Mapper**: Advanced input mapping and translation
- **Simple Mapper**: Basic input mapping for common devices

### Monitoring
- **Monitor Script**: Real-time input monitoring and logging
- **System Service**: Background monitoring service

### Device Support

- Sony DualSense (PS5 controller)
- Xbox controllers
- Generic HID gamepads
- Custom input devices

## Usage

### Map Gamepad Inputs
```bash
python3 scripts/gamepad_mapper.py --device /dev/input/js0
```

### Monitor Inputs
```bash
./scripts/gamepad_monitor.sh
```

### Start Service
```bash
sudo systemctl start gamepad-monitor.service
```

## Configuration

Device mappings are stored in JSON format:

```json
{
  "buttons": {
    "A": 0,
    "B": 1,
    "X": 2,
    "Y": 3
  },
  "axes": {
    "left_stick_x": 0,
    "left_stick_y": 1,
    "right_stick_x": 2,
    "right_stick_y": 3
  }
}
```

## Features

- Real-time input translation
- Device hotplugging support
- Custom mapping profiles
- Event logging and debugging
- Systemd service integration

## Dependencies

- Python evdev library
- Linux input subsystem
- systemd (for services)