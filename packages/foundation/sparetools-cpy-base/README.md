# sparetools-cpy-base

Base CPython environment package for the modular CPY system.

## Overview

`sparetools-cpy-base` is a zero-copy aggregator package that provides:
- **CPython 3.12.7**: Complete Python runtime (bin/, lib/, include/, share/)
- **shared-dev-tools**: SpareTools development utilities and scripts

This package serves as the foundation for specialized environments like HIL testing (`sparetools-cpy-hil`) and MCP development (`sparetools-cpy-mcp`).

## Architecture

```
sparetools-cpy-base/1.0.0
├── requires: sparetools-cpython/3.12.7
└── requires: sparetools-shared-dev-tools/2.0.4
```

The package is **zero-copy**: it doesn't duplicate files, only stores metadata about dependency locations for the `setup-cpy-environment.py` script to create symlinks.

## Usage

### As a Conan Package

```bash
# Install the package
conan install --requires=sparetools-cpy-base/1.0.0

# Use in conanfile.py
class MyPackage(ConanFile):
    def requirements(self):
        self.requires("sparetools-cpy-base/1.0.0")

    def build(self):
        # Access CPython
        cpython_folder = self.dependencies["sparetools-cpy-base"].conf_info.get("user.cpy-base:cpython_folder")
        python_bin = os.path.join(cpython_folder, "bin", "python3")
        self.run(f"{python_bin} my_script.py")
```

### With setup-cpy-environment.py

```bash
# Setup ~/CPY environment
python scripts/setup-cpy-environment.py --env base

# Activate
source ~/CPY/scripts/activate-base.sh

# Use Python
python --version  # Python 3.12.7
python -c "import shared_dev_tools"  # shared-dev-tools available
```

## Building

```bash
# Build the package
conan create packages/foundation/sparetools-cpy-base --build=missing

# Test the package
conan test packages/foundation/sparetools-cpy-base/test_package sparetools-cpy-base/1.0.0
```

## Exposed Configuration

The package exposes the following configuration:
- `user.cpy-base:cpython_folder`: Path to CPython installation
- `user.cpy-base:shared_dev_tools_folder`: Path to shared-dev-tools
- `user.cpy-base:python_version`: Python version (3.12.7)

## Dependencies

- `sparetools-cpython/3.12.7`: Python runtime
- `sparetools-shared-dev-tools/2.0.4`: Development utilities
- `sparetools-base/2.0.3`: Security gates and utilities (python_requires)

## License

Apache-2.0
