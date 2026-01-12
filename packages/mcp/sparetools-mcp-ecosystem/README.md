# SpareTools MCP Ecosystem

A comprehensive Model Context Protocol (MCP) ecosystem that integrates AI-assisted development workflows across the entire SpareTools platform.

## 🚀 Overview

The SpareTools MCP Ecosystem provides intelligent AI assistance for:

- **ESP32 Development**: Serial monitoring, firmware flashing, debugging
- **Android Development**: APK building, deployment, testing, debugging
- **Conan Package Management**: Dependency resolution, Cloudsmith publishing
- **Repository Maintenance**: Cleanup, optimization, health monitoring
- **Project Orchestration**: Template management, workflow automation
- **Cross-Platform Development**: Unified workflows for Linux, macOS, Windows

## 🎯 Key Features

### 🤖 AI-Assisted Workflows
- **Context-Aware Prompts**: Automatically suggests relevant workflows based on project context
- **Intelligent Tool Integration**: Direct access to development tools with AI guidance
- **Workflow Automation**: Guided multi-step processes for complex development tasks

### 🛠️ Integrated Tool Suite
- **28 MCP Tools** across 4 specialized servers
- **Project Templates** for quick project setup
- **Prompt Management** with versioning and categorization
- **Mermaid Diagram Generation** for documentation

### 🌐 Cross-Platform Support
- **Linux**: Native development environment
- **macOS**: Homebrew integration
- **Windows**: MSYS2/MinGW compatibility
- **Embedded**: ESP32, Arduino, Raspberry Pi support

## 📦 Installation

### Via Conan (Recommended)

```bash
# Install the complete MCP ecosystem
conan install sparetools-mcp-ecosystem/1.0.0@sparesparrow/stable
```

### Via Cloudsmith

```bash
# Add SpareSparrow Conan repository
conan remote add sparesparrow-conan https://cloudsmith.io/~sparesparrow-conan/repos/sparetools/

# Install the ecosystem
conan install sparetools-mcp-ecosystem/1.0.0@sparesparrow/stable
```

## 🛠️ Usage

### Quick Start

```bash
# Install the ecosystem
conan install sparetools-mcp-ecosystem/1.0.0@sparesparrow/stable

# Run setup
sparetools-mcp-ecosystem setup

# Configure Cursor (see configuration section below)
```

### Available Components

```bash
# Main ecosystem launcher
sparetools-mcp-ecosystem --help

# Individual components
sparetools-mcp-ecosystem mcp-prompts     # AI prompts server
sparetools-mcp-ecosystem mcp-servers     # Development tool servers
sparetools-mcp-ecosystem orchestrator    # Project orchestration
```

### Cursor IDE Integration

Add to your Cursor MCP configuration (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "sparetools-mcp-prompts": {
      "command": "sparetools-mcp-ecosystem",
      "args": ["mcp-prompts"],
      "env": {
        "MODE": "mcp",
        "LOG_LEVEL": "info"
      }
    },
    "sparetools-esp32": {
      "command": "sparetools-mcp-ecosystem",
      "args": ["mcp-servers", "esp32"],
      "env": {
        "ESP32_LOG_LEVEL": "info"
      }
    },
    "sparetools-android": {
      "command": "sparetools-mcp-ecosystem",
      "args": ["mcp-servers", "android"],
      "env": {
        "ANDROID_LOG_LEVEL": "info"
      }
    },
    "sparetools-conan": {
      "command": "sparetools-mcp-ecosystem",
      "args": ["mcp-servers", "conan"],
      "env": {
        "CONAN_LOG_LEVEL": "info",
        "CLOUDSMITH_API_KEY": "${CLOUDSMITH_API_KEY}"
      }
    },
    "sparetools-repo": {
      "command": "sparetools-mcp-ecosystem",
      "args": ["mcp-servers", "repo"],
      "env": {
        "LOG_LEVEL": "info"
      }
    }
  }
}
```

## 🔧 Development Workflows

### ESP32 Development

```bash
# Start ESP32 monitoring
cursor-agent --print "use start_serial_monitor with port /dev/ttyUSB0"

# Flash firmware
cursor-agent --print "use esp32_flash_firmware with firmware.bin"

# Debug application
cursor-agent --print "use esp32_debug_session with breakpoint main"
```

### Android Development

```bash
# Build and deploy APK
cursor-agent --print "use android_build_apk with project_path ./android"
cursor-agent --print "use android_deploy_apk with device_id emulator-5554"

# Monitor logs
cursor-agent --print "use android_logcat with filter MyApp:*"
```

### Package Management

```bash
# Create and publish package
cursor-agent --print "use conan_create_package with conanfile.py"
cursor-agent --print "use conan_upload_package with remote sparesparrow-conan"
```

### Repository Maintenance

```bash
# Analyze repository health
cursor-agent --print "use repo_cleanup_scan with scan_mode thorough"

# Clean large files
cursor-agent --print "use repo_cleanup_list_large_files with min_size_mb 50"
```

## 🏗️ Architecture

### Component Structure

```
sparetools-mcp-ecosystem/
├── mcp-prompts/           # AI prompts server (TypeScript)
│   ├── src/              # Source code
│   ├── dist/             # Compiled JavaScript
│   ├── data/             # Prompt templates
│   └── package.json      # Node.js dependencies
├── mcp-servers/          # Development tool servers (Python)
│   ├── esp32/            # ESP32 development tools
│   ├── android/          # Android development tools
│   ├── conan/            # Package management tools
│   └── repo/             # Repository maintenance tools
├── orchestrator/         # Project orchestration (Python)
│   ├── templates/        # Project templates
│   ├── workflows/        # Workflow definitions
│   └── automation/       # Automation scripts
├── config/               # Configuration files
├── scripts/              # Setup and utility scripts
└── docs/                 # Documentation
```

### MCP Server Tools

#### ESP32 Server (`sparetools-esp32`)
| Tool | Description | Parameters |
|------|-------------|------------|
| `start_serial_monitor` | Start ESP32 serial monitoring | port, baud_rate, terminal |
| `stop_serial_monitor` | Stop monitoring session | session_id, timeout |
| `send_serial_command` | Send command to ESP32 | session_id, command |
| `detect_esp32_ports` | Find available serial ports | - |
| `esp32_flash_firmware` | Flash firmware to device | firmware_path, port |
| `esp32_read_logs` | Read device logs | session_id, lines |

#### Android Server (`sparetools-android`)
| Tool | Description | Parameters |
|------|-------------|------------|
| `android_build_apk` | Build Android APK | project_path, build_type |
| `android_deploy_apk` | Deploy APK to device | apk_path, device_id |
| `android_run_tests` | Execute tests | project_path, test_type |
| `android_logcat` | Monitor device logs | device_id, filter |
| `android_device_info` | List connected devices | - |

#### Conan Server (`sparetools-conan`)
| Tool | Description | Parameters |
|------|-------------|------------|
| `conan_create_package` | Create Conan package | conanfile_path, profile |
| `conan_install_deps` | Install dependencies | conanfile_path, build_missing |
| `conan_upload_package` | Upload to remote | package_ref, remote_name |
| `conan_search_packages` | Search packages | query, remote_name |
| `validate_conanfile` | Validate conanfile | conanfile_path |

#### Repository Server (`sparetools-repo`)
| Tool | Description | Parameters |
|------|-------------|------------|
| `repo_cleanup_scan` | Scan for cleanup opportunities | repo_path, scan_mode |
| `repo_list_large_files` | Find large files | repo_path, min_size_mb |
| `repo_git_status` | Get repository status | repo_path |
| `repo_disk_usage` | Analyze disk usage | repo_path |

## 🎨 Project Orchestration

### Template Management

```bash
# Create project from template
sparetools-mcp-ecosystem orchestrator template create esp32-project

# List available templates
sparetools-mcp-ecosystem orchestrator template list

# Customize template
sparetools-mcp-ecosystem orchestrator template customize my-template
```

### Workflow Automation

```bash
# Run development workflow
sparetools-mcp-ecosystem orchestrator workflow run esp32-dev

# Create custom workflow
sparetools-mcp-ecosystem orchestrator workflow create my-workflow

# List available workflows
sparetools-mcp-ecosystem orchestrator workflow list
```

### Mermaid Diagram Generation

```bash
# Generate flowchart
sparetools-mcp-ecosystem orchestrator mermaid flowchart "A->B->C"

# Create sequence diagram
sparetools-mcp-ecosystem orchestrator mermaid sequence "User->Server:Request"

# Generate class diagram
sparetools-mcp-ecosystem orchestrator mermaid class "ClassA--ClassB"
```

## 🔧 Configuration

### Environment Variables

#### Global Settings
- `SPARETOOLS_MCP_ECOSYSTEM_DIR`: Package installation directory
- `LOG_LEVEL`: Logging level (debug, info, warn, error)

#### Component-Specific
- `ESP32_*`: ESP32 server configuration
- `ANDROID_*`: Android server configuration
- `CONAN_*`: Conan server configuration
- `CLOUDSMITH_API_KEY`: Cloudsmith publishing key

### Configuration Files

- `config/mcp.json`: MCP server configuration
- `config/cursor-mcp.json`: Cursor IDE integration
- `orchestrator/project_orchestration.json`: Project templates
- `orchestrator/project_templates.json`: Template definitions

## 📚 Available Prompts

### Development Domains

#### ESP32 Development (15 prompts)
- `esp32-monitor`, `esp32-flash`, `esp32-debug`
- `esp32-config`, `esp32-ota`, `esp32-testing`
- Serial monitoring, firmware management, debugging workflows

#### Android Development (12 prompts)
- `android-build`, `android-deploy`, `android-test`
- `android-debug`, `android-signing`, `android-optimization`
- Complete mobile development lifecycle

#### Conan Package Management (8 prompts)
- `conan-create`, `conan-publish`, `conan-resolve`
- `conan-inspect`, `conan-migrate`, `conan-troubleshoot`
- Package lifecycle management

#### Repository Maintenance (6 prompts)
- `repo-cleanup`, `repo-health`, `repo-sync`
- `repo-backup`, `repo-optimize`, `repo-monitor`
- Repository health and maintenance

### Specialized Templates

#### Embedded Systems
- Automotive camera systems
- IoT device development
- Sensor network configuration

#### Cloud Integration
- AWS SIP trunk deployment
- PrintCast agent setup
- ElevenLabs voice integration

#### Development Automation
- Cursor IDE workflows
- GitHub Actions CI/CD
- Docker containerization

## 🔄 Integration Features

### From mcp-project-orchestrator

**Cannibalized Features:**
- ✅ **Project Templates**: Integrated template system with SpareTools-specific templates
- ✅ **Component Orchestration**: Workflow automation for development tasks
- ✅ **Mermaid Generation**: Diagram creation for documentation
- ✅ **AWS Integration**: Cloud service management capabilities
- ✅ **Cursor IDE Integration**: Direct IDE workflow support

**Enhanced Features:**
- ✅ **SpareTools Context**: Templates pre-configured for SpareTools ecosystem
- ✅ **Cross-Platform**: Unified workflows across all supported platforms
- ✅ **MCP Integration**: All orchestration accessible via MCP tools
- ✅ **Version Management**: Automatic version synchronization

### From mcp-prompts

**Integrated Capabilities:**
- ✅ **Prompt Management**: Full prompt lifecycle management
- ✅ **Template System**: Variable substitution and customization
- ✅ **Workflow Guidance**: AI-assisted development workflows
- ✅ **Context Awareness**: Project-aware prompt suggestions

## 🐛 Troubleshooting

### Common Issues

1. **MCP Server Not Starting**
   ```bash
   # Check Node.js installation
   node --version

   # Check Python environment
   python --version

   # Run setup again
   sparetools-mcp-ecosystem setup
   ```

2. **Permission Denied**
   ```bash
   # Check Android ADB permissions
   adb devices

   # Check serial port permissions
   ls -la /dev/ttyUSB*
   ```

3. **Cloudsmith Upload Failed**
   ```bash
   # Verify API key
   echo $CLOUDSMITH_API_KEY

   # Check remote configuration
   conan remote list
   ```

4. **Template Not Found**
   ```bash
   # List available templates
   sparetools-mcp-ecosystem orchestrator template list

   # Check template directory
   ls $SPARETOOLS_MCP_ECOSYSTEM_DIR/orchestrator/templates/
   ```

### Debug Logging

Enable detailed logging:

```bash
export LOG_LEVEL=debug
export ESP32_LOG_LEVEL=debug
export ANDROID_LOG_LEVEL=debug
export CONAN_LOG_LEVEL=debug
```

### Log Locations

- MCP Prompts: `~/.sparetools/mcp-prompts/logs/`
- MCP Servers: `~/.sparetools/mcp-servers/logs/`
- Orchestrator: `~/.sparetools/orchestrator/logs/`

## 🤝 Contributing

This package is part of the SpareTools monorepo. See the main repository for contribution guidelines:

1. Fork [SpareTools](https://github.com/sparesparrow/sparetools)
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

Licensed under the MIT License. See LICENSE file for details.

## 🔗 Related Packages

- **sparetools-mcp-prompts**: AI prompts server
- **sparetools-mcp-servers**: Development tool servers
- **sparetools-mcp-project-orchestrator**: Project orchestration (integrated)
- **sparetools-base**: Foundation utilities
- **sparetools-cpython**: Bundled Python runtime
- **sparetools-protocols**: Shared FlatBuffers schemas

---

## 🎯 Quick Start Commands

```bash
# 1. Install ecosystem
conan install sparetools-mcp-ecosystem/1.0.0@sparesparrow/stable

# 2. Run setup
sparetools-mcp-ecosystem setup

# 3. Configure Cursor (add to ~/.cursor/mcp.json)
# See configuration section above

# 4. Test components
sparetools-mcp-ecosystem mcp-prompts --help
sparetools-mcp-ecosystem mcp-servers esp32 --help
sparetools-mcp-ecosystem orchestrator template list

# 5. Use in Cursor
# Try prompts like: /esp32-monitor, /android-build, /conan-create
```

The SpareTools MCP Ecosystem transforms development workflows with intelligent AI assistance, providing a unified interface for complex development tasks across the entire embedded and cross-platform development lifecycle! 🚀✨

