# SpareTools MCP Core

Core library providing reusable MCP (Model Context Protocol) utilities for templates, prompts, diagrams, device detection, and deployment orchestration.

## Features

- **Templates System**: Jinja2-based template engine with custom filters
- **Prompts Management**: Prompt template loading, rendering, and caching
- **Diagrams Generation**: Mermaid diagram generation (flowcharts, class diagrams, sequences)
- **Device Detection**: Pluggable device detection for embedded systems (ESP32, Arduino)
- **Deployment Orchestration**: Conan profile management and multi-device deployment
- **MCP Server Base**: Base classes for building MCP servers with composition support

## Installation

### Via Conan

```bash
conan install sparetools-mcp-core/1.0.0@
```

### Via pip

```bash
pip install sparetools-mcp-core
```

## Usage

### Templates

```python
from sparetools.mcp_core.templates import TemplateRenderer

renderer = TemplateRenderer(template_dir="./templates")
result = renderer.render_string("Hello {{ name | pascalcase }}", {"name": "world"})
```

### Device Detection

```python
from sparetools.mcp_core.devices import DeviceDetector
from sparetools.mcp_core.devices.identifiers import ESP32_S3_CDC

detector = DeviceDetector()
detector.add_identifier(ESP32_S3_CDC)

devices = detector.detect_all()
for device in devices:
    print(f"Found: {device.name} at {device.port}")
```

### Mermaid Diagrams

```python
from sparetools.mcp_core.diagrams import MermaidGenerator

generator = MermaidGenerator()
flowchart = generator.generate_flowchart(
    nodes=[("A", "Start"), ("B", "Process"), ("C", "End")],
    edges=[("A", "B", ""), ("B", "C", "")],
)
print(flowchart)
```

### MCP Server Composition

```python
from sparetools.mcp_core.server import ServerComposer

composer = ServerComposer("my-unified-server")
composer.add_tool("hello", lambda name: f"Hello {name}", description="Greet someone")

app = composer.get_server()
app.run()
```

## Components

| Module | Description |
|--------|-------------|
| `templates` | Template types, base classes, and Jinja2 renderer |
| `prompts` | Prompt template management and rendering |
| `diagrams` | Mermaid diagram generation utilities |
| `devices` | Device detection and serial communication |
| `deployment` | Deployment orchestration and Conan profiles |
| `server` | Base MCP server classes and composition |

## License

Apache-2.0
