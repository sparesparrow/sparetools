#!/bin/bash

set -e  # Exit on any error

# Gamepad Mapper Remote Deployment Script
# This script builds and uploads the package to a remote Conan repository

REMOTE_NAME=${1:-"studio"}
REMOTE_URL=${2:-"http://studio.local:9300"}

echo "=== Gamepad Mapper Remote Deployment ==="
echo "Remote: $REMOTE_NAME ($REMOTE_URL)"
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

# Add remote repository if it doesn't exist
echo "Configuring remote repository..."
if ! conan remote list | grep -q "^$REMOTE_NAME:"; then
    echo "Adding remote repository: $REMOTE_NAME"
    conan remote add "$REMOTE_NAME" "$REMOTE_URL"
else
    echo "Remote repository $REMOTE_NAME already exists"
fi

# Login to remote (optional, will prompt if needed)
echo "Note: Make sure you are logged in to the remote repository"
echo "Run: conan remote login $REMOTE_NAME <username>"
echo

# Create and upload package
echo "Creating and uploading package..."
conan create . --build=missing
conan upload "gamepad-mapper/1.0.0" -r "$REMOTE_NAME" --force

echo
echo "=== Remote deployment completed successfully! ==="
echo
echo "The package has been uploaded to $REMOTE_NAME remote repository."
echo "Other machines can now install it with:"
echo "  conan install gamepad-mapper/1.0.0@ -r $REMOTE_NAME"