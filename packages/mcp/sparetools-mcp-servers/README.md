# SpareTools MCP Servers Package

A comprehensive collection of MCP (Model Context Protocol) servers for development workflows, packaged for easy installation and distribution via Conan and Cloudsmith.

## 🚀 Overview

This package provides five specialized MCP servers designed to enhance development workflows:

- **Enhanced Static Analysis**: Comprehensive development tooling with MCP-Prompts integration
- **ESP32 Serial Monitor**: Monitor and interact with ESP32 devices
- **Android Dev Tools**: Build, deploy, and debug Android applications
- **Conan & Cloudsmith**: Package management and artifact publishing
- **Repo Cleanup**: Repository maintenance and cleanup operations

## 📦 Installation

### Via Conan (Recommended)

```bash
# Install the MCP servers package
conan install sparetools-mcp-servers/1.0.0@sparesparrow/stable

# Or install the full SpareTools monorepo (includes MCP servers)
conan install sparetools-monorepo/1.0.0@sparesparrow/stable
```

### Via Cloudsmith

```bash
# Add SpareSparrow Conan repository
conan remote add sparesparrow-conan https://cloudsmith.io/~sparesparrow-conan/repos/sparetools/

# Install the package
conan install sparetools-mcp-servers/1.0.0@sparesparrow/stable
```

## 🛠️ Usage

### Enhanced Static Analysis Server

The Enhanced Static Analysis MCP server provides a comprehensive development tooling oracle that integrates with MCP-Prompts for intelligent analysis interpretation.

#### Features

- **Tool Adapters**: Unified interface for 10+ development tools (Cppcheck, Clang-Tidy, Valgrind, GDB, pytest, etc.)
- **Workflow Orchestration**: Multi-tool analysis sequences with dependency management
- **MCP-Prompts Integration**: AI-powered result interpretation and recommendations
- **Context-Aware Analysis**: Project-specific configurations and quality gates
- **Comprehensive Reporting**: Multiple output formats (JSON, Markdown, HTML)

#### MCP Configuration

Add to your Cursor MCP configuration (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "sparetools-mcp-static-analysis": {
      "command": "python",
      "args": ["-m", "sparetools.mcp_servers.static_analysis.static_analysis_mcp_server"],
      "env": {
        "PYTHONPATH": "/path/to/sparetools-mcp-servers/src",
        "STATIC_ANALYSIS_MODE": "development",
        "MCP_PROMPTS_SERVER_URL": "http://localhost:3000",
        "STATIC_ANALYSIS_CONFIG_FILE": "/path/to/config/default_config.yaml"
      }
    }
  }
}
```

#### Available Tools

The server provides the following MCP tools:

**Discovery & Management:**
- `discover_tools` - Comprehensive tool discovery and capabilities
- `analyze_static` - Unified static analysis dispatcher
- `configure_tool` - Tool configuration management
- `get_recommendations` - AI-powered workflow suggestions

**Testing Framework Integration:**
- `run_test_suite` - Unified test execution (pytest, gtest, jest)

**Workflow Orchestration:**
- `create_workflow` - Define multi-step analysis workflows
- `execute_workflow` - Run predefined analysis sequences
- `workflow_status` - Track progress of complex analyses
- `list_workflows` - List all available workflows
- `cancel_workflow` - Cancel running workflows

**Result Interpretation:**
- `analyze_results_with_context` - AI-powered result interpretation
- `generate_report` - Create comprehensive analysis reports
- `compare_results` - Compare trends across analysis runs

**Legacy Tools:**
- `list_available_tools` - List available analysis tools
- `check_tool_status` - Check tool installation status
- `install_analysis_tool` - Install analysis tools
- `run_cppcheck`, `run_valgrind`, `run_gdb`, etc. - Individual tool runners
- `get_analysis_progress` - Check analysis progress
- `analyze_analysis_results` - Analyze completed results

#### Example Usage

```python
# Discover available tools
discover_tools()

# Run comprehensive analysis
analyze_static("cppcheck", "/path/to/project")

# Create and execute workflow
create_workflow("cpp_analysis", [
    {"tool_name": "cppcheck", "target_path": "/src", "arguments": {"enable_checks": ["all"]}},
    {"tool_name": "valgrind", "target_path": "./build/app", "arguments": {"leak_check": True}}
])
execute_workflow("cpp_analysis")

# Generate intelligent reports
analyze_results_with_context(["session_id_1", "session_id_2"], {"project_type": "cpp"})
generate_report(["session_id_1"], "markdown")
```

#### Configuration

The server supports comprehensive YAML configuration:

```yaml
# default_config.yaml
server:
  name: "sparetools-mcp-static-analysis"
  timeouts:
    analysis: 3600
  limits:
    max_concurrent_sessions: 5

mcp_prompts:
  enabled: true
  server_url: "http://localhost:3000"

tool_registry:
  tools:
    cppcheck:
      enabled: true
      timeout: 600
    pytest:
      enabled: true
      timeout: 600
```

### MCP Server Configuration

After installation, add the MCP servers to your Cursor configuration (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "sparetools-esp32": {
      "command": "sparetools-mcp-esp32",
      "env": {
        "ESP32_LOG_LEVEL": "INFO",
        "ESP32_LOG_DIR": "/tmp/esp32_logs",
        "ESP32_SESSION_STORAGE": "/tmp/esp32_sessions.json"
      }
    },
    "sparetools-android": {
      "command": "sparetools-mcp-android",
      "env": {
        "ANDROID_LOG_LEVEL": "INFO",
        "ANDROID_LOG_DIR": "/tmp/android_logs",
        "ANDROID_SESSION_STORAGE": "/tmp/android_sessions.json"
      }
    },
    "sparetools-conan": {
      "command": "sparetools-mcp-conan",
      "env": {
        "CONAN_LOG_LEVEL": "INFO",
        "CONAN_LOG_DIR": "/tmp/conan_logs",
        "CONAN_SESSION_STORAGE": "/tmp/conan_sessions.json",
        "CLOUDSMITH_API_KEY": "${CLOUDSMITH_API_KEY}",
        "CLOUDSMITH_ORG": "${CLOUDSMITH_ORG}"
      }
    },
    "sparetools-repo": {
      "command": "sparetools-mcp-repo",
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Available MCP Tools

#### ESP32 Serial Monitor (`sparetools-esp32`)

| Tool | Description | Parameters |
|------|-------------|------------|
| `start_serial_monitor` | Start monitoring ESP32 serial output | port, baud_rate, terminal |
| `stop_serial_monitor` | Stop a serial monitoring session | session_id, timeout |
| `kill_serial_monitor` | Force kill a serial monitoring session | session_id |
| `list_serial_sessions` | List all active serial sessions | - |
| `get_serial_status` | Get detailed status of a session | session_id |
| `detect_esp32_ports` | Detect available ESP32 serial ports | - |
| `read_serial_output` | Read serial output from log file | session_id, lines, tail |
| `send_serial_command` | Send command to serial device | session_id, command |

#### Android Dev Tools (`sparetools-android`)

| Tool | Description | Parameters |
|------|-------------|------------|
| `build_android_apk` | Build Android APK with Gradle | project_path, build_type, terminal |
| `deploy_android_apk` | Deploy APK to Android device | apk_path, device_id, terminal |
| `run_android_tests` | Execute Android unit/instrumentation tests | project_path, test_type, device_id, terminal |
| `android_device_info` | Get connected Android device information | - |
| `android_logcat` | Start Android logcat monitoring | device_id, filter_spec, terminal |
| `clear_android_data` | Clear app data on Android device | package_name, device_id |
| `uninstall_android_app` | Uninstall app from Android device | package_name, device_id |

#### Conan & Cloudsmith (`sparetools-conan`)

| Tool | Description | Parameters |
|------|-------------|------------|
| `validate_conanfile` | Validate conanfile.py syntax and dependencies | conanfile_path |
| `create_conan_package` | Create Conan package from conanfile | conanfile_path, terminal |
| `upload_conan_package` | Upload package to Conan remote | package_reference, remote_name, terminal |
| `search_conan_packages` | Search available Conan packages | query, remote_name |
| `install_conan_dependencies` | Install dependencies from conanfile | conanfile_path, install_folder, terminal |
| `conan_info` | Get package information | package_reference, remote_name |
| `setup_cloudsmith_remote` | Configure Cloudsmith remote | remote_name, repository |
| `upload_to_cloudsmith` | Upload package to Cloudsmith | package_reference, remote_name |
| `list_cloudsmith_packages` | List packages in Cloudsmith repository | repository |

#### Repo Cleanup (`sparetools-repo`)

| Tool | Description | Parameters |
|------|-------------|------------|
| `repo_cleanup_scan` | Scan repository for cleanup opportunities | repository_path, scan_mode |
| `repo_cleanup_list_large_files` | Find files over specified size threshold | repository_path, min_size_mb |
| `repo_cleanup_git_status` | Get Git repository status | repository_path |
| `repo_cleanup_disk_usage` | Analyze repository disk usage | repository_path |

## 🔧 Environment Variables

### ESP32 Serial Monitor
- `ESP32_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `ESP32_LOG_DIR`: Directory for log files (default: ~/esp32_logs)
- `ESP32_SESSION_STORAGE`: Path for session persistence (default: ~/.mcp/esp32_sessions.json)

### Android Dev Tools
- `ANDROID_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `ANDROID_LOG_DIR`: Directory for log files (default: ~/android_logs)
- `ANDROID_SESSION_STORAGE`: Path for session persistence (default: ~/.mcp/android_sessions.json)

### Conan & Cloudsmith
- `CONAN_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `CONAN_LOG_DIR`: Directory for log files (default: ~/conan_logs)
- `CONAN_SESSION_STORAGE`: Path for session persistence (default: ~/.mcp/conan_sessions.json)
- `CLOUDSMITH_API_KEY`: Cloudsmith API key for publishing
- `CLOUDSMITH_ORG`: Cloudsmith organization name

### Repo Cleanup
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## 📚 Examples

### ESP32 Development Workflow

```bash
# Start monitoring ESP32 device
cursor-agent --print "use start_serial_monitor tool with port /dev/ttyUSB0 and baud_rate 115200"

# Check device status
cursor-agent --print "use get_serial_status tool with session_id from previous command"
```

### Android Development Workflow

```bash
# List connected Android devices
cursor-agent --print "use android_device_info tool"

# Build and deploy Android app
cursor-agent --print "use build_android_apk tool with project_path /path/to/android/project and build_type debug"
cursor-agent --print "use deploy_android_apk tool with apk_path /path/to/app-debug.apk"
```

### Package Management Workflow

```bash
# Validate and create Conan package
cursor-agent --print "use validate_conanfile tool with conanfile_path conanfile.py"
cursor-agent --print "use create_conan_package tool with conanfile_path conanfile.py"

# Upload to Cloudsmith
cursor-agent --print "use setup_cloudsmith_remote tool with remote_name myremote and repository my-repo"
cursor-agent --print "use upload_to_cloudsmith tool with package_reference mylib/1.0@user/stable and remote_name myremote"
```

### Repository Maintenance

```bash
# Scan repository for cleanup opportunities
cursor-agent --print "use repo_cleanup_scan tool with repository_path /path/to/repo and scan_mode thorough"

# Find large files
cursor-agent --print "use repo_cleanup_list_large_files tool with repository_path /path/to/repo and min_size_mb 50"
```

## 🏗️ Architecture

### Package Structure

```
sparetools-mcp-servers/
├── src/sparetools/mcp_servers/
│   ├── esp32_serial_monitor/     # ESP32 serial monitoring server
│   ├── android_dev_tools/        # Android development tools server
│   ├── conan_cloudsmith/         # Conan & Cloudsmith server
│   └── repo_cleanup/             # Repository cleanup server
├── scripts/                      # Launch scripts for each server
├── config/                       # Sample MCP configuration
└── docs/                        # Documentation
```

### Dependencies

- **mcp>=0.1.0**: Model Context Protocol framework
- **fastmcp>=2.0.0**: FastMCP implementation
- **GitPython>=3.1.40**: Git operations for repo cleanup
- **aiofiles>=23.0.0**: Asynchronous file operations
- **rich>=13.0.0**: Enhanced terminal output

## 🔐 Security Considerations

- MCP servers run with the same permissions as the user
- Cloudsmith API keys should be stored securely
- Android ADB commands require proper device permissions
- Serial port access may require elevated privileges

## 🐛 Troubleshooting

### Common Issues

1. **MCP Server Not Found**: Ensure the package is properly installed and scripts are in PATH
2. **Permission Denied**: Check device permissions for Android ADB and serial ports
3. **Cloudsmith Upload Failed**: Verify API key and organization settings
4. **Conan Commands Failed**: Ensure Conan is installed and configured

### Debug Mode

Enable debug logging by setting the appropriate environment variable:

```bash
export ESP32_LOG_LEVEL=DEBUG
export ANDROID_LOG_LEVEL=DEBUG
export CONAN_LOG_LEVEL=DEBUG
export LOG_LEVEL=DEBUG
```

### Log Locations

- ESP32 logs: `~/esp32_logs/` or `$ESP32_LOG_DIR`
- Android logs: `~/android_logs/` or `$ANDROID_LOG_DIR`
- Conan logs: `~/conan_logs/` or `$CONAN_LOG_DIR`

## 🤝 Contributing

This package is part of the SpareTools monorepo. Contributions should be made to the main repository:

1. Fork the [SpareTools repository](https://github.com/sparesparrow/sparetools)
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This package is licensed under the Apache License 2.0. See the LICENSE file for details.

## 🔗 Related Packages

- **sparetools-py**: Python utilities and test harness
- **sparetools-embedded**: Embedded development tools
- **sparetools-protocols**: Protocol buffer schemas
- **sparetools-monorepo**: Meta-package including all SpareTools components

## 📞 Support

For issues and questions:

- GitHub Issues: [SpareTools MCP Servers](https://github.com/sparesparrow/sparetools/issues)
- Documentation: [SpareTools Docs](https://sparetools.readthedocs.io/)
- Discord: [SpareTools Community](https://discord.gg/sparesparrow)