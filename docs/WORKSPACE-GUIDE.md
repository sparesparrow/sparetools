# SpareTools VS Code Workspace Guide

Comprehensive guide for using VS Code workspaces with SpareTools OpenSSL development.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Workspace Structure](#workspace-structure)
5. [Common Tasks](#common-tasks)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Features](#advanced-features)

---

## Introduction

SpareTools provides pre-configured VS Code workspaces to streamline OpenSSL development across multiple packages and build methods. Each workspace is tailored for specific development scenarios.

### Benefits

✅ **Organized Development** - Logical grouping of related packages  
✅ **Integrated Tooling** - Pre-configured tasks, debugging, and extensions  
✅ **Cross-Platform** - Works on Linux, macOS, and Windows  
✅ **Zero Configuration** - Launch and start developing immediately  

---

## Prerequisites

### Required Software

1. **VS Code** (version 1.80+)
   ```bash
   # Check version
   code --version
   ```

2. **Python 3.12+**
   ```bash
   python3 --version
   ```

3. **Conan 2.21.0**
   ```bash
   pip install conan==2.21.0
   conan --version
   ```

4. **Git**
   ```bash
   git --version
   ```

### Recommended VS Code Extensions

Install these extensions for the best experience:

```bash
# Install via command line
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-vscode.cmake-tools
code --install-extension twxs.cmake
code --install-extension ms-vscode.makefile-tools
code --install-extension github.vscode-github-actions
```

Or install via VS Code Extensions panel:
- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **CMake Tools** (ms-vscode.cmake-tools)
- **CMake** (twxs.cmake)
- **Makefile Tools** (ms-vscode.makefile-tools)
- **GitHub Actions** (github.vscode-github-actions)

---

## Quick Start

### 1. Clone Repository

```bash
cd ~
git clone https://github.com/sparesparrow/sparetools.git
cd sparetools
```

### 2. Open Workspace

```bash
# Open the main integration workspace
code workspaces/openssl-integration.code-workspace
```

### 3. Configure Conan

```bash
# Detect platform profile
conan profile detect

# Add Cloudsmith remote
conan remote add sparesparrow-conan \
  https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/
```

### 4. Build Packages

Use VS Code tasks (Ctrl+Shift+P → "Tasks: Run Task"):
- **Build Base Packages** - Builds foundation tier
- **Build OpenSSL Tools** - Builds tool packages
- **Build OpenSSL** - Builds main OpenSSL package
- **Run Tests** - Executes test suite

---

## Workspace Structure

### Available Workspaces

SpareTools provides several specialized workspaces:

#### 1. **openssl-integration.code-workspace**

Main development workspace with all packages.

```json
{
  "folders": [
    { "path": "../packages/sparetools-base", "name": "🔧 Base" },
    { "path": "../packages/sparetools-cpython", "name": "🐍 CPython" },
    { "path": "../packages/sparetools-openssl-tools", "name": "🛠️ OpenSSL Tools" },
    { "path": "../packages/sparetools-openssl", "name": "🔐 OpenSSL" },
    { "path": "../packages/sparetools-bootstrap", "name": "🚀 Bootstrap" }
  ]
}
```

**Use Cases:**
- Full-stack development
- Cross-package refactoring
- Integration testing
- Release preparation

#### 2. **openssl-dev.code-workspace**

Focused workspace for OpenSSL package development.

**Use Cases:**
- OpenSSL recipe development
- Build method testing
- Profile configuration
- Provider testing

#### 3. **tools-dev.code-workspace**

Workspace for tooling development.

**Use Cases:**
- CLI development
- Build matrix generation
- FIPS validator enhancement
- SBOM generator work

### Workspace Settings

Each workspace includes pre-configured settings:

```json
{
  "settings": {
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "files.exclude": {
      "**/__pycache__": true,
      "**/*.pyc": true,
      "**/.conan2": true,
      "**/build": true
    }
  }
}
```

---

## Common Tasks

### Building Packages

#### Via VS Code Tasks

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
2. Type "Tasks: Run Task"
3. Select your task:
   - **Build sparetools-base**
   - **Build sparetools-cpython**
   - **Build sparetools-openssl**
   - **Build All Packages**

#### Via Terminal

```bash
# Build single package
cd packages/sparetools-openssl
conan create . --version=3.3.2 --build=missing

# Build with specific profile
conan create . --version=3.3.2 \
  -pr:b ../sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b ../sparetools-openssl-tools/profiles/features/fips-enabled
```

### Running Tests

#### Test Package

```bash
cd packages/sparetools-openssl
conan test test_package sparetools-openssl/3.3.2@
```

#### Provider Tests

```bash
# Build test package
cd packages/sparetools-openssl/test_package
cmake -B build -S .
cmake --build build

# Run provider ordering test
./build/test_provider_ordering

# Run FIPS smoke test
./build/test_fips_smoke
```

#### Unit Tests (Python)

```bash
# Run pytest
cd packages/sparetools-openssl-tools
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest tests/ --cov=openssl_tools --cov-report=html
```

### Code Navigation

#### Jump to Definition

- **F12** - Go to definition
- **Alt+F12** - Peek definition
- **Ctrl+Click** - Go to definition

#### Find References

- **Shift+F12** - Find all references
- **Alt+Shift+F12** - Peek references

#### Symbol Search

- **Ctrl+T** - Go to symbol in workspace
- **Ctrl+Shift+O** - Go to symbol in file

### Debugging

#### Debug Python Code

1. Set breakpoint (F9)
2. Press F5 or select "Run → Start Debugging"
3. Select "Python File"

#### Debug Configuration

`.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}"
    },
    {
      "name": "Python: Conan Create",
      "type": "python",
      "request": "launch",
      "module": "conans.client.command",
      "args": ["create", ".", "--version=3.3.2"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}/packages/sparetools-openssl"
    },
    {
      "name": "Test: Provider Ordering",
      "type": "cppdbg",
      "request": "launch",
      "program": "${workspaceFolder}/packages/sparetools-openssl/test_package/build/test_provider_ordering",
      "cwd": "${workspaceFolder}/packages/sparetools-openssl/test_package/build",
      "stopAtEntry": false,
      "externalConsole": false,
      "MIMode": "gdb"
    }
  ]
}
```

---

## Troubleshooting

### Common Issues

#### Issue 1: "Conan not found"

**Symptom:**
```
bash: conan: command not found
```

**Solution:**
```bash
# Install Conan
pip install conan==2.21.0

# Verify installation
conan --version

# Add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

#### Issue 2: "Python interpreter not found"

**Symptom:**
```
Python interpreter not found in workspace
```

**Solution:**
```bash
# Create virtual environment
cd ~/sparetools
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate.bat  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Issue 3: "Package not found on remote"

**Symptom:**
```
ERROR: Package 'sparetools-base/2.0.0' not found on any remote
```

**Solution:**
```bash
# Add Cloudsmith remote
conan remote add sparesparrow-conan \
  https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/

# List remotes
conan remote list

# Try building locally
cd packages/sparetools-base
conan create . --version=2.0.0
```

#### Issue 4: "Profile not found"

**Symptom:**
```
ERROR: Profile 'default' not found
```

**Solution:**
```bash
# Detect profile
conan profile detect --force

# Verify profile
conan profile show default
```

#### Issue 5: "Build fails on Windows"

**Symptom:**
```
error: command 'cl.exe' not found
```

**Solution:**
```bash
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/

# Or use vcvarsall.bat
"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64

# Then retry build
conan create packages/sparetools-openssl --version=3.3.2
```

### Performance Issues

#### Slow Builds

```bash
# Use multiple cores
conan create . --build=missing -c tools.cmake.cmake_program:jobs=8

# Use Ninja generator (faster than Make)
conan create . --build=missing -c tools.cmake.cmaketoolchain:generator=Ninja
```

#### Disk Space Issues

```bash
# Clean Conan cache
conan cache clean "*" --build
conan cache clean "*" --source

# Remove old packages
conan remove "*" --confirm
```

### Logging and Diagnostics

#### Enable Verbose Logging

```bash
# Conan verbose mode
conan create . --version=3.3.2 -vvv

# Save logs
conan create . --version=3.3.2 2>&1 | tee build.log
```

#### Check System Info

```bash
# Python info
python3 --version
pip list | grep conan

# Conan info
conan --version
conan profile show default
conan remote list

# System info
uname -a  # Linux/macOS
systeminfo  # Windows
```

---

## Advanced Features

### Custom Tasks

Add custom tasks in `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Build with FIPS",
      "type": "shell",
      "command": "conan create packages/sparetools-openssl --version=3.3.2 -pr:b packages/sparetools-openssl-tools/profiles/features/fips-enabled",
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Run Security Scan",
      "type": "shell",
      "command": "trivy fs --security-checks vuln . && syft packages . -o cyclonedx-json > sbom.json",
      "group": "test"
    },
    {
      "label": "Generate Build Matrix",
      "type": "shell",
      "command": "python3 -m openssl_tools.cli matrix generate --optimization high --output matrix.json",
      "group": "build"
    }
  ]
}
```

### Multi-Root Workspaces

Work on multiple projects simultaneously:

```json
{
  "folders": [
    { "path": "~/sparetools", "name": "SpareTools" },
    { "path": "~/projects/my-app", "name": "My App" },
    { "path": "~/projects/openssl-fork", "name": "OpenSSL Fork" }
  ]
}
```

### Integrated Terminal Profiles

Configure terminal profiles in `.vscode/settings.json`:

```json
{
  "terminal.integrated.profiles.linux": {
    "Conan Bash": {
      "path": "bash",
      "args": ["-l"],
      "env": {
        "CONAN_USER_HOME": "${workspaceFolder}/.conan2"
      }
    }
  },
  "terminal.integrated.profiles.windows": {
    "PowerShell (Conan)": {
      "path": "pwsh.exe",
      "env": {
        "CONAN_USER_HOME": "${workspaceFolder}\\.conan2"
      }
    }
  }
}
```

### Snippets

Create custom snippets in `.vscode/*.code-snippets`:

```json
{
  "Conan Create": {
    "prefix": "conan-create",
    "body": [
      "conan create . --version=${1:1.0.0} \\",
      "  -pr:b ${2:profile} \\",
      "  --build=missing"
    ]
  },
  "Conan Test": {
    "prefix": "conan-test",
    "body": [
      "conan test test_package ${1:package}/${2:version}@"
    ]
  }
}
```

---

## Platform-Specific Notes

### Linux

#### Prerequisites
```bash
sudo apt update
sudo apt install -y build-essential cmake ninja-build git python3-pip
pip3 install conan==2.21.0
```

#### Workspace Path
```bash
~/sparetools/
```

### macOS

#### Prerequisites
```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install cmake ninja git python@3.12
pip3 install conan==2.21.0
```

#### Workspace Path
```bash
~/sparetools/
```

### Windows

#### Prerequisites
```powershell
# Install Chocolatey if not present
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install dependencies
choco install -y cmake ninja git python312 visualstudio2022buildtools
pip install conan==2.21.0
```

#### Workspace Path
```powershell
C:\Users\<Username>\sparetools\
```

#### Terminal Configuration

Use PowerShell or CMD with Developer Command Prompt:

```json
{
  "terminal.integrated.profiles.windows": {
    "Developer PowerShell": {
      "path": "pwsh.exe",
      "args": [
        "-NoExit",
        "-Command",
        "& 'C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\Common7\\Tools\\Launch-VsDevShell.ps1'"
      ]
    }
  },
  "terminal.integrated.defaultProfile.windows": "Developer PowerShell"
}
```

---

## Integration with CI/CD

### GitHub Actions

Reference workspace tasks in workflows:

```yaml
- name: Build Packages
  run: |
    # Use same command as VS Code task
    conan create packages/sparetools-openssl --version=3.3.2 \
      -pr:b packages/sparetools-openssl-tools/profiles/base/${{ matrix.profile }} \
      --build=missing
```

### Local Testing

Test CI workflows locally using [act](https://github.com/nektos/act):

```bash
# Install act
brew install act  # macOS
sudo apt install act  # Linux

# Run workflow
act -j build
```

---

## Best Practices

### 1. **Use Virtual Environments**

Always use Python virtual environments:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. **Keep Workspaces Clean**

Add to `.gitignore`:

```
.venv/
.conan2/
build/
__pycache__/
*.pyc
.vscode/.ropeproject/
```

### 3. **Pin Versions**

Always pin tool versions:

```bash
pip install conan==2.21.0  # Good
pip install conan          # Bad - uses latest
```

### 4. **Use Tasks for Common Operations**

Define tasks instead of remembering commands:

```json
{
  "label": "Quick Build",
  "type": "shell",
  "command": "conan create . --version=3.3.2 --build=missing"
}
```

### 5. **Leverage IntelliSense**

Configure Python path for better autocomplete:

```json
{
  "python.analysis.extraPaths": [
    "${workspaceFolder}/packages/sparetools-openssl-tools"
  ]
}
```

---

## Resources

### Documentation
- [VS Code Documentation](https://code.visualstudio.com/docs)
- [Conan 2.x Documentation](https://docs.conan.io/2/)
- [SpareTools GitHub](https://github.com/sparesparrow/sparetools)

### Community
- [GitHub Discussions](https://github.com/sparesparrow/sparetools/discussions)
- [GitHub Issues](https://github.com/sparesparrow/sparetools/issues)

### Support
- **Email:** contact@sparesparrow.dev
- **GitHub:** [@sparesparrow](https://github.com/sparesparrow)

---

## Changelog

### Version 2.0.0 (2025-10-31)
- Initial workspace guide
- Added multi-platform support
- Comprehensive troubleshooting
- Advanced features documentation

---

**Last Updated:** 2025-10-31  
**Maintainer:** sparesparrow  
**Status:** Production Ready

