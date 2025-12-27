#!/bin/bash

set -e  # Exit on any error

# Gamepad Mapper Package Update Script
# This script updates the package to the latest version

REMOTE_NAME=${1:-"studio"}
UPDATE_TYPE=${2:-"remote"}  # "local" or "remote"

echo "=== Gamepad Mapper Package Update ==="
echo "Update Type: $UPDATE_TYPE"
echo "Remote: $REMOTE_NAME"
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

# Get current version
CURRENT_VERSION=$(grep "version = " conanfile.py | sed 's/.*version = "\(.*\)".*/\1/')
echo "Current version: $CURRENT_VERSION"

# Function to update from remote
update_remote() {
    echo "Updating from remote repository..."

    # Remove existing remote if it exists and re-add
    conan remote remove "$REMOTE_NAME" 2>/dev/null || true
    conan remote add "$REMOTE_NAME" "http://studio.local:9300"

    # Download latest package info
    echo "Checking for updates..."
    if conan search "gamepad-mapper/*" -r "$REMOTE_NAME" > /dev/null 2>&1; then
        # Get latest version from remote
        LATEST_VERSION=$(conan search "gamepad-mapper/*" -r "$REMOTE_NAME" | grep "gamepad-mapper/" | tail -1 | sed 's/.*gamepad-mapper\/\([^@]*\).*/\1/')

        if [[ "$LATEST_VERSION" != "$CURRENT_VERSION" ]]; then
            echo "New version available: $LATEST_VERSION (current: $CURRENT_VERSION)"

            # Install new version
            echo "Installing new version..."
            conan install "gamepad-mapper/$LATEST_VERSION@" -r "$REMOTE_NAME" --build=missing

            # Update system installation if it exists
            update_system_installation "$LATEST_VERSION"

            echo "Update completed successfully!"
        else
            echo "Already up to date (version $CURRENT_VERSION)"
        fi
    else
        echo "No packages found in remote repository"
        exit 1
    fi
}

# Function to update locally
update_local() {
    echo "Updating local package..."

    # Build and install locally
    echo "Rebuilding package..."
    conan create . --build=missing

    # Update system installation if it exists
    update_system_installation "$CURRENT_VERSION"

    echo "Local update completed successfully!"
}

# Function to update system installation
update_system_installation() {
    local version=$1
    local INSTALL_PREFIX="/usr/local"

    echo "Checking for system installation..."

    # Check if system installation exists
    if [[ -f "$INSTALL_PREFIX/bin/gamepad_mapper_app" ]]; then
        echo "Updating system installation..."

        # Backup current installation
        echo "Creating backup..."
        sudo cp -r "$INSTALL_PREFIX/share/gamepad-mapper" "$INSTALL_PREFIX/share/gamepad-mapper.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true

        # Get package from Conan cache
        CONAN_CACHE=$(conan cache path "gamepad-mapper/$version@")

        if [[ -d "$CONAN_CACHE" ]]; then
            # Update binaries
            if [[ -d "$CONAN_CACHE/bin" ]]; then
                sudo cp -r "$CONAN_CACHE/bin/"* "$INSTALL_PREFIX/bin/" || true
            fi

            # Update libraries
            if [[ -d "$CONAN_CACHE/lib" ]]; then
                sudo cp -r "$CONAN_CACHE/lib/"* "$INSTALL_PREFIX/lib/" || true
            fi

            # Update headers
            if [[ -d "$CONAN_CACHE/include" ]]; then
                sudo cp -r "$CONAN_CACHE/include/"* "$INSTALL_PREFIX/include/" || true
            fi

            # Update config files
            if [[ -d "$CONAN_CACHE/config" ]]; then
                sudo cp -r "$CONAN_CACHE/config/"* "$INSTALL_PREFIX/share/gamepad-mapper/config/" || true
            fi

            # Update pkg-config file
            if [[ -f "$CONAN_CACHE/lib/pkgconfig/gamepad-mapper.pc" ]]; then
                sudo cp "$CONAN_CACHE/lib/pkgconfig/gamepad-mapper.pc" "$INSTALL_PREFIX/lib/pkgconfig/" || true
            fi

            echo "System installation updated successfully!"
        else
            echo "Warning: Could not find package in Conan cache"
        fi
    else
        echo "No system installation found"
    fi
}

# Function to restart services
restart_services() {
    echo "Checking for running services..."

    # Check if systemd service is running
    if command -v systemctl >/dev/null 2>&1 && systemctl is-active --quiet gamepad-mapper 2>/dev/null; then
        echo "Restarting gamepad-mapper service..."
        sudo systemctl restart gamepad-mapper
        echo "Service restarted"
    fi

    # Check for running processes
    if pgrep -f "gamepad_mapper_app" >/dev/null; then
        echo "Warning: gamepad_mapper_app process is running"
        echo "You may need to restart applications that use the gamepad mapper"
    fi
}

# Main update logic
if [[ "$UPDATE_TYPE" == "remote" ]]; then
    update_remote
elif [[ "$UPDATE_TYPE" == "local" ]]; then
    update_local
else
    echo "Error: Invalid update type. Use 'local' or 'remote'"
    exit 1
fi

# Restart services if needed
restart_services

echo
echo "=== Update completed successfully! ==="
echo
echo "Package updated to latest version."
echo "You may need to restart any applications using the gamepad mapper."