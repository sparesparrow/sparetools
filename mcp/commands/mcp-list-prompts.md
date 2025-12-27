# mcp-list-prompts

List all available MCP prompts and their usage

## Usage

```bash
mcp-prompts list_prompts
```

## Description

Lists all available MCP prompts with their descriptions, categories, and usage examples. This command helps you discover what prompts are available and how to use them.

## Available Prompts

### Code Generation
- **mcp-code-generator**: Generate code based on requirements and specifications
  - Categories: code_generation
  - Variables: code_requirements, language, framework, complexity, style_guide, include_tests, include_docs

### Analysis
- **mcp-analysis-prompt**: Generate analysis prompts for code review, debugging, or system analysis
  - Categories: analysis
  - Variables: analysis_type, target_code, focus_areas, context, urgency, include_recommendations

### Documentation
- **mcp-documentation-prompt**: Generate documentation prompts for technical writing
  - Categories: documentation
  - Variables: doc_type, project_name, target_audience, scope, format, include_examples, include_diagrams

### Testing
- **mcp-testing-prompt**: Generate testing prompts for test case generation and quality assurance
  - Categories: testing
  - Variables: test_type, code_to_test, testing_framework, language, coverage_target, include_edge_cases, include_performance_tests

### Debugging
- **mcp-debugging-prompt**: Generate debugging prompts for troubleshooting and issue resolution
  - Categories: debugging
  - Variables: issue_description, error_message, environment, language, urgency, include_logs, include_solutions

### Architecture
- **mcp-architecture-prompt**: Generate architecture design prompts for system design and planning
  - Categories: architecture
  - Variables: system_type, requirements, scale, technology_stack, constraints, include_diagrams, include_security

## Quick Reference

```bash
# List all prompts
mcp-prompts list_prompts

# Apply a specific prompt
mcp-prompts apply_prompt <prompt_name> --param1 value1 --param2 value2

# Create a new template
mcp-prompts create_template <template_name> --description "Description" --content "Template content"

# Apply a template
mcp-prompts apply_template <template_name> --param1 value1 --param2 value2
```

## Related Commands

- `mcp-code-generator`: Code generation
- `mcp-analysis-prompt`: Code analysis
- `mcp-documentation-prompt`: Documentation generation
- `mcp-testing-prompt`: Test generation
- `mcp-debugging-prompt`: Debugging assistance
- `mcp-architecture-prompt`: Architecture design