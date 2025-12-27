#!/bin/bash

set -e  # Exit on any error

# Gamepad Mapper Studio.local Deployment Script
# This script deploys the package to studio.local via SSH

REMOTE_HOST="studio.local"
REMOTE_USER=${1:-"gamepad"}
REMOTE_NAME="studio"

echo "=== Gamepad Mapper Studio.local Deployment ==="
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
if ! ssh -o ConnectTimeout=10 "$REMOTE_USER@$REMOTE_HOST" "echo 'SSH connection successful'"; then
    echo "Error: Cannot connect to $REMOTE_USER@$REMOTE_HOST"
    echo "Please check your SSH configuration and network connection."
    echo "Make sure you have SSH keys set up for passwordless authentication."
    exit 1
fi

echo "SSH connection test passed."
echo

# Create temporary deployment directory
DEPLOY_DIR="/tmp/gamepad-mapper-deploy"
echo "Preparing deployment directory: $DEPLOY_DIR"
rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# Copy project files (excluding build artifacts and git)
echo "Copying project files..."
rsync -av --exclude='build*' --exclude='.git' --exclude='*.log' --exclude='*.tmp' \
    --exclude='__pycache__' --exclude='*.pyc' --exclude='.pytest_cache' \
    ./ "$DEPLOY_DIR/"

# Build and deploy on remote
echo "Building and deploying on $REMOTE_HOST..."
ssh "$REMOTE_USER@$REMOTE_HOST" << EOF
    set -e
    echo "Setting up deployment on studio.local..."

    # Create working directory
    mkdir -p ~/gamepad-mapper-deploy
    cd ~/gamepad-mapper-deploy

    echo "Configuring Conan..."
    conan profile detect --force

    echo "Setting up Conan remote repository..."
    # Remove existing remote if it exists
    conan remote remove studio 2>/dev/null || true
    # Add studio remote
    conan remote add studio http://localhost:9300

    echo "Logging in to remote repository..."
    # Note: This assumes credentials are set up, may need manual intervention
    echo "Please ensure you are logged in to the studio remote repository"
    echo "Run: conan remote login studio <username>"

    echo "Remote setup completed."
EOF

# Upload project files
echo "Uploading project files to remote..."
rsync -avz --delete "$DEPLOY_DIR/" "$REMOTE_USER@$REMOTE_HOST:~/gamepad-mapper-deploy/"

# Continue deployment on remote
ssh "$REMOTE_USER@$REMOTE_HOST" << EOF
    set -e
    cd ~/gamepad-mapper-deploy

    echo "Building package..."
    conan create . --build=missing --test-missing

    echo "Uploading package to studio remote..."
    conan upload "gamepad-mapper/1.0.0" -r studio --force

    echo "Installing MCP server configuration..."
    # Install MCP server configuration for AI assistants
    mkdir -p ~/.mcp/servers
    cp mcp-config.json ~/.mcp/servers/gamepad-mapper.json

    # Install for Claude Desktop if it exists
    if [ -d ~/.claude-desktop ]; then
        mkdir -p ~/.claude-desktop/mcp
        cp mcp-config.json ~/.claude-desktop/mcp/gamepad-mapper.json
    fi

    # Install for Cursor if it exists
    if [ -d ~/.cursor ]; then
        mkdir -p ~/.cursor/mcp
        cp mcp-config.json ~/.cursor/mcp/gamepad-mapper.json
    fi

    echo "Installing systemd service..."
    # Install systemd service for auto-start
    sudo cp scripts/gamepad-mapper.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable gamepad-mapper
    sudo systemctl start gamepad-mapper

    echo "Deployment to studio.local completed successfully!"
EOF

# Cleanup
echo "Cleaning up temporary files..."
rm -rf "$DEPLOY_DIR"

echo
echo "=== Studio.local Deployment completed successfully! ==="
echo
echo "The Gamepad Mapper has been deployed to studio.local with:"
echo "  - Conan package uploaded to studio remote repository"
echo "  - MCP server configuration installed"
echo "  - Systemd service configured and started"
echo
echo "The service should now be running automatically on startup."