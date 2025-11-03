# SpareTools OpenSSL DevOps Ecosystem

[![Build Status](https://img.shields.io/github/actions/workflow/status/sparesparrow/sparetools/ci.yml?branch=main&label=build&logo=github)](https://github.com/sparesparrow/sparetools/actions)
[![Security](https://img.shields.io/github/actions/workflow/status/sparesparrow/sparetools/security.yml?branch=main&label=security&logo=github)](https://github.com/sparesparrow/sparetools/actions)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Conan](https://img.shields.io/badge/conan-2.21.0%2B-orange.svg)](https://conan.io)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org)

Modern Conan 2.x ecosystem for OpenSSL development with multi-build methods, integrated security scanning, and zero-copy deployment pattern.

---

## 🚀 Quick Start (5 minutes)

### Install from Cloudsmith

```bash
# Add remote (one-time)
conan remote add sparesparrow-conan \
  https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/

# Install OpenSSL
conan install --requires=sparetools-openssl/3.3.2 --build=missing
```

### Build from Source

```bash
# Default Perl Configure build
conan create packages/sparetools-openssl --version=3.3.2 --build=missing

# With CMake
conan create packages/sparetools-openssl --version=3.3.2 \
  -o build_method=cmake --build=missing

# With FIPS enabled
conan create packages/sparetools-openssl --version=3.3.2 \
  -pr:b packages/sparetools-openssl-tools/profiles/features/fips-enabled \
  --build=missing
```

---

## 📊 Architecture at a Glance

### Package Ecosystem

```mermaid
graph TD
    subgraph "Production Packages v2.0.0"
        openssl[sparetools-openssl/3.3.2<br/>MAIN DELIVERABLE]
        tools[sparetools-openssl-tools/2.0.0]
        base[sparetools-base/2.0.0<br/>FOUNDATION]
        cpython[sparetools-cpython/3.12.7]
        shared[sparetools-shared-dev-tools/2.0.0]
        bootstrap[sparetools-bootstrap/2.0.0]
    end

    subgraph "Dependencies"
        openssl -.->|tool_requires| tools
        openssl -.->|tool_requires| cpython
        openssl -->|python_requires| base

        tools -->|python_requires| base
        shared -->|python_requires| base
        cpython -->|python_requires| base
        bootstrap -->|python_requires| base
    end

    style openssl fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:3px
    style base fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:3px
    style tools fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:2px
    style cpython fill:#9C27B0,stroke:#6A1B9A,color:#fff,stroke-width:2px
    style shared fill:#FFC107,stroke:#F57C00,color:#000,stroke-width:2px
    style bootstrap fill:#607D8B,stroke:#37474F,color:#fff,stroke-width:2px
```

### Multi-Build System

```mermaid
graph LR
    A[sparetools-openssl] --> B{build_method option}

    B -->|perl<br/>default| C[Perl Configure<br/>✅ Production]
    B -->|cmake| D[CMake Build<br/>✅ Modern]
    B -->|autotools| E[Autotools<br/>✅ Unix]
    B -->|python| F[Python configure.py<br/>⚠️ Experimental]

    C --> G[OpenSSL 3.3.2]
    D --> G
    E --> G
    F --> G

    style C fill:#4CAF50,stroke:#2E7D32,color:#fff
    style D fill:#2196F3,stroke:#1565C0,color:#fff
    style E fill:#FF9800,stroke:#E65100,color:#fff
    style F fill:#FFC107,stroke:#F57C00,color:#000
    style G fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:3px
```

---

## ✨ Key Features

### Zero-Copy Deployment
```
~/.conan2/p/openssl/   → 500 MB (single copy)
_Build/packages/       → 50 KB (symlinks)
workspace/lib/         → 50 KB (symlinks)
────────────────────────────────────────────
Traditional copies:    1.5 GB
With symlinks:         500 MB
Savings:              ✅ 66% (1 GB saved)
```

### Multi-Platform Support
| Platform | Compiler | Status |
|----------|----------|--------|
| Linux | GCC 11+ | ✅ Stable |
| Linux | Clang 14+ | ✅ Stable |
| macOS | Apple Clang | ✅ Stable |
| Windows | MSVC 2022 | ⚠️ Experimental |

### Security Integration
```mermaid
graph LR
    A[Build] --> B[Trivy Scan]
    B --> C[Syft SBOM]
    C --> D[CodeQL]
    D --> E{FIPS?}
    E -->|Required| F[FIPS Validation]
    E -->|Optional| G[Package]
    F --> G

    style B fill:#E91E63,stroke:#880E4F,color:#fff
    style C fill:#2196F3,stroke:#1565C0,color:#fff
    style D fill:#FF9800,stroke:#E65100,color:#fff
    style G fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:2px
```

---

## 📦 Package Overview

| Package | Version | Type | Purpose |
|---------|---------|------|---------|
| **sparetools-openssl** | 3.3.2 | library | OpenSSL with 4 build methods |
| **sparetools-openssl-tools** | 2.0.0 | python-require | Build profiles, FIPS validator |
| **sparetools-base** | 2.0.0 | python-require | Foundation utilities, security gates |
| **sparetools-cpython** | 3.12.7 | application | Prebuilt Python 3.12.7 runtime |
| **sparetools-shared-dev-tools** | 2.0.0 | python-require | Dev utilities, helpers |
| **sparetools-bootstrap** | 2.0.0 | python-require | 3-agent orchestration system |
| **sparetools-mcp-orchestrator** | 2.0.0 | python-require | MCP/AI integration |

→ **Full details:** [docs/PACKAGES.md](docs/PACKAGES.md)

---

## 🎯 Common Tasks

### Building

```bash
# Quick build (Perl Configure)
conan create packages/sparetools-openssl --version=3.3.2

# With specific profile
conan create packages/sparetools-openssl --version=3.3.2 \
  -pr:b packages/sparetools-openssl-tools/profiles/base/linux-gcc11

# With features
conan create packages/sparetools-openssl --version=3.3.2 \
  -pr:b packages/sparetools-openssl-tools/profiles/features/fips-enabled \
  -pr:b packages/sparetools-openssl-tools/profiles/features/performance
```

### Testing

```bash
# Run integration test
conan test packages/sparetools-openssl/test_package \
  sparetools-openssl/3.3.2

# Run unit tests
pytest test/unit/ -v

# With coverage
pytest test/unit/ --cov=packages/sparetools-base --cov-report=html
```

### Security Scanning

```bash
# Trivy vulnerability scan
trivy fs --security-checks vuln .

# Generate SBOM
syft packages . -o cyclonedx-json > sbom.json

# FIPS validation (if module present)
python3 -c "from bootstrap.openssl.fips_validator import FIPSValidator; \
  FIPSValidator().validate_module('/path/to/fips/module')"
```

### Publishing

```bash
# Build all packages in order
conan create packages/sparetools-base --version=2.0.0
conan create packages/sparetools-cpython --version=3.12.7
conan create packages/sparetools-openssl-tools --version=2.0.0
conan create packages/sparetools-openssl --version=3.3.2

# Upload to Cloudsmith (requires CLOUDSMITH_API_KEY)
conan upload "sparetools-*/*" -r sparesparrow-conan --confirm
```

→ **More examples:** [docs/QUICK-REFERENCE.md](docs/QUICK-REFERENCE.md)

---

## 📚 Documentation

### Getting Started
- **[Quick Reference](docs/QUICK-REFERENCE.md)** - Commands and options cheat sheet (5 min)
- **[Architecture](ARCHITECTURE.md)** - Visual system design with mermaid diagrams (15 min)
- **[Testing Guide](docs/TESTING-GUIDE.md)** - Comprehensive testing procedures

### Operations
- **[CI/CD Guide](docs/CI-CD-GUIDE.md)** - GitHub Actions workflows and operations
- **[CI/CD Troubleshooting](docs/CI-CD-TROUBLESHOOTING.md)** - Common workflow issues
- **[GitHub Secrets Setup](docs/GITHUB-SECRETS-SETUP.md)** - Configure CI/CD secrets

### Reference
- **[Package Reference](docs/PACKAGES.md)** - Complete package documentation
- **[Migration Guide](docs/MIGRATION-GUIDE.md)** - Upgrade from v1.x to v2.0.0
- **[OpenSSL 3.6.0 Analysis](docs/OPENSSL-360-BUILD-ANALYSIS.md)** - Deep dive on 3.6.0 builds
- **[Assembly Optimizations](docs/ASSEMBLY-OPTIMIZATIONS.md)** - Performance tuning
- **[Workspace Guide](docs/WORKSPACE-GUIDE.md)** - VS Code setup

### Changelog
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and breaking changes
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute

---

## 🏗️ CI/CD Pipeline

```mermaid
graph TD
    A[Push/PR] --> B[ci.yml<br/>Multi-Platform]
    B --> C{All Pass?}
    C -->|Yes| D[security.yml<br/>Scanning]
    C -->|No| E[Fix Issues]
    D --> F{CRITICAL?}
    F -->|No| G[publish.yml<br/>Cloudsmith]
    F -->|Yes| H[Block Release]
    G --> I[Manual Approval]
    I --> J[Production]

    style B fill:#2196F3,stroke:#1565C0,color:#fff
    style D fill:#E91E63,stroke:#880E4F,color:#fff
    style H fill:#F44336,stroke:#B71C1C,color:#fff
    style J fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:3px
```

**Active Workflows:**
- `ci.yml` - Multi-platform builds (Linux, macOS, Windows)
- `security.yml` - Trivy, Syft, CodeQL, FIPS validation
- `publish.yml` - Cloudsmith + GitHub Packages publishing
- `nightly.yml` - Daily comprehensive regression testing
- `release.yml` - Version management and releases

→ **Details:** [docs/CI-CD-GUIDE.md](docs/CI-CD-GUIDE.md)

---

## 🤝 Support

- **Issues:** [GitHub Issues](https://github.com/sparesparrow/sparetools/issues)
- **Discussions:** [GitHub Discussions](https://github.com/sparesparrow/sparetools/discussions)
- **Packages:** [Cloudsmith Repository](https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/)
- **CI/CD:** [GitHub Actions](https://github.com/sparesparrow/sparetools/actions)

---

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

---

## 🎉 Quick Links

| Resource | Description |
|----------|-------------|
| [Packages](docs/PACKAGES.md) | Complete package reference |
| [Architecture](ARCHITECTURE.md) | System design diagrams |
| [Quick Reference](docs/QUICK-REFERENCE.md) | Command cheat sheet |
| [CI/CD Guide](docs/CI-CD-GUIDE.md) | Workflow operations |
| [Testing Guide](docs/TESTING-GUIDE.md) | Test procedures |
| [Cloudsmith](https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/) | Package registry |

**Repository:** https://github.com/sparesparrow/sparetools
**v2.0.0** | **Conan 2.21.0+** | **Python 3.12+** | **OpenSSL 3.3.2**
