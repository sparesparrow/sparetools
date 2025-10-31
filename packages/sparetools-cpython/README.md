# sparetools-cpython

Prebuilt Python 3.12.7 runtime as a Conan tool_requires package.

## Purpose

Provides a consistent, prebuilt Python 3.12.7 runtime for SpareTools packages, eliminating dependency on system Python installations and ensuring build reproducibility.

## Installation

```bash
conan install --tool-requires=sparetools-cpython/3.12.7
```

## Features

- **Prebuilt Python 3.12.7**: No compilation required
- **Cross-platform**: Linux, Windows, macOS support
- **Tool Requires**: Used as build-time dependency
- **Isolated**: No system Python conflicts

## Usage

### In conanfile.py

```python
from conan import ConanFile

class MyPackage(ConanFile):
    tool_requires = "sparetools-cpython/3.12.7"
    
    def build(self):
        # Python 3.12.7 is now in PATH
        self.run("python3 --version")
        self.run("python3 my_build_script.py")
```

### In Profiles

```ini
[tool_requires]
sparetools-cpython/3.12.7
```

## Configuration

No configuration required. Python is automatically added to PATH when used as tool_requires.

## Build from Source

If prebuilt binaries not available:

```bash
conan create packages/sparetools-cpython --version=3.12.7 --build=missing
```

## Platform Support

| Platform | Status |
|----------|--------|
| Linux x86_64 | ✅ Tested |
| Windows x86_64 | ⏳ Planned |
| macOS x86_64 | ⏳ Planned |
| macOS ARM64 | ⏳ Planned |

## License

Apache-2.0 (package), Python Software Foundation License (Python itself)

## Version

Current: 3.12.7

## Related Packages

- sparetools-base: Uses this for Python scripts
- sparetools-openssl: Uses for Python configure.py
