#!/bin/bash

set -e  # Exit on any error

# Gamepad Mapper Local Installation Script
# This script installs the built package locally for development use

PACKAGE_VERSION=${1:-"1.0.0"}
INSTALL_PREFIX=${2:-"/usr/local"}

echo "=== Gamepad Mapper Local Installation ==="
echo "Version: $PACKAGE_VERSION"
echo "Install Prefix: $INSTALL_PREFIX"
echo

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command_exists conan; then
    echo "Error: Conan package manager is required but not installed."
    echo "Please install Conan: pip install conan"
    exit 1
fi

echo "Prerequisites check passed."
echo

# Configure Conan profile
echo "Configuring Conan..."
conan profile detect --force

# Install package locally
echo "Installing package locally..."
conan install "gamepad-mapper/$PACKAGE_VERSION@" --build=missing

# Install system-wide if requested
if [ "$INSTALL_PREFIX" != "/usr/local" ] || [ "$1" = "system" ]; then
    echo "Installing to system location..."

    # Create package directory
    PACKAGE_DIR="$INSTALL_PREFIX/share/gamepad-mapper"
    BIN_DIR="$INSTALL_PREFIX/bin"
    LIB_DIR="$INSTALL_PREFIX/lib"
    INCLUDE_DIR="$INSTALL_PREFIX/include"
    CONFIG_DIR="$INSTALL_PREFIX/share/gamepad-mapper/config"

    sudo mkdir -p "$PACKAGE_DIR"
    sudo mkdir -p "$BIN_DIR"
    sudo mkdir -p "$LIB_DIR"
    sudo mkdir -p "$INCLUDE_DIR"
    sudo mkdir -p "$CONFIG_DIR"

    # Copy files from Conan cache
    CONAN_CACHE=$(conan cache path "gamepad-mapper/$PACKAGE_VERSION@")

    if [ -d "$CONAN_CACHE/bin" ]; then
        sudo cp -r "$CONAN_CACHE/bin/"* "$BIN_DIR/"
    fi

    if [ -d "$CONAN_CACHE/lib" ]; then
        sudo cp -r "$CONAN_CACHE/lib/"* "$LIB_DIR/"
    fi

    if [ -d "$CONAN_CACHE/include" ]; then
        sudo cp -r "$CONAN_CACHE/include/"* "$INCLUDE_DIR/"
    fi

    if [ -d "$CONAN_CACHE/config" ]; then
        sudo cp -r "$CONAN_CACHE/config/"* "$CONFIG_DIR/"
    fi

    # Install pkg-config file
    if [ -f "$CONAN_CACHE/lib/pkgconfig/gamepad-mapper.pc" ]; then
        sudo mkdir -p "$INSTALL_PREFIX/lib/pkgconfig"
        sudo cp "$CONAN_CACHE/lib/pkgconfig/gamepad-mapper.pc" "$INSTALL_PREFIX/lib/pkgconfig/"
    fi

    # Install desktop file for applications
    cat > /tmp/gamepad-mapper.desktop << EOF
[Desktop Entry]
Name=Gamepad Mapper
Comment=Multi-backend gamepad to keyboard/mouse input mapper
Exec=gamepad_mapper_app
Icon=input-gaming
Terminal=false
Type=Application
Categories=Utility;Game;
EOF

    sudo cp /tmp/gamepad-mapper.desktop "$INSTALL_PREFIX/share/applications/"
    rm /tmp/gamepad-mapper.desktop

    echo "System installation completed."
fi

echo
echo "=== Local Installation completed successfully! ==="
echo
echo "Package installed: gamepad-mapper/$PACKAGE_VERSION"
echo
echo "To run the application:"
echo "  gamepad_mapper_app"
echo
echo "To run with MCP server:"
echo "  gamepad_mapper_app --port 8080"
echo
echo "Configuration files are located in:"
echo "  $CONFIG_DIR"