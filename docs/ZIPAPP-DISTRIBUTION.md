# Zipapp Distribution Guide

Python Zip applications (zipapps) provide a simple way to distribute pure-Python applications as a single executable file. This guide covers how to create, build, and distribute zipapps for SpareTools Python tools.

## Overview

A Python zipapp is a ZIP file containing Python code with a `__main__.py` entry point. When executed with Python, it automatically runs the entry point, making it ideal for distributing CLI tools and applications.

### Benefits

- **Single File Distribution**: All code bundled into one `.pyz` file
- **No Installation Required**: Just download and run
- **Cross-Platform**: Works on any system with Python 3.5+
- **Simple Deployment**: No virtual environments or package managers needed

### Limitations

- **Pure Python Only**: Cannot include C extensions or compiled code
- **No External Dependencies**: All dependencies must be bundled or available in the target environment
- **Python Version**: Requires Python 3.5+ (zipapp support)

---

## Creating a Zipapp

### Basic Structure

A zipapp requires:
1. A `__main__.py` file that serves as the entry point
2. All Python modules and dependencies
3. Optional: A shebang line for direct execution on Unix

### Example: Simple CLI Tool

```python
# mytool/__main__.py
import sys

def main():
    print("Hello from zipapp!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Building with Python's zipapp Module

```bash
# Basic build
python -m zipapp mytool -o mytool.pyz

# With shebang for Unix execution
python -m zipapp mytool -o mytool.pyz -p "/usr/bin/env python3"

# Include dependencies
python -m zipapp mytool -o mytool.pyz --main "mytool.__main__:main"
```

---

## Building SpareTools Zipapps

### Using the Build Script

We provide a build script to create zipapps for SpareTools tools:

```bash
# Build zipapp for bootstrap-obd
python scripts/build/build-zipapp.py bootstrap-obd.py

# Build with custom output name
python scripts/build/build-zipapp.py bootstrap-obd.py -o sparetools-bootstrap.pyz

# Build with dependencies bundled
python scripts/build/build-zipapp.py bootstrap-obd.py --bundle-deps
```

### Manual Build Process

1. **Prepare the source structure**:
```bash
mkdir -p dist/mytool
cp -r mytool/* dist/mytool/
```

2. **Create `__main__.py` entry point**:
```python
# dist/mytool/__main__.py
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mytool.main import main

if __name__ == "__main__":
    sys.exit(main())
```

3. **Build the zipapp**:
```bash
python -m zipapp dist/mytool -o dist/mytool.pyz -p "/usr/bin/env python3"
```

4. **Make executable**:
```bash
chmod +x dist/mytool.pyz
```

---

## Distribution via GitHub Releases

### Automated Release Workflow

The example below shows how to distribute zipapps via GitHub Releases (similar to cloudsmith-cli):

```bash
# Download latest release and make it executable
curl -s https://api.github.com/repos/sparesparrow/sparetools/releases/latest | \
  sed -n 's/"browser_download_url": //p' | \
  grep '\.pyz$' | \
  head -1 | \
  xargs wget -qO sparetools-bootstrap.pyz

chmod +x ./sparetools-bootstrap.pyz

# Move it into your $PATH
sudo mv ./sparetools-bootstrap.pyz /usr/local/bin/sparetools-bootstrap
```

### GitHub Actions Workflow

Create `.github/workflows/release-zipapp.yml`:

```yaml
name: Build and Release Zipapp

on:
  release:
    types: [created]

jobs:
  build-zipapp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Build zipapp
        run: |
          python scripts/build/build-zipapp.py bootstrap-obd.py \
            -o sparetools-bootstrap.pyz
      
      - name: Upload release asset
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ github.event.release.upload_url }}
          asset_path: ./sparetools-bootstrap.pyz
          asset_name: sparetools-bootstrap.pyz
          asset_content_type: application/zip
```

---

## Installation Methods

### Method 1: Direct Download (Recommended)

```bash
# Download latest release
curl -s https://api.github.com/repos/sparesparrow/sparetools/releases/latest | \
  sed -n 's/"browser_download_url": //p' | \
  grep 'sparetools-bootstrap\.pyz' | \
  xargs wget -qO sparetools-bootstrap.pyz

chmod +x sparetools-bootstrap.pyz
sudo mv sparetools-bootstrap.pyz /usr/local/bin/sparetools-bootstrap
```

### Method 2: Using a Package Manager Script

Create an installation script `install-sparetools.sh`:

```bash
#!/bin/bash
set -e

REPO="sparesparrow/sparetools"
TOOL="sparetools-bootstrap"
INSTALL_DIR="/usr/local/bin"

echo "Installing $TOOL..."

# Get latest release URL
DOWNLOAD_URL=$(curl -s "https://api.github.com/repos/$REPO/releases/latest" | \
  grep "browser_download_url.*$TOOL\.pyz" | \
  cut -d '"' -f 4)

if [ -z "$DOWNLOAD_URL" ]; then
  echo "Error: Could not find download URL"
  exit 1
fi

# Download
echo "Downloading from $DOWNLOAD_URL..."
wget -q "$DOWNLOAD_URL" -O "/tmp/$TOOL.pyz" || curl -L "$DOWNLOAD_URL" -o "/tmp/$TOOL.pyz"

# Install
chmod +x "/tmp/$TOOL.pyz"
sudo mv "/tmp/$TOOL.pyz" "$INSTALL_DIR/$TOOL"

echo "Installed $TOOL to $INSTALL_DIR/$TOOL"
echo "Run: $TOOL --help"
```

### Method 3: pipx (Alternative)

If the tool is also available as a package:

```bash
pipx install sparetools-bootstrap
```

---

## Best Practices

### 1. Include Version Information

```python
# mytool/__main__.py
__version__ = "1.0.0"

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=__version__)
    # ...
```

### 2. Handle Dependencies

For tools with external dependencies:

**Option A: Bundle dependencies** (for small, pure-Python deps):
```bash
pip install -t mytool/vendor requests
python -m zipapp mytool -o mytool.pyz
```

**Option B: Check and install at runtime**:
```python
# mytool/__main__.py
import subprocess
import sys

def ensure_dependency(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

ensure_dependency("requests")
```

### 3. Error Handling

```python
# mytool/__main__.py
import sys

def main():
    try:
        # Your code here
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### 4. Testing Zipapps

```bash
# Test locally before release
python mytool.pyz --help
python mytool.pyz --version

# Test on different Python versions
python3.8 mytool.pyz --help
python3.12 mytool.pyz --help
```

---

## Troubleshooting

### Issue: "No module named X"

**Solution**: Ensure all dependencies are either:
- Bundled in the zipapp
- Available in the target Python environment
- Installed via runtime check

### Issue: "Permission denied" on Unix

**Solution**: Make the file executable:
```bash
chmod +x mytool.pyz
```

### Issue: Windows execution fails

**Solution**: On Windows, run with Python explicitly:
```cmd
python mytool.pyz
```

Or create a `.bat` wrapper:
```batch
@echo off
python "%~dp0mytool.pyz" %*
```

### Issue: Large file size

**Solution**: 
- Use `--exclude` to remove unnecessary files
- Consider using external dependencies instead of bundling
- Use compression (zipapp files are already compressed)

---

## Examples

### Example 1: Bootstrap Tool Zipapp

```bash
# Build
python scripts/build/build-zipapp.py bootstrap-obd.py -o sparetools-bootstrap.pyz

# Test
./sparetools-bootstrap.pyz --help

# Install
sudo mv sparetools-bootstrap.pyz /usr/local/bin/sparetools-bootstrap
```

### Example 2: Custom Tool with Dependencies

```python
# tools/mycli/__main__.py
import sys
import os

# Add vendor directory to path
vendor_path = os.path.join(os.path.dirname(__file__), 'vendor')
if os.path.exists(vendor_path):
    sys.path.insert(0, vendor_path)

from mycli.main import cli

if __name__ == "__main__":
    sys.exit(cli())
```

Build with bundled dependencies:
```bash
pip install -t tools/mycli/vendor requests click
python -m zipapp tools/mycli -o mycli.pyz -p "/usr/bin/env python3"
```

---

## SpareTools Zipapps

The SpareTools project provides official zipapp distributions for key CLI tools. These are built automatically via CI and attached to GitHub releases.

### Available Zipapps

| Zipapp | Purpose | Size (est.) |
|--------|---------|-------------|
| `sparetools-bootstrap.pyz` | Multi-purpose bootstrap for OBD-II simulation and project templating | ~50KB |
| `sparetools-audit-conan.pyz` | Audit Conan recipes for compliance | ~40KB |
| `sparetools-validate-openssl.pyz` | Validate OpenSSL compatibility | ~35KB |
| `sparetools-matrix-generator.pyz` | Generate CI/CD build matrices | ~30KB |
| `sparetools-report-generator.pyz` | Generate CI/CD reports | ~45KB |
| `sparetools-artifact-uploader.pyz` | Upload CI/CD artifacts | ~35KB |
| `sparetools-validate-tier1.pyz` | Tier 1 validation (syntax) | ~25KB |
| `sparetools-validate-tier2.pyz` | Tier 2 validation (dependencies) | ~30KB |
| `sparetools-validate-tier3.pyz` | Tier 3 validation (cross-consumer) | ~40KB |
| `sparetools-validate-tier4.pyz` | Tier 4 validation (integration) | ~45KB |
| `sparetools-validate-tier5.pyz` | Tier 5 validation (security) | ~50KB |
| `sparetools-test-runner.pyz` | Unified test runner | ~35KB |
| `sparetools-test-cross-repo.pyz` | Cross-repository testing | ~30KB |
| `sparetools-doc-linker.pyz` | Documentation cross-referencing | ~25KB |
| `sparetools-bootstrap-helper.pyz` | Bootstrap helper utilities | ~20KB |
| `sparetools-complete-bootstrap.pyz` | Complete bootstrap orchestration | ~25KB |

### Installation

#### Method 1: Download from GitHub Releases

```bash
# Download specific zipapp (replace TOOL_NAME)
TOOL_NAME="sparetools-bootstrap"
curl -s https://api.github.com/repos/sparesparrow/sparetools/releases/latest | \
  sed -n 's/"browser_download_url": //p' | \
  grep "${TOOL_NAME}\.pyz" | \
  xargs wget -qO "${TOOL_NAME}.pyz"

chmod +x "${TOOL_NAME}.pyz"
sudo mv "${TOOL_NAME}.pyz" /usr/local/bin/
```

#### Method 2: Bulk Download All Zipapps

```bash
# Create directory for zipapps
mkdir -p ~/sparetools-zipapps
cd ~/sparetools-zipapps

# Download all zipapps from latest release
curl -s https://api.github.com/repos/sparesparrow/sparetools/releases/latest | \
  jq -r '.assets[] | select(.name | endswith(".pyz")) | .browser_download_url' | \
  xargs -n1 wget -q

# Make all executable and optionally add to PATH
chmod +x *.pyz
echo 'export PATH="$HOME/sparetools-zipapps:$PATH"' >> ~/.bashrc
```

#### Method 3: Manual Installation

```bash
# Build locally from source
git clone https://github.com/sparesparrow/sparetools.git
cd sparetools

# Install PyYAML for manifest parsing
pip install PyYAML

# Build all zipapps
python scripts/build/build-zipapps-from-manifest.py -o ~/sparetools-zipapps

# Install to system PATH
sudo cp ~/sparetools-zipapps/*.pyz /usr/local/bin/
```

### Usage Examples

```bash
# Use bootstrap tool
sparetools-bootstrap --help
sparetools-bootstrap --template=mia --name=my-project

# Use validation tools
sparetools-validate-tier1 --help
sparetools-validate-openssl --help

# Use CI/CD tools
sparetools-matrix-generator --help
sparetools-report-generator --help
```

### Building Zipapps

To build zipapps locally or contribute new ones:

```bash
# Build specific zipapp
python scripts/build/build-zipapp.py bootstrap-obd.py -o sparetools-bootstrap.pyz

# Build all zipapps from manifest
python scripts/build/build-zipapps-from-manifest.py -o dist/

# Build only specific zipapps
python scripts/build/build-zipapps-from-manifest.py --names sparetools-bootstrap sparetools-audit-conan
```

See [`scripts/build/zipapps.yaml`](scripts/build/zipapps.yaml) for the complete manifest of available zipapps.

---

## References

- [Python zipapp Documentation](https://docs.python.org/3/library/zipapp.html)
- [PEP 441 - Improving Python ZIP Application Support](https://peps.python.org/pep-0441/)
- [Cloudsmith CLI Example](https://github.com/cloudsmith-io/cloudsmith-cli)

---

## Related Documentation

- [Package Distribution](docs/PACKAGES.md)
- [CI/CD Guide](docs/CI-CD-GUIDE.md)
- [Quick Reference](docs/QUICK-REFERENCE.md)

