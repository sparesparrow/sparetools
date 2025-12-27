# mcp-code-generator

Generate code based on requirements and specifications using MCP prompts

## Usage

```bash
mcp-prompts apply_prompt mcp-code-generator \
  --code_requirements "Create a basic function" \
  --language "Python" \
  --framework "None" \
  --complexity "simple" \
  --style_guide "PEP 8" \
  --include_tests false \
  --include_docs false
```

## Description

Uses the MCP prompts system to generate code based on specific requirements. The prompt template includes support for multiple programming languages, frameworks, and complexity levels.

## Parameters

- **code_requirements**: Description of what code needs to be created
- **language**: Programming language (Python, JavaScript, Java, etc.)
- **framework**: Framework to use (None, React, Django, etc.)
- **complexity**: Complexity level (simple, medium, complex)
- **style_guide**: Style guide to follow (PEP 8, ESLint, etc.)
- **include_tests**: Whether to include tests (true/false)
- **include_docs**: Whether to include documentation (true/false)

## Examples

### Generate Python API
```bash
mcp-prompts apply_prompt mcp-code-generator \
  --code_requirements "Create a REST API for user management" \
  --language "Python" \
  --framework "Flask" \
  --complexity "medium" \
  --style_guide "PEP 8" \
  --include_tests true \
  --include_docs true
```

### Generate JavaScript Component
```bash
mcp-prompts apply_prompt mcp-code-generator \
  --code_requirements "Create a React component for data visualization" \
  --language "JavaScript" \
  --framework "React" \
  --complexity "complex" \
  --style_guide "ESLint" \
  --include_tests true \
  --include_docs false
```

## Related Commands

- `mcp-analysis-prompt`: Code analysis and review
- `mcp-testing-prompt`: Test case generation
- `mcp-documentation-prompt`: Documentation generation