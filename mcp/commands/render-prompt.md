# renderPrompt

Render a prompt template with variables

## Usage

```json
{
  "template_name": "template-name-here",
  "variables": {
    "key": "value"
  }
}
```

## Description

Renders a prompt template by substituting variables into the template content. The template must exist in the MCP prompt database.

## Parameters

- `template_name` (string, required): Name of the template to render
- `variables` (object, optional): Variables to substitute in the template

## Examples

```json
{
  "template_name": "mcp-code-generator",
  "variables": {
    "code_requirements": "Create a REST API with authentication",
    "language": "Python"
  }
}
```

## Related Commands

- `generateDiagram`: Create visual diagrams from templates
- `generateProject`: Generate complete project structures
- `generateComponent`: Generate individual components