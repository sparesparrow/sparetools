#!/bin/bash

set -e  # Exit on any error

# Gamepad Mapper SSH Deployment Script
# This script deploys the package to a remote machine via SSH

REMOTE_HOST=${1:-"studio.local"}
REMOTE_USER=${2:-"$USER"}
REMOTE_NAME=${3:-"studio"}

echo "=== Gamepad Mapper SSH Deployment ==="
echo "Target: $REMOTE_USER@$REMOTE_HOST"
echo "Remote repository: $REMOTE_NAME"
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

if ! command_exists rsync; then
    echo "Error: rsync is required but not installed."
    echo "Please install rsync."
    exit 1
fi

echo "Prerequisites check passed."
echo

# Test SSH connection
echo "Testing SSH connection to $REMOTE_USER@$REMOTE_HOST..."
if ! ssh -o ConnectTimeout=5 "$REMOTE_USER@$REMOTE_HOST" "echo 'SSH connection successful'"; then
    echo "Error: Cannot connect to $REMOTE_USER@$REMOTE_HOST"
    echo "Please check your SSH configuration and network connection."
    exit 1
fi

echo "SSH connection test passed."
echo

# Sync project to remote
echo "Syncing project files to remote..."
rsync -avz --exclude='build*' --exclude='.git' --exclude='*.log' \
    ./ "$REMOTE_USER@$REMOTE_HOST:~/gamepad-mapper-deploy/"

# Build and deploy on remote
echo "Building and deploying on remote machine..."
ssh "$REMOTE_USER@$REMOTE_HOST" << EOF
    set -e
    cd ~/gamepad-mapper-deploy

    echo "Configuring Conan on remote..."
    conan profile detect --force

    echo "Adding remote repository..."
    if ! conan remote list | grep -q "^$REMOTE_NAME:"; then
        conan remote add "$REMOTE_NAME" "http://localhost:9300"
    fi

    echo "Creating package..."
    conan create . --build=missing

    echo "Uploading to remote repository..."
    conan upload "gamepad-mapper/1.0.0" -r "$REMOTE_NAME" --force

    echo "Installing MCP configuration..."
    # Install MCP server configuration
    mkdir -p ~/.mcp/servers
    cp mcp-config.json ~/.mcp/servers/gamepad-mapper.json

    echo "Remote deployment completed successfully!"
EOF

echo
echo "=== SSH deployment completed successfully! ==="
echo
echo "The package has been built and deployed to $REMOTE_HOST."
echo "MCP server configuration has been installed."