# SpareTools ESP32 BPM Prompts

Aggregated ESP32 BPM detector development prompts from `mcp-prompts` GitHub repository, combined with SpareTools ecosystem capabilities.

## Overview

This Conan package aggregates ESP32-specific prompts from the `@sparesparrow/mcp-prompts` npm package (published to GitHub Packages) and makes them available to ESP32 BPM detector projects via Conan.

## Installation

```bash
# Via Conan
conan install sparetools-esp32-bpm-prompts/1.0.0@sparesparrow/stable

# Via Cloudsmith
conan install sparetools-esp32-bpm-prompts/1.0.0@sparesparrow/stable -r sparetools
```

## Included Prompts

### ESP32 Development (7 prompts)
- `esp32-network-ap-mode-configuration` - WiFi AP mode setup
- `esp32-platformio-serial-upload-debugging` - Build/upload troubleshooting
- `esp32-flatbuffers-schema-sync-workflow` - Schema regeneration
- `esp32-mcp-server-http-api-integration` - HTTP API setup
- `embedded-esp32-full-bringup-workflow` - Complete setup workflow
- `esp32-fft-configuration-guide` - FFT optimization guide
- `esp32-fft-optimization-methodology` - Advanced FFT tuning

### Embedded Systems (5 prompts)
- `embedded-audio-fft-memory-constraints` - Memory optimization
- `embedded-device-detection` - Device identification
- `embedded-firmware-deployment` - Firmware deployment
- `embedded-jtag-workflow` - JTAG debugging
- `embedded-serial-debugging` - Serial communication

### MCP Development (1 prompt)
- `mcp-server-file-storage-index-sync` - Index synchronization

## Usage in esp32-bpm-detector

The package is automatically included when using `sparetools-bpm-detector`:

```python
# conanfile.py
requires = [
    "sparetools-esp32-bpm-prompts/1.0.0",
    # ... other dependencies
]
```

### Accessing Prompts

Prompts are available via environment variables:

```bash
# Prompt directory
echo $SPARETOOLS_ESP32_BPM_PROMPTS_DIR

# Index file
echo $SPARETOOLS_ESP32_BPM_PROMPTS_INDEX

# MCP prompts path (for MCP servers)
echo $MCP_PROMPTS_PATH
```

### Using with MCP Servers

```json
{
  "mcpServers": {
    "mcp-prompts": {
      "command": "mcp-prompts",
      "args": ["start", "--mode", "mcp"],
      "env": {
        "PROMPTS_DIR": "${SPARETOOLS_ESP32_BPM_PROMPTS_DIR}",
        "STORAGE_TYPE": "file"
      }
    }
  }
}
```

## Source

Prompts are sourced from:
- **Repository**: https://github.com/sparesparrow/mcp-prompts
- **Version**: v3.12.5
- **Package**: @sparesparrow/mcp-prompts@3.12.5 (GitHub Packages)

## Integration with SpareTools

This package combines:
1. **mcp-prompts prompts** - From GitHub repository
2. **SpareTools MCP servers** - ESP32 serial monitor, Conan, etc.
3. **SpareTools workflows** - Complete development workflows

## Related Packages

- `sparetools-mcp-prompts` - Full MCP prompts server
- `sparetools-mcp-servers` - MCP server implementations
- `sparetools-bpm-detector` - ESP32 BPM detector firmware
- `sparetools-mcp-core` - Core MCP utilities

## Versioning

Package version follows semantic versioning:
- **Major**: Breaking changes to prompt structure
- **Minor**: New prompts added
- **Patch**: Bug fixes or prompt updates

Source mcp-prompts version is tracked in package metadata.