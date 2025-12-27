# Gamepad Mapper - Mapping Configuration Guide

This guide provides comprehensive documentation for all available gamepad mapping configurations in the Gamepad Mapper project.

## Table of Contents

- [Overview](#overview)
- [Configuration Structure](#configuration-structure)
- [Available Mappings](#available-mappings)
- [Installation and Usage](#installation-and-usage)
- [Service Installation](#service-installation)
- [Customization](#customization)

## Overview

The Gamepad Mapper supports various mapping configurations optimized for different applications and use cases. Each configuration file contains button mappings, analog stick controls, sensitivity settings, and application-specific shortcuts.

## Configuration Structure

All mapping files follow this JSON structure:

```json
{
  "description": "Description of the mapping configuration",
  "mappings": {
    "BUTTON_NAME": "KEYBOARD_KEY_OR_ACTION"
  },
  "analog_mappings": {
    "AXIS_NAME": "MOUSE_OR_KEY_ACTION"
  },
  "special_mappings": {
    "COMBINATION": "ACTION"
  },
  "sensitivity": {
    "mouse_speed": 3.0,
    "scroll_speed": 1.0,
    "analog_threshold": 0.1
  },
  "application_specific": {
    "shortcut_name": "KEY_COMBINATION"
  }
}
```

### Button Names

- `A`, `B`, `X`, `Y`: Face buttons
- `LB`, `RB`: Left/Right bumpers
- `LT`, `RT`: Left/Right triggers (digital)
- `SELECT`, `START`: Menu buttons
- `LS`, `RS`: Left/Right stick clicks
- `DPAD_UP/DOWN/LEFT/RIGHT`: D-pad directions
- `LEFT_TRIGGER`, `RIGHT_TRIGGER`: Analog triggers

### Analog Axes

- `LEFT_X`, `LEFT_Y`: Left analog stick
- `RIGHT_X`, `RIGHT_Y`: Right analog stick

### Output Actions

- **Keyboard**: `KEY_NAME` (e.g., `KEY_ENTER`, `KEY_SPACE`)
- **Modifiers**: `KEY_MOD+KEY_NAME` (e.g., `KEY_LEFTCTRL+KEY_C`)
- **Mouse**: `MOUSE_LEFT_CLICK`, `MOUSE_RIGHT_CLICK`, `MOUSE_MOVE_X`, `MOUSE_MOVE_Y`

## Available Mappings

### 1. Default Mappings (`config/default_mappings.json`)

**Use Case**: General-purpose computing, web browsing, document editing
**Description**: Basic mappings suitable for most desktop computing tasks

**Key Mappings**:
- `A`: Enter (confirm/activate)
- `B`: Escape (cancel/close)
- `X`: Space (pause/play, select)
- `Y`: Tab (switch focus)
- Left stick: Mouse movement
- Right stick: Arrow key navigation
- Triggers: Mouse clicks

**Best For**:
- General desktop use
- Web browsing
- Office applications
- Basic navigation

---

### 2. Browser Mappings (`config/browser_mappings.json`)

**Use Case**: Web browsers (Chrome, Firefox, Edge)
**Description**: Optimized for web browsing with tab management and page navigation

**Key Mappings**:
- `A`: Enter
- `B`: Escape
- `X`: Tab (cycle through links)
- `Y`: Ctrl+T (new tab)
- `LB/RB`: Alt+Left/Right (back/forward)
- `SELECT`: Ctrl+W (close tab)
- `START`: F12 (developer tools)
- Left stick: Mouse movement
- Right stick: Arrow keys
- Triggers: Mouse clicks

**Special Features**:
- Tab management shortcuts
- History navigation
- Developer tools access

**Best For**:
- Intensive web browsing
- Tab-heavy workflows
- Web development

---

### 3. Cursor IDE Mappings (`config/cursor_mappings.json`)

**Use Case**: Cursor IDE and similar code editors
**Description**: Tailored for programming and development workflows

**Key Mappings**:
- `A`: Enter
- `B`: Escape
- `X`: Ctrl+Space (autocomplete)
- `Y`: Ctrl+P (command palette)
- `LB/RB`: Alt+Left/Right (navigate)
- `SELECT`: Ctrl+W (close tab)
- `START`: Ctrl+B (split editor)
- Left stick: Mouse movement
- Right stick: Arrow keys

**Special Features**:
- Code completion
- File navigation
- Editor management
- Git operations

**Best For**:
- Programming
- Code editing
- Development workflows

---

### 4. Media Player Mappings (`config/media_player_mappings.json`)

**Use Case**: Media players (VLC, YouTube, Netflix, local video/audio)
**Description**: Full media control with playback, volume, and playlist management

**Key Mappings**:
- `A`: Space (play/pause)
- `B`: Escape
- `X`: F (fullscreen)
- `Y`: M (mute)
- `LB/RB`: Left/Right (seek)
- `LT/RT`: Down/Up (volume)
- `SELECT`: Ctrl+S (save playlist)
- `START`: F11 (fullscreen toggle)
- Left stick: Mouse movement
- Triggers: Mouse clicks

**Special Features**:
- Playback controls
- Volume management
- Fullscreen toggle
- Playlist navigation
- Subtitle/audio track switching

**Best For**:
- Video playback
- Music listening
- Media center control
- Streaming services

---

### 5. Presentation Mappings (`config/presentation_mappings.json`)

**Use Case**: Presentation software (LibreOffice Impress, PowerPoint)
**Description**: Slide navigation and presentation control

**Key Mappings**:
- `A`: Right arrow (next slide)
- `B`: Left arrow (previous slide)
- `X`: F5 (start presentation)
- `Y`: Escape
- `LB/RB`: Page Up/Down
- `SELECT`: Ctrl+S (save)
- `START`: F11 (fullscreen)
- Left stick: Mouse movement (laser pointer)
- Triggers: Mouse clicks

**Special Features**:
- Slide navigation
- Presentation control
- Zoom and fit controls
- Overview mode
- Notes view

**Best For**:
- Presentations
- Slide shows
- Public speaking
- Teaching

---

### 6. Terminal Mappings (`config/terminal_mappings.json`)

**Use Case**: Command line interfaces and terminal applications
**Description**: Efficient terminal navigation and command management

**Key Mappings**:
- `A`: Enter (execute)
- `B`: Ctrl+C (interrupt)
- `X`: Tab (autocomplete)
- `Y`: Ctrl+L (clear screen)
- `LB/RB`: Left/Right
- `LT/RT`: Ctrl+R/Ctrl+Z (history/undo)
- `SELECT`: Ctrl+D (exit)
- `START`: Ctrl+T (new tab)
- Left stick: Mouse movement
- Triggers: Mouse clicks

**Special Features**:
- Command execution
- History navigation
- Tab management
- Text selection and editing
- Process control

**Best For**:
- Command line work
- System administration
- Development workflows
- Server management

---

### 7. Video Editing Mappings (`config/video_editing_mappings.json`)

**Use Case**: Video editing software (DaVinci Resolve, Kdenlive, HitFilm)
**Description**: Professional video editing controls and timeline navigation

**Key Mappings**:
- `A`: Space (play/pause)
- `B`: Ctrl+Z (undo)
- `X`: Ctrl+X (cut)
- `Y`: Ctrl+C (copy)
- `LB/RB`: Left/Right (frame navigation)
- `LT/RT`: Comma/Period (second navigation)
- `SELECT`: Ctrl+S (save)
- `START`: Ctrl+R (render)
- Left stick: Mouse movement
- Right stick: Precise cursor control

**Special Features**:
- Timeline navigation
- Editing operations
- Playback control
- Render management
- Tool switching

**Best For**:
- Video editing
- Post-production
- Content creation
- Film production

---

### 8. Music Production Mappings (`config/music_production_mappings.json`)

**Use Case**: Music production software (Ardour, LMMS, Audacity)
**Description**: DAW controls and music production workflow

**Key Mappings**:
- `A`: Space (play/pause)
- `B`: Ctrl+Z (undo)
- `X`: Ctrl+X (cut)
- `Y`: Ctrl+C (copy)
- `LB/RB`: Left/Right
- `LT/RT`: Down/Up
- `SELECT`: Ctrl+S (save)
- `START`: Ctrl+R (export)
- Left stick: Mouse movement
- Triggers: Mouse clicks

**Special Features**:
- Transport controls
- Recording functions
- Editing operations
- Effect management
- Track controls

**Best For**:
- Music production
- Audio editing
- Sound design
- Podcasting

---

### 9. 3D Modeling Mappings (`config/3d_modeling_mappings.json`)

**Use Case**: 3D modeling and CAD software (Blender, FreeCAD, Fusion 360)
**Description**: 3D navigation and modeling controls

**Key Mappings**:
- `A`: Ctrl+Left Click (select)
- `B`: Escape
- `X`: Ctrl+X (cut)
- `Y`: Ctrl+C (copy)
- `LB/RB`: Left/Right
- `LT/RT`: Down/Up
- `SELECT`: Ctrl+S (save)
- `START`: Ctrl+P (render)
- Left stick: 3D view rotation
- Right stick: Zoom/pan

**Special Features**:
- 3D navigation
- Object manipulation
- Viewport controls
- Modeling tools
- Render controls

**Best For**:
- 3D modeling
- CAD design
- Animation
- Game development

---

### 10. Photo Editing Mappings (`config/photo_editing_mappings.json`)

**Use Case**: Photo editing software (GIMP, Krita, Photoshop)
**Description**: Image editing and manipulation controls

**Key Mappings**:
- `A`: Ctrl+Left Click (select)
- `B`: Escape
- `X`: Ctrl+X (cut)
- `Y`: Ctrl+C (copy)
- `LB/RB`: [ ] (brush size)
- `LT/RT`: Down/Up
- `SELECT`: Ctrl+S (save)
- `START`: Ctrl+P (print)
- Left stick: Precise cursor control
- Right stick: Brush control

**Special Features**:
- Tool selection
- Brush controls
- Selection tools
- Layer management
- Color picking

**Best For**:
- Photo editing
- Digital art
- Graphic design
- Image manipulation

---

### 11. File Manager Mappings (`config/file_manager_mappings.json`)

**Use Case**: File managers (Dolphin, Nautilus, Thunar)
**Description**: File system navigation and management

**Key Mappings**:
- `A`: Enter (open)
- `B`: Backspace (go back)
- `X`: Ctrl+C (copy)
- `Y`: Ctrl+X (cut)
- `LB/RB`: Left/Right
- `LT/RT`: Down/Up
- `SELECT`: Ctrl+A (select all)
- `START`: F2 (rename)
- Left stick: Mouse movement
- Triggers: Mouse clicks

**Special Features**:
- File operations
- Navigation
- Selection management
- View options
- Search functions

**Best For**:
- File management
- System navigation
- File organization
- Archive management

---

### 12. Remote Desktop Mappings (`config/remote_desktop_mappings.json`)

**Use Case**: Remote desktop connections (VNC, RDP, TeamViewer)
**Description**: Remote system control and navigation

**Key Mappings**:
- `A`: Left click
- `B`: Right click
- `X`: Ctrl+C (copy)
- `Y`: Ctrl+V (paste)
- `LB/RB`: Left/Right
- `LT/RT`: Down/Up
- `SELECT`: Ctrl+Alt+Del
- `START`: F11 (fullscreen)
- Left stick: Mouse movement
- Triggers: Mouse clicks

**Special Features**:
- Remote control
- Clipboard operations
- Session management
- View controls

**Best For**:
- Remote administration
- Technical support
- Cloud computing
- Multi-system management

---

### 13. Gaming Mappings (`config/gaming_mappings.json`)

**Use Case**: Multiple controller gaming and streaming
**Description**: Advanced multi-controller setup for gaming and content creation

**Features**:
- Multiple controller profiles
- Player-specific mappings
- Streaming controls
- Voice alerts
- Tournament mode

**Best For**:
- Local multiplayer gaming
- Game streaming
- Esports
- Gaming content creation

---

### 14. Professional Mappings (`config/professional_mappings.json`)

**Use Case**: Professional multi-device control and remote management
**Description**: Advanced setup for professional use with remote device control

**Features**:
- Remote computer control
- Multi-protocol support
- Network device management
- Advanced automation

**Best For**:
- Professional workflows
- Remote administration
- Multi-device management
- Automation tasks

---

### 15. Accessibility Mappings (`config/accessibility_mappings.json`)

**Use Case**: Accessibility and assistive technology
**Description**: Enhanced controls for users with motor impairments

**Features**:
- Sticky keys
- Key repetition control
- Alternative input methods
- Adaptive controls

**Best For**:
- Accessibility support
- Assistive technology
- Motor impairment accommodation
- Adaptive computing

---

### 16. Bluetooth Mappings (`config/bluetooth_mappings.json`)

**Use Case**: Bluetooth HID device configuration
**Description**: Wireless controller setup and management

**Features**:
- Bluetooth device scanning
- Auto-pairing
- Device-specific profiles
- Connection management

**Best For**:
- Wireless gaming
- Mobile device control
- Bluetooth peripherals

## Installation and Usage

### Basic Usage

```bash
# Start with default mappings
./gamepad_mapper_app

# Use specific configuration
./gamepad_mapper_app -c config/browser_mappings.json

# Start as MCP server
./gamepad_mapper_app -m
```

### Service Installation

For automatic startup, install as a systemd service:

```bash
# Build the project
./scripts/build-dev.sh

# Install as service (requires root)
sudo ./scripts/install-service.sh

# Check service status
systemctl status gamepad-mapper.service

# View logs
journalctl -u gamepad-mapper.service -f
```

## Service Installation Details

The service installation script performs the following:

1. **Binary Installation**: Installs executables to `/usr/local/bin/`
2. **Configuration Setup**: Creates `/etc/gamepad-mapper/` with all config files
3. **User Creation**: Creates dedicated `gamepad-mapper` user
4. **Permissions**: Sets proper file ownership and permissions
5. **Udev Rules**: Installs input device access rules
6. **Systemd Service**: Creates and enables the service
7. **Logging**: Sets up `/var/log/gamepad-mapper/` for logs

### Service Management

```bash
# Start/stop service
sudo systemctl start gamepad-mapper.service
sudo systemctl stop gamepad-mapper.service

# Enable/disable auto-start
sudo systemctl enable gamepad-mapper.service
sudo systemctl disable gamepad-mapper.service

# Restart service
sudo systemctl restart gamepad-mapper.service

# View status and logs
sudo systemctl status gamepad-mapper.service
sudo journalctl -u gamepad-mapper.service -f
```

## Customization

### Creating Custom Mappings

1. Copy an existing mapping file as a template
2. Modify the button mappings according to your needs
3. Adjust sensitivity settings for your preferences
4. Test the configuration
5. Save and deploy

### Advanced Configuration

For complex setups with multiple controllers or remote devices, use the gaming or professional mapping templates as starting points.

### Performance Tuning

Adjust sensitivity values based on your controller and use case:

- **mouse_speed**: Higher values for faster mouse movement (2.0-5.0)
- **analog_threshold**: Deadzone for analog sticks (0.05-0.2)
- **scroll_speed**: Mouse wheel sensitivity (0.5-2.0)

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure user is in `input` group or install udev rules
2. **No Controllers Detected**: Check Bluetooth connections or USB device permissions
3. **Service Won't Start**: Check logs with `journalctl -u gamepad-mapper.service`
4. **Configuration Errors**: Validate JSON syntax and file paths

### Debug Mode

Enable verbose logging by modifying the source code or running manually:

```bash
./gamepad_mapper_app -c config/debug_mappings.json
```

## Contributing

To add new mapping configurations:

1. Create a new JSON file in the `config/` directory
2. Follow the established naming convention: `{purpose}_mappings.json`
3. Document the use case and key features
4. Test thoroughly with target applications
5. Submit a pull request

## License

All mapping configurations are provided under the same license as the main project.