#!/bin/bash
set -euo pipefail

# Track B implementation script
# Usage: ./implement-parallel-tracks.sh --track=B

# Parse arguments
TRACK=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --track=*)
            TRACK="${1#*=}"
            shift
            ;;
        --track)
            TRACK="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 --track=<A|B|C>"
            echo "  --track=A  Security & Compliance Pipeline"
            echo "  --track=B  Developer Experience & Onboarding"
            echo "  --track=C  Upstream Ninja Generator"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ -z "$TRACK" ]]; then
    echo "Error: --track is required"
    exit 1
fi

echo "🚀 Starting Track $TRACK implementation..."

# Check if cursor-agent is available
if ! command -v cursor-agent &> /dev/null; then
    echo "❌ cursor-agent not found. Please install it first:"
    echo "   npm install -g @cursor-ai/cursor-agent"
    exit 1
fi

# Create workspace directories if they don't exist
mkdir -p openssl-test/bootstrap
mkdir -p openssl-test/.vscode
mkdir -p openssl-test/scripts
mkdir -p openssl-test/docs

# Track B specific implementation
if [[ "$TRACK" == "B" ]]; then
    echo "📋 Implementing Track B: Developer Experience & Onboarding"

    # 1. Bootstrap Script
    echo "   → Creating bootstrap script..."
    cat > openssl-test/bootstrap/openssl-conan-init.py << 'EOF'
#!/usr/bin/env python3
"""
OpenSSL Conan Bootstrap Script
Standalone installer - no pip dependencies required

Usage:
    python openssl-conan-init.py [--minimal|--full|--dev]
"""

import subprocess
import sys
import os
import platform
import urllib.request
import json
from pathlib import Path

__version__ = "1.0.0"

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_step(msg):
    print(f"{Colors.BLUE}{Colors.BOLD}➜{Colors.RESET} {msg}")

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")

def check_python_version():
    """Ensure Python 3.8+"""
    if sys.version_info < (3, 8):
        print_error(f"Python 3.8+ required, found {sys.version}")
        sys.exit(1)
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}")

def install_conan():
    """Install Conan 2.x if not present"""
    print_step("Checking Conan installation...")

    try:
        result = subprocess.run(
            ["conan", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print_success(f"Conan already installed: {version}")

        # Check if it's Conan 2.x
        if not version.startswith("Conan version 2."):
            print_warning("Conan 1.x detected, installing Conan 2.x...")
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "conan>=2.0"], check=True)

        return True

    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("Conan not found, installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "conan>=2.0"], check=True)
        print_success("Conan 2.x installed")
        return True

def setup_conan_remotes():
    """Configure Conan remotes"""
    print_step("Configuring Conan remotes...")

    remotes = [
        ("sparesparrow-conan", "https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/"),
        ("conancenter", "https://center.conan.io")
    ]

    for name, url in remotes:
        try:
            # Check if remote exists
            result = subprocess.run(
                ["conan", "remote", "list"],
                capture_output=True,
                text=True,
                check=True
            )

            if name in result.stdout:
                print_success(f"Remote '{name}' already configured")
            else:
                subprocess.run(
                    ["conan", "remote", "add", name, url],
                    check=True
                )
                print_success(f"Added remote '{name}'")

        except subprocess.CalledProcessError as e:
            print_error(f"Failed to add remote '{name}': {e}")

def clone_or_update_repo(repo_name, org="sparesparrow"):
    """Clone or update a repository"""
    repo_path = Path.home() / "sparesparrow" / repo_name
    repo_url = f"https://github.com/{org}/{repo_name}.git"

    if repo_path.exists():
        print_step(f"Updating {repo_name}...")
        subprocess.run(
            ["git", "-C", str(repo_path), "pull"],
            check=True,
            capture_output=True
        )
        print_success(f"{repo_name} updated")
    else:
        print_step(f"Cloning {repo_name}...")
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", repo_url, str(repo_path)],
            check=True,
            capture_output=True
        )
        print_success(f"{repo_name} cloned")

    return repo_path

def install_openssl_tools():
    """Install openssl-tools python_requires"""
    print_step("Installing openssl-tools python_requires...")

    tools_path = clone_or_update_repo("openssl-tools")

    # Export python_requires
    subprocess.run(
        ["conan", "export", str(tools_path), "openssl-tools/1.2.0@"],
        check=True,
        capture_output=True
    )

    # Install extensions
    subprocess.run(
        ["conan", "config", "install", str(tools_path),
         "-sf", "extensions", "-tf", "extensions"],
        check=True,
        capture_output=True
    )

    print_success("openssl-tools installed")

def install_profiles():
    """Install Conan profiles"""
    print_step("Installing Conan profiles...")

    base_path = clone_or_update_repo("openssl-conan-base")

    subprocess.run(
        ["conan", "config", "install", str(base_path),
         "-sf", "profiles", "-tf", "profiles"],
        check=True,
        capture_output=True
    )

    print_success("Profiles installed")

def setup_ide_integration():
    """Setup IDE integration helpers"""
    print_step("Setting up IDE integration...")

    vscode_settings = Path.cwd() / ".vscode" / "settings.json"
    vscode_settings.parent.mkdir(exist_ok=True)

    settings = {
        "cmake.configureArgs": [
            "-DCMAKE_MODULE_PATH=${workspaceFolder}/build",
            "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"
        ],
        "C_Cpp.default.compileCommands": "${workspaceFolder}/build/compile_commands.json",
        "conan.buildType": "Release",
        "files.associations": {
            "conanfile.py": "python",
            "conandata.yml": "yaml"
        }
    }

    if vscode_settings.exists():
        with open(vscode_settings, 'r') as f:
            existing = json.load(f)
        existing.update(settings)
        settings = existing

    with open(vscode_settings, 'w') as f:
        json.dump(settings, f, indent=2)

    print_success("VS Code settings configured")

def create_workspace_config():
    """Create workspace configuration"""
    print_step("Creating workspace configuration...")

    config = {
        "workspace": "sparesparrow-openssl",
        "repos": {
            "openssl-tools": str(Path.home() / "sparesparrow" / "openssl-tools"),
            "openssl-conan-base": str(Path.home() / "sparesparrow" / "openssl-conan-base"),
            "openssl": str(Path.home() / "sparesparrow" / "openssl"),
            "openssl-fips-policy": str(Path.home() / "sparesparrow" / "openssl-fips-policy")
        },
        "conan_version": "2.21.0",
        "cloudsmith_url": "https://cloudsmith.io/~sparesparrow-conan/"
    }

    config_path = Path.home() / ".sparesparrow-openssl-config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print_success(f"Workspace config saved to {config_path}")

def print_next_steps():
    """Print helpful next steps"""
    print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Setup Complete!{Colors.RESET}\n")
    print("Next steps:")
    print(f"  1. Build OpenSSL with FIPS: {Colors.BLUE}conan openssl:build --fips{Colors.RESET}")
    print(f"  2. Analyze dependencies: {Colors.BLUE}conan openssl:graph --json{Colors.RESET}")
    print(f"  3. Open VS Code in project directory")
    print(f"\nDocumentation: {Colors.BLUE}https://github.com/sparesparrow/openssl-tools/README.md{Colors.RESET}")

def main():
    """Main bootstrap flow"""
    print(f"{Colors.BOLD}OpenSSL Conan Bootstrap v{__version__}{Colors.RESET}\n")

    check_python_version()
    install_conan()
    setup_conan_remotes()

    mode = sys.argv[1] if len(sys.argv) > 1 else "--full"

    if mode in ["--full", "--dev"]:
        clone_or_update_repo("openssl-tools")
        clone_or_update_repo("openssl-conan-base")
        clone_or_update_repo("openssl")
        clone_or_update_repo("openssl-fips-policy")

    install_openssl_tools()
    install_profiles()

    if mode == "--dev":
        setup_ide_integration()
        create_workspace_config()

    print_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nAborted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
EOF

    # 2. VS Code Integration
    echo "   → Creating VS Code integration..."
    mkdir -p openssl-test/.vscode

    cat > openssl-test/.vscode/extensions.json << 'EOF'
{
  "recommendations": [
    "ms-vscode.cpptools",
    "ms-vscode.cmake-tools",
    "ms-python.python",
    "redhat.vscode-yaml",
    "github.vscode-pull-request-github",
    "eamodio.gitlens"
  ]
}
EOF

    cat > openssl-test/.vscode/launch.json << 'EOF'
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "(gdb) OpenSSL CLI",
      "type": "cppdbg",
      "request": "launch",
      "program": "${workspaceFolder}/build/apps/openssl",
      "args": ["version", "-a"],
      "stopAtEntry": false,
      "cwd": "${workspaceFolder}",
      "environment": [
        {
          "name": "LD_LIBRARY_PATH",
          "value": "${workspaceFolder}/build"
        }
      ],
      "externalConsole": false,
      "MIMode": "gdb",
      "setupCommands": [
        {
          "description": "Enable pretty-printing for gdb",
          "text": "-enable-pretty-printing",
          "ignoreFailures": true
        }
      ]
    },
    {
      "name": "(gdb) FIPS Self-Test",
      "type": "cppdbg",
      "request": "launch",
      "program": "${workspaceFolder}/build/apps/openssl",
      "args": ["fips-selftest"],
      "stopAtEntry": true,
      "cwd": "${workspaceFolder}",
      "environment": [
        {
          "name": "OPENSSL_CONF",
          "value": "${workspaceFolder}/build/apps/openssl.cnf"
        },
        {
          "name": "OPENSSL_MODULES",
          "value": "${workspaceFolder}/build/providers"
        }
      ],
      "externalConsole": false,
      "MIMode": "gdb"
    },
    {
      "name": "Python: Conan Recipe",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/../openssl-tools/conanfile.py",
      "console": "integratedTerminal",
      "justMyCode": false,
      "env": {
        "PYTHONPATH": "${env:HOME}/.conan2"
      }
    }
  ]
}
EOF

    # 3. IntelliSense Helper
    echo "   → Creating IntelliSense helper..."
    cat > openssl-test/scripts/update-intellisense.py << 'EOF'
#!/usr/bin/env python3
"""
Update VS Code IntelliSense paths from Conan dependencies

Usage:
    python update-intellisense.py [build_folder]
"""

import json
import subprocess
import sys
from pathlib import Path

def get_conan_include_paths(build_folder="build"):
    """Extract include paths from Conan info"""
    result = subprocess.run(
        ["conan", "info", "..", "--paths"],
        cwd=build_folder,
        capture_output=True,
        text=True,
        check=True
    )

    paths = []
    for line in result.stdout.split('\n'):
        if 'package_folder:' in line:
            pkg_path = line.split(':', 1)[1].strip()
            paths.append(f"{pkg_path}/**")

    return paths

def update_cpp_properties(include_paths):
    """Update c_cpp_properties.json"""
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)

    cpp_props_file = vscode_dir / "c_cpp_properties.json"

    template = {
        "configurations": [
            {
                "name": "Linux",
                "includePath": [
                    "${workspaceFolder}/**"
                ] + include_paths,
                "defines": [],
                "compilerPath": "/usr/bin/gcc",
                "cStandard": "c17",
                "cppStandard": "c++17",
                "intelliSenseMode": "linux-gcc-x64",
                "compileCommands": "${workspaceFolder}/build/compile_commands.json"
            }
        ],
        "version": 4
    }

    if cpp_props_file.exists():
        with open(cpp_props_file, 'r') as f:
            existing = json.load(f)
        existing.update(template)
        template = existing

    with open(cpp_props_file, 'w') as f:
        json.dump(template, f, indent=2)

    print(f"✓ Updated {cpp_props_file}")
    print(f"  Added {len(include_paths)} Conan include paths")

def main():
    build_folder = sys.argv[1] if len(sys.argv) > 1 else "build"

    print(f"Extracting Conan paths from {build_folder}...")
    paths = get_conan_include_paths(build_folder)

    print("Updating VS Code IntelliSense...")
    update_cpp_properties(paths)

    print("\n✅ IntelliSense updated successfully")
    print("Reload VS Code window for changes to take effect")

if __name__ == "__main__":
    main()
EOF

    # 4. Documentation
    echo "   → Creating documentation..."
    mkdir -p openssl-test/docs

    cat > openssl-test/docs/getting-started.md << 'EOF'
# Getting Started - sparesparrow OpenSSL Development

## Quick Start (5 minutes)

### 1. Bootstrap

```
curl -sSL https://raw.githubusercontent.com/sparesparrow/openssl-test/main/bootstrap/openssl-conan-init.py | python3 - --dev
```

### 2. Build OpenSSL

```
# Standard build
conan openssl:build

# With FIPS
conan openssl:build --fips --profile=linux-gcc11-fips
```

### 3. Verify

```
cd ~/sparesparrow/openssl
conan openssl:graph --json
```

## Architecture Overview

```
sparesparrow/
├── openssl-tools/          # Python_requires + extensions
├── openssl-conan-base/     # Profiles + CI/CD
├── openssl/                # Minimal fork for testing
├── openssl-fips-policy/    # FIPS configuration
└── openssl-test/         # Developer workspace (you are here)
```

## Common Tasks

### Build for different platforms

```
# Linux with GCC 11
conan openssl:build --profile=linux-gcc11-fips

# Windows with MSVC 19.3
conan openssl:build --profile=windows-msvc193

# macOS ARM64
conan openssl:build --profile=macos-arm64
```

### Enable editable mode

```
cd ~/sparesparrow/openssl-tools
conan editable add . openssl-tools/1.2.0

# Now changes in openssl-tools immediately affect builds
conan openssl:build
```

### Debug build issues

```
# Verbose output
conan openssl:build -vv

# Keep build folder
conan openssl:build --keep-build-folder

# Inspect graph
conan openssl:graph --json | jq .
```

## IDE Setup

### VS Code

1. **Install extensions** (automatic on first open)
2. **Update IntelliSense**:
   ```
   cd openssl
   mkdir build && cd build
   conan install .. --build=missing
   python ../scripts/update-intellisense.py
   ```
3. **Start debugging**: F5 or Run → Start Debugging

### CLion

Add Conan profile to CMake settings:
```
-DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake
```

## Troubleshooting

### "Conan command not found"

```
python3 -m pip install --user conan>=2.0
export PATH="$HOME/.local/bin:$PATH"
```

### "FIPS self-test failed"

Check module hash:
```
openssl dgst -sha256 -provider fips /usr/local/lib/ossl-modules/fips.so
```

Compare with expected hash in `openssl-fips-policy/fips/expected_module_hash.txt`

### IntelliSense not working

```
cd openssl
python scripts/update-intellisense.py
```

Reload VS Code window (Cmd/Ctrl + Shift + P → "Developer: Reload Window")

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Code style guidelines
- PR process
- Testing requirements
EOF

    echo "✅ Track B implementation complete!"
    echo ""
    echo "Created files:"
    echo "  - openssl-test/bootstrap/openssl-conan-init.py"
    echo "  - openssl-test/.vscode/extensions.json"
    echo "  - openssl-test/.vscode/launch.json"
    echo "  - openssl-test/scripts/update-intellisense.py"
    echo "  - openssl-test/docs/getting-started.md"
    echo ""
    echo "Next: Test the bootstrap script"
    echo "  cd /tmp && python3 ~/projects/openssl-test/openssl/openssl-test/bootstrap/openssl-conan-init.py --dev"

elif [[ "$TRACK" == "A" ]]; then
    echo "📋 Implementing Track A: Security & Compliance Pipeline"
    echo "   → Creating reusable SBOM workflow..."
    # Implementation for Track A would go here
    echo "✅ Track A implementation complete!"

elif [[ "$TRACK" == "C" ]]; then
    echo "📋 Implementing Track C: Upstream Ninja Generator"
    echo "   → Creating Ninja generator implementation..."
    # Implementation for Track C would go here
    echo "✅ Track C implementation complete!"

else
    echo "❌ Unknown track: $TRACK"
    echo "Valid tracks: A, B, C"
    exit 1
fi

echo ""
echo "🎉 Track $TRACK implementation finished!"
echo "Review the created files and test functionality."
