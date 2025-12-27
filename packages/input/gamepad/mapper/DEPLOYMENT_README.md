# Gamepad Mapper - Conan Packaging & Deployment

This document describes the complete Conan packaging and deployment pipeline for the Gamepad Mapper project.

## Overview

The Gamepad Mapper uses Conan for package management and supports multiple deployment scenarios:
- Local development builds
- Remote repository deployment
- SSH-based deployment to target machines
- MCP server integration with AI assistants

## Prerequisites

- Conan 2.x (`pip install conan`)
- CMake 3.20+
- C++17 compatible compiler
- Python 3.x (for MCP server)
- SSH access to target machines (for remote deployment)

## Project Structure

```
gamepad-mapper/
├── conanfile.py              # Conan package recipe
├── CMakeLists.txt            # Build configuration
├── scripts/                  # Deployment scripts
│   ├── build-dev.sh         # Development build
│   ├── build-test.sh        # Build with tests
│   ├── create-package.sh    # Package creation
│   ├── install-local.sh     # Local installation
│   ├── deploy-local.sh      # Local deployment
│   ├── deploy-remote.sh     # Remote deployment
│   ├── deploy-ssh.sh        # SSH deployment
│   ├── deploy-studio.sh     # Studio.local deployment
│   ├── deploy-full.sh       # Complete deployment
│   ├── update-package.sh    # Package updates
│   ├── install-mcp.sh       # MCP server installation
│   └── *.service            # Systemd service files
├── tools/
│   └── gamepad_mcp_server.py # MCP server implementation
├── tests/                   # Unit tests
├── config/                  # Configuration files
└── mcp-config.json         # MCP configuration
```

## Quick Start

### 1. Local Development Build

```bash
# Configure Conan
conan profile detect --force

# Build and test
./scripts/build-test.sh Release ON

# Install locally
./scripts/install-local.sh
```

### 2. Create and Deploy Package

```bash
# Create package
./scripts/create-package.sh

# Deploy locally
./scripts/deploy-local.sh

# Deploy to remote
./scripts/deploy-remote.sh studio http://studio.local:9300
```

### 3. Full Deployment to Studio.local

```bash
# Complete deployment pipeline
./scripts/deploy-full.sh studio.local gamepad
```

### 4. Install MCP Server for AI Assistants

```bash
# Install for all available AI assistants
./scripts/install-mcp.sh

# Or install for specific assistants
./scripts/install-mcp-claude.sh
./scripts/install-mcp-cursor.sh
```

## Conan Package Configuration

### Package Options

The Conan package supports the following options:

- `shared`: Build shared libraries (default: False)
- `fPIC`: Position independent code (default: True)
- `with_x11`: Enable X11 backend (default: True)
- `with_wayland`: Enable Wayland backend (default: True)
- `with_kde`: Enable KDE backend (default: True)
- `with_sdl2`: Enable SDL2 backend (default: True)
- `with_uinput`: Enable UInput backend (default: True)
- `with_mcp`: Enable MCP server (default: False)
- `with_bluetooth`: Enable Bluetooth support (default: False)
- `with_clipboard`: Enable clipboard monitoring (default: True)
- `with_alsa`: Enable ALSA audio (default: True)
- `with_pulseaudio`: Enable PulseAudio (default: True)

### Dependencies

Core dependencies:
- `nlohmann_json/3.11.2`
- `jsoncpp/1.9.5`
- `libcurl/8.4.0`

Test dependencies:
- `gtest/1.14.0`

## Deployment Scenarios

### 1. Local Development

For development and testing on the local machine:

```bash
# Build with all features enabled
./scripts/build-test.sh Release ON

# Install system-wide
./scripts/install-local.sh system
```

### 2. Remote Repository Deployment

Deploy to a Conan remote repository:

```bash
# Add remote repository
conan remote add studio http://studio.local:9300

# Create and upload package
conan create . --build=missing
conan upload "gamepad-mapper/1.0.0" -r studio --force
```

### 3. SSH Deployment to Target Machine

Deploy directly to a target machine via SSH:

```bash
# Deploy to studio.local
./scripts/deploy-studio.sh gamepad

# The script will:
# - Build the package locally
# - Upload to remote repository
# - Install on target machine
# - Configure systemd service
# - Install MCP server
```

### 4. Manual Installation

For manual installation on a target system:

```bash
# Install from remote repository
conan install "gamepad-mapper/1.0.0@" -r studio --build=missing

# Install system-wide
sudo ./scripts/install-local.sh system
```

## MCP Server Integration

The Gamepad Mapper includes MCP (Model Context Protocol) server integration for AI assistants.

### Available Tools

- `start_gamepad_mapper`: Start the gamepad mapper service
- `stop_gamepad_mapper`: Stop the gamepad mapper service
- `get_gamepad_status`: Get current status
- `list_mappings`: List available mappings
- `load_mapping`: Load a specific mapping

### Supported AI Assistants

- Claude Desktop
- Cursor
- Windsurf
- VS Code (with MCP extension)

### Installation

```bash
# Install for all assistants
./scripts/install-mcp.sh

# Restart your AI assistant to load the configuration
```

## Update Mechanism

To update to the latest version:

```bash
# Update from remote repository
./scripts/update-package.sh studio remote

# Update local installation
./scripts/update-package.sh local

# The script will:
# - Download the latest version
# - Replace old binaries
# - Restart services
# - Preserve configuration files
```

## Systemd Service

The deployment includes a systemd service for automatic startup:

```bash
# Service management
sudo systemctl start gamepad-mapper
sudo systemctl stop gamepad-mapper
sudo systemctl status gamepad-mapper
sudo systemctl enable gamepad-mapper  # Auto-start on boot
```

## Configuration Files

Configuration files are installed to `/usr/local/share/gamepad-mapper/config/`:

- `default_mappings.json`: Default key mappings
- `gaming_mappings.json`: Gaming-specific mappings
- `professional_mappings.json`: Professional application mappings
- And many more specialized configurations

## Troubleshooting

### Conan Issues

```bash
# Clean Conan cache
conan cache clean

# Re-detect profile
conan profile detect --force

# List remotes
conan remote list
```

### Build Issues

```bash
# Clean build directory
rm -rf build*

# Rebuild dependencies
conan install . --build=missing
```

### Deployment Issues

```bash
# Check SSH connection
ssh user@studio.local

# Check remote repository
conan remote ping studio

# Check service status
sudo systemctl status gamepad-mapper
```

### MCP Issues

```bash
# Test MCP server directly
python3 tools/gamepad_mcp_server.py

# Check configuration
cat ~/.config/Claude/mcp-config.json
```

## Advanced Usage

### Custom Build Options

```bash
# Build with specific options
cmake .. \
    -DWITH_X11=ON \
    -DWITH_WAYLAND=ON \
    -DWITH_MCP=ON \
    -DBUILD_TESTS=ON
```

### Remote Repository Setup

To set up a Conan remote repository on studio.local:

```bash
# On the server
conan_server --port 9300

# Or using Docker
docker run -p 9300:9300 conanio/conan-server
```

### Custom Deployment

For custom deployment scenarios, modify the deployment scripts in the `scripts/` directory.

## Contributing

When making changes to the package:

1. Update version in `conanfile.py`
2. Test locally: `./scripts/build-test.sh`
3. Update documentation
4. Create new package: `./scripts/create-package.sh`
5. Deploy: `./scripts/deploy-full.sh`

## License

This project is licensed under the MIT License. See LICENSE file for details.