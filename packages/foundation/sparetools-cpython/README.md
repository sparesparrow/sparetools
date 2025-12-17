# sparetools-cpython

Prebuilt Python 3.12.7 runtime as a Conan tool_requires package with **zero-copy architecture**.

## Purpose

Provides a consistent, prebuilt Python 3.12.7 runtime for SpareTools packages, eliminating dependency on system Python installations and ensuring build reproducibility. Uses **zero-copy architecture**: builds directly to Conan cache with no intermediate staging directories.

## Installation

```bash
conan install --tool-requires=sparetools-cpython/3.12.7
```

## Features

- **Zero-Copy Build**: Builds directly to Conan cache (`package_folder`) - no `/tmp` staging
- **Prebuilt Python 3.12.7**: Compiled from source with optimizations
- **Cross-platform**: Linux, Windows, macOS support
- **Tool Requires**: Used as build-time dependency
- **Isolated**: No system Python conflicts
- **Optimized**: Built with `--enable-optimizations --with-lto` by default

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

Builds directly to Conan cache (zero-copy):

```bash
cd packages/sparetools-cpython
conan create . --version=3.12.7 --build=missing \
  -o shared=True \
  -o optimize=2
```

**Options:**
- `shared`: Enable shared library build (default: False)
- `fips`: Enable FIPS support (default: False)
- `optimize`: Optimization level 0-3 (default: 2)

**Zero-Copy Verification:**
```bash
# Package goes directly to Conan cache
conan cache path sparetools-cpython/3.12.7

# No intermediate copies - check for /tmp staging:
# ❌ OLD: /tmp/cpython-3.12.7-staging/usr/local
# ✅ NEW: ~/.conan2/p/.../sparetools-cpython/package/.../
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
- sparetools-bootstrap: Uses this for build automation
