# Input Backends

Multi-platform input simulation system with fallback support for the gamepad-mapper ecosystem.

## Overview

Input Backends provides platform-specific implementations for simulating keyboard and mouse input across different Linux desktop environments. It includes multiple backend implementations with automatic fallback and priority-based selection.

## Supported Backends

### X11 Backend
- **Best Compatibility**: Works on most Linux systems with X11
- **Features**: Full keyboard and mouse simulation
- **Requirements**: X11 display server
- **Priority**: High (most widely compatible)

### Wayland Backend
- **Modern Systems**: Optimized for Wayland compositors
- **Features**: Full keyboard and mouse simulation
- **Requirements**: Wayland session
- **Priority**: High (when available)

### KDE Backend
- **KDE Integration**: Specialized for KDE Plasma desktop
- **Features**: Enhanced KDE-specific features
- **Requirements**: KDE desktop environment
- **Priority**: Medium-High

### SDL2 Backend
- **Cross-Platform**: SDL2-based input simulation
- **Features**: Basic keyboard and mouse simulation
- **Requirements**: SDL2 library
- **Priority**: Medium

### UInput Backend
- **Kernel Level**: Direct kernel input device creation
- **Features**: High-performance, low-latency input
- **Requirements**: `/dev/uinput` access (usually requires root/sudo)
- **Priority**: Fallback (best performance when available)

## Features

- **Automatic Detection**: Detects available backends at runtime
- **Priority Selection**: Chooses best backend based on system capabilities
- **Fallback Support**: Gracefully falls back to available alternatives
- **Unified API**: Single interface for all backend implementations
- **Thread Safe**: Designed for concurrent access
- **Performance Optimized**: Minimal latency input simulation

## Dependencies

- **System Libraries**: X11, Wayland, SDL2 (depending on enabled backends)
- **C++17**: Modern C++ standard required
- **CMake**: Build system
- **PkgConfig**: System library detection

## Building

### Using Conan

```bash
# Install dependencies (adjust options as needed)
conan install . --build missing \
    -o with_x11=True \
    -o with_wayland=True \
    -o with_kde=True \
    -o with_sdl2=True \
    -o with_uinput=True

# Build with CMake
cmake --preset conan-release
cmake --build build --config Release

# Install
cmake --install build
```

### Manual Build

```bash
# Install system dependencies
sudo apt-get install libx11-dev libxtst-dev libwayland-dev libsdl2-dev

# Build
mkdir build && cd build
cmake .. -DWITH_X11=ON -DWITH_WAYLAND=ON -DWITH_SDL2=ON
make -j$(nproc)
sudo make install
```

## Usage

### Basic Usage

```cpp
#include <input_backend_manager.h>

// Create backend manager
input_backends::InputBackendManager manager;
manager.initialize();

// Create best available simulator
auto simulator = manager.create_best_simulator();
if (simulator) {
    // Simulate input
    simulator->simulate_key_press(KEY_SPACE);
    simulator->simulate_mouse_click(MouseButton::LEFT);
}
```

### Advanced Usage

```cpp
// Check available backends
auto available = manager.get_available_backends();
for (const auto& backend : available) {
    auto caps = manager.get_backend_capabilities(backend);
    std::cout << "Backend: " << backend
              << ", Performance: " << caps.performance_rating
              << ", Compatibility: " << caps.compatibility_rating << std::endl;
}

// Use specific backend
auto x11_simulator = manager.create_simulator("x11");
if (x11_simulator) {
    // Use X11-specific features
}

// Set preferred backend
manager.set_preferred_backend("wayland");
auto preferred = manager.create_best_simulator();
```

### Direct Backend Creation

```cpp
#include <input_backend_manager.h>

// Create specific backends directly
auto x11 = input_backends::create_x11_simulator();
auto wayland = input_backends::create_wayland_simulator();
auto uinput = input_backends::create_uinput_simulator();
```

## Configuration

### CMake Options

```cmake
# Enable/disable specific backends
option(WITH_X11 "Enable X11 backend" ON)
option(WITH_WAYLAND "Enable Wayland backend" ON)
option(WITH_KDE "Enable KDE backend" ON)
option(WITH_SDL2 "Enable SDL2 backend" ON)
option(WITH_UINPUT "Enable UInput backend" ON)
```

### Runtime Configuration

```cpp
InputBackendManager manager;

// Set preferred backend
manager.set_preferred_backend("x11");

// Check what's available
auto available = manager.get_available_backends();
```

## API Reference

### InputSimulator Interface

All backends implement this common interface:

```cpp
class InputSimulator {
public:
    virtual bool simulate_key_press(int key_code) = 0;
    virtual bool simulate_mouse_move(int x, int y) = 0;
    virtual bool simulate_mouse_click(MouseButton button) = 0;
    virtual std::string get_backend_name() const = 0;
    // ... more methods
};
```

### BackendCapabilities

```cpp
struct BackendCapabilities {
    std::string name;
    bool available;
    bool supports_keyboard;
    bool supports_mouse;
    bool requires_root;
    int performance_rating;    // 1-10 scale
    int compatibility_rating;  // 1-10 scale
};
```

## Testing

```bash
# Build with tests
cmake -DBUILD_TESTS=ON ..
make

# Run tests
ctest --output-on-failure

# Run specific backend tests
./tests/x11_backend_test
./tests/wayland_backend_test
```

## Performance Considerations

### Backend Performance Comparison

| Backend | Performance | Latency | Compatibility | Requirements |
|---------|-------------|---------|----------------|--------------|
| UInput  | Excellent   | Lowest  | Good          | Root access  |
| X11     | Very Good   | Low     | Excellent     | X11 display  |
| Wayland | Good        | Medium  | Limited       | Wayland session |
| KDE     | Very Good   | Low     | Limited       | KDE desktop  |
| SDL2    | Good        | Medium  | Good          | SDL2 library |

### Optimization Tips

1. **Use UInput for Gaming**: Best performance for gaming applications
2. **X11 for Compatibility**: Most compatible across different systems
3. **Wayland for Modern**: Best for modern Wayland-only systems
4. **Automatic Selection**: Let the manager choose the best backend

## Troubleshooting

### Common Issues

1. **No backends available**
   ```bash
   # Check system libraries
   ldconfig -p | grep X11
   ldconfig -p | grep wayland

   # Check display server
   echo $DISPLAY
   echo $WAYLAND_DISPLAY
   ```

2. **UInput permission denied**
   ```bash
   # Check uinput device permissions
   ls -la /dev/uinput

   # Add user to input group or use sudo
   sudo usermod -a -G input $USER
   ```

3. **Wayland not detected**
   ```bash
   # Check if running under Wayland
   echo $XDG_SESSION_TYPE
   loginctl show-session $(loginctl | grep $(whoami) | awk '{print $1}') -p Type
   ```

### Debug Information

```cpp
// Get detailed backend information
auto manager = InputBackendManager();
manager.initialize();

auto available = manager.get_available_backends();
for (const auto& backend : available) {
    auto caps = manager.get_backend_capabilities(backend);
    std::cout << "Backend: " << caps.name << std::endl;
    std::cout << "  Available: " << (caps.available ? "Yes" : "No") << std::endl;
    std::cout << "  Performance: " << caps.performance_rating << "/10" << std::endl;
    std::cout << "  Compatibility: " << caps.compatibility_rating << "/10" << std::endl;
}
```

## Integration

Input Backends integrates with other gamepad-mapper components:

- **gamepad-core**: Provides input simulation for mappings
- **gamepad-mcp-server**: Exposes backend control through MCP
- **Main Orchestrator**: Coordinates backend selection and usage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add new backend implementations following the InputSimulator interface
4. Add comprehensive tests
5. Update documentation
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Related Projects

- [gamepad-core](https://github.com/sparesparrow/gamepad-core) - Core mapping logic
- [gamepad-mapper](https://github.com/sparesparrow/gamepad-mapper) - Main orchestrator
- [gamepad-mcp-server](https://github.com/sparesparrow/gamepad-mcp-server) - MCP integration