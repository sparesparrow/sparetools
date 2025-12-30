# {{cookiecutter.project_name}}

{{cookiecutter.project_short_description}}

Generated from SpareTools ESP32 firmware template.

## Features

{% if cookiecutter.include_wifi == 'y' %}
- ✅ WiFi connectivity with web server
{% endif %}
{% if cookiecutter.include_websocket == 'y' %}
- ✅ WebSocket communication for real-time data
{% endif %}
{% if cookiecutter.include_display == 'y' %}
- ✅ OLED display support (SSD1306)
{% endif %}
{% if cookiecutter.schema_component != 'none' %}
- ✅ SpareTools protocol integration ({{cookiecutter.schema_component|upper}})
{% endif %}
- ✅ PlatformIO build system
- ✅ Conan dependency management
- ✅ SpareTools ecosystem integration

## Quick Start

1. **Install dependencies:**
   ```bash
   # Install PlatformIO
   pip install platformio

   # Install Conan
   pip install conan

   # Setup SpareTools remotes
   conan remote add sparetools https://cloudsmith.io/~sparesparrow/repos/sparetools/
   ```

2. **Build the project:**
   ```bash
   # Install dependencies and build
   platformio run
   ```

3. **Upload to ESP32:**
   ```bash
   # Upload firmware
   platformio run --target upload

   # Monitor serial output
   platformio device monitor
   ```

## Project Structure

```
{{cookiecutter.project_slug}}/
├── src/                    # ESP32 firmware source
│   └── main.cpp           # Main application
├── include/               # Header files
├── test/                  # Unit tests
├── scripts/               # Build scripts
│   └── conan_install.py   # Dependency setup
├── .github/workflows/     # CI/CD workflows
├── platformio.ini         # PlatformIO configuration
├── conanfile.txt          # Conan dependencies
└── README.md             # This file
```

## Dependencies

This project uses the SpareTools ecosystem:

- **sparesparrow-protocols/1.0.0**: FlatBuffers protocol schemas
{% if cookiecutter.schema_component != 'none' %}
- **Schema component**: {{cookiecutter.schema_component|upper}} protocol definitions
{% endif %}
- **ESP32 Arduino framework**: Hardware abstraction
{% if cookiecutter.include_display == 'y' %}
- **Adafruit SSD1306**: OLED display driver
{% endif %}
{% if cookiecutter.include_websocket == 'y' %}
- **ESPAsyncWebServer**: WebSocket server
{% endif %}

## Configuration

Edit `platformio.ini` to configure:

- **Board type**: `{{cookiecutter.board_type}}`
- **WiFi settings**: Modify `WIFI_SSID` and `WIFI_PASSWORD` in `main.cpp`
- **Protocol settings**: Configure {{cookiecutter.schema_component|upper}} message parameters

## Development

### Adding New Features

1. **Protocol messages**: Use FlatBuffers builders in SpareTools schemas
2. **Web interface**: Add routes to the web server
3. **Hardware integration**: Add sensors/actuators in `setup()` and `loop()`

### Testing

```bash
# Run unit tests
platformio test

# Run integration tests
platformio test --environment test
```

### Debugging

```bash
# Enable debug build
platformio run --environment debug

# Attach debugger
platformio debug
```

## SpareTools Integration

This project is part of the SpareTools ecosystem. Key benefits:

- **Shared protocols**: Consistent message formats across projects
- **Dependency management**: Automatic package resolution
- **CI/CD ready**: Pre-configured build pipelines
- **Documentation**: Comprehensive guides and examples

## Contributing

1. Follow SpareTools coding standards
2. Update documentation for new features
3. Test on target hardware before submitting
4. Use semantic commit messages

## License

{{cookiecutter.project_name}} is licensed under the MIT License.

## Support

- **Documentation**: [SpareTools ESP32 Guide](https://github.com/sparesparrow/sparetools)
- **Issues**: [GitHub Issues]({{cookiecutter.repository_url}}/issues)
- **Discussions**: [GitHub Discussions]({{cookiecutter.repository_url}}/discussions)

---

*Generated from SpareTools template on {{cookiecutter.__today__}}*




