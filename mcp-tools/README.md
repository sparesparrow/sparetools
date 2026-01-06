# MCP (Model Context Protocol) Tools

This directory contains tools for MCP prompt management, rendering, and web interfaces.

## Directory Structure

```
mcp-tools/
├── scripts/          # Core MCP scripts
│   ├── create_prompt_commands.py
│   ├── prompt_renderer.py
│   ├── render_prompt_example.py
│   └── test_prompt_renderer.py
├── web/              # Web interfaces
│   └── prompt_web_interface.py
├── templates/        # Template systems
│   ├── diagram_templates/
│   └── prompt_templates/
├── examples/         # Usage examples
├── config/           # Configuration files
│   ├── mcp_prompts.json
│   └── prompt_commands.json
├── docs/             # Documentation
│   └── system_architecture.mmd
└── README.md
```

## Components

### Prompt Management
- **Command Creation**: Generate MCP command structures
- **Prompt Rendering**: Convert prompts to various formats
- **Testing**: Validation and testing utilities

### Web Interface
- **Prompt Web Interface**: Web-based prompt management
- **Interactive Rendering**: Browser-based prompt editing

### Templates
- **Diagram Templates**: Mermaid diagram templates
- **Prompt Templates**: Reusable prompt structures

## Usage

### Create Prompt Commands
```bash
python3 scripts/create_prompt_commands.py --template code-generator
```

### Render Prompts
```bash
python3 scripts/prompt_renderer.py --input prompts.json --output rendered.md
```

### Start Web Interface
```bash
python3 web/prompt_web_interface.py --port 8080
```

### Test Renderer
```bash
python3 scripts/test_prompt_renderer.py
```

## Configuration

Prompt configurations are stored in JSON format:

```json
{
  "prompts": [
    {
      "name": "code-generator",
      "description": "Generate code from specifications",
      "template": "code_template.md",
      "parameters": {
        "language": "python",
        "framework": "flask"
      }
    }
  ]
}
```

## Features

- Multi-format prompt rendering (Markdown, JSON, XML)
- Template-based prompt generation
- Web interface for interactive editing
- Validation and testing framework
- Integration with MCP servers

## Dependencies

- Python 3.8+
- Flask (for web interface)
- Jinja2 (for templating)
- JSON/YAML libraries