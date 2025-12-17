# {{project_name}} MCP Server

{{project_description}}

## Overview

This is an MCP (Model Context Protocol) server template that provides tools and resources to AI assistants. Built with SpareTools for hermetic, cross-platform operation.

## Features

- MCP server implementation with stdio transport
- Tool and resource providers
- Hermetic Python environment via SpareTools
- Comprehensive logging and error handling
- Testing framework with MCP protocol validation
- Docker containerization support
- CI/CD pipeline ready

## Prerequisites

- Conan 2.x
- Python 3.12+ (system Python for bootstrapping only)
- Node.js 18+ (for MCP client testing)
- Docker (optional, for containerized deployment)

## Quick Start

1. Clone this template:
```bash
git clone {{repository_url}}
cd {{project_name}}
```

2. Install dependencies and build:
```bash
conan install . --build=missing
conan build .
```

3. Run the MCP server:
```bash
conan run . -- server
```

## Project Structure

```
{{project_name}}/
├── conanfile.py           # Conan recipe
├── pyproject.toml         # Python package configuration
├── src/{{module_name}}/   # Source code
│   ├── server.py          # MCP server implementation
│   ├── tools/             # Tool implementations
│   └── resources/         # Resource providers
├── test/                  # Unit and integration tests
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── docker/                # Docker configuration
└── test_package/          # Conan test package
```

## MCP Tools

This server provides the following tools:

{% for tool in tools %}
- `{{tool.name}}`: {{tool.description}}
{% endfor %}

## MCP Resources

This server provides the following resources:

{% for resource in resources %}
- `{{resource.uri}}`: {{resource.description}}
{% endfor %}

## Development

### Environment Setup

```bash
# Create isolated environment
conan install . --build=missing

# Activate environment
conan build .
```

### Running the Server

```bash
# Run in development mode
python -m {{module_name}}.server

# Run with specific configuration
python -m {{module_name}}.server --config config.json
```

### Testing

```bash
# Run unit tests
pytest test/unit/

# Run integration tests
pytest test/integration/

# Test MCP protocol compliance
pytest test/mcp_protocol/

# Run with MCP client
npm test  # Requires Node.js MCP client setup
```

### Code Quality

```bash
# Lint code
ruff check .

# Format code
black .

# Type check
mypy src/
```

## Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t {{project_name}} .

# Run container
docker run -p 3000:3000 {{project_name}}
```

## Configuration

The server can be configured via environment variables or a JSON config file:

```json
{
  "host": "localhost",
  "port": 3000,
  "log_level": "INFO",
  "tools": {
    "enabled": ["{{tools[0].name if tools else 'example_tool'}}"]
  }
}
```

## Contributing

See the main SpareTools documentation for contribution guidelines and coding standards.