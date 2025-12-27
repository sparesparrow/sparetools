# MCP Server Configuration for Cursor

This directory contains MCP (Model Context Protocol) server configurations for Cursor IDE.

## Available Configurations

### 1. `mcp.json` (Current - with sudo)
- **File-based storage** with persistent data
- **5 sample prompts** included
- **Requires sudo** for Docker access
- **Recommended for development**

### 2. `mcp-memory.json` (Alternative)
- **Memory-based storage** (temporary)
- **No persistent data**
- **Requires sudo** for Docker access
- **Good for testing**

### 3. `mcp-no-sudo.json` (Future)
- **File-based storage** with persistent data
- **No sudo required** (after docker group setup)
- **Requires logout/login** to take effect

## MCP Server Capabilities

The MCP Prompts server provides these tools:
- `add_prompt` - Add new prompts
- `get_prompt` - Retrieve specific prompts
- `list_prompts` - List all prompts
- `update_prompt` - Update existing prompts
- `delete_prompt` - Delete prompts
- `apply_template` - Apply template variables
- `get_stats` - Get server statistics

## Sample Prompts Included

1. **Code Review Assistant** - Review code for quality and best practices
2. **Documentation Writer** - Generate comprehensive documentation
3. **Bug Analyzer** - Analyze and debug code issues
4. **Architecture Reviewer** - Review system architecture
5. **Test Case Generator** - Generate test cases

## Usage

1. **Current setup**: Cursor will use `mcp.json` automatically
2. **Switch configurations**: Rename files as needed
3. **Test connection**: Use MCP Inspector or direct Docker commands

## Docker Commands

```bash
# Test MCP server directly
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' | sudo docker run --rm -i mcp-prompts-mcp-prompts-file

# List available prompts
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "list_prompts", "arguments": {}}}' | sudo docker run --rm -i mcp-prompts-mcp-prompts-file

# Get specific prompt
echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_prompt", "arguments": {"id": "code-review-assistant"}}}' | sudo docker run --rm -i mcp-prompts-mcp-prompts-file
```

## Troubleshooting

- **Permission denied**: Use `sudo` or ensure user is in docker group
- **Container not found**: Run `sudo docker-compose -f docker-compose.file.yml up --build -d` first
- **Connection issues**: Check if Docker is running with `sudo systemctl status docker`