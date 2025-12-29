# SpareTools Multi-Domain Architecture

## Overview

SpareTools is a comprehensive, multi-domain package ecosystem spanning embedded systems, AI/ML, cybersecurity, aerospace, and enterprise applications. It provides hermetic builds, security-first architecture, and zero-copy deployment patterns across diverse technology domains.

## Core Architecture

### Multi-Domain Package Ecosystem

```mermaid
graph TD
    subgraph "Foundation Layer"
        base[sparetools-base/2.0.0<br/>SECURITY & UTILITIES]
        cpython[sparetools-cpython/3.12.7<br/>PYTHON RUNTIME]
        shared[sparetools-shared-dev-tools/2.0.0<br/>DEV TOOLS]
        bootstrap[sparetools-bootstrap/2.0.0<br/>ORCHESTRATION]
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
        openssl[sparetools-openssl<br/>CRYPTOGRAPHIC LIBRARY]
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

**Legend:**
- Solid arrows (→): `python_requires` (recipe dependencies)
- Dashed arrows (-.->): `tool_requires` (build-time tools)

### Multi-Build System

```mermaid
graph LR
    A[Consumer Package] --> B{build_method option}

    B -->|perl<br/>default| C[Perl Configure<br/>✅ Production Ready]
    B -->|cmake| D[CMake Build<br/>✅ Modern]
    B -->|autotools| E[Autotools<br/>✅ Unix Standard]
    B -->|python| F[Python configure.py<br/>⚠️ Experimental]
    B -->|meson| G[Meson Build<br/>✅ Cross-Platform]
    B -->|bazel| H[Bazel<br/>⚠️ Experimental]

    C --> I[Package Binary]
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I

    style C fill:#4CAF50,stroke:#2E7D32,color:#fff
    style D fill:#2196F3,stroke:#1565C0,color:#fff
    style E fill:#FF9800,stroke:#E65100,color:#fff
    style G fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style A fill:#607D8B,stroke:#37474F,color:#fff,stroke-width:2px
    style I fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:3px
```

### Profile Composition System

```mermaid
graph TD
    subgraph "Base Profiles"
        B1[linux-gcc11]
        B2[linux-clang14]
        B3[darwin-clang-arm64]
        B4[windows-msvc2022]
    end

    subgraph "Build Methods"
        M1[perl-configure]
        M2[cmake-build]
        M3[autotools]
        M4[python-configure]
    end

    subgraph "Features"
        F1[fips-enabled]
        F2[shared-libs]
        F3[static-only]
        F4[minimal]
        F5[performance]
    end

    B1 --> M1
    M1 --> F1
    F1 --> R[Final Build Configuration]

    B2 --> M2
    M2 --> F5
    F5 --> R

    B3 --> M1
    M1 --> F2
    F2 --> R

    style R fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:3px
```

**Profile Location:** `packages/sparetools-openssl-tools/profiles/`
- **base/** — Platform + compiler (6 profiles)
- **build-methods/** — Build system selection (4 profiles)
- **features/** — Feature toggles (5 profiles)

## CI/CD Workflow Chain

```mermaid
graph TD
    A[Push/PR] --> B{Change Detection}

    B -->|Code Changes| C[ci.yml<br/>Multi-Platform Build]
    B -->|Docs Only| D[Skip Build]

    C --> E[Build Matrix<br/>Linux/macOS/Windows]
    E --> F[Integration Tests]
    F --> G{All Pass?}

    G -->|Yes| H[security.yml<br/>Security Scanning]
    G -->|No| I[Fix Issues]

    H --> J[Trivy Scan<br/>Vulnerabilities]
    J --> K[Syft SBOM<br/>Generation]
    K --> L[CodeQL Analysis]
    L --> M{FIPS Validation}
    M --> N{All Clear?}

    N -->|Yes| O[publish.yml<br/>Package Publishing]
    N -->|No| P[Block Release]

    O --> Q[Cloudsmith<br/>Staging]
    Q --> R[Manual Approval]
    R --> S[Production<br/>Deploy]

    style C fill:#2196F3,stroke:#1565C0,color:#fff
    style H fill:#E91E63,stroke:#880E4F,color:#fff
    style O fill:#4CAF50,stroke:#2E7D32,color:#fff
    style S fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:3px
```

## Zero-Copy Deployment Pattern

```mermaid
graph LR
    subgraph "Conan Cache (~/.conan2/p/)"
        C1[sparetools-base<br/>Package Folder]
        C2[sparetools-cpython<br/>Package Folder]
        C3[sparetools-openssl<br/>Package Folder]
    end

    subgraph "_Build/packages/ (Symlinks)"
        S1[sparetools-base]
        S2[sparetools-cpython]
        S3[sparetools-openssl]
    end

    subgraph "Workspace Projects"
        W1[Project A]
        W2[Project B]
        W3[Project C]
    end

    C1 -.->|symlink| S1
    C2 -.->|symlink| S2
    C3 -.->|symlink| S3

    S1 -.->|symlink| W1
    S2 -.->|symlink| W1
    S3 -.->|symlink| W1

    S1 -.->|symlink| W2
    S2 -.->|symlink| W2

    S1 -.->|symlink| W3
    S3 -.->|symlink| W3

    style C1 fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:2px
    style C2 fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:2px
    style C3 fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:2px

    style S1 fill:#FFE0B2,stroke:#E65100,color:#000
    style S2 fill:#BBDEFB,stroke:#1565C0,color:#000
    style S3 fill:#C8E6C9,stroke:#2E7D32,color:#000
```

**Benefits:**
- ✅ **99% disk space savings** (symlinks ~50KB vs binaries ~500MB)
- ✅ **Instant environment setup** (no binary copying)
- ✅ **Atomic updates** (change symlink target = instant upgrade)
- ✅ **Single source of truth** (all binaries in Conan cache)

## Security Integration

```mermaid
graph TD
    A[Build Artifacts] --> B{Security Gates}

    B --> C[Trivy Scanner<br/>Vulnerability Detection]
    B --> D[Syft<br/>SBOM Generation]
    B --> E[FIPS Validator<br/>Compliance Check]

    C -->|Scan| F{Findings?}
    D -->|Generate| G[SBOM Report<br/>CycloneDX/SPDX]
    E -->|Validate| H{Compliant?}

    F -->|CRITICAL| I[❌ Block Promotion]
    F -->|OK| J[✅ Continue]

    H -->|No| I
    H -->|Yes| J

    G --> J
    J --> K[Package Promotion]

    style C fill:#E91E63,stroke:#880E4F,color:#fff
    style D fill:#2196F3,stroke:#1565C0,color:#fff
    style E fill:#FF9800,stroke:#E65100,color:#fff
    style I fill:#F44336,stroke:#B71C1C,color:#fff,stroke-width:3px
    style K fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:3px
```

## Directory Structure

```
sparetools/
├── packages/                    # Conan packages by domain
│   ├── foundation/              # Core infrastructure
│   │   ├── sparetools-base/      # Security gates & utilities
│   │   ├── sparetools-cpython/   # Prebuilt Python runtime
│   │   ├── sparetools-bootstrap/ # Orchestration framework
│   │   └── sparetools-shared-dev-tools/ # Development utilities
│   ├── consumers/               # Domain-specific applications
│   │   ├── mcp/                  # AI assistant protocols
│   │   ├── esp32/                # Embedded systems
│   │   ├── aerospace/            # Aviation software
│   │   ├── android/              # Mobile development
│   │   ├── openssl/              # Cryptographic libraries
│   │   └── [other-domains]/      # Additional consumer domains
│   ├── [other-categories]/       # SDR, security, streaming, etc.
│   └── deprecated/               # Archived packages
├── _Build/                      # Zero-copy build artifacts
│   ├── packages/                # Symlinks to Conan cache
│   └── conan-cache -> ~/.conan2 # Symlink to cache root
├── build_results/               # Build reports & artifacts
├── test_results/                # Test outputs & coverage
├── test/                        # Multi-domain test suite
├── scripts/                     # Automation & utilities
├── docs/                        # Comprehensive documentation
├── templates/                   # Project templates by domain
├── workspaces/                  # IDE configurations
├── mcp/                         # MCP server ecosystem
└── .github/workflows/           # CI/CD pipelines
```

## Component Relationships

### Bootstrap Orchestration

```mermaid
graph TD
    O[ORCHESTRATOR<br/>Coordinates Workflows] --> E[EXECUTOR<br/>Builds & Packages]
    E --> V[VALIDATOR<br/>Verifies Artifacts]
    V -->|Pass| O
    V -->|Fail| E

    subgraph "EXECUTOR Tasks"
        E1[Build OpenSSL]
        E2[Package with Conan]
        E3[Generate Artifacts]
    end

    subgraph "VALIDATOR Tasks"
        V1[Run Tests]
        V2[Security Scans<br/>Trivy/Syft]
        V3[Generate SBOM]
        V4[FIPS Validation]
    end

    subgraph "ORCHESTRATOR Tasks"
        O1[Manage Build Queue]
        O2[Coordinate Agents]
        O3[Report Results]
    end

    E --> E1
    E --> E2
    E --> E3

    V --> V1
    V --> V2
    V --> V3
    V --> V4

    O --> O1
    O --> O2
    O --> O3

    style O fill:#9C27B0,stroke:#6A1B9A,color:#fff,stroke-width:3px
    style E fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:3px
    style V fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:3px
```

## Key Design Principles

1. **Multi-Domain Architecture**: Consumer-centric organization spanning diverse technology domains
2. **Hermetic Builds**: No system dependencies beyond SpareTools packages
3. **Zero-Copy Deployment**: Symlinks eliminate binary duplication across domains
4. **Security-First Approach**: Integrated scanning, FIPS compliance, and supply chain security
5. **Layered Design**: Foundation → Runtime → Utilities → Orchestration → Consumer layers
6. **Template-Based Development**: Rapid project creation across technology domains
7. **CI/CD Integration**: Automated workflows with manual approvals for production releases

## Data Flow

### Multi-Domain Build Process

1. **Source** → Domain-specific package (e.g., `packages/consumers/mcp/sparetools-mcp-orchestrator/`)
2. **Dependencies** → Resolve via Conan (foundation + domain-specific requirements)
3. **Configuration** → Apply profiles (platform + features + domain requirements)
4. **Build** → Execute selected method (varies by domain: cmake, meson, autotools, etc.)
5. **Package** → Create Conan package in cache with domain metadata
6. **Test** → Run domain-specific integration and unit tests
7. **Scan** → Security validation (Trivy, Syft, domain-specific checks)
8. **Publish** → Upload to Cloudsmith with domain categorization

### Cross-Domain Consumption Pattern

1. **Remote Add** → `conan remote add sparesparrow-conan ...`
2. **Install Foundation** → `conan install --tool-requires=sparetools-cpython/3.12.7`
3. **Install Domain** → `conan install --requires=sparetools-mcp-orchestrator/2.0.3`
4. **Symlink** → Zero-copy deployment across multiple domains
5. **Orchestrate** → Use bootstrap tools for multi-domain project setup

## External Integrations

### Package Management
- **Conan Center**: Base dependencies (CMake, Ninja, Meson, etc.)
- **Cloudsmith**: Primary package registry with domain categorization
- **GitHub Packages**: Secondary registry and container hosting

### Development Tools
- **VS Code**: Workspace configurations for multi-domain development
- **Cursor**: AI-assisted development with domain-specific prompts
- **GitHub Copilot**: Code completion across technology domains

### Security & Compliance
- **Trivy**: Vulnerability scanning across all domains
- **Syft**: SBOM generation with domain-specific metadata
- **CodeQL**: Static analysis for multiple languages
- **FIPS Validators**: Cryptographic compliance across domains

### CI/CD & Testing
- **GitHub Actions**: Multi-platform, multi-domain build matrices
- **Dependabot**: Automated dependency updates across domains
- **Codecov**: Test coverage tracking for all packages

### Domain-Specific Integrations
- **ESP32**: PlatformIO, ESP-IDF toolchain integration
- **Android**: JNI, NDK, cross-ABI compilation
- **Aerospace**: DO-178C compliance tooling
- **MCP**: Model Context Protocol server ecosystem
- **SDR**: RTL-SDR, HackRF, and other radio hardware

---

*Last Updated: December 29, 2025*