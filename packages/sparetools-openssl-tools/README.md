# sparetools-openssl-tools

Complete OpenSSL build automation, FIPS validation, and development tools.

## Purpose

Comprehensive tooling for OpenSSL development and deployment, including build automation, FIPS 140-3 validation, security scanning, SBOM generation, and Conan build profiles.

## Installation

```bash
conan export packages/sparetools-openssl-tools --version=1.0.0
```

## Features

- **Build Automation**: Orchestrate complex OpenSSL builds
- **FIPS Validation**: FIPS 140-3 compliance validation and reporting
- **Security Integration**: Trivy scanning, vulnerability management
- **SBOM Generation**: CycloneDX and SPDX support
- **Build Profiles**: 15+ Conan profiles for different platforms/features
- **Version Management**: OpenSSL version detection and management
- **Monitoring**: Build performance and security monitoring
- **Testing**: Integration test runners and validators

## Usage

### As tool_requires

```python
from conan import ConanFile

class MyPackage(ConanFile):
    tool_requires = "sparetools-openssl-tools/1.0.0"
```

### Using Build Profiles

```bash
# Build with specific profile
conan create packages/sparetools-openssl --version=3.3.2 \
  -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b sparetools-openssl-tools/profiles/build-methods/perl-configure \
  -pr:b sparetools-openssl-tools/profiles/features/fips-enabled
```

### CLI Tools

```bash
# FIPS validation
python -m openssl_tools.fips_validator --module fips-3.0.8 --strict

# Generate SBOM
python -m openssl_tools.sbom_generator --format cyclonedx

# Version management
python -m openssl_tools.version_manager list-versions
```

## Included Modules

### Core Modules
- `openssl_tools/build.py` - Build orchestration
- `openssl_tools/cli.py` - Command-line interface
- `openssl_tools/conan_functions.py` - Conan integration

### Automation
- `openssl_tools/automation/build_orchestrator.py` - Build pipeline automation
- `openssl_tools/automation/` - Additional automation tools

### Security
- `openssl_tools/security/fips_validator.py` - FIPS 140-3 validation
- `openssl_tools/security/sbom_generator.py` - SBOM generation
- `openssl_tools/security/` - Security scanning tools

### Core Utilities
- `openssl_tools/core/version_manager.py` - Version management
- `openssl_tools/core/` - Core utilities

## Build Profiles

Located in `profiles/` directory. See `profiles/README.md` for complete documentation.

### Profile Categories

- **base/** - Platform/compiler combinations (linux-gcc11, windows-msvc2022, darwin-clang, etc.)
- **build-methods/** - Build system selection (perl, cmake, autotools, python)
- **features/** - Feature configurations (fips-enabled, shared-libs, static-only, minimal, performance)
- **matrix/** - Build matrix documentation

## Scripts

Located in `scripts/` directory:

- `test-openssl-3.5.2-enhanced.py` - Enhanced OpenSSL testing
- `enhanced-sbom-generator.py` - Advanced SBOM generation
- `implement-parallel-tracks.sh` - Parallel build orchestration
- `monitor-performance.sh` - Performance monitoring
- `monitor-security-results.sh` - Security monitoring
- `run-integration-tests.sh` - Integration test runner
- `verify-bootstrap.sh` - Bootstrap verification
- And 10+ more automation scripts

## Dependencies

- Python 3.8+
- Conan 2.x
- sparetools-base/1.0.0

## Platform Support

All major platforms via profiles:
- Linux (x86_64, ARM64)
- Windows (x86_64)
- macOS (x86_64, ARM64)

## License

Apache-2.0

## Resources

- [Build Profiles Documentation](profiles/README.md)
- [Build Matrix](profiles/matrix/README.md)
- [GitHub Repository](https://github.com/sparesparrow/sparetools)

## Version

Current: 1.0.0

## Related Packages

- sparetools-openssl: Uses these tools for building
- sparetools-base: Foundation utilities
- sparetools-cpython: Python runtime

