# generateDiagram

Generate a Mermaid diagram from a template

## Usage

```json
{
  "template_name": "flowchart-template",
  "variables": {
    "title": "My Process",
    "steps": ["Start", "Process", "End"]
  },
  "output_format": "svg"
}
```

## Description

Creates visual diagrams using Mermaid syntax from predefined templates. Supports flowcharts, sequence diagrams, class diagrams, and more.

## Parameters

- `template_name` (string, required): Name of the diagram template
- `variables` (object, optional): Variables for diagram generation
- `output_format` (string, optional): Output format - "svg", "png", or "pdf" (default: "svg")

## Examples

```json
{
  "template_name": "mermaid-class-diagram-generator",
  "variables": {
    "class_name": "UserService",
    "methods": ["login()", "logout()", "getProfile()"]
  },
  "output_format": "png"
}
```

## Supported Diagram Types

- Flowcharts
- Sequence diagrams
- Class diagrams
- State diagrams
- Gantt charts
- Pie charts
- Mind maps

## Related Commands

- `renderPrompt`: Text-based template rendering
- `generateProject`: Generate project structures
- `generateComponent`: Generate individual components