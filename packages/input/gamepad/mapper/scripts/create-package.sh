#!/bin/bash

set -e  # Exit on any error

# Gamepad Mapper Package Creation Script
# This script creates a Conan package for distribution

PACKAGE_VERSION=${1:-"1.0.0"}
BUILD_TYPE=${2:-"Release"}

echo "=== Gamepad Mapper Package Creation ==="
echo "Version: $PACKAGE_VERSION"
echo "Build Type: $BUILD_TYPE"
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

# Create package with testing
echo "Creating Conan package with tests..."
conan create . --build=missing --test-missing

# Verify package creation
echo "Verifying package creation..."
if conan search "gamepad-mapper/$PACKAGE_VERSION" | grep -q "gamepad-mapper/$PACKAGE_VERSION"; then
    echo "Package created successfully: gamepad-mapper/$PACKAGE_VERSION"
else
    echo "Error: Package creation failed"
    exit 1
fi

# Show package information
echo "Package information:"
conan inspect "gamepad-mapper/$PACKAGE_VERSION"

echo
echo "=== Package Creation completed successfully! ==="
echo
echo "Package: gamepad-mapper/$PACKAGE_VERSION"
echo
echo "To install locally:"
echo "  conan install gamepad-mapper/$PACKAGE_VERSION@ --build=missing"
echo
echo "To upload to remote repository:"
echo "  conan upload gamepad-mapper/$PACKAGE_VERSION@ -r <remote-name> --force"