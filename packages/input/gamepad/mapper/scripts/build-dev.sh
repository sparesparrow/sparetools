#!/bin/bash

set -e  # Exit on any error

# Gamepad Mapper Development Build Script
# This script sets up the development environment and builds the project

echo "=== Gamepad Mapper Development Build ==="
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

if ! command_exists cmake; then
    echo "Error: CMake is required but not installed."
    echo "Please install CMake from your package manager."
    exit 1
fi

if ! command_exists make; then
    echo "Error: Make is required but not installed."
    echo "Please install build-essential or equivalent."
    exit 1
fi

echo "Prerequisites check passed."
echo

# Create build directory
BUILD_DIR="build-dev"
echo "Creating build directory: $BUILD_DIR"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Configure Conan profile
echo "Configuring Conan..."
conan profile detect --force

# Install dependencies
echo "Installing dependencies with Conan..."
conan install .. --build=missing

# Configure with CMake using Conan toolchain
echo "Configuring with CMake..."
cmake .. -G "Unix Makefiles" \
         -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake \
         -DCMAKE_POLICY_DEFAULT_CMP0091=NEW \
         -DCMAKE_BUILD_TYPE=Debug \
         -DWITH_X11=ON \
         -DWITH_WAYLAND=ON \
         -DWITH_KDE=OFF \
         -DWITH_SDL2=ON \
         -DWITH_UINPUT=ON \
         -DWITH_MCP=OFF \
         -DWITH_BLUETOOTH=OFF \
         -DBUILD_TESTS=OFF

# Build
echo "Building project..."
make -j$(nproc)

echo
echo "=== Build completed successfully! ==="
echo
echo "To run the gamepad mapper:"
echo "  ./gamepad_mapper_app"
echo
echo "To run with MCP server:"
echo "  ./gamepad_mapper_app --port 8080"
echo
echo "To run tests (if built):"
echo "  make test"
echo
echo "Binary location: $BUILD_DIR/gamepad_mapper_app"