# MCP (Model Context Protocol) Integration

This directory contains MCP server configurations, prompts, and documentation for Cursor IDE integration.

## Directory Structure

```
mcp/
├── configs/           # MCP server configuration files
│   ├── mcp.json      # Current configuration (with sudo)
│   ├── mcp-memory.json    # Memory-based configuration
│   └── mcp-no-sudo.json   # No-sudo configuration
├── commands/          # MCP command documentation
│   └── *.md          # Individual command guides
└── docs/             # Documentation
    └── MCP-README.md # Setup and usage guide
```

## Available MCP Commands

### Analysis & Development
- `mcp-analysis-prompt` - Generate analysis prompts for code review, debugging, or system analysis
- `mcp-architecture-prompt` - Architecture design and review prompts
- `mcp-code-generator` - Code generation prompts
- `mcp-debugging-prompt` - Debugging assistance prompts
- `mcp-documentation-prompt` - Documentation generation prompts
- `mcp-testing-prompt` - Test case generation prompts

### Project Management
- `generate-component` - Component generation
- `generate-diagram` - Diagram generation
- `generate-project` - Project scaffolding

### System Integration
- `cast-test-urls` - Cast service testing
- `continuous-screen-cast` - Screen casting utilities
- `rtsp-screen-stream` - RTSP streaming
- `screen-capture-tv-compatible` - TV-compatible screen capture
- `upnp-discovery` - UPnP device discovery

## MCP Server Capabilities

The MCP Prompts server provides these tools:
- `add_prompt` - Add new prompts
- `get_prompt` - Retrieve specific prompts
- `list_prompts` - List all prompts
- `update_prompt` - Update existing prompts
- `delete_prompt` - Delete prompts
- `apply_template` - Apply template variables
- `get_stats` - Get server statistics

## Usage

1. Copy desired configuration from `configs/` to `~/.cursor/mcp.json`
2. Restart Cursor IDE
3. Use MCP commands via Cursor's MCP integration

## Integration with Sparetools

This MCP integration is designed to work seamlessly with the sparetools ecosystem:

- **Prompt Templates**: Located in `../templates/prompts/`
- **Configuration Files**: Located in `../configs/`
- **Scripts**: Available via sparetools packages
- **Documentation**: Cross-referenced with main sparetools docs

## Docker Setup

The MCP configurations expect Docker containers to be available. See the main sparetools documentation for Docker setup instructions.

## Troubleshooting

- **Permission denied**: Use `sudo` or ensure user is in docker group
- **Container not found**: Run Docker Compose setup first
- **Connection issues**: Check Docker service status

For detailed setup instructions, see `docs/MCP-README.md`.