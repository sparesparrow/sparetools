# sparetools-mcp-orchestrator

MCP (Model Context Protocol) integration and AI-assisted development orchestration.

## Purpose

Provides MCP server integration, AI-assisted development tools, Mermaid diagram generation, and project orchestration capabilities. Enables cursor-based AI development workflows and multi-agent orchestration.

## Installation

```bash
conan export packages/sparetools-mcp-orchestrator --version=1.0.0
```

## Features

- **MCP Server Integration**: FastMCP and custom MCP servers
- **AI-Assisted Development**: Cursor integration and AI workflows
- **Mermaid Diagram Generation**: Automatic architecture diagrams
- **Prompt Management**: 700+ AI prompt templates
- **Project Orchestration**: Multi-agent coordination
- **Ecosystem Monitoring**: Project health and metrics
- **AWS Integration**: AWS MCP support

## Usage

```python
from conan import ConanFile

class MyPackage(ConanFile):
    python_requires = "sparetools-mcp-orchestrator/1.0.0"
```

## Modules

### Core
- `mcp_project_orchestrator/core/` - Core MCP functionality
- `mcp_project_orchestrator/fastmcp.py` - FastMCP integration

### AI & Orchestration
- `mcp_project_orchestrator/project_orchestration.py` - Project orchestration
- `mcp_project_orchestrator/fan_out_orchestrator.py` - Fan-out patterns
- `mcp_project_orchestrator/ecosystem_monitor.py` - Ecosystem monitoring

### Mermaid
- `mcp_project_orchestrator/mermaid/generator.py` - Diagram generation
- `mcp_project_orchestrator/mermaid/renderer.py` - Diagram rendering
- `mcp_project_orchestrator/mermaid/` - Complete Mermaid tooling

### Prompts
- `mcp_project_orchestrator/prompts/` - 700+ prompt templates
- `mcp_project_orchestrator/prompt_manager/` - Prompt management

## Commands

### MCP Server

```bash
# Start MCP server
python -m mcp_project_orchestrator.server

# Run CLI
python -m mcp_project_orchestrator.cli
```

### Diagram Generation

```python
from mcp_project_orchestrator.mermaid import generate_diagram

diagram = generate_diagram(
    type="architecture",
    components=["frontend", "backend", "database"]
)
```

## Dependencies

- Python 3.8+
- sparetools-base/1.0.0

## Use Cases

- AI-assisted code generation
- Architecture diagram automation
- Multi-repository orchestration
- Prompt-driven development
- Cursor IDE integration

## Note

This is a general-purpose tool not specific to OpenSSL. Consider separating into its own repository (sparesparrow/mcp-orchestrator) for broader reuse.

## License

Apache-2.0

## Resources

- [MCP Protocol](https://modelcontextprotocol.io/)
- [Mermaid Documentation](https://mermaid.js.org/)
- [Cursor IDE](https://cursor.sh/)

## Version

Current: 1.0.0

## Related Packages

- sparetools-base: Foundation utilities

