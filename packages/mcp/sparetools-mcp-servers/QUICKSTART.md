# Quick Start: SpareTools MCP Servers

Get up and running with SpareTools MCP servers in under 5 minutes.

## 🚀 Installation

### Option 1: Install MCP Servers Only
```bash
conan install sparetools-mcp-servers/1.0.0@sparesparrow/stable
```

### Option 2: Install Full SpareTools Suite
```bash
conan install sparetools-monorepo/1.0.0@sparesparrow/stable
```

## ⚙️ Configuration

### 1. Add Cloudsmith Repository (if not already added)
```bash
conan remote add sparesparrow-conan https://cloudsmith.io/~sparesparrow-conan/repos/sparetools/
```

### 2. Configure Cursor MCP Servers

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "sparetools-esp32": {
      "command": "sparetools-mcp-esp32"
    },
    "sparetools-android": {
      "command": "sparetools-mcp-android"
    },
    "sparetools-conan": {
      "command": "sparetools-mcp-conan",
      "env": {
        "CLOUDSMITH_API_KEY": "${CLOUDSMITH_API_KEY}",
        "CLOUDSMITH_ORG": "${CLOUDSMITH_ORG}"
      }
    },
    "sparetools-repo": {
      "command": "sparetools-mcp-repo"
    }
  }
}
```

## 🎯 Quick Tests

### ESP32 Serial Monitor
```bash
cursor-agent --print "use detect_esp32_ports tool"
```

### Android Development
```bash
cursor-agent --print "use android_device_info tool"
```

### Repository Analysis
```bash
cursor-agent --print "use repo_cleanup_scan tool with repository_path /path/to/your/project"
```

### Conan Package Management
```bash
cursor-agent --print "use search_conan_packages tool with query boost"
```

## 🔧 Environment Setup

### For Android Development
```bash
export ANDROID_HOME=/path/to/android/sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

### For Cloudsmith Publishing
```bash
export CLOUDSMITH_API_KEY=your_api_key_here
export CLOUDSMITH_ORG=your_org_name
```

### For ESP32 Development
```bash
# Ensure you have permission to access serial ports
sudo usermod -a -G dialout $USER
# Logout and login again for group changes to take effect
```

## 📊 What You Get

### 4 Specialized MCP Servers

| Server | Purpose | Key Tools |
|--------|---------|-----------|
| **ESP32 Serial Monitor** | Device monitoring & interaction | Serial port detection, log monitoring |
| **Android Dev Tools** | Mobile app development | APK building, device deployment, testing |
| **Conan & Cloudsmith** | Package management | Package creation, publishing, dependency management |
| **Repo Cleanup** | Repository maintenance | Disk usage analysis, cleanup recommendations |

### 18+ MCP Tools Total

All tools are accessible through natural language commands in Cursor chat.

## 🎉 You're Ready!

Start using the MCP servers in your development workflow:

- **ESP32 projects**: Monitor device output and debug firmware
- **Android apps**: Build, test, and deploy without leaving Cursor
- **Package management**: Create and publish Conan packages seamlessly
- **Repository health**: Keep your codebase clean and optimized

For detailed documentation, see the main README.md file.