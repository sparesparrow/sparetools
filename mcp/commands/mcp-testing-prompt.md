# mcp-testing-prompt

Generate testing prompts for test case generation and quality assurance using MCP prompts

## Usage

```bash
mcp-prompts apply_prompt mcp-testing-prompt \
  --test_type "unit tests" \
  --code_to_test "Function or component to test" \
  --testing_framework "pytest" \
  --language "Python" \
  --coverage_target 90 \
  --include_edge_cases true \
  --include_performance_tests false
```

## Description

Uses the MCP prompts system to generate comprehensive testing prompts for test case generation and quality assurance. The template supports various testing frameworks and includes coverage targets and edge case considerations.

## Parameters

- **test_type**: Type of tests (unit tests, integration tests, e2e tests, etc.)
- **code_to_test**: Code or component to test
- **testing_framework**: Testing framework (pytest, Jest, JUnit, etc.)
- **language**: Programming language (Python, JavaScript, Java, etc.)
- **coverage_target**: Target code coverage percentage (0-100)
- **include_edge_cases**: Whether to include edge case tests (true/false)
- **include_performance_tests**: Whether to include performance tests (true/false)

## Examples

### Unit Tests
```bash
mcp-prompts apply_prompt mcp-testing-prompt \
  --test_type "unit tests" \
  --code_to_test "Authentication service" \
  --testing_framework "pytest" \
  --language "Python" \
  --coverage_target 95 \
  --include_edge_cases true \
  --include_performance_tests false
```

### Integration Tests
```bash
mcp-prompts apply_prompt mcp-testing-prompt \
  --test_type "integration tests" \
  --code_to_test "API endpoints" \
  --testing_framework "pytest" \
  --language "Python" \
  --coverage_target 80 \
  --include_edge_cases true \
  --include_performance_tests true
```

### End-to-End Tests
```bash
mcp-prompts apply_prompt mcp-testing-prompt \
  --test_type "e2e tests" \
  --code_to_test "User registration flow" \
  --testing_framework "Selenium" \
  --language "Python" \
  --coverage_target 70 \
  --include_edge_cases true \
  --include_performance_tests false
```

## Related Commands

- `mcp-code-generator`: Code generation
- `mcp-analysis-prompt`: Code analysis
- `mcp-debugging-prompt`: Debugging assistance