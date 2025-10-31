# SpareTools OpenSSL Build Profiles

Conan 2.x profiles for building OpenSSL with different configurations, platforms, and features.

## Structure

```
profiles/
├── base/              # Platform and compiler combinations
├── build-methods/     # Build system selection (perl, cmake, autotools, python)
├── features/          # Feature-specific configurations (FIPS, shared/static, etc.)
└── matrix/            # Build matrix documentation
```

## Quick Start

### Basic Usage

```bash
# Build with default (linux-gcc11 + perl)
conan create packages/sparetools-openssl --version=3.3.2 \
  -pr:h default \
  -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11

# Build with CMake
conan create packages/sparetools-openssl --version=3.3.2 \
  -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b sparetools-openssl-tools/profiles/build-methods/cmake-build
```

### Profile Composition

Profiles can be layered to combine settings:

```bash
# Linux GCC + Perl Configure + FIPS
conan create packages/sparetools-openssl --version=3.3.2 \
  -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b sparetools-openssl-tools/profiles/build-methods/perl-configure \
  -pr:b sparetools-openssl-tools/profiles/features/fips-enabled

# macOS ARM64 + Python configure + Shared libs
conan create packages/sparetools-openssl --version=3.3.2 \
  -pr:b sparetools-openssl-tools/profiles/base/darwin-clang-arm64 \
  -pr:b sparetools-openssl-tools/profiles/build-methods/python-configure \
  -pr:b sparetools-openssl-tools/profiles/features/shared-libs
```

## Base Profiles (Platform/Compiler)

### Linux Profiles

#### `base/linux-gcc11`
- **Platform**: Linux x86_64
- **Compiler**: GCC 11
- **Use case**: Primary development, Ubuntu 22.04+

```bash
conan create . -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11
```

#### `base/linux-clang14`
- **Platform**: Linux x86_64
- **Compiler**: Clang 14
- **Use case**: Alternative toolchain, LLVM ecosystem

```bash
conan create . -pr:b sparetools-openssl-tools/profiles/base/linux-clang14
```

#### `base/linux-gcc11-arm64`
- **Platform**: Linux ARM64 (aarch64)
- **Compiler**: GCC 11 (cross-compilation)
- **Use case**: ARM servers, Raspberry Pi, embedded ARM

```bash
conan create . -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11-arm64
```

### Windows Profiles

#### `base/windows-msvc2022`
- **Platform**: Windows x86_64
- **Compiler**: MSVC 193 (Visual Studio 2022)
- **Use case**: Windows desktop/server applications

```bash
conan create . -pr:b sparetools-openssl-tools/profiles/base/windows-msvc2022
```

### macOS Profiles

#### `base/darwin-clang`
- **Platform**: macOS x86_64 (Intel)
- **Compiler**: Apple Clang 15
- **Use case**: Intel Macs

```bash
conan create . -pr:b sparetools-openssl-tools/profiles/base/darwin-clang
```

#### `base/darwin-clang-arm64`
- **Platform**: macOS ARM64 (Apple Silicon)
- **Compiler**: Apple Clang 15
- **Use case**: M1/M2/M3 Macs

```bash
conan create . -pr:b sparetools-openssl-tools/profiles/base/darwin-clang-arm64
```

## Build Method Profiles

### `build-methods/perl-configure` (Default)
- **Method**: Standard Perl Configure script
- **Status**: Production-ready, most stable
- **Recommendation**: Default for all production builds

```bash
conan create . -pr:b sparetools-openssl-tools/profiles/build-methods/perl-configure
```

### `build-methods/cmake-build`
- **Method**: CMake build system
- **Status**: Experimental (if supported by OpenSSL version)
- **Recommendation**: Use for modern CMake workflows

```bash
conan create . -pr:b sparetools-openssl-tools/profiles/build-methods/cmake-build
```

### `build-methods/autotools`
- **Method**: Conan Autotools integration
- **Status**: Supported for cross-compilation
- **Recommendation**: Use for embedded/cross-compilation scenarios

```bash
conan create . -pr:b sparetools-openssl-tools/profiles/build-methods/autotools
```

### `build-methods/python-configure`
- **Method**: Python configure.py (SpareTools innovation)
- **Status**: Experimental (65% feature parity)
- **Recommendation**: Testing and Python-centric environments only

```bash
conan create . -pr:b sparetools-openssl-tools/profiles/build-methods/python-configure
```

## Feature Profiles

### `features/fips-enabled`
- **Feature**: FIPS 140-3 compliance mode
- **Options**: `fips=True`, `enable_legacy=False`
- **Use case**: Government/enterprise compliance requirements

```bash
conan create . \
  -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b sparetools-openssl-tools/profiles/features/fips-enabled
```

### `features/shared-libs`
- **Feature**: Shared library build (.so, .dll, .dylib)
- **Options**: `shared=True`
- **Use case**: Dynamic linking, plugin architectures

```bash
conan create . \
  -pr:b sparetools-openssl-tools/profiles/features/shared-libs
```

### `features/static-only`
- **Feature**: Static library build (.a, .lib)
- **Options**: `shared=False`
- **Use case**: Single-binary distributions, embedded systems

```bash
conan create . \
  -pr:b sparetools-openssl-tools/profiles/features/static-only
```

### `features/minimal`
- **Feature**: Minimal build configuration
- **Options**: Disables threads, asm, zlib, legacy algorithms
- **Use case**: Constrained embedded systems, minimal footprint

```bash
conan create . \
  -pr:b sparetools-openssl-tools/profiles/features/minimal
```

### `features/performance`
- **Feature**: Performance-optimized build
- **Options**: Enables all optimizations (threads, asm, zlib)
- **Use case**: High-performance servers, throughput-critical applications

```bash
conan create . \
  -pr:b sparetools-openssl-tools/profiles/features/performance
```

## Profile Composition Examples

### Example 1: Production Linux Build with FIPS

```bash
conan create packages/sparetools-openssl --version=3.3.2 \
  -pr:h default \
  -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b sparetools-openssl-tools/profiles/build-methods/perl-configure \
  -pr:b sparetools-openssl-tools/profiles/features/fips-enabled
```

### Example 2: Windows Development Build

```bash
conan create packages/sparetools-openssl --version=3.3.2 \
  -pr:h default \
  -pr:b sparetools-openssl-tools/profiles/base/windows-msvc2022 \
  -pr:b sparetools-openssl-tools/profiles/build-methods/cmake-build \
  -pr:b sparetools-openssl-tools/profiles/features/shared-libs
```

### Example 3: macOS M1/M2 with Python Configure

```bash
conan create packages/sparetools-openssl --version=3.3.2 \
  -pr:h default \
  -pr:b sparetools-openssl-tools/profiles/base/darwin-clang-arm64 \
  -pr:b sparetools-openssl-tools/profiles/build-methods/python-configure \
  -pr:b sparetools-openssl-tools/profiles/features/performance
```

### Example 4: Embedded ARM with Minimal Config

```bash
conan create packages/sparetools-openssl --version=3.3.2 \
  -pr:h default \
  -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11-arm64 \
  -pr:b sparetools-openssl-tools/profiles/build-methods/autotools \
  -pr:b sparetools-openssl-tools/profiles/features/minimal
```

## Build Matrix

See `matrix/README.md` for complete build matrix documentation and CI/CD integration examples.

## Creating Custom Profiles

You can create custom profiles by inheriting from existing ones:

```ini
# custom-profile
include(sparetools-openssl-tools/profiles/base/linux-gcc11)
include(sparetools-openssl-tools/profiles/features/fips-enabled)

[options]
# Add your custom options
sparetools-openssl/*:enable_zlib=False

[conf]
# Add your custom configuration
tools.build:jobs=16
```

## Profile Validation

Validate your profile before building:

```bash
conan profile show sparetools-openssl-tools/profiles/base/linux-gcc11
```

## CI/CD Integration

### GitHub Actions Example

```yaml
strategy:
  matrix:
    include:
      - os: ubuntu-22.04
        profile: base/linux-gcc11
        method: build-methods/perl-configure
      - os: windows-2022
        profile: base/windows-msvc2022
        method: build-methods/cmake-build
      - os: macos-14
        profile: base/darwin-clang-arm64
        method: build-methods/python-configure

steps:
  - name: Build OpenSSL
    run: |
      conan create packages/sparetools-openssl --version=3.3.2 \
        -pr:b sparetools-openssl-tools/profiles/${{ matrix.profile }} \
        -pr:b sparetools-openssl-tools/profiles/${{ matrix.method }}
```

## Troubleshooting

### Profile Not Found

```bash
# Error: Profile not found
# Solution: Use full path or add to conan profile path
conan config home  # Shows config location
# Copy profiles to: <config_home>/profiles/
```

### Profile Conflicts

```bash
# Error: Conflicting settings/options
# Solution: Order matters - last profile wins
# Wrong:
-pr:b features/shared-libs -pr:b features/static-only  # Conflict!
# Right:
-pr:b features/static-only  # Only one linkage type
```

### Build Method Not Supported

```bash
# Error: CMake not supported by OpenSSL version
# Solution: Use fallback (profile auto-detects and falls back to perl)
# Or explicitly use perl:
-pr:b build-methods/perl-configure
```

## License

Apache-2.0

## Related Documentation

- [SpareTools OpenSSL Package README](../README.md)
- [Conan Profiles Documentation](https://docs.conan.io/2/reference/config_files/profiles.html)
- [Build Matrix](matrix/README.md)

