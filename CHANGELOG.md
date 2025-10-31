# Changelog

All notable changes to the SpareTools OpenSSL DevOps Ecosystem will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-31

### 🚨 Breaking Changes

This is a major version with significant architectural changes. Migration required for existing users.

#### Removed Packages
- **sparetools-openssl-cmake** - Consolidated into unified `sparetools-openssl` package
- **sparetools-openssl-autotools** - Consolidated into unified `sparetools-openssl` package
- **sparetools-openssl-hybrid** - Consolidated into unified `sparetools-openssl` package
- **sparetools-openssl-tools-mini** - Scripts migrated to appropriate packages

#### Changed Behavior
- Build method now specified via Conan option instead of separate packages
- Scripts from mini package redistributed to `sparetools-shared-dev-tools` and `sparetools-openssl-tools`
- Profile-based configuration system replaces hardcoded build variants

### Added

#### Package Consolidation
- **Unified OpenSSL Package**: Single `sparetools-openssl` package with multiple build methods
  - Build method selection via `-o sparetools-openssl/*:build_method=<method>`
  - Supported methods: `perl`, `cmake`, `autotools`, `python_configure`
- **27,621-byte configure.py**: Python replacement for Perl Configure (experimental)
  - Functional for Makefile generation
  - Platform detection for Linux, macOS, Windows, BSD
  - 65% feature parity with Perl Configure

#### Conan Build Profiles (15 Total)
- **Base Profiles** (6):
  - linux-gcc11, linux-clang14, linux-gcc11-arm64
  - windows-msvc2022, darwin-clang, darwin-clang-arm64
- **Build Method Profiles** (4):
  - perl-configure, cmake-build, autotools, python-configure
- **Feature Profiles** (5):
  - fips-enabled, shared-libs, static-only, minimal, performance

#### GitHub Actions Workflows
- **build-test.yml**: Multi-platform matrix builds (Linux, Windows, macOS)
- **security.yml**: Trivy, Syft SBOM, CodeQL analysis
- **release.yml**: Automated Cloudsmith deployment
- **integration.yml**: Consumer project testing, FIPS validation

#### Documentation
- **README.md** for all 7 packages:
  - sparetools-base, sparetools-cpython, sparetools-openssl
  - sparetools-openssl-tools, sparetools-shared-dev-tools
  - sparetools-bootstrap, sparetools-mcp-orchestrator
- **Profiles Documentation**:
  - 450+ line profiles/README.md
  - 350+ line profiles/matrix/README.md with CI/CD examples
- **PROGRESS-REPORT.md**: Comprehensive status tracking

### Changed

#### sparetools-shared-dev-tools
- Added generic scripts from mini package:
  - setup-conan-env.sh, setup-dev-env.sh
  - validate-conan-packages.py
- Updated `conanfile.py` to export `scripts/` directory

#### sparetools-openssl-tools
- Added OpenSSL-specific scripts from mini package (15 scripts)
- Added Python modules: build_orchestrator.py, version_manager.py, fips_validator.py
- Created `profiles/` directory structure
- Updated `conanfile.py` to export profiles and scripts

#### sparetools-openssl
- Replaced placeholder with comprehensive unified package
- 560+ line `conanfile.py` with dynamic build method selection
- Integrated configure.py (27,621 bytes) for Python-based configuration
- Created `test_package/` with CMake integration tests
- Comprehensive README (600+ lines)

### Fixed
- Removed redundant `sparetools-openssl-tools-mini` package
- Eliminated duplicate script maintenance
- Consolidated variant packages into single configurable package
- Improved package organization and separation of concerns

### Security
- Integrated Trivy vulnerability scanning
- Automated SBOM generation (CycloneDX and SPDX formats)
- CodeQL static analysis
- FIPS validation framework

### Migration Guide

#### For v1.x Users

**Before (v1.x):**
```bash
# Separate packages for each build method
conan install --requires=sparetools-openssl-cmake/3.3.2
```

**After (v2.0.0):**
```bash
# Single package with build method option
conan install --requires=sparetools-openssl/2.0.0 \
  -o sparetools-openssl/*:build_method=cmake

# Or use profiles
conan install --requires=sparetools-openssl/2.0.0 \
  -pr:b sparetools-openssl-tools/profiles/build-methods/cmake-build \
  -pr:b sparetools-openssl-tools/profiles/features/fips-enabled
```

**Script Locations Changed:**
- Generic scripts: `sparetools-shared-dev-tools/scripts/`
- OpenSSL scripts: `sparetools-openssl-tools/scripts/`
- Build automation: `sparetools-openssl-tools/automation/`

#### Profile-Based Configuration

**Example: FIPS Build:**
```bash
conan create packages/sparetools-openssl --version=2.0.0 \
  -pr:b packages/sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b packages/sparetools-openssl-tools/profiles/build-methods/perl-configure \
  -pr:b packages/sparetools-openssl-tools/profiles/features/fips-enabled
```

**Example: Minimal Static Build:**
```bash
conan create packages/sparetools-openssl --version=2.0.0 \
  -pr:b packages/sparetools-openssl-tools/profiles/features/static-only \
  -pr:b packages/sparetools-openssl-tools/profiles/features/minimal
```

### Known Issues
- Python configure.py provider ordering incomplete (50% complete)
- Assembly optimizations not implemented in Python configure
- Cross-compilation not supported in Python configure
- Windows platform testing incomplete

### Contributors
- sparesparrow (@sparesparrow)

---

## [1.0.0] - 2025-10-30

### Added
- Initial release of SpareTools OpenSSL DevOps Ecosystem
- 8 core packages:
  - sparetools-base/1.0.0
  - sparetools-cpython/3.12.7
  - sparetools-shared-dev-tools/1.0.0
  - sparetools-bootstrap/1.0.0
  - sparetools-openssl-tools/1.0.0
  - sparetools-openssl-tools-mini/1.0.0
  - sparetools-mcp-orchestrator/1.0.0
  - sparetools-openssl/3.3.2
- OpenSSL 3.3.2 successfully packaged
- Zero-copy deployment pattern (symlink-based)
- Security gates integration (Trivy, Syft, FIPS)
- Bootstrap automation with 3-agent orchestration
- MCP integration for AI-assisted development

---

## Version History

- **2.0.0** (2025-10-31) - Major consolidation and modernization
- **1.0.0** (2025-10-30) - Initial release

---

## Links

- **Repository**: https://github.com/sparesparrow/sparetools
- **Cloudsmith**: https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/
- **Issues**: https://github.com/sparesparrow/sparetools/issues
- **Documentation**: https://github.com/sparesparrow/sparetools/tree/main/docs

