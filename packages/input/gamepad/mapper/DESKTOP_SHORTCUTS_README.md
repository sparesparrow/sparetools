# 🎮 Gamepad Desktop Shortcuts & Keyboard Simulation

Transform your gamepad into a powerful desktop control device with comprehensive keyboard shortcut mapping and mouse simulation.

## ✨ Features

### 🎯 **Comprehensive Shortcut Mapping**
- **Window Management**: Alt+Tab, Alt+F4, window switching
- **Text Editing**: Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+S, and more
- **Browser Control**: Tab switching, navigation, search
- **System Shortcuts**: Meta key combinations, function keys
- **Multi-Modifier Support**: Complex combinations like Ctrl+Alt+Shift+Key

### 🖱️ **Mouse Simulation**
- **Analog Stick Control**: Precise mouse movement
- **Trigger Clicks**: Left/right mouse buttons
- **Scroll Wheel**: Right analog stick for scrolling
- **Configurable Sensitivity**: Adjustable mouse speed and precision

### 🎮 **Gamepad Support**
- **Multiple Controllers**: Support for up to 4 controllers simultaneously
- **Hotplug Detection**: Automatic controller detection and configuration
- **Per-Controller Profiles**: Different mappings for different controllers
- **Bluetooth Support**: Wireless controller connectivity

### 🖥️ **Desktop Environment Support**
- **KDE Plasma**: Optimized for KDE desktop effects and KRunner
- **GNOME**: Activities overview and workspace switching
- **XFCE**: Panel control and window management
- **Generic X11/Wayland**: Cross-desktop compatibility

## 🚀 Quick Start

### 1. Build the Project
```bash
cd repos/gamepad-mapper
./build_desktop_shortcuts.sh
```

### 2. Connect Your Gamepad
- USB gamepad: Plug in and it will be detected automatically
- Bluetooth gamepad: Pair through system settings first
- Multiple gamepads: All will be detected and configured

### 3. Run the Desktop Shortcuts
```bash
cd build-desktop-shortcuts
./test_desktop_shortcuts
```

## 📋 Control Reference

### Basic Controls
| Gamepad Input | Desktop Action | Description |
|---------------|----------------|-------------|
| **A Button** | Enter | Confirm, execute |
| **B Button** | Escape | Cancel, close dialogs |
| **X Button** | Space | Space bar |
| **Y Button** | Tab | Tab navigation |
| **D-Pad** | Arrow Keys | Navigation |
| **Left Trigger** | Left Mouse Click | Click, select |
| **Right Trigger** | Right Mouse Click | Context menu |
| **Left Stick** | Mouse Movement | Cursor control |
| **Right Stick** | Mouse Scroll | Scroll wheel |

### Modifier Combinations
| Gamepad Input | Desktop Action | Description |
|---------------|----------------|-------------|
| **LB + A** | Alt+Tab | Window switcher |
| **LB + B** | Alt+F4 | Close window |
| **RB + A** | Ctrl+Alt+Tab | Task switcher |
| **RB + B** | Ctrl+Alt+Delete | System menu |
| **LT + A** | Alt+Shift+Tab | Reverse window switcher |
| **RT + A** | Meta+Enter | Open terminal |
| **RT + B** | Meta+Escape | Activities overview |

### Text Editing Shortcuts
| Gamepad Input | Desktop Action | Description |
|---------------|----------------|-------------|
| **SELECT + A** | Ctrl+A | Select all |
| **SELECT + C** | Ctrl+C | Copy |
| **SELECT + V** | Ctrl+V | Paste |
| **SELECT + X** | Ctrl+X | Cut |
| **SELECT + S** | Ctrl+S | Save |
| **SELECT + Z** | Ctrl+Z | Undo |
| **SELECT + Y** | Ctrl+Y | Redo |
| **SELECT + F** | Ctrl+F | Find |
| **SELECT + H** | Ctrl+H | Find & replace |
| **SELECT + N** | Ctrl+N | New |
| **SELECT + O** | Ctrl+O | Open |
| **SELECT + P** | Ctrl+P | Print |
| **SELECT + W** | Ctrl+W | Close tab/window |
| **SELECT + T** | Ctrl+T | New tab |
| **SELECT + Q** | Ctrl+Q | Quit |

### Browser Shortcuts
| Gamepad Input | Desktop Action | Description |
|---------------|----------------|-------------|
| **START + A** | Ctrl+T | New tab |
| **START + B** | Ctrl+W | Close tab |
| **START + X** | Ctrl+Tab | Next tab |
| **START + Y** | Ctrl+Shift+Tab | Previous tab |
| **START + ←** | Alt+← | Back |
| **START + →** | Alt+→ | Forward |

### Function Keys
| Gamepad Input | Desktop Action | Description |
|---------------|----------------|-------------|
| **RS + A** | F1 | Help |
| **RS + B** | F2 | Rename |
| **RS + X** | F3 | Search |
| **RS + Y** | F4 | Close |
| **RS + ↑** | F5 | Refresh |
| **RS + ↓** | F6 | Next panel |
| **RS + ←** | F7 | Previous panel |
| **RS + →** | F8 | Next window |

## ⚙️ Configuration

### Configuration Files
- `config/desktop_shortcuts_mappings.json` - Main desktop shortcuts
- `config/terminal_mappings.json` - Terminal-specific shortcuts
- `config/browser_mappings.json` - Browser shortcuts
- `config/professional_mappings.json` - Advanced multi-controller setup

### Customizing Mappings
Edit the JSON configuration files to customize your shortcuts:

```json
{
  "mappings": {
    "A": "KEY_ENTER",
    "B": "KEY_ESC",
    "X": "KEY_SPACE",
    "Y": "KEY_TAB"
  },
  "keyboard_shortcuts": {
    "window_management": {
      "LB+A": "KEY_LEFTALT+KEY_TAB",
      "LB+B": "KEY_LEFTALT+KEY_F4"
    }
  }
}
```

### Sensitivity Settings
```json
{
  "sensitivity": {
    "mouse_speed": 3.0,
    "scroll_speed": 1.0,
    "analog_threshold": 0.15,
    "key_repeat_delay": 50,
    "key_repeat_rate": 30
  }
}
```

## 🔧 Advanced Features

### Multi-Controller Setup
Support for multiple controllers with different profiles:

```json
{
  "controllers": {
    "primary_controller": {
      "device_id": "auto_detect",
      "name": "Primary Controller",
      "mappings": { ... }
    },
    "secondary_controller": {
      "device_id": "auto_detect", 
      "name": "Secondary Controller",
      "mappings": { ... }
    }
  }
}
```

### Voice Feedback
Optional voice announcements for controller events:

```json
{
  "voice_feedback": {
    "enabled": true,
    "announce_shortcuts": false,
    "announce_mode_changes": true,
    "announce_errors": true
  }
}
```

### Bluetooth Support
Automatic detection and pairing of Bluetooth controllers:

```json
{
  "bluetooth": {
    "enabled": true,
    "auto_connect": true,
    "scan_timeout": 10
  }
}
```

## 🛠️ Troubleshooting

### Controller Not Detected
1. Check USB connection or Bluetooth pairing
2. Verify controller is recognized by system: `ls /dev/input/`
3. Check permissions: `sudo usermod -a -G input $USER`

### Shortcuts Not Working
1. Verify configuration file syntax
2. Check if target application supports the shortcuts
3. Ensure no conflicting key bindings

### Mouse Movement Issues
1. Adjust sensitivity in configuration
2. Check analog stick calibration
3. Verify X11/Wayland compatibility

### Build Issues
1. Install required dependencies:
   ```bash
   sudo apt install libx11-dev libxtst-dev libxrandr-dev
   sudo apt install libwayland-dev libsdl2-dev
   sudo apt install libbluetooth-dev libasound2-dev
   ```
2. Check CMake configuration
3. Verify compiler support for C++17

## 📚 API Reference

### Core Classes
- `GamepadMapper` - Main controller class
- `KeyboardShortcutHandler` - Shortcut processing
- `EnhancedInputSimulator` - Input simulation with shortcuts
- `KeyCombination` - Shortcut definition structure

### Key Methods
```cpp
// Initialize the mapper
bool initialize();

// Load configuration
bool load_mappings(const std::string& config_file);

// Start/stop processing
void start();
void stop();

// Execute shortcuts
bool send_key_combination(const std::string& combination);

// Controller management
std::vector<ControllerInfo> get_connected_controllers();
void scan_for_controllers();
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Linux input subsystem
- X11/Wayland display servers
- SDL2 for cross-platform support
- Bluetooth HID specification
- KDE Connect integration

---

**Happy Gaming and Desktop Control! 🎮🖥️**
