# sparetools-openssl

Unified OpenSSL package with multiple build method support for the SpareTools ecosystem.

## Purpose

This package provides a flexible, production-ready OpenSSL library with support for multiple build methods (Perl Configure, CMake, Autotools, Python configure.py). It consolidates all OpenSSL build variants into a single package, simplifying dependency management while providing maximum flexibility for different build environments and requirements.

## Features

- **Multiple Build Methods**: Choose between Perl Configure (default), CMake, Autotools, or Python configure.py
- **FIPS Support**: Optional FIPS 140-3 compliance mode
- **Security Integration**: Built-in Trivy scanning and SBOM generation
- **Cross-Platform**: Linux, Windows, macOS support
- **Configurable**: Extensive options for shared/static libs, threading, assembly optimizations
- **Production-Ready**: Based on proven ConanCenter patterns with SpareTools enhancements

## Installation

### Basic Installation

```bash
conan install --requires=sparetools-openssl/3.3.2
```

### With Specific Build Method

```bash
# Using CMake build
conan install --requires=sparetools-openssl/3.3.2 \
  -o sparetools-openssl/*:build_method=cmake

# Using Python configure.py  
conan install --requires=sparetools-openssl/3.3.2 \
  -o sparetools-openssl/*:build_method=python

# Using Autotools integration
conan install --requires=sparetools-openssl/3.3.2 \
  -o sparetools-openssl/*:build_method=autotools
```

### With Conan Profiles

```bash
# Using build profile
conan install --requires=sparetools-openssl/3.3.2 \
  -pr:h default \
  -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b sparetools-openssl-tools/profiles/build-methods/perl-configure
```

## Configuration Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `build_method` | perl, cmake, autotools, python | perl | Build system to use |
| `shared` | True, False | False | Build shared libraries |
| `fPIC` | True, False | True | Position-independent code |
| `fips` | True, False | False | Enable FIPS 140-3 mode |
| `enable_threads` | True, False | True | Threading support |
| `enable_asm` | True, False | True | Assembly optimizations |
| `enable_zlib` | True, False | True | Zlib compression |
| `enable_legacy` | True, False | False | Legacy algorithms (MD2, MD4, RC5) |

## Usage

### C/C++ Project (CMake)

```cmake
find_package(OpenSSL REQUIRED)

add_executable(myapp main.c)
target_link_libraries(myapp OpenSSL::SSL OpenSSL::Crypto)
```

### conanfile.txt

```ini
[requires]
sparetools-openssl/3.3.2

[generators]
CMakeDeps
CMakeToolchain

[options]
sparetools-openssl/*:build_method=perl
sparetools-openssl/*:fips=False
```

### conanfile.py

```python
from conan import ConanFile

class MyProjectConan(ConanFile):
    requires = "sparetools-openssl/3.3.2"
    
    def configure(self):
        # Configure OpenSSL options
        self.options["sparetools-openssl"].build_method = "perl"
        self.options["sparetools-openssl"].shared = False
        self.options["sparetools-openssl"].fips = True
```

## Build Methods Explained

### 1. Perl Configure (Default - Production)

The standard, battle-tested OpenSSL build system.

**Pros:**
- Most stable and reliable
- Full OpenSSL feature support
- Proven in production
- Best compatibility

**When to use:** Production deployments, when stability is critical

### 2. CMake

Modern CMake-based build (if supported by OpenSSL version).

**Pros:**
- Better IDE integration
- Native Conan CMake support
- Faster configuration

**When to use:** Development environments, Windows builds, modern toolchains

### 3. Autotools

Conan Autotools integration wrapper around Perl Configure.

**Pros:**
- Standardized Conan Autotools patterns
- Cross-compilation support
- Toolchain integration

**When to use:** Cross-compilation scenarios, embedded targets

### 4. Python configure.py (Experimental)

Modern Python replacement for Perl Configure (SpareTools innovation).

**Pros:**
- Pure Python (no Perl dependency)
- Extensible and maintainable
- Modern Python tooling

**When to use:** Python-centric environments, when extending build logic

**Note:** Currently at 65% feature parity with Perl Configure. Production use requires testing.

## Dependencies

### Requirements
- None (standalone library)

### Tool Requirements
- `sparetools-openssl-tools/1.0.0` - Build automation tools
- `sparetools-cpython/3.12.7` - Python runtime for scripts

### Python Requirements
- `sparetools-base/1.0.0` - Foundation utilities

## Security Features

### Vulnerability Scanning

Automatic Trivy scanning during build (if sparetools-base available):

```bash
conan create packages/sparetools-openssl --version=3.3.2
# Trivy scan runs automatically
```

### SBOM Generation

Software Bill of Materials generated automatically:

```bash
# SBOM output in CycloneDX format
# Located in: <package_folder>/sbom.json
```

### FIPS Mode

Enable FIPS 140-3 compliance:

```bash
conan install --requires=sparetools-openssl/3.3.2 \
  -o sparetools-openssl/*:fips=True
```

## Development

### Building Locally

```bash
cd packages/sparetools-openssl
conan create . --version=3.3.2 --build=missing
```

### Testing

```bash
conan test test_package sparetools-openssl/3.3.2@
```

### With Different Build Methods

```bash
# Test Perl Configure
conan create . --version=3.3.2 -o build_method=perl

# Test CMake
conan create . --version=3.3.2 -o build_method=cmake

# Test Python configure.py
conan create . --version=3.3.2 -o build_method=python
```

## Platform Support

| Platform | Architecture | Status | Notes |
|----------|-------------|---------|-------|
| Linux | x86_64 | ✅ Tested | Primary development platform |
| Linux | ARM64 | ✅ Supported | Via cross-compilation |
| Windows | x86_64 | ✅ Supported | Requires Visual Studio |
| macOS | x86_64 | ✅ Supported | Intel Macs |
| macOS | ARM64 | ✅ Supported | Apple Silicon (M1/M2) |
| FreeBSD | x86_64 | ⚠️ Experimental | Limited testing |

## Troubleshooting

### Build Fails with Provider Errors

OpenSSL 3.x has complex provider dependencies. If build fails:

1. Try disabling legacy algorithms: `-o enable_legacy=False`
2. Use Perl Configure method: `-o build_method=perl`
3. Check OpenSSL version compatibility

### Python configure.py Fails

The Python configure is experimental. Fallback options:

1. Use Perl Configure: `-o build_method=perl`
2. Report issues to: https://github.com/sparesparrow/sparetools/issues

### FIPS Validation Errors

FIPS mode requires specific configuration:

1. Use OpenSSL 3.0+ with FIPS module
2. Enable with: `-o fips=True`
3. Validate with: `sparetools-openssl-tools fips-validator`

## Migration from Separate Packages

If you were using the old separate packages:

```bash
# Old way (deprecated)
conan install --requires=sparetools-openssl-cmake/3.3.2
conan install --requires=sparetools-openssl-hybrid/3.3.2

# New way (unified)
conan install --requires=sparetools-openssl/3.3.2 -o build_method=cmake
conan install --requires=sparetools-openssl/3.3.2 -o build_method=python
```

See `docs/MIGRATION-GUIDE.md` for complete migration details.

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

### Reporting Issues

https://github.com/sparesparrow/sparetools/issues

### Development Setup

```bash
git clone git@github.com:sparesparrow/sparetools.git
cd sparetools/packages/sparetools-openssl
conan create . --version=3.3.2 --build=missing
```

## License

Apache-2.0

See LICENSE file for details.

## Related Packages

- **sparetools-openssl-tools**: Build automation and FIPS validation tools
- **sparetools-base**: Foundation utilities and security gates
- **sparetools-cpython**: Python 3.12.7 runtime

## Resources

- **OpenSSL Homepage**: https://www.openssl.org
- **SpareTools Repository**: https://github.com/sparesparrow/sparetools
- **Cloudsmith Repository**: https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/
- **Documentation**: https://github.com/sparesparrow/sparetools/tree/main/docs

## Version History

### 3.3.2 (Current)
- Unified package consolidating all build variants
- Support for 4 build methods (Perl, CMake, Autotools, Python)
- FIPS 140-3 support
- Security gates integration
- Comprehensive test suite

---

**Part of the SpareTools Ecosystem** - Modern DevOps tooling for OpenSSL development

