#!/bin/bash

set -e  # Exit on any error

# Install Gamepad Mapper MCP Server
# This script installs MCP configuration for available AI assistants

echo "=== Installing Gamepad Mapper MCP Server ==="
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

# Make the MCP server executable
chmod +x tools/gamepad_mcp_server.py

# Install for Claude Desktop
install_claude() {
    local CLAUDE_CONFIG_DIR=""

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
    fi

    if [[ -n "$CLAUDE_CONFIG_DIR" ]]; then
        echo "Installing for Claude Desktop..."
        mkdir -p "$CLAUDE_CONFIG_DIR"

        # Backup existing config if it exists
        if [[ -f "$CLAUDE_CONFIG_DIR/mcp-config.json" ]]; then
            cp "$CLAUDE_CONFIG_DIR/mcp-config.json" "$CLAUDE_CONFIG_DIR/mcp-config.json.backup.$(date +%Y%m%d_%H%M%S)"
            echo "✓ Backed up existing Claude Desktop MCP config"
        fi

        # Append gamepad-mapper to existing config or create new
        if [[ -f "$CLAUDE_CONFIG_DIR/mcp-config.json" ]]; then
            # Merge with existing config
            python3 -c "
import json
import sys

# Load existing config
with open('$CLAUDE_CONFIG_DIR/mcp-config.json', 'r') as f:
    config = json.load(f)

# Add gamepad-mapper if not already present
if 'mcpServers' not in config:
    config['mcpServers'] = {}

if 'gamepad-mapper' not in config['mcpServers']:
    config['mcpServers']['gamepad-mapper'] = {
        'command': 'python3',
        'args': ['tools/gamepad_mcp_server.py'],
        'env': {'PYTHONPATH': '.'}
    }
    
    # Write updated config
    with open('$CLAUDE_CONFIG_DIR/mcp-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    print('✓ Added gamepad-mapper to existing Claude Desktop MCP config')
else:
    print('✓ gamepad-mapper already exists in Claude Desktop MCP config')
"
        else
            # Create new config
            cat > "$CLAUDE_CONFIG_DIR/mcp-config.json" << 'EOF'
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
        echo "✓ Claude Desktop configuration installed"
    fi
}

# Install for Cursor
install_cursor() {
    local CURSOR_CONFIG_DIR=""

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        CURSOR_CONFIG_DIR="$HOME/.config/cursor"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        CURSOR_CONFIG_DIR="$HOME/Library/Application Support/Cursor"
    fi

    if [[ -n "$CURSOR_CONFIG_DIR" ]]; then
        echo "Installing for Cursor..."
        mkdir -p "$CURSOR_CONFIG_DIR"

        # Backup existing config if it exists
        if [[ -f "$CURSOR_CONFIG_DIR/mcp-config.json" ]]; then
            cp "$CURSOR_CONFIG_DIR/mcp-config.json" "$CURSOR_CONFIG_DIR/mcp-config.json.backup.$(date +%Y%m%d_%H%M%S)"
            echo "✓ Backed up existing Cursor MCP config"
        fi

        # Append gamepad-mapper to existing config or create new
        if [[ -f "$CURSOR_CONFIG_DIR/mcp-config.json" ]]; then
            # Merge with existing config
            python3 -c "
import json
import sys

# Load existing config
with open('$CURSOR_CONFIG_DIR/mcp-config.json', 'r') as f:
    config = json.load(f)

# Add gamepad-mapper if not already present
if 'mcpServers' not in config:
    config['mcpServers'] = {}

if 'gamepad-mapper' not in config['mcpServers']:
    config['mcpServers']['gamepad-mapper'] = {
        'command': 'python3',
        'args': ['tools/gamepad_mcp_server.py'],
        'env': {'PYTHONPATH': '.'}
    }
    
    # Write updated config
    with open('$CURSOR_CONFIG_DIR/mcp-config.json', 'w') as f:
        json.dump(config, f, indent=2)
    print('✓ Added gamepad-mapper to existing Cursor MCP config')
else:
    print('✓ gamepad-mapper already exists in Cursor MCP config')
"
        else
            # Create new config
            cat > "$CURSOR_CONFIG_DIR/mcp-config.json" << 'EOF'
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
        echo "✓ Cursor configuration installed"
    fi
}

# Install for Windsurf (if detected)
install_windsurf() {
    local WINDSURF_CONFIG_DIR="$HOME/.windsurf"

    if [[ -d "$WINDSURF_CONFIG_DIR" ]]; then
        echo "Installing for Windsurf..."
        mkdir -p "$WINDSURF_CONFIG_DIR/mcp"

        # Backup existing config if it exists
        if [[ -f "$WINDSURF_CONFIG_DIR/mcp/gamepad-mapper.json" ]]; then
            cp "$WINDSURF_CONFIG_DIR/mcp/gamepad-mapper.json" "$WINDSURF_CONFIG_DIR/mcp/gamepad-mapper.json.backup.$(date +%Y%m%d_%H%M%S)"
            echo "✓ Backed up existing Windsurf gamepad-mapper config"
        fi

        # Create or update Windsurf config
        cat > "$WINDSURF_CONFIG_DIR/mcp/gamepad-mapper.json" << 'EOF'
{
  "command": "python3",
  "args": ["tools/gamepad_mcp_server.py"],
  "env": {
    "PYTHONPATH": "."
  }
}
EOF
        echo "✓ Windsurf configuration installed"
    fi
}

# Install for VS Code (if MCP extension is available)
install_vscode() {
    local VSCODE_CONFIG_DIR=""

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        VSCODE_CONFIG_DIR="$HOME/.config/Code/User"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        VSCODE_CONFIG_DIR="$HOME/Library/Application Support/Code/User"
    fi

    if [[ -n "$VSCODE_CONFIG_DIR" ]]; then
        echo "Installing for VS Code (if MCP extension is available)..."
        mkdir -p "$VSCODE_CONFIG_DIR/mcp"

        cat > "$VSCODE_CONFIG_DIR/mcp/gamepad-mapper.json" << 'EOF'
{
  "command": "python3",
  "args": ["tools/gamepad_mcp_server.py"],
  "env": {
    "PYTHONPATH": "."
  }
}
EOF
        echo "✓ VS Code configuration installed (requires MCP extension)"
    fi
}

# Install system-wide MCP config (generic)
install_system() {
    echo "Installing system-wide MCP configuration..."
    mkdir -p "$HOME/.mcp/servers"

    cat > "$HOME/.mcp/servers/gamepad-mapper.json" << 'EOF'
{
  "command": "python3",
  "args": ["tools/gamepad_mcp_server.py"],
  "env": {
    "PYTHONPATH": "."
  }
}
EOF
    echo "✓ System-wide MCP configuration installed"
}

# Run installations
install_claude
install_cursor
install_windsurf
install_vscode
install_system

echo
echo "=== Installation completed successfully! ==="
echo
echo "MCP Server installed for available AI assistants."
echo
echo "To use the gamepad mapper with your AI assistant:"
echo "1. Restart your AI assistant application"
echo "2. The gamepad mapper tools should be available in your conversations"
echo
echo "Available tools:"
echo "  - start_gamepad_mapper: Start the gamepad mapper service"
echo "  - stop_gamepad_mapper: Stop the gamepad mapper service"
echo "  - get_gamepad_status: Get current status"
echo "  - list_mappings: List available mappings"
echo "  - load_mapping: Load a specific mapping"
echo
echo "Configuration files installed in:"
echo "  - Claude Desktop: ~/.config/Claude/mcp-config.json"
echo "  - Cursor: ~/.config/cursor/mcp-config.json"
echo "  - Windsurf: ~/.windsurf/mcp/gamepad-mapper.json"
echo "  - VS Code: ~/.config/Code/User/mcp/gamepad-mapper.json"
echo "  - System: ~/.mcp/servers/gamepad-mapper.json"