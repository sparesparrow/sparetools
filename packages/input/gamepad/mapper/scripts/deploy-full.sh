#!/bin/bash

set -e  # Exit on any error

# Gamepad Mapper Full Deployment Script
# This script performs a complete deployment: build, test, package, and deploy

REMOTE_HOST=${1:-"studio.local"}
REMOTE_USER=${2:-"gamepad"}
REMOTE_NAME=${3:-"studio"}

echo "=== Gamepad Mapper Full Deployment ==="
echo "Target: $REMOTE_USER@$REMOTE_HOST"
echo "Remote Repository: $REMOTE_NAME"
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

if ! command_exists ssh; then
    echo "Error: SSH client is required but not installed."
    echo "Please install OpenSSH client."
    exit 1
fi

echo "Prerequisites check passed."
echo

# Step 1: Build and test locally
echo "=== Step 1: Build and Test Locally ==="
echo

./scripts/build-test.sh Release ON

echo
echo "Local build and test completed successfully!"
echo

# Step 2: Create package
echo "=== Step 2: Create Package ==="
echo

./scripts/create-package.sh

echo
echo "Package creation completed successfully!"
echo

# Step 3: Deploy to remote
echo "=== Step 3: Deploy to Remote ==="
echo

./scripts/deploy-studio.sh "$REMOTE_USER"

echo
echo "Remote deployment completed successfully!"
echo

# Step 4: Install MCP server
echo "=== Step 4: Install MCP Server ==="
echo

./scripts/install-mcp.sh

echo
echo "MCP server installation completed successfully!"
echo

echo "=== Full Deployment Completed Successfully! ==="
echo
echo "Summary:"
echo "✓ Local build and tests passed"
echo "✓ Package created and uploaded to $REMOTE_NAME remote"
echo "✓ Deployed to $REMOTE_HOST with systemd service"
echo "✓ MCP server configured for AI assistants"
echo
echo "The Gamepad Mapper is now fully deployed and ready to use!"
echo
echo "To update in the future:"
echo "  ./scripts/update-package.sh $REMOTE_NAME remote"
echo
echo "To manually start/stop the service:"
echo "  sudo systemctl start gamepad-mapper"
echo "  sudo systemctl stop gamepad-mapper"
echo "  sudo systemctl status gamepad-mapper"