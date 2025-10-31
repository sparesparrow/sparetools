# SpareTools OpenSSL DevOps Ecosystem

[![Build and Test](https://img.shields.io/github/actions/workflow/status/sparesparrow/sparetools/build-test.yml?branch=main&label=build&logo=github)](https://github.com/sparesparrow/sparetools/actions)
[![Security Scanning](https://img.shields.io/github/actions/workflow/status/sparesparrow/sparetools/security.yml?branch=main&label=security&logo=github)](https://github.com/sparesparrow/sparetools/actions)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Conan](https://img.shields.io/badge/conan-2.21.0%2B-orange.svg)](https://conan.io)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org)

Modern, Python-based tooling ecosystem for OpenSSL development, building, and deployment.

## 🎯 Features

- **🔧 Unified OpenSSL Package**: Single package with multiple build methods (Perl, CMake, Autotools, Python)
- **📋 Conan Profile System**: 15+ comprehensive profiles for platform/compiler/feature combinations
- **🔒 Security First**: Integrated Trivy, Syft SBOM, CodeQL, and FIPS validation
- **🚀 CI/CD Ready**: GitHub Actions workflows for multi-platform builds
- **⚡ Zero-Copy Deployment**: Symlink-based pattern for 80% disk space savings
- **🐍 Python Configure**: Experimental 27KB Python replacement for Perl Configure (65% feature parity)
- **🌍 Cross-Platform**: Linux, Windows, macOS support

---

## 📦 Packages

| Package | Version | Purpose |
|---------|---------|---------|
| **sparetools-openssl** | 2.0.0 | Unified OpenSSL library with multi-method builds |
| **sparetools-openssl-tools** | 2.0.0 | Build automation, FIPS validation, security scanning |
| **sparetools-base** | 2.0.0 | Foundation utilities and security gates |
| **sparetools-cpython** | 3.12.7 | Prebuilt Python 3.12.7 runtime |
| **sparetools-shared-dev-tools** | 2.0.0 | Shared development utilities |
| **sparetools-bootstrap** | 2.0.0 | Bootstrap automation (3-agent orchestration) |
| **sparetools-mcp-orchestrator** | 2.0.0 | MCP integration for AI-assisted development |

---

## 🚀 Quick Start

### Installation

```bash
# Add Cloudsmith remote
conan remote add sparesparrow-conan \
  https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/

# Install OpenSSL package
conan install --requires=sparetools-openssl/2.0.0 \
  --tool-requires=sparetools-openssl-tools/2.0.0 \
  --build=missing
```

### Build with Specific Method

```bash
# Using Perl Configure (default, most stable)
conan create packages/sparetools-openssl --version=2.0.0 \
  -o sparetools-openssl/*:build_method=perl_configure \
  --build=missing

# Using CMake (modern, IDE-friendly)
conan create packages/sparetools-openssl --version=2.0.0 \
  -o sparetools-openssl/*:build_method=cmake \
  --build=missing

# Using Python Configure (experimental)
conan create packages/sparetools-openssl --version=2.0.0 \
  -o sparetools-openssl/*:build_method=python_configure \
  --build=missing
```

### Build with Profiles

```bash
# FIPS-enabled build
conan create packages/sparetools-openssl --version=2.0.0 \
  -pr:b packages/sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b packages/sparetools-openssl-tools/profiles/features/fips-enabled \
  --build=missing

# Performance-optimized build
conan create packages/sparetools-openssl --version=2.0.0 \
  -pr:b packages/sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b packages/sparetools-openssl-tools/profiles/features/performance \
  --build=missing
```

---

## 📚 Documentation

- **[CHANGELOG.md](CHANGELOG.md)** - Version history and breaking changes
- **[CLAUDE.md](CLAUDE.md)** - Developer guidance and architecture overview
- **[Migration Guide](docs/MIGRATION-GUIDE.md)** - Upgrading from v1.x to v2.0.0
- **[Package READMEs](packages/)** - Individual package documentation
- **[Profiles Guide](packages/sparetools-openssl-tools/profiles/README.md)** - Profile system documentation
- **[_Build Directory](_Build/README.md)** - Zero-copy build artifacts explanation
- **[Build Results](build_results/)** - Build reports and validation output
- **[Reviews](reviews/)** - Release reviews and comprehensive summaries

---

## 🏗️ Architecture

### Directory Structure

```
sparetools/
├── packages/                 # Conan packages (source)
├── _Build/                   # Build artifacts (zero-copy symlinks)
│   ├── openssl-builds/       # OpenSSL build results
│   ├── packages/             # Symlinks to Conan cache
│   └── conan-cache -> ~/.conan2
├── build_results/            # Build reports
├── reviews/                  # Release reviews
├── test_results/             # Test reports
├── test/integration/         # Integration test suite
├── scripts/                  # Automation scripts
├── docs/                     # Documentation
└── workspaces/               # VS Code workspace configs
```

**Zero-Copy Pattern**: The `_Build/` directory uses symlinks to `~/.conan2/` to avoid duplicating binaries, saving 80%+ disk space. See [_Build/README.md](_Build/README.md) for details.

### Package Dependencies

```
sparetools-openssl (production)
├── tool_requires: sparetools-openssl-tools (FIPS, security, profiles)
├── tool_requires: sparetools-cpython (Python runtime)
└── python_requires: sparetools-base (foundation utilities)

sparetools-openssl-tools
└── python_requires: sparetools-base

sparetools-shared-dev-tools
└── python_requires: sparetools-base
```

### Build System Options

The unified `sparetools-openssl` package supports multiple build methods:

1. **perl_configure** (default) - Standard OpenSSL Perl Configure
2. **cmake** - Modern CMake build system
3. **autotools** - Unix Autotools integration
4. **python_configure** - Experimental Python-based configuration

### Profile System

Profiles are organized in three categories:

```
profiles/
├── base/              # Platform + compiler (6 profiles)
│   ├── linux-gcc11
│   ├── linux-clang14
│   ├── linux-gcc11-arm64
│   ├── windows-msvc2022
│   ├── darwin-clang
│   └── darwin-clang-arm64
├── build-methods/     # Build system (4 profiles)
│   ├── perl-configure
│   ├── cmake-build
│   ├── autotools
│   └── python-configure
└── features/          # Feature toggles (5 profiles)
    ├── fips-enabled
    ├── shared-libs
    ├── static-only
    ├── minimal
    └── performance
```

---

## 🔒 Security

### Integrated Security Tools

- **Trivy**: Vulnerability scanning (container & filesystem)
- **Syft**: SBOM generation (CycloneDX, SPDX formats)
- **CodeQL**: Static code analysis
- **FIPS**: Validation framework for FIPS 140-3 compliance

### Security Workflows

```bash
# Run security scan locally
trivy fs --security-checks vuln .

# Generate SBOM
syft dir:. -o cyclonedx-json > sbom.json

# FIPS validation (requires built OpenSSL)
python -m sparetools.openssl_tools.fips_validator --strict
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/sparesparrow/sparetools.git
cd sparetools

# Install Conan
pip install conan==2.21.0

# Configure remotes
conan remote add sparesparrow-conan \
  https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/

# Build locally
cd packages/sparetools-openssl
conan create . --version=2.0.0 --build=missing
```

### Running Tests

```bash
# Unit tests
pytest tests/

# Integration tests
conan test test_package sparetools-openssl/2.0.0@

# Full CI/CD locally
act -W .github/workflows/build-test.yml
```

---

## 📊 Project Status

### Phase 1 Complete ✅

- [x] 7/7 essential packages built and documented
- [x] Unified OpenSSL package with 4 build methods
- [x] 15 Conan profiles created
- [x] Package consolidation (mini package removed)
- [x] Comprehensive documentation
- [x] 4 GitHub Actions workflows
- [x] Version bump to 2.0.0

### Current Metrics

| Metric | Status |
|--------|--------|
| Package Consolidation | ✅ 100% |
| Profiles Created | ✅ 15/15 |
| READMEs | ✅ 7/7 |
| GitHub Workflows | ✅ 4/4 |
| Version Bump | ✅ 2.0.0 |
| Documentation | ✅ Complete |

### Next Steps

- [ ] VS Code workspace configurations
- [ ] Cloudsmith upload automation
- [ ] Cross-repository GitHub issues
- [ ] TODO.json distribution

---

## 🔗 Links

- **Repository**: https://github.com/sparesparrow/sparetools
- **Cloudsmith**: https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/
- **Issues**: https://github.com/sparesparrow/sparetools/issues
- **Discussions**: https://github.com/sparesparrow/sparetools/discussions
- **OpenSSL**: https://github.com/openssl/openssl
- **Conan**: https://conan.io

---

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- OpenSSL team for the amazing cryptography library
- Conan team for the excellent package manager
- NGA aerospace for the zero-copy pattern inspiration
- Community contributors and testers

---

## 📞 Support

- **Email**: contact@sparesparrow.dev
- **GitHub Issues**: https://github.com/sparesparrow/sparetools/issues
- **Discussions**: https://github.com/sparesparrow/sparetools/discussions

---

**Made with ❤️ by the SpareTools team**

*Last Updated: 2025-10-31*
