# sparetools-shared-dev-tools

Shared development tools and utilities for the SpareTools ecosystem.

## Purpose

Provides reusable development scripts, CLI tools, and utilities used across multiple SpareTools packages. Includes Conan helpers, configuration loaders, file operations, and general-purpose automation scripts.

## Installation

```bash
conan export packages/sparetools-shared-dev-tools --version=1.0.0
```

## Features

- **CLI Tools**: Command-line interface for common operations
- **Conan Utilities**: Helper functions for Conan workflows
- **Configuration Management**: YAML config loading and validation
- **File Operations**: Safe file and directory operations
- **Generic Scripts**: Reusable bash/python scripts

## Usage

### As python_requires

```python
from conan import ConanFile

class MyPackage(ConanFile):
    python_requires = "sparetools-shared-dev-tools/1.0.0"
```

### CLI Usage

```bash
# Show Conan version
python -m shared_dev_tools.cli conan version

# Create symlink
python -m shared_dev_tools.cli file symlink /source /target

# List configurations
python -m shared_dev_tools.cli config list
```

## Included Scripts

Located in `scripts/` directory:

- `setup-conan-env.sh` - Conan environment setup
- `setup-dev-env.sh` - Development environment configuration
- `validate-conan-packages.py` - Package validation tool

## Dependencies

- Python 3.8+
- Conan 2.x

## License

Apache-2.0

## Related Packages

- sparetools-base: Foundation utilities
- sparetools-openssl-tools: OpenSSL-specific tools

