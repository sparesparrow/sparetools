# MIA Integration Guide

This guide explains how to integrate sparetools Conan packages into MIA (Main IoT Architecture) projects.

## Overview

SpareTools packages are published to Cloudsmith and can be consumed by MIA projects using standard Conan 2.x dependency management.

## Prerequisites

- **Conan 2.x**: `pip install conan==2.21.0`
- **Python 3.12+**: Required for some sparetools packages
- **Cloudsmith Access**: Access to sparesparrow-conan repository

## Remote Configuration

### 1. Add Cloudsmith Remote

```bash
conan remote add sparesparrow-conan \
  https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/ \
  --force
```

### 2. Verify Remote

```bash
conan remote list
```

You should see `sparesparrow-conan` in the list.

### 3. Authenticate (if needed)

If packages are private, authenticate with Cloudsmith:

```bash
conan remote login sparesparrow-conan sparesparrow --password YOUR_API_KEY
```

## Using SpareTools Packages in MIA

### Basic Usage

Add sparetools packages to your `conanfile.py`:

```python
from conan import ConanFile

class MIAProjectConan(ConanFile):
    name = "mia-project"
    version = "1.0.0"
    
    requires = [
        "sparetools-openssl/3.3.2",
    ]
    
    tool_requires = [
        "sparetools-cpython/3.12.7",  # If you need Python
    ]
    
    python_requires = "sparetools-base/2.0.0"  # For utilities
```

### Installing Dependencies

```bash
# Install all dependencies
conan install . --build=missing

# Install specific package
conan install --requires=sparetools-openssl/3.3.2 --build=missing
```

### Building with Dependencies

```bash
# Build your project
conan build .

# Or use CMake/other build systems
conan install . --build=missing
cmake --build build
```

## Available Packages

### Core Packages

- **sparetools-openssl/3.3.2**: OpenSSL library with multiple build methods
- **sparetools-base/2.0.0**: Foundation utilities (python_requires)
- **sparetools-cpython/3.12.7**: Prebuilt Python 3.12.7 (tool_requires)

### Utility Packages

- **sparetools-openssl-tools/2.0.0**: Build tools and profiles (python_requires)
- **sparetools-bootstrap/2.0.0**: Bootstrap utilities (python_requires)
- **sparetools-shared-dev-tools/2.0.0**: Shared development tools (python_requires)

## Hermetic Python Environments with sparetools-cpython

### Overview

`sparetools-cpython/3.12.7` provides prebuilt CPython 3.12.7 with OpenSSL support, enabling hermetic Python environments for MIA projects. This eliminates system Python dependencies and ensures consistent runtime behavior across different environments.

### Key Features

- **Zero-copy architecture**: Builds directly to package folder
- **Optimization enabled**: Includes `--enable-optimizations` and `--with-lto`
- **Environment isolation**: Sets `PYTHONHOME`, `PATH`, and `LD_LIBRARY_PATH`
- **Conf info exposure**: Provides `user.cpython:executable` and `user.cpython:home`

### Usage in Conan Recipes

```python
from conan import ConanFile

class MIAProjectConan(ConanFile):
    name = "mia-project"
    version = "1.0.0"

    # Get bundled Python as tool requirement
    tool_requires = "sparetools-cpython/3.12.7"

    # Access Python in package_info
    def package_info(self):
        python_exe = self.conf_info["user.cpython:executable"]
        python_home = self.conf_info["user.cpython:home"]

        # Use in build scripts or expose to consumers
        self.buildenv_info.define("MY_PYTHON_EXE", python_exe)
```

### Environment Variables

When consumed, sparetools-cpython automatically sets:

```bash
export PYTHONHOME="/path/to/sparetools-cpython/package"
export PATH="/path/to/sparetools-cpython/bin:$PATH"
export LD_LIBRARY_PATH="/path/to/sparetools-cpython/lib:$LD_LIBRARY_PATH"
```

### Best Practices

1. **Always use bundled Python**: Never rely on system Python in production
2. **Pin versions**: Use exact versions like `sparetools-cpython/3.12.7`
3. **Test with bundled environment**: Run tests using the bundled Python executable
4. **Environment activation**: Use Conan generators like `VirtualRunEnv` for proper environment setup

## sparetools-base Utilities

### Overview

`sparetools-base/2.0.0` provides foundation utilities for common operations across SpareTools packages.

### Available Utilities

- **security-gates.py**: Security validation and gatekeeping functions
- **symlink-helpers.py**: Cross-platform symlink creation and management

### Usage

```python
# In conanfile.py
python_requires = "sparetools-base/2.0.0"

# In build scripts or other Python code
from sparetools_base.security_gates import validate_security
from sparetools_base.symlink_helpers import create_symlink

# Use utilities
if not validate_security():
    raise Exception("Security validation failed")
```

### Integration Pattern

```python
from conan import ConanFile
from sparetools_base.security_gates import validate_build_environment

class SecurePackage(ConanFile):
    python_requires = "sparetools-base/2.0.0"

    def configure(self):
        if not validate_build_environment():
            raise ConanException("Build environment security check failed")
```

## Dependency Resolution

### Version Resolution

Conan will resolve dependencies automatically:

```python
requires = [
    "sparetools-openssl/3.3.2",  # Exact version
    "sparetools-base/[>=2.0.0]",  # Version range
]
```

### Cross-Repository Dependencies

SpareTools packages can depend on other packages from different repositories. Conan will resolve them automatically if remotes are configured correctly.

## Example: MIA Consumer

See `examples/mia-consumer/conanfile.py` for a complete example.

### Running the Example

```bash
cd examples/mia-consumer
conan install . --build=missing
conan build .
```

## Troubleshooting

### Package Not Found

If you get "package not found" errors:

1. Verify remote is configured: `conan remote list`
2. Check package exists: `conan search sparetools-openssl/3.3.2 -r sparesparrow-conan`
3. Verify authentication if packages are private

### Version Conflicts

If you encounter version conflicts:

1. Check your `conanfile.py` for version constraints
2. Use `conan graph explain` to see dependency graph
3. Update to compatible versions

### Build Failures

If builds fail:

1. Check prerequisites: `conan profile detect`
2. Verify build requirements are met
3. Check logs for specific error messages
4. See [CI/CD Troubleshooting](CI-CD-TROUBLESHOOTING.md)

## Best Practices

### 1. Pin Versions

For production, pin exact versions:

```python
requires = [
    "sparetools-openssl/3.3.2",  # Exact version
]
```

### 2. Use Version Ranges for Development

For development, use version ranges:

```python
requires = [
    "sparetools-openssl/[>=3.3.0]",  # Allow patch updates
]
```

### 3. Cache Management

Conan caches packages locally. To clear cache:

```bash
conan remove "sparetools-*/*" --force
```

### 4. CI/CD Integration

In CI/CD pipelines:

1. Configure remote in workflow
2. Cache Conan cache directory
3. Use `--build=missing` for first-time builds

## OBD-II Simulation

For OBD-II development and testing, consume the packaged tool via Conan with bundled CPython:

```bash
# Install with bundled Python environment
conan install --requires=sparetools-obd-sim/2.0.0 \
  --build=missing \
  -r sparesparrow-conan \
  -g VirtualRunEnv \
  -of .conan

# Activate the environment (includes bundled Python)
source .conan/activate.sh        # macOS/Linux
.\.conan\activate.bat            # Windows

# Run the OBD bootstrap script
python -m sparetools_obd
```

The packaged bootstrap now uses bundled CPython from `sparetools-cpython/3.12.7`:
- No system Python dependency required
- Hermetic Python environment via Conan tool requirements
- Automatic environment setup through `VirtualRunEnv` generator
- Installs ELM327-emulator and obd packages in isolated environment
- Launches the emulator in car scenario mode

### Updated Integration Pattern

```python
# In your MIA project conanfile.py
class MIAOBDProject(ConanFile):
    requires = [
        "sparetools-obd-sim/2.0.0",  # Includes bundled Python
    ]
    tool_requires = [
        "sparetools-cpython/3.12.7",  # Explicit Python requirement
    ]
    python_requires = "sparetools-base/2.0.0"  # Utilities
```

See [OBD Simulation Guide](OBD-SIMULATION.md) for detailed usage and troubleshooting.

## Related Documentation

- [Quick Reference](QUICK-REFERENCE.md) - Quick reference for sparetools
- [Packages](PACKAGES.md) - Complete package documentation
- [MIA Contributor Guide](MIA-CONTRIBUTOR-GUIDE.md) - Guide for MIA contributors
- [Cross-Repo Testing](CROSS-REPO-TESTING.md) - Testing cross-repo dependencies
- [OBD Simulation Guide](OBD-SIMULATION.md) - OBD-II simulation setup and usage

## Support

For issues or questions:

1. Check [CI/CD Troubleshooting](CI-CD-TROUBLESHOOTING.md)
2. Review package documentation in [Packages](PACKAGES.md)
3. Open an issue on GitHub

## Version Compatibility

- **Conan**: 2.x required (tested with 2.21.0)
- **Python**: 3.12+ for some packages
- **OpenSSL**: 3.3.2 (latest supported)

## Updates

This integration guide is maintained alongside the codebase. Last updated: 2025-12-03
