#!/bin/bash

set -e  # Exit on any error

# Gamepad Mapper Build & Test Pipeline Script
# This script builds the project with Conan and runs tests

BUILD_TYPE=${1:-"Release"}
ENABLE_TESTS=${2:-"ON"}

echo "=== Gamepad Mapper Build & Test Pipeline ==="
echo "Build Type: $BUILD_TYPE"
echo "Tests Enabled: $ENABLE_TESTS"
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
BUILD_DIR="build-pipeline"
echo "Creating build directory: $BUILD_DIR"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Configure Conan profile
echo "Configuring Conan..."
conan profile detect --force

# Install dependencies
echo "Installing dependencies with Conan..."
conan install .. --build=missing

# Configure with CMake
echo "Configuring with CMake..."
cmake .. -G "Unix Makefiles" \
         -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake \
         -DCMAKE_POLICY_DEFAULT_CMP0091=NEW \
         -DCMAKE_BUILD_TYPE="$BUILD_TYPE" \
         -DWITH_X11=ON \
         -DWITH_WAYLAND=ON \
         -DWITH_KDE=ON \
         -DWITH_SDL2=ON \
         -DWITH_UINPUT=ON \
         -DWITH_MCP=ON \
         -DWITH_BLUETOOTH=ON \
         -DWITH_CLIPBOARD=ON \
         -DBUILD_TESTS="$ENABLE_TESTS"

# Build
echo "Building project..."
make -j$(nproc)

# Run tests if enabled
if [ "$ENABLE_TESTS" = "ON" ]; then
    echo "Running tests..."
    make test
    echo "All tests passed!"
fi

echo
echo "=== Build & Test Pipeline completed successfully! ==="
echo
echo "Build artifacts location: $BUILD_DIR"
echo
echo "To run the application:"
echo "  ./gamepad_mapper_app"
echo
echo "To run with MCP server:"
echo "  ./gamepad_mapper_app --port 8080"
echo
if [ "$ENABLE_TESTS" = "ON" ]; then
    echo "Test results: Run 'make test' in $BUILD_DIR to re-run tests"
fi