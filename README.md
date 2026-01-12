# SpareTools Multi-Domain Package Ecosystem

[![Build Status](https://img.shields.io/github/actions/workflow/status/sparesparrow/sparetools/ci.yml?branch=main&label=build&logo=github)](https://github.com/sparesparrow/sparetools/actions)
[![Security](https://img.shields.io/github/actions/workflow/status/sparesparrow/sparetools/security.yml?branch=main&label=security&logo=github)](https://github.com/sparesparrow/sparetools/actions)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Conan](https://img.shields.io/badge/conan-2.21.0%2B-orange.svg)](https://conan.io)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org)

Comprehensive Conan 2.x ecosystem spanning embedded systems, AI/ML, cybersecurity, aerospace, and enterprise applications with hermetic builds, security-first architecture, and zero-copy deployment.

---

## 🚀 Quick Start (5 minutes)

### Install from Cloudsmith

```bash
# Add remote (one-time)
conan remote add sparesparrow-conan \
  https://dl.cloudsmith.io/public/sparesparrow-conan/sparetools/

# Install Python runtime (foundation)
conan install --tool-requires=sparetools-cpython/3.12.7 --build=missing

# Install AI assistant tools (MCP ecosystem)
conan install --requires=sparetools-mcp-orchestrator/2.0.3 --build=missing

# Install embedded development tools (ESP32)
conan install --requires=sparetools-nucleus/2.0.0 --build=missing

# Install cybersecurity toolkit
conan install --requires=sparetools-pentest-toolkit/2.0.0 --build=missing
```

### Build from Source

```bash
# Build foundation layer
conan create packages/foundation/sparetools-base --version=2.0.3 --build=missing
conan create packages/foundation/sparetools-cpython --version=3.12.7 --build=missing

# Build AI/ML ecosystem (MCP)
conan create packages/consumers/mcp/sparetools-mcp-orchestrator --version=2.0.3 --build=missing

# Build embedded systems (ESP32)
conan create packages/consumers/esp32/sparetools-nucleus --version=2.0.0 --build=missing

# Build cybersecurity tools
conan create packages/pentest/sparetools-pentest-toolkit --version=2.0.0 --build=missing

# Build MIA project
conan create mia-project --build=missing

# Build ESP32 BPM detector
conan create packages/consumers/esp32/sparetools-bpm-detector --build=missing
```

### Zero-Copy Development (CPY System)

For consumer projects, SpareTools provides a zero-copy development environment using symlinks to Conan cache instead of versioned Cloudsmith packages:

```bash
# Setup CPY environment for MIA project
cd ~/projects/mia
mkdir CPY
cd CPY

# Create symlinks to cache packages
ln -sf $(conan cache path sparetools-base/2.0.3) sparetools-base
ln -sf $(conan cache path sparetools-embedded/1.0.0) sparetools-embedded
ln -sf $(conan cache path sparetools-cpython/3.12.7) sparetools-cpython

# Build using symlinked dependencies
export LD_LIBRARY_PATH="$PWD/sparetools-base/lib:$LD_LIBRARY_PATH"
conan build ..  # Uses symlinked packages
```

**Benefits:**
- ⚡ Zero-copy: No package duplication
- 🔄 Instant updates: Changes in cache immediately available
- 🛡️ Isolated development: Local changes don't affect others
- 📦 Simplified maintenance: No version management for internal packages

See [`docs/CPY_SYSTEM.md`](docs/CPY_SYSTEM.md) for complete documentation.

---

## 📋 Multi-Domain Ecosystem

**December 2025**: SpareTools provides a comprehensive multi-domain package ecosystem spanning AI/ML, embedded systems, cybersecurity, aerospace, and enterprise applications.

### Package Distribution
- **Primary Registry**: Cloudsmith (sparesparrow-conan/sparetools)
- **Domain-Specific**: Specialized packages for each technology domain
- **Cross-Platform**: Linux, macOS, Windows, Android, Embedded

---

## 🚀 Install CLI Tools (Zipapps)

For quick access to SpareTools CLI utilities without full environment setup, use our Python zipapp distributions:

```bash
# Install bootstrap tool (multi-domain project templating)
curl -s https://api.github.com/repos/sparesparrow/sparetools/releases/latest | \
  sed -n 's/"browser_download_url": //p' | \
  grep 'sparetools-bootstrap\.pyz' | \
  xargs wget -qO sparetools-bootstrap.pyz

chmod +x sparetools-bootstrap.pyz
sudo mv sparetools-bootstrap.pyz /usr/local/bin/sparetools-bootstrap

# Now use it
sparetools-bootstrap --help
sparetools-bootstrap --template=mcp --name=my-ai-project
sparetools-bootstrap --template=esp32 --name=my-embedded-project
sparetools-bootstrap --template=aerospace --name=my-avionics-project
```

**Available zipapps**: bootstrap, MCP servers, embedded tools, cybersecurity utilities, and domain-specific generators. See [Zipapp Distribution](docs/ZIPAPP-DISTRIBUTION.md) for complete list.

---

## 📊 Architecture at a Glance

### Multi-Domain Package Ecosystem

```mermaid
graph TD
    subgraph "Foundation Layer"
        base[sparetools-base/2.0.3<br/>SECURITY & UTILITIES]
        cpython[sparetools-cpython/3.12.7<br/>PYTHON RUNTIME]
        shared[sparetools-shared-dev-tools/2.0.3<br/>DEV TOOLS]
        bootstrap[sparetools-bootstrap/2.0.3<br/>ORCHESTRATION]
    end

    subgraph "Consumer Domains"
        mcp[sparetools-mcp-orchestrator<br/>AI ASSISTANTS]
        esp32[sparetools-nucleus<br/>EMBEDDED SYSTEMS]
        aerospace[sparetools-aerospace<br/>AVIATION SOFTWARE]
        android[sparetools-cliphist-android<br/>MOBILE DEVELOPMENT]
        wifi[sparetools-wifi-sensing<br/>NETWORK ANALYSIS]
        sdr[sparetools-sdr-tools<br/>SOFTWARE RADIO]
        security[sparetools-crypto-suite<br/>CYBERSECURITY]
        pentest[sparetools-pentest-toolkit<br/>PENETRATION TESTING]
    end

    subgraph "Specialized Packages"
        streaming[sparetools-streaming-solutions<br/>MEDIA STREAMING]
        input[sparetools-input-backends<br/>HUMAN INTERFACE]
        schemas[sparetools-bpm-schemas<br/>PROTOCOL SCHEMAS]
    end

    base --> mcp
    base --> esp32
    base --> aerospace
    base --> android
    cpython --> mcp
    cpython --> pentest
    shared -->|All Consumers| mcp

    style base fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:3px
    style cpython fill:#9C27B0,stroke:#6A1B9A,color:#fff,stroke-width:2px
    style mcp fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:2px
    style esp32 fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:2px
    style aerospace fill:#FF5722,stroke:#D84315,color:#fff,stroke-width:2px
```

### Package Categories

**Foundation Layer:**
- `sparetools-base/2.0.3`: Core utilities, security gates, zero-copy patterns
- `sparetools-cpython/3.12.7`: Prebuilt Python 3.12.7 runtime environment
- `sparetools-bootstrap/2.0.3`: Multi-domain project orchestration
- `sparetools-versioning/1.0.0`: Git-based versioning utilities

**Consumer Domains:**
- **AI/ML**: MCP orchestrator, prompt systems, AI assistants
- **Embedded**: ESP32, aerospace, IoT devices
- **Mobile**: Android JNI, cross-platform development
- **Security**: Cryptography, penetration testing, network analysis
- **Media**: Streaming solutions, audio/video processing
- **Input**: Gamepad mapping, human interface devices

---

## ✨ Key Features

### Zero-Copy Deployment
```
~/.conan2/p/packages/  → 500 MB (single copy)
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

### Component Relationships
```mermaid
graph TD
    ORCHESTRATOR[ORCHESTRATOR<br/>Coordinates Workflow]
    EXECUTOR[EXECUTOR<br/>Builds & Packages]
    VALIDATOR[VALIDATOR<br/>Verifies & Tests]
    
    ORCHESTRATOR --> EXECUTOR
    ORCHESTRATOR --> VALIDATOR
    EXECUTOR --> VALIDATOR
    
    EXECUTOR --> BUILD[Build Artifacts]
    EXECUTOR --> PACKAGE[Package Creation]
    VALIDATOR --> SECURITY[Security Scan]
    VALIDATOR --> TESTS[Run Tests]
    VALIDATOR --> SBOM[Generate SBOM]
    
    style ORCHESTRATOR fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:3px
    style EXECUTOR fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:2px
    style VALIDATOR fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:2px
```

### Domain-Specific Architectures

#### MIA (Modular Integration Architecture) Projects
```mermaid
graph TD
    ORCH[MIA ORCHESTRATOR<br/>Project Coordination]
    EXEC[MIA EXECUTOR<br/>Build & Deploy]
    VALID[MIA VALIDATOR<br/>Integration Tests]
    
    ORCH --> EXEC
    ORCH --> VALID
    EXEC --> VALID
    
    EXEC --> PYTHON[Python Services]
    EXEC --> CPP[C++ Components]
    EXEC --> DOCKER[Docker Containers]
    VALID --> UNIT[Unit Tests]
    VALID --> INTEG[Integration Tests]
    VALID --> E2E[End-to-End Tests]
    
    style ORCH fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:3px
    style EXEC fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:2px
    style VALID fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:2px
```

#### ESP32 BPM Detector
```mermaid
graph TD
    ORCH[ESP32 ORCHESTRATOR<br/>Firmware Pipeline]
    EXEC[ESP32 EXECUTOR<br/>Compile & Flash]
    VALID[ESP32 VALIDATOR<br/>Hardware Tests]
    
    ORCH --> EXEC
    ORCH --> VALID
    EXEC --> VALID
    
    EXEC --> PLATFORMIO[PlatformIO Build]
    EXEC --> FLATBUFFERS[Schema Generation]
    EXEC --> FLASH[Device Flashing]
    VALID --> HOST[Host Unit Tests]
    VALID --> HARDWARE[Hardware Tests]
    VALID --> INTEGRATION[Integration Tests]
    
    style ORCH fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:3px
    style EXEC fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:2px
    style VALID fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:2px
```

#### MCP Ecosystem
```mermaid
graph TD
    ORCH[MCP ORCHESTRATOR<br/>AI Workflow Coordination]
    EXEC[MCP EXECUTOR<br/>Server Deployment]
    VALID[MCP VALIDATOR<br/>Protocol Validation]
    
    ORCH --> EXEC
    ORCH --> VALID
    EXEC --> VALID
    
    EXEC --> SERVERS[MCP Servers]
    EXEC --> PROMPTS[Prompt Management]
    EXEC --> TOOLS[Tool Integration]
    VALID --> PROTOCOL[Protocol Tests]
    VALID --> AI[AI Response Validation]
    VALID --> SECURITY[Security Checks]
    
    style ORCH fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:3px
    style EXEC fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:2px
    style VALID fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:2px
```

#### Python Projects
```mermaid
graph TD
    ORCH[Python ORCHESTRATOR<br/>Environment Setup]
    EXEC[Python EXECUTOR<br/>Build & Install]
    VALID[Python VALIDATOR<br/>Quality Checks]
    
    ORCH --> EXEC
    ORCH --> VALID
    EXEC --> VALID
    
    EXEC --> VENV[Virtual Environment]
    EXEC --> INSTALL[Package Install]
    EXEC --> WHEEL[Wheel Building]
    VALID --> PYTEST[Pytest Tests]
    VALID --> LINT[Linting]
    VALID --> TYPE[Type Checking]
    
    style ORCH fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:3px
    style EXEC fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:2px
    style VALID fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:2px
```

#### C++ Projects
```mermaid
graph TD
    ORCH[C++ ORCHESTRATOR<br/>Build Configuration]
    EXEC[C++ EXECUTOR<br/>Compile & Link]
    VALID[C++ VALIDATOR<br/>Static Analysis]
    
    ORCH --> EXEC
    ORCH --> VALID
    EXEC --> VALID
    
    EXEC --> CMAKE[CMake Configure]
    EXEC --> COMPILE[Compilation]
    EXEC --> LINK[Linking]
    VALID --> CLANG[Clang-Tidy]
    VALID --> CPPCHECK[Cppcheck]
    VALID --> TESTS[Unit Tests]
    
    style ORCH fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:3px
    style EXEC fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:2px
    style VALID fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:2px
```

#### Node.js Projects
```mermaid
graph TD
    ORCH[Node.js ORCHESTRATOR<br/>Dependency Resolution]
    EXEC[Node.js EXECUTOR<br/>Build & Bundle]
    VALID[Node.js VALIDATOR<br/>Quality Assurance]
    
    ORCH --> EXEC
    ORCH --> VALID
    EXEC --> VALID
    
    EXEC --> NPM[NPM Install]
    EXEC --> BUILD[Build Scripts]
    EXEC --> BUNDLE[Bundling]
    VALID --> JEST[Jest Tests]
    VALID --> ESLINT[ESLint]
    VALID --> TYPESCRIPT[TypeScript Check]
    
    style ORCH fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:3px
    style EXEC fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:2px
    style VALID fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:2px
```

#### Docker Containers
```mermaid
graph TD
    ORCH[Docker ORCHESTRATOR<br/>Container Orchestration]
    EXEC[Docker EXECUTOR<br/>Build & Push]
    VALID[Docker VALIDATOR<br/>Security & Compliance]
    
    ORCH --> EXEC
    ORCH --> VALID
    EXEC --> VALID
    
    EXEC --> BUILD[Image Build]
    EXEC --> TAG[Image Tagging]
    EXEC --> PUSH[Registry Push]
    VALID --> TRIVY[Trivy Scan]
    VALID --> SBOM[SBOM Generation]
    VALID --> COMPLIANCE[Compliance Check]
    
    style ORCH fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:3px
    style EXEC fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:2px
    style VALID fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:2px
```

---

## 📦 Package Overview

```mermaid
graph TD
    subgraph "Foundation & Infrastructure"
        base[sparetools-base/2.0.3<br/>CORE UTILITIES]
        cpython[sparetools-cpython/3.12.7<br/>PYTHON RUNTIME]
        bootstrap[sparetools-bootstrap/2.0.3<br/>ORCHESTRATION]
        shared[sparetools-shared-dev-tools/2.0.3<br/>DEV TOOLS]
        testharness[sparetools-test-harness/2.0.3<br/>TESTING]
        recipe[sparetools-recipe-base/2.0.3<br/>RECIPES]
        icd[sparetools-icd/2.0.0<br/>SCHEMAS]
        versioning[sparetools-versioning/1.0.0<br/>VERSIONING]
    end

    subgraph "Consumer Domains"
        mcp[sparetools-mcp-orchestrator<br/>AI ASSISTANTS]
        mcp_servers[sparetools-mcp-servers<br/>MCP SERVERS]
        prompt[sparetools-prompt-system<br/>PROMPT ENGINEERING]
        nucleus[sparetools-nucleus<br/>EMBEDDED ESP32]
        bpm[sparetools-bpm-detector<br/>IOT DEVICES]
        hal[sparetools-hal-sunton<br/>HARDWARE]
        aerospace[sparetools-aerospace<br/>AVIATION]
        android[sparetools-cliphist-android<br/>MOBILE]
        pentest[sparetools-pentest-toolkit<br/>PENETRATION TESTING]
        crypto[sparetools-crypto-suite<br/>CRYPTOGRAPHY]
        wifi[sparetools-wifi-sensing<br/>NETWORK ANALYSIS]
        streaming[sparetools-streaming-solutions<br/>MEDIA STREAMING]
        sdr[sparetools-sdr-tools<br/>SOFTWARE RADIO]
        input[sparetools-input-backends<br/>HUMAN INTERFACE]
        gamepad[sparetools-gamepad-*<br/>GAMEPADS]
    end

    subgraph "Specialized & Legacy"
        bpm_schemas[sparetools-bpm-schemas<br/>PROTOCOL SCHEMAS]
        protocols[sparetools-protocols<br/>FLATBUFFERS]
        crypto_lib[sparetools-openssl<br/>CRYPTO LIBRARIES]
        crypto_tools[sparetools-openssl-tools<br/>CRYPTO TOOLS]
        py_tools[sparetools-py<br/>PYTHON UTILITIES]
        proc_tools[sparetools-proc-tools<br/>PROCESS TOOLS]
        fs_tools[sparetools-fs-tools<br/>FILESYSTEM]
    end

    base --> mcp
    base --> nucleus
    base --> aerospace
    base --> android
    base --> pentest
    cpython --> mcp
    cpython --> prompt
    cpython --> py_tools
    shared -->|All Consumers| mcp
    versioning -->|All Packages| base
    bootstrap -->|Orchestrates| mcp
    bootstrap -->|Orchestrates| nucleus

    style base fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:3px
    style cpython fill:#9C27B0,stroke:#6A1B9A,color:#fff,stroke-width:2px
    style versioning fill:#00BCD4,stroke:#00838F,color:#fff,stroke-width:2px
    style mcp fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:2px
    style nucleus fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:2px
    style aerospace fill:#FF5722,stroke:#D84315,color:#fff,stroke-width:2px
    style pentest fill:#E91E63,stroke:#880E4F,color:#fff,stroke-width:2px
    style crypto fill:#E91E63,stroke:#880E4F,color:#fff,stroke-width:2px
```

### Foundation & Infrastructure (8 packages)
| Package | Version | Purpose |
|---------|---------|---------|
| **sparetools-base** | 2.0.3 | Core utilities, security gates, zero-copy patterns |
| **sparetools-cpython** | 3.12.7 | Prebuilt Python 3.12.7 runtime environment |
| **sparetools-bootstrap** | 2.0.3 | Multi-domain project orchestration framework |
| **sparetools-shared-dev-tools** | 2.0.3 | Development utilities and build helpers |
| **sparetools-test-harness** | 2.0.3 | Testing infrastructure and frameworks |
| **sparetools-recipe-base** | 2.0.3 | Base Conan recipes and templates |
| **sparetools-icd** | 2.0.0 | Interface control documents and schemas |
| **sparetools-versioning** | 1.0.0 | Git-based versioning utilities |

### Consumer Domains (15+ packages)
| Domain | Key Packages | Purpose |
|--------|--------------|---------|
| **AI/ML** | `sparetools-mcp-orchestrator`<br/>`sparetools-mcp-servers`<br/>`sparetools-prompt-system` | Model Context Protocol, AI assistants, prompt engineering |
| **Embedded** | `sparetools-nucleus`<br/>`sparetools-bpm-detector`<br/>`sparetools-hal-sunton` | ESP32 development, IoT, real-time systems |
| **Aerospace** | `sparetools-aerospace` | Aviation software and avionics systems |
| **Mobile** | `sparetools-cliphist-android` | Android JNI integration and mobile development |
| **Security** | `sparetools-pentest-toolkit`<br/>`sparetools-crypto-suite` | Penetration testing, cryptography, network security |
| **Networking** | `sparetools-wifi-sensing`<br/>`sparetools-streaming-solutions` | WiFi analysis, media streaming, network tools |
| **SDR** | `sparetools-sdr-tools` | Software-defined radio applications |
| **Input** | `sparetools-input-backends`<br/>`sparetools-gamepad-*` | Human interface devices, game controllers |

### Specialized & Legacy (10+ packages)
| Category | Examples | Purpose |
|----------|----------|---------|
| **Schemas** | `sparetools-bpm-schemas`<br/>`sparetools-protocols` | Protocol definitions, data schemas |
| **Cryptography** | `sparetools-openssl`<br/>`sparetools-openssl-tools`<br/>`sparetools-crypto-suite` | Cryptographic libraries and security tools |
| **Python Tools** | `sparetools-py`<br/>`sparetools-proc-tools`<br/>`sparetools-fs-tools` | Python utilities and system tools |

→ **Complete package reference:** [docs/PACKAGES.md](docs/PACKAGES.md)

---

## 🎯 Common Tasks

### Building Foundation Packages

```bash
# Build core infrastructure
conan create packages/foundation/sparetools-base --version=2.0.3 --build=missing
conan create packages/foundation/sparetools-cpython --version=3.12.7 --build=missing

# Build development tools
conan create packages/foundation/sparetools-shared-dev-tools --version=2.0.3 --build=missing
conan create packages/foundation/sparetools-bootstrap --version=2.0.3 --build=missing
conan create packages/foundation/sparetools-versioning --version=1.0.0 --build=missing
```

### Building Consumer Packages

```bash
# AI/ML ecosystem (MCP)
conan create packages/consumers/mcp/sparetools-mcp-orchestrator --version=2.0.3 --build=missing
conan create packages/mcp/sparetools-mcp-ecosystem --version=1.1.0 --build=missing

# Embedded systems (ESP32)
conan create packages/consumers/esp32/sparetools-nucleus --version=2.0.0 --build=missing
conan create packages/consumers/esp32/sparetools-bpm-detector --version=2.0.0 --build=missing

# MIA projects
conan create mia-project --build=missing

# Cybersecurity tools
conan create packages/pentest/sparetools-pentest-toolkit --version=2.0.0 --build=missing

# Aerospace software
conan create packages/aerospace/sparetools-aerospace --version=2.0.0 --build=missing
```

### Testing

```bash
# Run integration test
conan test test_package my-package/1.0.0

# Run unit tests
pytest test/unit/ -v

# With coverage
pytest test/unit/ --cov=packages/sparetools-base --cov-report=html
```

### Security Scanning

```bash
# Comprehensive vulnerability scan
trivy fs --security-checks vuln --scanners vuln .

# Generate SBOM for entire ecosystem
syft packages . -o cyclonedx-json > sparetools-sbom.json

# Security validation for packages
python3 -c "from sparetools_base.security import apply_security_gates; \
  apply_security_gates(['sparetools-crypto-suite'])"

# CodeQL security analysis
codeql database create --language=python --source-root=. codeql-db
codeql database analyze codeql-db --format=sarif-latest --output=security-results.sarif
```

### Publishing

```bash
# Build foundation layer first
conan create packages/foundation/sparetools-base --version=2.0.3 --build=missing
conan create packages/foundation/sparetools-cpython --version=3.12.7 --build=missing

# Build and publish consumer domains
for domain in mcp esp32 aerospace android wifi sdr security streaming; do
  echo "Building $domain consumer packages..."
  # Build domain-specific packages
  conan create "packages/consumers/$domain/*" --version=2.0.0 --build=missing
done

# Build specialized packages
conan create packages/consumers/esp32/sparetools-bpm-detector --version=2.0.0 --build=missing
conan create mia-project --build=missing

# Upload all packages to Cloudsmith (requires CLOUDSMITH_API_KEY)
conan upload "sparetools-*/*" -r sparesparrow-conan --confirm --parallel=4
```

→ **More examples:** [docs/QUICK-REFERENCE.md](docs/QUICK-REFERENCE.md)

---

## 📚 Documentation

### Getting Started
- **[Quick Reference](docs/QUICK-REFERENCE.md)** - Commands and options cheat sheet (5 min)
- **[Architecture Overview](docs/ARCHITECTURE.md)** - Comprehensive system design and domains (15 min)
- **[Testing Guide](docs/TESTING-GUIDE.md)** - Multi-domain testing procedures

### Consumer Domain Guides
- **[MCP Ecosystem Guide](mcp/README.md)** - AI assistants and Model Context Protocol
- **[ESP32 Development](docs/consumers/esp32/README.md)** - Embedded systems and IoT
- **[Aerospace Integration](packages/aerospace/sparetools-aerospace/README.md)** - Aviation software development
- **[Android Development](packages/consumers/android/sparetools-cliphist-android/README.md)** - Mobile and JNI integration
- **[Cybersecurity Toolkit](packages/pentest/sparetools-pentest-toolkit/README.md)** - Penetration testing and security

### Operations
- **[Publishing Guide](docs/PUBLISHING-GUIDE.md)** - Multi-domain package publishing
- **[CI/CD Guide](docs/CI-CD-GUIDE.md)** - GitHub Actions workflows and operations
- **[CI/CD Troubleshooting](docs/CI-CD-TROUBLESHOOTING.md)** - Common workflow issues
- **[GitHub Secrets Setup](docs/GITHUB-SECRETS-SETUP.md)** - Configure CI/CD secrets

### Reference
- **[Package Reference](docs/PACKAGES.md)** - Complete ecosystem documentation
- **[Migration Guide](docs/MIGRATION-GUIDE.md)** - Upgrade from v1.x to v2.0.0
- **[Security Architecture](docs/ENTERPRISE-SECURITY.md)** - Security gates and compliance
- **[Performance Guide](docs/ASSEMBLY-OPTIMIZATIONS.md)** - Optimization and performance tuning
- **[Workspace Guide](docs/WORKSPACE-GUIDE.md)** - VS Code and development environment setup
- **[Zipapp Distribution](docs/ZIPAPP-DISTRIBUTION.md)** - CLI tools and distribution

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

## 🤝 Support & Community

- **Issues:** [GitHub Issues](https://github.com/sparesparrow/sparetools/issues)
- **Discussions:** [GitHub Discussions](https://github.com/sparesparrow/sparetools/discussions)
- **Documentation:** [Complete Documentation](docs/README.md)
- **Packages:** [Cloudsmith Registry](https://cloudsmith.io/~sparesparrow-conan/repos/sparetools/)
- **CI/CD:** [GitHub Actions](https://github.com/sparesparrow/sparetools/actions)
- **Domain-Specific:** Check individual package READMEs for specialized support

---

## 📄 License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

---

## 🎉 Quick Links

| Resource | Description |
|----------|-------------|
| [Complete Package Reference](docs/PACKAGES.md) | All 40+ packages across domains |
| [Architecture Overview](docs/ARCHITECTURE.md) | Multi-domain system design |
| [MCP Ecosystem](mcp/README.md) | AI assistants and protocol servers |
| [ESP32 Development](docs/consumers/esp32/README.md) | Embedded systems guide |
| [Security Architecture](docs/ENTERPRISE-SECURITY.md) | Security gates and compliance |
| [Publishing Guide](docs/PUBLISHING-GUIDE.md) | Multi-domain publishing workflows |
| [CI/CD Operations](docs/CI-CD-GUIDE.md) | Workflow management and automation |
| [Testing Procedures](docs/TESTING-GUIDE.md) | Comprehensive testing across domains |
| [Cloudsmith Registry](https://cloudsmith.io/~sparesparrow-conan/repos/sparetools/) | Package distribution |

**Repository:** https://github.com/sparesparrow/sparetools
**v2.0.0** | **Conan 2.21.0+** | **Python 3.12+** | **40+ Packages** | **10+ Domains**
