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

## Related Documentation

- [Quick Reference](QUICK-REFERENCE.md) - Quick reference for sparetools
- [Packages](PACKAGES.md) - Complete package documentation
- [MIA Contributor Guide](MIA-CONTRIBUTOR-GUIDE.md) - Guide for MIA contributors
- [Cross-Repo Testing](CROSS-REPO-TESTING.md) - Testing cross-repo dependencies

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
