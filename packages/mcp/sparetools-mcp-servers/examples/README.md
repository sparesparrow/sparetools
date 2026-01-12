# Enhanced Static Analysis MCP Server Examples

This directory contains example configurations, workflows, and usage patterns for the Enhanced Static Analysis MCP server.

## 📁 Directory Structure

```
examples/
├── workflows/           # Pre-defined analysis workflows
│   ├── cpp_project_workflow.json
│   └── python_project_workflow.json
└── README.md           # This file
```

## 🔄 Example Workflows

### C++ Project Analysis Workflow

**File**: `workflows/cpp_project_workflow.json`

A comprehensive workflow for C++ projects that includes:
- Static analysis with Cppcheck
- Memory leak detection with Valgrind
- Unit testing with GTest
- Performance profiling with Callgrind

**Usage**:
```bash
# Create the workflow
create_workflow("cpp_analysis", @workflows/cpp_project_workflow.json)

# Execute the workflow
execute_workflow("cpp_analysis")

# Monitor progress
workflow_status("cpp_analysis")
```

### Python Project Analysis Workflow

**File**: `workflows/python_project_workflow.json`

A complete testing and analysis pipeline for Python projects featuring:
- Dependency validation
- Unit test execution with coverage
- Integration testing
- Performance benchmarking

**Usage**:
```bash
# Create and run the workflow
create_workflow("python_analysis", @workflows/python_project_workflow.json)
execute_workflow("python_analysis")
```

## 🚀 Quick Start Examples

### Basic Tool Discovery
```python
# Discover all available tools and their capabilities
discover_tools()
```

### Project Analysis Recommendations
```python
# Get AI-powered recommendations for your project
get_recommendations("/path/to/your/project")
```

### Individual Tool Analysis
```python
# Run specific analysis tools
analyze_static("cppcheck", "/src", {"enable_checks": ["all"]})
analyze_static("pytest", ".", {"coverage": True})
```

### Configuration Management
```python
# Get project-specific tool configurations
configure_tool("pytest", "web", "javascript")
configure_tool("cppcheck", "library", "c++")
```

### Result Analysis and Reporting
```python
# Analyze results with AI interpretation
analyze_results_with_context(["session_1", "session_2"], {
    "project_type": "web",
    "language": "typescript"
})

# Generate comprehensive reports
generate_report(["session_1", "session_2"], "markdown")
generate_report(["session_1"], "html", True)
```

### Result Comparison
```python
# Compare analysis results across runs
compare_results(["baseline_session"], ["current_session"], "trends")
compare_results(["run_1", "run_2"], ["run_3", "run_4"], "improvements")
```

## ⚙️ Configuration Examples

### Environment Variables
```bash
# MCP-Prompts integration
export MCP_PROMPTS_SERVER_URL="http://localhost:3000"
export MCP_PROMPTS_API_KEY="your-api-key"

# Server configuration
export STATIC_ANALYSIS_MODE="development"
export STATIC_ANALYSIS_MAX_WORKERS="4"
export STATIC_ANALYSIS_TIMEOUT="3600"

# Tool-specific settings
export CPPCHECK_TIMEOUT="600"
export PYTEST_PARALLEL="4"
```

### Custom Workflow Creation
```json
{
  "name": "Custom Security Analysis",
  "description": "Security-focused analysis workflow",
  "steps": [
    {
      "step_id": "dependency_scan",
      "tool_name": "docker",
      "target_path": ".",
      "arguments": {"subcommand": "scan", "image": "myapp:latest"}
    },
    {
      "step_id": "static_security",
      "tool_name": "cppcheck",
      "target_path": "src",
      "arguments": {
        "enable_checks": ["warning", "style"],
        "suppress_rules": ["unusedFunction"]
      },
      "dependencies": ["dependency_scan"]
    }
  ]
}
```

## 🔧 Advanced Usage Patterns

### Conditional Workflows
Use conditions to create dynamic analysis flows:

```json
{
  "step_id": "advanced_analysis",
  "tool_name": "clang_tidy",
  "condition": "previous_step.result.issues.length < 5",
  "dependencies": ["basic_checks"]
}
```

### Parallel Execution
Steps without dependencies run in parallel automatically.

### Error Handling
Configure retry logic for unreliable tools:

```json
{
  "step_id": "flaky_test",
  "tool_name": "integration_test",
  "max_retries": 3,
  "retry_count": 0
}
```

## 📊 Integration with CI/CD

### GitHub Actions Example
```yaml
name: Comprehensive Analysis
on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Analysis Workflow
        run: |
          # Configure MCP server
          echo "Starting analysis workflow..."

          # This would integrate with your MCP client
          # to execute comprehensive analysis workflows
```

### Docker Integration
```dockerfile
FROM sparetools-mcp-static-analysis:latest

# Copy your project
COPY . /project

# Run analysis workflow
RUN analyze_static cppcheck /project/src && \
    run_test_suite pytest /project && \
    generate_report session_ids markdown
```

## 📈 Monitoring and Metrics

The server provides comprehensive monitoring:

- **Health Checks**: `/health` endpoint
- **Metrics**: `/metrics` endpoint
- **Workflow Progress**: Real-time status updates
- **Performance Monitoring**: Execution times and resource usage

## 🆘 Troubleshooting

### Common Issues

1. **Tool Not Found**: Ensure tools are installed and in PATH
2. **MCP-Prompts Unavailable**: Falls back to basic interpretation
3. **Timeout Errors**: Increase timeout values in configuration
4. **Memory Issues**: Reduce concurrent operations or increase limits

### Debug Mode
Enable debug logging:
```bash
export STATIC_ANALYSIS_LOG_LEVEL=DEBUG
export STATIC_ANALYSIS_DEBUG=true
```

### Performance Tuning
```yaml
performance:
  caching_enabled: true
  max_workers: 2
  timeout_buffer: 30
```