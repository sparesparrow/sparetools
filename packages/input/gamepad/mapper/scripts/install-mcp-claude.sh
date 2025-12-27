#!/bin/bash

set -e  # Exit on any error

# Install Gamepad Mapper MCP Server for Claude Desktop
# This script installs the MCP configuration for Claude Desktop

echo "=== Installing Gamepad Mapper MCP Server for Claude Desktop ==="
echo

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command_exists python3; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3."
    exit 1
fi

echo "Prerequisites check passed."
echo

# Determine Claude Desktop config directory
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
else
    echo "Error: Unsupported operating system: $OSTYPE"
    exit 1
fi

# Create Claude config directory if it doesn't exist
echo "Setting up Claude Desktop configuration..."
mkdir -p "$CLAUDE_CONFIG_DIR"

# Copy MCP configuration
MCP_CONFIG_FILE="$CLAUDE_CONFIG_DIR/mcp-config.json"
echo "Installing MCP configuration to: $MCP_CONFIG_FILE"

cat > "$MCP_CONFIG_FILE" << 'EOF'
{
  "mcpServers": {
    "gamepad-mapper": {
      "command": "python3",
      "args": ["tools/gamepad_mcp_server.py"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
EOF

# Make the MCP server executable
chmod +x tools/gamepad_mcp_server.py

echo
echo "=== Installation completed successfully! ==="
echo
echo "MCP Server installed for Claude Desktop."
echo "Configuration file: $MCP_CONFIG_FILE"
echo
echo "To use the gamepad mapper with Claude Desktop:"
echo "1. Restart Claude Desktop"
echo "2. The gamepad mapper tools should be available in your conversations"
echo
echo "Available tools:"
echo "  - start_gamepad_mapper: Start the gamepad mapper service"
echo "  - stop_gamepad_mapper: Stop the gamepad mapper service"
echo "  - get_gamepad_status: Get current status"
echo "  - list_mappings: List available mappings"
echo "  - load_mapping: Load a specific mapping"