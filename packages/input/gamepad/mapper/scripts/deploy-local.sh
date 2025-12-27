#!/bin/bash

set -e  # Exit on any error

# Gamepad Mapper Local Deployment Script
# This script builds and installs the package locally using Conan

echo "=== Gamepad Mapper Local Deployment ==="
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

# Create package
echo "Creating Conan package..."
conan create . --build=missing --test-missing

# Install package locally
echo "Installing package locally..."
conan install gamepad-mapper/1.0.0@ --build=missing

echo
echo "=== Local deployment completed successfully! ==="
echo
echo "The package has been built and installed to your local Conan cache."
echo "You can now use it in other projects by adding:"
echo "  self.requires(\"gamepad-mapper/1.0.0\")"
echo "to your conanfile.py or conanfile.txt"