#!/bin/bash

# Gamepad Mapper Service Installation Script
# This script installs the gamepad mapper as a systemd service

set -e

echo "=== Gamepad Mapper Service Installation ==="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root (sudo)"
    exit 1
fi

# Configuration
INSTALL_PREFIX="/usr/local"
CONFIG_DIR="/etc/gamepad-mapper"
LOG_DIR="/var/log/gamepad-mapper"
SERVICE_USER="gamepad-mapper"
SERVICE_GROUP="gamepad-mapper"

echo "Installation configuration:"
echo "  Install prefix: $INSTALL_PREFIX"
echo "  Config directory: $CONFIG_DIR"
echo "  Log directory: $LOG_DIR"
echo "  Service user: $SERVICE_USER"
echo "  Service group: $SERVICE_GROUP"
echo

# Check if gamepad_mapper_app exists
if [ ! -f "build-conan/gamepad_mapper_app" ]; then
    echo "Error: gamepad_mapper_app not found. Please build the project first."
    echo "Run: ./scripts/build-dev.sh"
    exit 1
fi

echo "Installing binaries..."
# Install binaries
install -m 755 build-conan/gamepad_mapper_app "$INSTALL_PREFIX/bin/"
if [ -f "build-conan/advanced_gamepad_mapper" ]; then
    install -m 755 build-conan/advanced_gamepad_mapper "$INSTALL_PREFIX/bin/"
fi

echo "Installing configuration files..."
# Create config directory
mkdir -p "$CONFIG_DIR"

# Install config files
cp -r config/* "$CONFIG_DIR/"

# Set proper permissions
chmod 644 "$CONFIG_DIR"/*.json

echo "Creating log directory..."
# Create log directory
mkdir -p "$LOG_DIR"
chmod 755 "$LOG_DIR"

echo "Creating service user..."
# Create service user if it doesn't exist
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd --system --shell /bin/false --home-dir /nonexistent --no-create-home "$SERVICE_USER"
fi

# Create service group if needed
if ! getent group "$SERVICE_GROUP" &>/dev/null; then
    groupadd "$SERVICE_GROUP"
fi

# Add user to groups
usermod -a -G input,bluetooth "$SERVICE_USER" 2>/dev/null || true

echo "Setting ownership..."
# Set ownership
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$CONFIG_DIR"
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$LOG_DIR"

echo "Installing udev rules..."
# Install udev rules
if [ -f "scripts/99-gamepad-mapper.rules" ]; then
    cp scripts/99-gamepad-mapper.rules /etc/udev/rules.d/
    udevadm control --reload-rules
    udevadm trigger
fi

echo "Installing systemd service..."
# Install systemd service
cp scripts/gamepad-mapper.service /etc/systemd/system/
systemctl daemon-reload

echo "Enabling and starting service..."
# Enable and start service
systemctl enable gamepad-mapper.service
systemctl start gamepad-mapper.service

echo
echo "=== Installation Complete ==="
echo
echo "Service status:"
systemctl status gamepad-mapper.service --no-pager -l
echo
echo "Service commands:"
echo "  Start:   systemctl start gamepad-mapper.service"
echo "  Stop:    systemctl stop gamepad-mapper.service"
echo "  Restart: systemctl restart gamepad-mapper.service"
echo "  Status:  systemctl status gamepad-mapper.service"
echo "  Logs:    journalctl -u gamepad-mapper.service -f"
echo
echo "Configuration files are in: $CONFIG_DIR"
echo "Log files are in: $LOG_DIR"
echo
echo "To modify configuration, edit files in $CONFIG_DIR and restart the service."