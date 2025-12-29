# SpareTools MCP Integration Guide

## Overview

This document provides comprehensive guidance for integrating the SpareTools MCP (Model Context Protocol) ecosystem into development workflows, combining AI-assisted prompts with practical development tools.

## Architecture

### Component Integration

The SpareTools MCP ecosystem consists of four main components:

1. **MCP Prompts Server** (`sparetools-mcp-prompts`)
   - TypeScript-based MCP server providing AI prompts
   - 50+ specialized prompts for development workflows
   - Context-aware prompt suggestions

2. **MCP Development Servers** (`sparetools-mcp-servers`)
   - Python-based MCP servers for development tools
   - 28 tools across ESP32, Android, Conan, and Repo servers
   - Direct tool integration with real development workflows

3. **Project Orchestrator** (`sparetools-mcp-project-orchestrator`)
   - Project template management and workflow automation
   - Mermaid diagram generation
   - AWS integration capabilities

4. **Unified Ecosystem** (`sparetools-mcp-ecosystem`)
   - Complete integration package
   - Single installation for all components
   - Unified launcher and configuration

## Installation

### Single Command Installation

```bash
# Install the complete MCP ecosystem
conan install sparetools-mcp-ecosystem/1.0.0@sparesparrow/stable

# Run setup to configure environment
sparetools-mcp-ecosystem setup
```

### Component-by-Component Installation

```bash
# Install individual components if needed
conan install sparetools-mcp-prompts/3.13.0@sparesparrow/stable
conan install sparetools-mcp-servers/1.0.0@sparesparrow/stable
conan install sparetools-mcp-project-orchestrator/0.1.0@sparesparrow/stable
```

## Cursor IDE Integration

### Automatic Configuration

The ecosystem provides automatic Cursor integration:

```bash
# Generate Cursor MCP configuration
sparetools-mcp-ecosystem setup --cursor

# This creates/updates ~/.cursor/mcp.json with all servers
```

### Manual Configuration

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "sparetools-mcp-prompts": {
      "command": "sparetools-mcp-ecosystem",
      "args": ["mcp-prompts"],
      "env": {
        "MODE": "mcp",
        "LOG_LEVEL": "info",
        "PORT": "3001"
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

## Development Workflows

### ESP32 Development Workflow

```bash
# Start monitoring ESP32 device
cursor> /esp32-monitor
# Prompts for: port selection, baud rate, monitoring options

# Flash firmware
cursor> /esp32-flash
# Guides through: firmware selection, flash options, verification

# Debug application
cursor> /esp32-debug
# Provides: breakpoint setup, variable inspection, troubleshooting
```

### Android Development Workflow

```bash
# Build APK
cursor> /android-build
# Prompts for: build type, optimization options, signing config

# Deploy to device
cursor> /android-deploy
# Guides through: device selection, deployment options, verification

# Monitor logs
cursor> /android-logcat
# Provides: filter setup, log analysis, debugging assistance
```

### Package Management Workflow

```bash
# Create Conan package
cursor> /conan-create
# Prompts for: conanfile validation, package options, build settings

# Publish to Cloudsmith
cursor> /conan-publish
# Guides through: remote selection, authentication, upload verification

# Resolve dependencies
cursor> /conan-resolve
# Provides: conflict analysis, resolution suggestions, testing
```

## Available MCP Tools

### MCP Prompts Server

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_prompt` | Retrieve specific prompt | `id: string` |
| `list_prompts` | List prompts by category | `category?: string, limit?: number` |
| `apply_template` | Apply variables to template | `template_id: string, variables: object` |
| `search_prompts` | Search prompts by query | `query: string, category?: string` |

### ESP32 Server

| Tool | Description | Parameters |
|------|-------------|------------|
| `start_serial_monitor` | Start ESP32 monitoring | `port: string, baud_rate?: number` |
| `stop_serial_monitor` | Stop monitoring | `session_id: string` |
| `send_serial_command` | Send command | `session_id: string, command: string` |
| `detect_esp32_ports` | Find serial ports | - |
| `esp32_flash_firmware` | Flash firmware | `firmware_path: string, port: string` |
| `esp32_read_logs` | Read device logs | `session_id: string, lines?: number` |

### Android Server

| Tool | Description | Parameters |
|------|-------------|------------|
| `android_build_apk` | Build APK | `project_path: string, build_type?: string` |
| `android_deploy_apk` | Deploy APK | `apk_path: string, device_id?: string` |
| `android_run_tests` | Run tests | `project_path: string, test_type?: string` |
| `android_logcat` | Monitor logs | `device_id?: string, filter?: string` |
| `android_device_info` | List devices | - |

### Conan Server

| Tool | Description | Parameters |
|------|-------------|------------|
| `conan_create_package` | Create package | `conanfile_path: string, profile?: string` |
| `conan_install_deps` | Install dependencies | `conanfile_path: string, build_missing?: boolean` |
| `conan_upload_package` | Upload package | `package_ref: string, remote_name: string` |
| `conan_search_packages` | Search packages | `query: string, remote_name?: string` |
| `validate_conanfile` | Validate conanfile | `conanfile_path: string` |

### Repository Server

| Tool | Description | Parameters |
|------|-------------|------------|
| `repo_cleanup_scan` | Scan repository | `repo_path: string, scan_mode?: string` |
| `repo_list_large_files` | Find large files | `repo_path: string, min_size_mb?: number` |
| `repo_git_status` | Get Git status | `repo_path: string` |
| `repo_disk_usage` | Analyze disk usage | `repo_path: string` |

## Project Orchestration

### Template Management

```bash
# Create project from SpareTools template
sparetools-mcp-ecosystem orchestrator template create esp32-bpm-detector

# List available templates
sparetools-mcp-ecosystem orchestrator template list

# Customize template
sparetools-mcp-ecosystem orchestrator template customize my-esp32-project
```

### Workflow Automation

```bash
# Run development workflow
sparetools-mcp-ecosystem orchestrator workflow run embedded-dev

# List available workflows
sparetools-mcp-ecosystem orchestrator workflow list

# Create custom workflow
sparetools-mcp-ecosystem orchestrator workflow create ci-pipeline
```

### Diagram Generation

```bash
# Generate architecture diagram
sparetools-mcp-ecosystem orchestrator mermaid flowchart "ESP32->Android:Data->Cloudsmith:Package"

# Create workflow diagram
sparetools-mcp-ecosystem orchestrator mermaid sequence "Developer->ESP32:Flash->Android:Deploy->User:Test"
```

## Integration Examples

### Complete Development Session

```bash
# 1. Set up new ESP32 project
cursor> /template-create esp32-bpm-detector
# Creates project structure with SpareTools integration

# 2. Monitor device during development
cursor> /esp32-monitor
# Real-time serial monitoring with intelligent filtering

# 3. Build and test Android companion app
cursor> /android-build
cursor> /android-deploy
cursor> /android-logcat

# 4. Package and publish
cursor> /conan-create
cursor> /conan-publish

# 5. Maintain repository health
cursor> /repo-cleanup
```

### CI/CD Integration

```yaml
# .github/workflows/ci.yml
name: CI/CD with SpareTools MCP

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup SpareTools MCP
        run: |
          conan install sparetools-mcp-ecosystem/1.0.0@sparesparrow/stable
          sparetools-mcp-ecosystem setup

      - name: Run ESP32 Tests
        run: sparetools-mcp-ecosystem orchestrator workflow run esp32-test

      - name: Build Android APK
        run: sparetools-mcp-ecosystem mcp-servers android build-apk --project ./android

      - name: Package and Upload
        run: |
          sparetools-mcp-ecosystem mcp-servers conan create-package
          sparetools-mcp-ecosystem mcp-servers conan upload-package
```

## Advanced Configuration

### Environment Variables

```bash
# Global settings
export SPARETOOLS_MCP_ECOSYSTEM_DIR="/path/to/installation"
export LOG_LEVEL="debug"

# Component-specific
export ESP32_DEFAULT_PORT="/dev/ttyUSB0"
export ESP32_DEFAULT_BAUD="115200"
export ANDROID_DEFAULT_DEVICE="emulator-5554"
export CLOUDSMITH_API_KEY="your-api-key"
export CLOUDSMITH_ORG="sparesparrow-conan"
```

### Custom Prompts

Create custom prompts in `~/.sparetools/mcp-prompts/custom/`:

```json
{
  "id": "my-custom-workflow",
  "name": "My Custom Development Workflow",
  "description": "Custom workflow for my development process",
  "category": "custom",
  "template": "Step 1: {step1}\nStep 2: {step2}\nStep 3: {step3}",
  "variables": [
    {
      "name": "step1",
      "description": "First step in the workflow",
      "required": true
    }
  ]
}
```

### Workflow Customization

Create custom workflows in `~/.sparetools/orchestrator/workflows/`:

```json
{
  "name": "custom-dev-workflow",
  "description": "Custom development workflow",
  "steps": [
    {
      "name": "setup",
      "description": "Project setup",
      "commands": [
        "sparetools-mcp-ecosystem orchestrator template create base-project",
        "sparetools-mcp-ecosystem mcp-servers conan install-deps"
      ]
    },
    {
      "name": "develop",
      "description": "Development phase",
      "commands": [
        "sparetools-mcp-ecosystem mcp-servers esp32 start-monitor",
        "sparetools-mcp-ecosystem mcp-servers android build-apk"
      ]
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **MCP Server Not Connecting**
   ```bash
   # Check Node.js and Python installations
   node --version
   python --version

   # Verify package installation
   sparetools-mcp-ecosystem --version

   # Check logs
   tail -f ~/.sparetools/mcp-ecosystem/logs/*.log
   ```

2. **Tool Execution Failed**
   ```bash
   # Enable debug logging
   export LOG_LEVEL=debug

   # Check tool permissions
   ls -la /dev/ttyUSB*  # For ESP32
   adb devices          # For Android

   # Verify environment
   sparetools-mcp-ecosystem setup
   ```

3. **Prompt Not Found**
   ```bash
   # List available prompts
   cursor> /list-prompts

   # Check prompt categories
   cursor> /list-prompts category:esp32

   # Update prompts
   sparetools-mcp-ecosystem mcp-prompts update
   ```

4. **Template Issues**
   ```bash
   # List available templates
   sparetools-mcp-ecosystem orchestrator template list

   # Check template directory
   ls $SPARETOOLS_MCP_ECOSYSTEM_DIR/orchestrator/templates/
   ```

### Performance Optimization

```bash
# Enable caching
export MCP_PROMPT_CACHE_ENABLED=true
export MCP_PROMPT_CACHE_TTL=3600

# Optimize logging
export LOG_LEVEL=warn  # Reduce log verbosity

# Configure resource limits
export MCP_SERVER_MAX_CONNECTIONS=10
export MCP_PROMPT_CACHE_SIZE=100
```

### Backup and Recovery

```bash
# Backup configuration
cp ~/.cursor/mcp.json ~/.cursor/mcp.json.backup
cp ~/.sparetools/ ~/.sparetools.backup/ -r

# Reset ecosystem
sparetools-mcp-ecosystem setup --reset

# Restore configuration
cp ~/.cursor/mcp.json.backup ~/.cursor/mcp.json
```

## Security Considerations

- MCP servers run with user permissions
- API keys stored securely in environment variables
- Tool execution logged for audit trails
- Network operations isolated to development workflows

## Contributing

### Adding New Prompts

1. Create prompt JSON in appropriate category directory
2. Test prompt with MCP server
3. Add documentation
4. Submit pull request

### Adding New Tools

1. Implement tool in appropriate MCP server
2. Add unit tests
3. Update documentation
4. Test integration

### Customizing Workflows

1. Create workflow JSON in workflows directory
2. Test workflow execution
3. Document custom workflow
4. Share with team

## Support and Resources

- **Documentation**: https://sparetools.readthedocs.io/mcp/
- **GitHub**: https://github.com/sparesparrow/sparetools/tree/main/packages/mcp
- **Discord**: https://discord.gg/sparesparrow
- **Issues**: https://github.com/sparesparrow/sparetools/issues

---

## Quick Reference

### Essential Commands

```bash
# Install ecosystem
conan install sparetools-mcp-ecosystem/1.0.0@sparesparrow/stable

# Setup environment
sparetools-mcp-ecosystem setup

# Test components
sparetools-mcp-ecosystem mcp-prompts --help
sparetools-mcp-ecosystem mcp-servers esp32 --help
sparetools-mcp-ecosystem orchestrator template list
```

### Cursor Slash Commands

```
/esp32-monitor    # ESP32 development
/esp32-flash      # Firmware flashing
/android-build    # APK building
/android-deploy   # App deployment
/conan-create     # Package creation
/repo-cleanup     # Repository maintenance
/template-create  # Project templates
```

The SpareTools MCP ecosystem transforms development workflows by providing intelligent AI assistance combined with practical development tools, creating a seamless and productive development experience! 🚀✨
