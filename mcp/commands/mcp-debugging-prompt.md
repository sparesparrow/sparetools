# mcp-debugging-prompt

Generate debugging prompts for troubleshooting and issue resolution using MCP prompts

## Usage

```bash
mcp-prompts apply_prompt mcp-debugging-prompt \
  --issue_description "Description of the problem" \
  --error_message "Error message or symptoms" \
  --environment "development" \
  --language "Python" \
  --urgency "high" \
  --include_logs true \
  --include_solutions true
```

## Description

Uses the MCP prompts system to generate systematic debugging prompts for troubleshooting and issue resolution. The template provides a structured approach to identify and resolve problems with comprehensive analysis and solution recommendations.

## Parameters

- **issue_description**: Description of the problem
- **error_message**: Error message or symptoms
- **environment**: Environment (development, staging, production)
- **language**: Programming language (Python, JavaScript, Java, etc.)
- **urgency**: Urgency level (low, medium, high, critical)
- **include_logs**: Whether to include log analysis (true/false)
- **include_solutions**: Whether to include solution recommendations (true/false)

## Examples

### High Priority Bug
```bash
mcp-prompts apply_prompt mcp-debugging-prompt \
  --issue_description "API returning 500 errors" \
  --error_message "Internal Server Error: Database connection failed" \
  --environment "production" \
  --language "Python" \
  --urgency "critical" \
  --include_logs true \
  --include_solutions true
```

### Performance Issue
```bash
mcp-prompts apply_prompt mcp-debugging-prompt \
  --issue_description "Slow response times" \
  --error_message "API responses taking 10+ seconds" \
  --environment "production" \
  --language "Python" \
  --urgency "high" \
  --include_logs true \
  --include_solutions true
```

### Development Issue
```bash
mcp-prompts apply_prompt mcp-debugging-prompt \
  --issue_description "Tests failing locally" \
  --error_message "AssertionError: Expected 5, got 3" \
  --environment "development" \
  --language "Python" \
  --urgency "medium" \
  --include_logs false \
  --include_solutions true
```

## Related Commands

- `mcp-analysis-prompt`: Code analysis
- `mcp-testing-prompt`: Test generation
- `mcp-code-generator`: Code generation