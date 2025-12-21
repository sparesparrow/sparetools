# SpareTools ↔ NucleusESP32 Integration Guide

## Overview

This guide documents the comprehensive integration between SpareTools and NucleusESP32, implementing enterprise-grade stability and scalability for ESP32-based firmware development.

## Architecture

### Core Components

1. **SpareToolsVersions**: Centralized version management
2. **Conan-PlatformIO Bridge**: Seamless dependency management
3. **Enterprise Packages**:
   - `sparetools-hal-sunton`: Hardware abstraction for Sunton displays
   - `sparetools-crypto-suite`: Cryptographic APIs with hardware acceleration
   - `sparetools-ci-templates`: Reusable CI/CD workflows
4. **Enhanced CI/CD**: Multi-board testing, security scanning, quality assurance

### Integration Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   NucleusESP32  │────│  Conan-PlatformIO│────│   SpareTools    │
│   Consumer      │    │      Bridge      │    │   Ecosystem     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌────────────────────┐
                    │  Enterprise CI/CD  │
                    │    Workflows       │
                    └────────────────────┘
```

## Quick Start

### 1. Environment Setup

```bash
# Clone repositories
git clone https://github.com/sparesparrow/sparetools.git
cd sparetools

# Setup Python environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Setup Conan
conan config set general.revisions_enabled=True
conan profile detect --force
```

### 2. Build NucleusESP32

```bash
# Navigate to consumer package
cd packages/consumers/esp32/sparetools-nucleus

# Install dependencies with Conan
conan install . --profile conan_profiles/esp32_sunton_v3.prof --build=missing

# Build with PlatformIO
platformio run -e esp32s3_sunton
```

### 3. Run Tests

```bash
# Run unit tests
conan build .

# Run integration tests (from repository root)
python -m pytest test/integration/ -v
```

## Version Management

### Centralized Version Control

SpareTools uses a centralized version management system to prevent dependency drift:

```python
from sparetools_base import SpareToolsVersions

# Access centralized versions
cpython_version = SpareToolsVersions.versions["cpython"]  # "3.12.7"
gtest_version = SpareToolsVersions.versions["gtest"]     # "1.14.0"
lvgl_version = SpareToolsVersions.versions["lvgl"]       # "8.3.11"
```

### Version Configuration File

Versions are defined in `versions.yaml`:

```yaml
foundation:
  sparetools-base: "2.0.3"
  sparetools-cpython: "3.12.7"

testing:
  gtest: "1.14.0"

embedded:
  lvgl: "8.3.11"
  openssl: "3.3.2"
```

## Conan-PlatformIO Bridge

### Overview

The Conan-PlatformIO bridge provides seamless integration between Conan's dependency management and PlatformIO's build system.

### Basic Usage

```bash
# Bridge command
python scripts/conan_pio_bridge.py \
    --conan-profile esp32_base.prof \
    --pio-env esp32dev \
    --packages "gtest/1.14.0 lvgl/8.3.11"
```

### Advanced Configuration

```python
from shared_dev_tools.conan_pio_bridge import ConanPIOBridge, ConanPackage

# Initialize bridge
bridge = ConanPIOBridge()

# Define packages
packages = [
    ConanPackage("gtest", "1.14.0"),
    ConanPackage("lvgl", "8.3.11", options={"shared": False}),
    ConanPackage("openssl", "3.3.2", options={"fips": True})
]

# Execute bridge
config = bridge.bridge("esp32_security.prof", "esp32s3_sunton", packages)
print(config)  # PlatformIO configuration string
```

### Profile Caching

The bridge caches resolved dependencies to improve build performance:

```
.conan_pio_cache/
├── abc123...json    # Cached configuration
└── install_abc123/  # Cached installation
```

## Enterprise Packages

### Hardware Abstraction Layer (HAL)

The `sparetools-hal-sunton` package provides hardware abstraction for Sunton ESP32-2432S028Rv3 displays:

```cpp
#include <hal/sunton/display.h>

// Initialize display
sunton_display_handle_t* display = sunton_display_init(NULL);
sunton_display_set_brightness(display, 255);

// Initialize touch
sunton_touch_init(NULL);

// Main loop
while (true) {
    uint16_t x, y;
    bool pressed;
    if (sunton_touch_read(&x, &y, &pressed) && pressed) {
        // Handle touch input
    }
}
```

**Conan Integration:**
```python
# conanfile.py
def requirements(self):
    self.requires("sparetools-hal-sunton/1.0.0")

def package_info(self):
    self.cpp_info.libs = ["sparetools-hal-sunton"]
    self.cpp_info.defines = ["SPARETOOLS_HAL_SUNTON_ENABLED=1"]
```

### Cryptographic Suite

The `sparetools-crypto-suite` package provides enterprise-grade cryptographic APIs:

```cpp
#include <crypto/esp32_crypto.h>

// Initialize crypto
esp32_crypto_result_t result = esp32_crypto_init(ESP32_CRYPTO_BACKEND_MBEDTLS);

// AES encryption
esp32_aes_context_t* aes_ctx;
esp32_aes_init(&aes_ctx, key, ESP32_CRYPTO_AES_256, ESP32_CRYPTO_AES_MODE_GCM, true);

// SHA-256 hashing
uint8_t hash[32];
esp32_sha_compute(ESP32_CRYPTO_SHA_256, data, data_len, hash, &hash_len);

// ECC operations
esp32_ecc_context_t* ecc_ctx;
esp32_ecc_init(&ecc_ctx, ESP32_CRYPTO_ECC_P256);
esp32_ecc_generate_keypair(ecc_ctx, private_key, &priv_len, public_key, &pub_len);
```

**Security Profiles:**

- **Basic**: AES-256, SHA-256, ECC-P256
- **Enterprise**: Full hardware acceleration, secure boot, FIPS compliance

### CI/CD Templates

The `sparetools-ci-templates` package provides reusable GitHub Actions workflows:

```yaml
# .github/workflows/ci.yml
name: ESP32 CI/CD

on:
  push:
    branches: [main]
  pull_request:

jobs:
  security:
    uses: sparesparrow/sparetools/.github/workflows/security-scan-template.yml@main
    with:
      scan_level: 'standard'
      fail_on_findings: false

  build:
    uses: sparesparrow/sparetools/.github/workflows/esp32-build-template.yml@main
    with:
      esp32_variants: 'esp32,esp32s3,esp32c3'
      conan_profile: 'esp32_base'

  quality:
    uses: sparesparrow/sparetools/.github/workflows/esp32-quality-template.yml@main
    with:
      coverage_enabled: true
      coverage_threshold: '80'
```

## PlatformIO Integration

### Project Configuration

```ini
; platformio.ini
[platformio]
default_envs = esp32s3_sunton

[env:esp32s3_sunton]
platform = espressif32
board = esp32-s3-devkitc-1
framework = espidf

; Conan-PlatformIO Bridge
extra_scripts = scripts/conan_pio_bridge.py
conan_profile = ../conan_profiles/esp32_sunton_v3.prof

; Build configuration
build_flags =
    -Os
    -DNUCLEUS_ESP32=1
    -DSPARETOOLS_ECOSYSTEM=1
    -DCONFIG_MBEDTLS_HARDWARE_AES=1
```

### Conan Profiles

**esp32_base.prof**: Basic ESP32 configuration
**esp32_s3_sunton.prof**: Sunton display-specific configuration
**esp32_security.prof**: Security-hardened configuration

## CI/CD Workflows

### Multi-Board Build Matrix

```yaml
jobs:
  build-matrix:
    strategy:
      matrix:
        variant: ['esp32', 'esp32s3', 'esp32c3', 'esp32c6']

    steps:
    - uses: actions/checkout@v4

    - name: Setup Conan and PlatformIO
      run: |
        pip install conan==2.21.0
        curl -fsSL https://raw.githubusercontent.com/platformio/platformio-core-installer/master/get-platformio.py | python -

    - name: Build firmware
      run: |
        conan install . --profile esp32_base.prof --build=missing
        platformio run -e ${{ matrix.variant }}
```

### Security Scanning

The enhanced security workflow includes:

- **Secret Scanning**: TruffleHog and Gitleaks
- **Static Analysis**: clang-tidy, cppcheck, ESP-IDF analyzer
- **SCA**: Conan dependency vulnerability scanning
- **Firmware Security**: Binary analysis and entropy checking
- **SBOM Generation**: CycloneDX format

### Quality Assurance

The quality workflow provides:

- **Code Coverage**: Automated coverage reporting (>80% threshold)
- **Complexity Analysis**: McCabe cyclomatic complexity checking
- **Performance Benchmarking**: Regression detection
- **Duplication Detection**: Code clone analysis

## Testing

### Integration Tests

Run the comprehensive integration test suite:

```bash
# Version management tests
python -m pytest test/integration/test_sparetools_versions.py -v

# Bridge functionality tests
python -m pytest test/integration/test_conan_pio_bridge.py -v

# Enterprise packages tests
python -m pytest test/integration/test_enterprise_packages.py -v
```

### Unit Tests

```bash
# Build and run unit tests
conan install . --profile esp32_base.prof
conan build .

# Run tests with coverage
ctest --output-on-failure
```

## Troubleshooting

### Common Issues

**Conan Toolchain Not Found:**
```bash
# Ensure Conan install was run
conan install . --profile esp32_base.prof

# Check CMake configuration
cmake .. -DCMAKE_TOOLCHAIN_FILE=build/conan_toolchain.cmake
```

**PlatformIO Build Failures:**
```bash
# Clear PlatformIO cache
platformio run --target clean

# Rebuild dependencies
conan install . --build=missing
```

**Version Conflicts:**
```python
# Check SpareToolsVersions
from sparetools_base import SpareToolsVersions
print(SpareToolsVersions.versions)
```

### Debug Mode

Enable verbose logging:

```bash
# Conan verbose output
export CONAN_TRACE_FILE=conan.log
conan install . -v

# PlatformIO debug
platformio run -v
```

## Performance Optimization

### Build Optimizations

- **Link Time Optimization (LTO)**: Enabled with `-flto`
- **Function Sections**: Eliminates unused code with `--gc-sections`
- **Profile-Guided Optimization (PGO)**: Available for performance-critical builds

### Memory Optimization

- **ESP32-S3 PSRAM**: Enabled for additional memory
- **Heap Tracing**: Available in debug builds
- **Stack Size Optimization**: Automatic stack analysis

## Security Hardening

### Secure Boot

```cpp
// Enable secure boot verification
esp32_crypto_result_t result = esp32_secure_boot_verify(
    firmware_image, image_len,
    signature, sig_len,
    public_key, key_len
);
```

### Flash Encryption

- Automatic firmware encryption
- Secure key storage
- Anti-rollback protection

### Runtime Security

- Stack canaries
- Address space layout randomization (ASLR)
- Non-executable memory regions

## Migration Guide

### From Legacy Builds

1. **Update conanfile.py**:
   ```python
   # Old
   self.requires("gtest/1.13.0")

   # New
   from sparetools_base import SpareToolsVersions
   self.tool_requires(f"gtest/{SpareToolsVersions.versions['gtest']}")
   ```

2. **Update PlatformIO configuration**:
   ```ini
   ; Add bridge script
   extra_scripts = scripts/conan_pio_bridge.py
   conan_profile = ../conan_profiles/esp32_base.prof
   ```

3. **Update CI workflows**:
   ```yaml
   # Use new reusable workflows
   uses: sparesparrow/sparetools/.github/workflows/esp32-build-template.yml@main
   ```

## Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run integration tests
5. Submit pull request

### Code Standards

- **C++**: C++17 with ESP-IDF extensions
- **Python**: PEP 8 with type hints
- **Documentation**: Markdown with code examples
- **Testing**: 80%+ coverage requirement

## Support

### Resources

- **Documentation**: https://github.com/sparesparrow/sparetools/docs/
- **Issues**: https://github.com/sparesparrow/sparetools/issues
- **Discussions**: https://github.com/sparesparrow/sparetools/discussions

### Getting Help

1. Check existing documentation
2. Search GitHub issues
3. Create a new issue with:
   - PlatformIO environment
   - Conan profile used
   - Full error output
   - Steps to reproduce

---

This integration provides a solid foundation for enterprise-grade ESP32 firmware development with SpareTools. The modular architecture ensures scalability while maintaining security and performance standards.