# SpareTools Architecture

## Overview

SpareTools is a modern, Python-based tooling ecosystem for OpenSSL development, building, and deployment. It provides a unified package system with multiple build methods, comprehensive security integration, and zero-copy deployment patterns.

## Core Architecture

### Package Ecosystem

```mermaid
graph TD
    subgraph "Production Packages"
        openssl[sparetools-openssl/3.3.2<br/>MAIN DELIVERABLE]
        tools[sparetools-openssl-tools/2.0.0]
        base[sparetools-base/2.0.0<br/>FOUNDATION]
        cpython[sparetools-cpython/3.12.7]
        shared[sparetools-shared-dev-tools/2.0.0]
        bootstrap[sparetools-bootstrap/2.0.0]
    end

    subgraph "Build Dependencies"
        openssl -.->|tool_requires| tools
        openssl -.->|tool_requires| cpython
        openssl -->|python_requires| base

        tools -->|python_requires| base
        shared -->|python_requires| base
        cpython -->|python_requires| base
        bootstrap -.->|should add| base
    end

    style openssl fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:3px
    style base fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:3px
    style tools fill:#2196F3,stroke:#1565C0,color:#fff,stroke-width:2px
    style cpython fill:#9C27B0,stroke:#6A1B9A,color:#fff,stroke-width:2px
    style shared fill:#FFC107,stroke:#F57C00,color:#000,stroke-width:2px
    style bootstrap fill:#607D8B,stroke:#37474F,color:#fff,stroke-width:2px
```

**Legend:**
- Solid arrows (→): `python_requires` (recipe dependencies)
- Dashed arrows (-.->): `tool_requires` (build-time tools)

### Multi-Build System

```mermaid
graph LR
    A[sparetools-openssl] --> B{build_method option}

    B -->|perl<br/>default| C[Perl Configure<br/>✅ Production Ready]
    B -->|cmake| D[CMake Build<br/>✅ Modern]
    B -->|autotools| E[Autotools<br/>✅ Unix Standard]
    B -->|python| F[Python configure.py<br/>⚠️ Experimental]

    C --> G[OpenSSL Binary]
    D --> G
    E --> G
    F --> G

    style C fill:#4CAF50,stroke:#2E7D32,color:#fff
    style D fill:#2196F3,stroke:#1565C0,color:#fff
    style E fill:#FF9800,stroke:#E65100,color:#fff
    style F fill:#FFC107,stroke:#F57C00,color:#000
    style A fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style G fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:3px
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
├── packages/                    # Conan packages (source)
│   ├── sparetools-base/         # Foundation utilities
│   ├── sparetools-cpython/      # Prebuilt Python runtime
│   ├── sparetools-openssl/      # Main OpenSSL package
│   ├── sparetools-openssl-tools/# Build tooling & profiles
│   ├── sparetools-shared-dev-tools/
│   ├── sparetools-bootstrap/    # Orchestration system
│   └── deprecated/              # Archived packages
├── _Build/                      # Zero-copy build artifacts
│   ├── openssl-builds/          # OpenSSL build results
│   │   ├── master/              # Development branch
│   │   └── 3.3.2/               # Release builds
│   ├── packages/                # Symlinks to Conan cache
│   └── conan-cache -> ~/.conan2 # Symlink to cache root
├── build_results/               # Build reports
├── reviews/                     # Release reviews
├── test_results/                # Test outputs
├── test/                        # Test suite
├── scripts/                     # Automation scripts
├── docs/                        # Documentation
├── workspaces/                  # IDE configurations
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

1. **Single Source of Truth**: All artifacts stored once in Conan cache
2. **Zero-Copy Deployment**: Symlinks eliminate binary duplication
3. **Multi-Method Flexibility**: Support multiple build systems
4. **Security First**: Integrated scanning and validation
5. **CI/CD Integration**: Automated workflows with manual approvals
6. **Modular Architecture**: Independent packages with clear dependencies

## Data Flow

### Build Process

1. **Source** → `packages/sparetools-openssl/`
2. **Dependencies** → Resolve via Conan (base, tools, cpython)
3. **Configuration** → Apply profiles (platform + features)
4. **Build** → Execute selected method (perl/cmake/autotools/python)
5. **Package** → Create Conan package in cache
6. **Test** → Run integration tests
7. **Scan** → Security validation (Trivy, Syft, FIPS)
8. **Publish** → Upload to Cloudsmith + GitHub Packages

### Consumption Pattern

1. **Remote Add** → `conan remote add sparesparrow-conan ...`
2. **Install** → `conan install --requires=sparetools-openssl/3.3.2`
3. **Symlink** → Zero-copy deployment to workspace
4. **Use** → Link libraries in consumer projects

## External Integrations

- **Conan Center**: Base dependencies (CMake, Ninja, etc.)
- **Cloudsmith**: Package hosting and distribution
- **GitHub Packages**: Secondary package registry
- **Security Tools**: Trivy, Syft, CodeQL integration
- **CI/CD**: GitHub Actions for multi-platform builds

---

*Last Updated: 2025-11-03*