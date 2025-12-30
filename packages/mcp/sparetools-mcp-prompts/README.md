# SpareTools MCP Prompts

A comprehensive MCP (Model Context Protocol) server providing AI-assisted development workflows for the SpareTools ecosystem.

## 🚀 Overview

This package integrates MCP Prompts with SpareTools, providing intelligent AI assistance for:

- **ESP32 Development**: Serial monitoring, flashing, debugging
- **Android Development**: APK building, deployment, testing
- **Conan Package Management**: Dependency resolution, publishing to Cloudsmith
- **Repository Maintenance**: Cleanup, optimization, health monitoring
- **Embedded Systems**: Cross-platform development workflows

## 📦 Installation

### Via Conan (Recommended)

```bash
# Install the MCP Prompts package
conan install sparetools-mcp-prompts/3.13.0@sparesparrow/stable

# Or install the full SpareTools MCP ecosystem
conan install sparetools-mcp-ecosystem/1.0.0@sparesparrow/stable
```

### Via Cloudsmith

```bash
# Add SpareSparrow Conan repository
conan remote add sparesparrow-conan https://cloudsmith.io/~sparesparrow-conan/repos/sparetools/
conan install sparetools-mcp-prompts/3.13.0@sparesparrow/stable
```

## 🛠️ Usage

### MCP Server Configuration

Add to your Cursor MCP configuration (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "sparetools-mcp-prompts": {
      "command": "sparetools-mcp-prompts",
      "env": {
        "MODE": "mcp",
        "LOG_LEVEL": "info"
      }
    }
  }
}
```

### Available Prompt Categories

#### ESP32 Development (`esp32-*`)
- `esp32-monitor` - Serial monitoring and device interaction
- `esp32-flash` - Firmware flashing and OTA updates
- `esp32-debug` - Debugging and troubleshooting

#### Android Development (`android-*`)
- `android-build` - APK building and optimization
- `android-deploy` - Device deployment and testing
- `android-debug` - Logcat monitoring and debugging

#### Package Management (`conan-*`)
- `conan-create` - Package creation and validation
- `conan-publish` - Publishing to Cloudsmith
- `conan-resolve` - Dependency resolution

#### Repository Management (`repo-*`)
- `repo-cleanup` - Repository cleanup and optimization
- `repo-health` - Health monitoring and analysis
- `repo-maintenance` - Automated maintenance tasks

### Command Line Usage

```bash
# Start MCP server
sparetools-mcp-prompts

# Start HTTP server
sparetools-mcp-prompts-http

# CLI tools
sparetools-mcp-prompts-cli --help
```

## 🔧 Integration

### With Cursor IDE

The MCP server integrates seamlessly with Cursor, providing AI assistance for:

1. **Context-Aware Prompts**: Automatically suggests relevant workflows based on project context
2. **Tool Integration**: Direct access to development tools (ESP32 flashing, Android deployment, etc.)
3. **Workflow Automation**: Guided workflows for complex development tasks

### With SpareTools Ecosystem

- **Version Management**: Automatic version synchronization via `sparetools-base`
- **Bundled Python**: Consistent Python runtime via `sparetools-cpython`
- **Cross-Platform**: Works on Linux, macOS, and Windows

## 📚 Available Prompts

### ESP32 Development
- `esp32-monitor` - Real-time serial monitoring with filtering
- `esp32-flash` - Firmware flashing with verification
- `esp32-debug` - Debugging workflows and troubleshooting
- `esp32-config` - Device configuration and setup

### Android Development
- `android-build` - Gradle build optimization and APK generation
- `android-deploy` - ADB deployment with device selection
- `android-test` - Unit and instrumentation testing
- `android-debug` - Logcat monitoring and crash analysis

### Conan Package Management
- `conan-create` - Package creation with validation
- `conan-publish` - Publishing to Cloudsmith repositories
- `conan-resolve` - Dependency resolution and conflict resolution
- `conan-inspect` - Package inspection and analysis

### Repository Maintenance
- `repo-cleanup` - Large file removal and optimization
- `repo-health` - Repository health analysis and reporting
- `repo-sync` - Repository synchronization and backup
- `repo-maintain` - Automated maintenance tasks

## 🔧 Configuration

### Environment Variables

- `MODE`: Server mode (`mcp` or `http`) - default: `mcp`
- `PORT`: HTTP server port - default: `3000`
- `LOG_LEVEL`: Logging level (`debug`, `info`, `warn`, `error`) - default: `info`
- `DATA_DIR`: Data directory path - default: `./data`

### MCP Configuration

The server provides these MCP tools:

- `get_prompt` - Retrieve a specific prompt by ID
- `list_prompts` - List prompts by category or search
- `apply_template` - Apply variables to prompt templates
- `search_prompts` - Search prompts by content or tags

## 🏗️ Architecture

### Core Components

- **MCP Server**: Handles Model Context Protocol communication
- **Prompt Engine**: Manages prompt templates and variables
- **Tool Integration**: Interfaces with SpareTools development tools
- **Workflow Manager**: Orchestrates complex development workflows

### Data Structure

```
data/
├── prompts/
│   ├── esp32/           # ESP32 development prompts
│   ├── android/         # Android development prompts
│   ├── conan/           # Package management prompts
│   └── repo/            # Repository management prompts
├── templates/           # Reusable prompt templates
└── workflows/           # Multi-step workflow definitions
```

## 🔐 Security

- **No External API Keys**: All operations use local tools and configurations
- **Local Execution**: All development tools run locally
- **Isolated Environment**: Uses bundled Python runtime for consistency
- **Audit Logging**: All operations are logged for transparency

## 🐛 Troubleshooting

### Common Issues

1. **MCP Server Not Found**: Ensure the package is properly installed and binaries are in PATH
2. **Permission Denied**: Check file permissions for development tools
3. **Port Already in Use**: Change the HTTP server port using PORT environment variable
4. **Missing Dependencies**: Run setup scripts to install required tools

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=debug
sparetools-mcp-prompts
```

### Log Locations

- Application logs: `~/.sparetools/mcp-prompts/logs/`
- MCP communication: `~/.sparetools/mcp-prompts/debug/`

## 🤝 Contributing

This package is part of the SpareTools monorepo. Contributions should be made to the main repository:

1. Fork the [SpareTools repository](https://github.com/sparesparrow/sparetools)
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This package is licensed under the MIT License. See the LICENSE file for details.

## 🔗 Related Packages

- **sparetools-mcp-servers**: MCP servers for development workflows
- **sparetools-mcp-ecosystem**: Complete MCP ecosystem integration
- **sparetools-base**: Foundation utilities and version management
- **sparetools-cpython**: Bundled Python runtime

