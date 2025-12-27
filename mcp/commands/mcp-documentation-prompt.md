# mcp-documentation-prompt

Generate documentation prompts for technical writing and documentation using MCP prompts

## Usage

```bash
mcp-prompts apply_prompt mcp-documentation-prompt \
  --doc_type "API documentation" \
  --project_name "My Project" \
  --target_audience "developers" \
  --scope "complete system" \
  --format "markdown" \
  --include_examples true \
  --include_diagrams false
```

## Description

Uses the MCP prompts system to generate comprehensive documentation prompts for technical writing. The template supports various documentation types and formats with customizable content structure.

## Parameters

- **doc_type**: Type of documentation (API documentation, User guide, Technical specs, etc.)
- **project_name**: Name of the project
- **target_audience**: Target audience (developers, users, administrators, etc.)
- **scope**: Documentation scope (complete system, specific module, etc.)
- **format**: Output format (markdown, HTML, PDF, etc.)
- **include_examples**: Whether to include examples (true/false)
- **include_diagrams**: Whether to include diagrams (true/false)

## Examples

### API Documentation
```bash
mcp-prompts apply_prompt mcp-documentation-prompt \
  --doc_type "API documentation" \
  --project_name "User Management API" \
  --target_audience "developers" \
  --scope "complete system" \
  --format "markdown" \
  --include_examples true \
  --include_diagrams true
```

### User Guide
```bash
mcp-prompts apply_prompt mcp-documentation-prompt \
  --doc_type "User guide" \
  --project_name "Mobile App" \
  --target_audience "end users" \
  --scope "complete system" \
  --format "markdown" \
  --include_examples true \
  --include_diagrams false
```

### Technical Specifications
```bash
mcp-prompts apply_prompt mcp-documentation-prompt \
  --doc_type "Technical specifications" \
  --project_name "Database Schema" \
  --target_audience "developers" \
  --scope "database module" \
  --format "markdown" \
  --include_examples true \
  --include_diagrams true
```

## Related Commands

- `mcp-code-generator`: Code generation
- `mcp-architecture-prompt`: Architecture design
- `mcp-testing-prompt`: Test documentation