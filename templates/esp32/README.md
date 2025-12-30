# SpareTools ESP32 Firmware Template

This directory contains the Cookiecutter template for generating ESP32 firmware projects that integrate with the SpareTools ecosystem.

## Features

- **SpareTools Integration**: Pre-configured with `sparesparrow-protocols` and Conan dependency management
- **Multiple Board Support**: ESP32, ESP32-S3, ESP32-C3 configurations
- **Protocol Support**: BPM, MIA, MCP protocol integration options
- **Web Interface**: Optional WiFi, web server, and WebSocket support
- **Display Support**: Optional OLED SSD1306 display integration
- **CI/CD Ready**: Pre-configured GitHub Actions workflows
- **Testing Framework**: Unit test setup with PlatformIO

## Usage

### Prerequisites

```bash
# Install Cookiecutter
pip install cookiecutter

# Install PlatformIO
pip install platformio

# Install Conan
pip install conan
```

### Generate New Project

```bash
# Generate from local template
cookiecutter /path/to/sparetools/templates/esp32

# Or from GitHub (when published)
cookiecutter gh:sparesparrow/sparetools/templates/esp32
```

### Template Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `project_name` | Project name | `esp32-sensor-project` |
| `project_short_description` | Brief description | `ESP32-based sensor project...` |
| `author` | Author name | `SpareSparrow` |
| `email` | Contact email | `contact@sparesparrow.com` |
| `repository_url` | Git repository URL | `https://github.com/sparesparrow/...` |
| `version` | Initial version | `1.0.0` |
| `schema_component` | Protocol schema (bpm/mia/mcp/none) | `bpm` |
| `board_type` | ESP32 board variant | `esp32dev` |
| `include_wifi` | Enable WiFi/web server | `y` |
| `include_display` | Enable OLED display | `y` |
| `include_websocket` | Enable WebSocket server | `y` |

### Non-Interactive Generation

```bash
cookiecutter /path/to/sparetools/templates/esp32 \
  --no-input \
  --config-file my_config.yaml
```

Example `my_config.yaml`:
```yaml
default_context:
  project_name: "esp32-temperature-sensor"
  schema_component: "bpm"
  board_type: "esp32-s3-devkitc-1"
  include_wifi: "y"
  include_display: "n"
  include_websocket: "y"
```

## Generated Project Structure

```
my-esp32-project/
├── .github/
│   └── workflows/
│       └── build.yml          # GitHub Actions CI/CD
├── docs/                      # Documentation
├── include/                   # Header files
├── scripts/
│   └── conan_install.py       # Dependency setup script
├── src/
│   └── main.cpp              # Main firmware application
├── test/
│   └── test_main.cpp         # Unit tests
├── conanfile.txt             # Conan dependencies
├── platformio.ini            # PlatformIO configuration
└── README.md                 # Project documentation
```

## Integration Options

### Protocol Components

Choose the appropriate protocol component for your project:

- **BPM**: Beat detection and audio processing
- **MIA**: Multi-Interface Adapter (vehicle diagnostics, RF)
- **MCP**: Model Context Protocol (AI agent integration)
- **None**: Basic ESP32 project without protocols

### Hardware Features

Enable/disable features based on your hardware requirements:

- **WiFi**: Web server on port 80 for configuration/status
- **WebSocket**: Real-time data streaming on port 81
- **Display**: SSD1306 OLED display support

## Development Workflow

1. **Generate project** using Cookiecutter
2. **Configure hardware** in `platformio.ini`
3. **Implement features** in `src/main.cpp`
4. **Add tests** in `test/` directory
5. **Build and flash** using PlatformIO
6. **Monitor** using `platformio device monitor`

## SpareTools Ecosystem

Generated projects automatically integrate with:

- **sparesparrow-protocols**: Shared FlatBuffers schemas
- **Conan package management**: Automatic dependency resolution
- **CI/CD pipelines**: Pre-configured GitHub Actions
- **Documentation**: Comprehensive project guides

## Examples

### Simple Sensor Project
```bash
cookiecutter /path/to/sparetools/templates/esp32 \
  --no-input \
  project_name=my-sensor \
  schema_component=none \
  include_display=n
```

### BPM Detector
```bash
cookiecutter /path/to/sparetools/templates/esp32 \
  --no-input \
  project_name=bpm-detector \
  schema_component=bpm \
  board_type=esp32-s3-devkitc-1
```

### Vehicle Interface
```bash
cookiecutter /path/to/sparetools/templates/esp32 \
  --no-input \
  project_name=vehicle-interface \
  schema_component=mia \
  include_wifi=y \
  include_websocket=y
```

## Customization

### Adding New Features

1. **Modify cookiecutter.json** to add new variables
2. **Update templates** with conditional logic using Jinja2
3. **Add dependencies** to platformio.ini template
4. **Update documentation** and examples

### Board Support

To add support for new ESP32 boards:

1. Add board configuration to `platformio.ini` template
2. Update `cookiecutter.json` choices
3. Add board-specific build flags if needed

## Contributing

When contributing to the template:

1. Test generation with various configurations
2. Ensure PlatformIO builds succeed
3. Update documentation for new features
4. Follow Cookiecutter best practices

## Troubleshooting

### Common Issues

**Conan remote not configured:**
```bash
conan remote add sparetools https://cloudsmith.io/~sparesparrow/repos/sparetools/
```

**PlatformIO not found:**
```bash
pip install --upgrade platformio
```

**Template variables not applied:**
Ensure cookiecutter.json syntax is valid JSON

## Support

- **Template Issues**: [SpareTools Issues](https://github.com/sparesparrow/sparetools/issues)
- **PlatformIO**: [PlatformIO Documentation](https://docs.platformio.org/)
- **Conan**: [Conan Documentation](https://docs.conan.io/)

---

*SpareTools ESP32 Template v1.0.0*




