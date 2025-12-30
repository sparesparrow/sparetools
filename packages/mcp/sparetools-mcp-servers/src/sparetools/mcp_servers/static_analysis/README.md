# Static Code Analysis MCP Server

MCP server for running, installing, checking progress, and analyzing results of static code analysis tools.

## Supported Tools

- **cppcheck**: Static analysis for C/C++
- **valgrind**: Memory debugging and profiling
- **gdb**: GNU Debugger
- **strace**: System call tracer (Linux)
- **uiautomator**: Android UI automation

## Installation

```bash
# Install via Conan
conan install sparetools-mcp-servers/1.0.1 --build=missing

# Or install tools directly
# Linux
sudo apt-get install cppcheck valgrind gdb strace
pip install uiautomator2

# macOS
brew install cppcheck valgrind gdb strace
pip install uiautomator2
```

## Usage

### Cursor IDE Configuration

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "static-analysis": {
      "command": "python",
      "args": [
        "-m",
        "sparetools.mcp_servers.static_analysis.static_analysis_mcp_server"
      ]
    }
  }
}
```

## Available Tools

### Tool Management
- `list_available_tools` - List all supported tools and installation status
- `check_tool_status` - Check if a specific tool is installed
- `install_analysis_tool` - Install a tool on the system

### Analysis Execution
- `run_cppcheck` - Run cppcheck on C/C++ code
- `run_valgrind` - Run valgrind memory analysis
- `run_gdb` - Run GDB debugger
- `run_strace` - Run strace system call tracer
- `run_uiautomator` - Run Android UI automation

### Progress & Results
- `get_analysis_progress` - Check progress of running analysis
- `list_analysis_sessions` - List all analysis sessions
- `analyze_analysis_results` - Analyze and summarize results
- `get_analysis_log` - Get log output from analysis
- `stop_analysis` - Stop a running analysis

## Examples

### Run cppcheck
```python
# Run cppcheck on a directory
run_cppcheck(
    target_path="/path/to/cpp/project",
    enable_all=True
)
```

### Run valgrind
```python
# Run valgrind on an executable
run_valgrind(
    executable_path="/path/to/program",
    leak_check=True
)
```

### Check Progress
```python
# Check analysis progress
get_analysis_progress(session_id="<session-id>")
```

### Analyze Results
```python
# Analyze completed analysis
analyze_analysis_results(session_id="<session-id>")
```

## Architecture

Follows ORCHESTRATOR → EXECUTOR → VALIDATOR pattern:

- **ORCHESTRATOR**: Coordinates analysis workflows and session management
- **EXECUTOR**: Runs analysis tools and captures output
- **VALIDATOR**: Analyzes results and generates reports
