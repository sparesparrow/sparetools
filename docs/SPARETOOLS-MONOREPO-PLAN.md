# SpareTools Monorepo Reorganization: Enhanced Plan

**Status:** Draft  
**Version:** 2.0 Enhanced  
**Last Updated:** December 13, 2025

---

## Executive Summary

This document improves upon the initial monorepo plan by introducing a **layered architecture** with clear separation of concerns, consumer-centric organization, and robust automation frameworks. The goal is to transform SpareTools into a scalable, maintainable monorepo supporting multiple consumers (openssl-tools, MIA, mcp-project-orchestrator, tinymcp, mcpserver.cpp, rtp-midi, automotive/obd-sim) while maintaining coherent build pipelines, documentation, and developer workflows.

### Key Improvements Over Initial Plan

1. **Shared Scripts Layer** - Centralized automation (bootstrap, build, validation)
2. **Recipe Inheritance** - Consistent conanfile patterns via base classes
3. **Consumer Templates** - Standardized structure for each consumer domain
4. **Nested Workspaces** - VS Code workspaces at multiple levels
5. **Documentation Module** - Consumer-aware docs with auto-generation
6. **Validation Framework** - Multi-tier validation with consumer contexts
7. **CI/CD Orchestration** - Matrix-driven, per-consumer workflows
8. **Shared Packaging** - Reusable container and distribution logic

---

## 🏗️ Part 1: Enhanced Directory Structure

### Root-Level Organization

```
sparetools/                          # Monorepo root
├── .github/                         # GitHub organization (workflows, templates)
├── .tooling/                        # Meta-tooling (repo orchestration)
├── docs/                            # Central documentation hub
├── scripts/                         # Shared scripts (bootstrap, validation, build)
├── tools/                           # Shared tools (CLI, utilities)
├── packages/                        # All Conan packages
│   ├── foundation/                  # Layer 1: Shared foundation
│   └── consumers/                   # Layer 2-4: Consumer-specific
├── examples/                        # Consumer integration examples
├── workspaces/                      # VS Code multi-level workspaces
├── _Build/                          # Build artifacts (gitignored)
├── conanfile.py                     # Root metafile (orchestration)
└── SPARETOOLS-MONOREPO-PLAN.md     # This plan
```

---

## 📦 Part 2: Detailed Package Structure

### 2.1 Foundation Layer (Shared Across All Consumers)

```
packages/foundation/
├── sparetools-base/                 # Core utilities, security gates
│   ├── conanfile.py
│   ├── src/
│   │   ├── symlink_helpers.py       # Cross-platform symlink operations
│   │   ├── security_gates.py        # FIPS, Trivy, SBOM validation
│   │   └── conan_extensions.py      # Custom Conan helpers
│   ├── tests/
│   ├── docs/
│   │   ├── API.md                   # API reference
│   │   ├── EXAMPLES.md              # Usage examples
│   │   └── INTEGRATION.md           # Integration patterns
│   └── README.md
│
├── sparetools-bootstrap/            # Bootstrap orchestration
│   ├── conanfile.py
│   ├── src/
│   │   ├── orchestrator.py          # 3-agent orchestration
│   │   ├── environment.py           # Environment validation
│   │   └── matchers.py              # Pattern matching for bootstrap
│   ├── scripts/
│   │   ├── complete-bootstrap.py    # Main bootstrap script
│   │   ├── validate-bootstrap.sh    # Validation harness
│   │   └── activate-env.sh          # Environment activation
│   ├── tests/
│   ├── docs/
│   │   ├── BOOTSTRAP-FLOW.md        # Architecture diagram
│   │   ├── TROUBLESHOOTING.md       # Common issues
│   │   └── RECOVERY-PATTERNS.md     # A/B/C/D failure recovery
│   └── README.md
│
├── sparetools-shared-dev-tools/     # Development utilities
│   ├── conanfile.py
│   ├── src/
│   │   ├── file_operations.py
│   │   ├── yaml_config.py
│   │   ├── cli_tools.py
│   │   └── conan_helpers.py
│   ├── scripts/
│   │   ├── setup-conan-env.sh
│   │   ├── setup-dev-env.sh
│   │   └── validate-packages.py
│   ├── tests/
│   ├── docs/
│   └── README.md
│
└── sparetools-cpython/              # Prebuilt CPython 3.12.7
    ├── conanfile.py
    ├── build-scripts/
    │   ├── build-cpython.sh         # Build orchestration
    │   ├── optimize-cpython.sh      # Apply optimizations
    │   └── validate-cpython.py      # Runtime validation
    ├── patches/                      # Platform-specific patches
    │   ├── macos-arm64.patch
    │   ├── windows-msvc.patch
    │   └── linux-musl.patch
    ├── docs/
    │   ├── BUILD-INSTRUCTIONS.md    # How to rebuild CPython
    │   ├── PLATFORM-SUPPORT.md      # Platform matrix
    │   └── SECURITY-NOTES.md        # Security considerations
    └── README.md
```

### 2.2 Consumer Layers (Organized by Domain)

```
packages/consumers/
│
├── openssl/                         # OpenSSL Consumer Domain
│   ├── sparetools-openssl/          # Main OpenSSL package
│   │   ├── conanfile.py
│   │   ├── src/
│   │   ├── build-methods/
│   │   │   ├── perl_configure.py
│   │   │   ├── cmake_build.py
│   │   │   ├── autotools.py
│   │   │   └── python_configure.py
│   │   ├── test_package/
│   │   ├── docs/
│   │   │   ├── BUILD-MATRIX.md      # All supported configurations
│   │   │   ├── PROVIDER-ORDERING.md # OpenSSL 3.x specifics
│   │   │   ├── FIPS-VALIDATION.md   # FIPS 140-3 guide
│   │   │   └── PROFILES.md          # Profile reference
│   │   └── README.md
│   │
│   └── sparetools-openssl-tools/    # OpenSSL build tools
│       ├── conanfile.py
│       ├── src/
│       │   ├── build.py
│       │   ├── cli.py
│       │   ├── security/
│       │   │   ├── fips_validator.py
│       │   │   └── sbom_generator.py
│       │   ├── automation/
│       │   │   └── build_orchestrator.py
│       │   └── core/
│       │       └── version_manager.py
│       ├── profiles/
│       │   ├── base/
│       │   ├── build-methods/
│       │   └── features/
│       ├── scripts/
│       │   ├── test-openssl-*.py    # Test harnesses
│       │   ├── enhanced-sbom-generator.py
│       │   └── monitor-builds.sh
│       ├── tests/
│       ├── docs/
│       │   ├── PROFILE-GUIDE.md
│       │   ├── SECURITY-GATES.md
│       │   └── SBOM-FORMATS.md
│       └── README.md
│
├── mia/                             # MIA IoT Architecture Consumer
│   ├── sparetools-mia/              # MIA-specific utilities
│   │   ├── conanfile.py
│   │   ├── src/
│   │   │   ├── bootstrap.py         # MIA-specific bootstrap
│   │   │   ├── obd_sim.py           # OBD-II simulation
│   │   │   ├── cloud_integration.py
│   │   │   └── device_manager.py
│   │   ├── scripts/
│   │   │   ├── bootstrap-mia.py
│   │   │   └── setup-device-sim.sh
│   │   ├── tests/
│   │   ├── docs/
│   │   │   ├── MIA-INTEGRATION.md
│   │   │   ├── OBD-SIMULATION.md
│   │   │   └── DEVICE-DRIVERS.md
│   │   └── README.md
│   │
│   └── sparetools-obd-sim/          # OBD-II simulation (automotive)
│       ├── conanfile.py
│       ├── src/
│       │   ├── emulator.py
│       │   ├── scenarios/
│       │   │   ├── car.py
│       │   │   ├── truck.py
│       │   │   └── hybrid.py
│       │   └── protocols/
│       │       ├── elm327.py
│       │       └── obd2.py
│       ├── scripts/
│       │   └── bootstrap-obd.py
│       ├── tests/
│       ├── docs/
│       │   ├── OBD-SIMULATION.md
│       │   ├── EMULATOR-MODES.md
│       │   └── PROTOCOL-REFERENCE.md
│       └── README.md
│
├── mcp/                             # MCP (Model Context Protocol) Consumer
│   ├── sparetools-mcp-orchestrator/ # MCP integration layer
│   │   ├── conanfile.py
│   │   ├── src/
│   │   │   ├── mcp_server.py
│   │   │   ├── fastmcp_integration.py
│   │   │   ├── project_orchestration.py
│   │   │   ├── mermaid/
│   │   │   │   ├── generator.py
│   │   │   │   └── renderer.py
│   │   │   ├── prompts/
│   │   │   │   └── (700+ templates)
│   │   │   └── ecosystem/
│   │   │       └── monitor.py
│   │   ├── scripts/
│   │   │   ├── start-mcp-server.py
│   │   │   └── generate-architecture.sh
│   │   ├── tests/
│   │   ├── docs/
│   │   │   ├── MCP-ARCHITECTURE.md
│   │   │   ├── FASTMCP-GUIDE.md
│   │   │   └── PROMPT-TEMPLATES.md
│   │   └── README.md
│   │
│   ├── sparetools-tinymcp/          # TinyMCP integration
│   │   ├── conanfile.py
│   │   ├── src/
│   │   ├── tests/
│   │   ├── docs/
│   │   └── README.md
│   │
│   └── sparetools-mcpserver-cpp/    # C++ MCP server
│       ├── conanfile.py
│       ├── src/
│       │   ├── server.cpp
│       │   ├── protocol.hpp
│       │   └── handlers/
│       ├── tests/
│       ├── docs/
│       │   └── CPP-SERVER-GUIDE.md
│       └── README.md
│
├── audio/                           # Audio/Media Consumer Domain
│   └── sparetools-rtp-midi/         # RTP-MIDI streaming
│       ├── conanfile.py
│       ├── src/
│       │   ├── rtp_handler.py
│       │   ├── midi_encoder.py
│       │   └── network.py
│       ├── tests/
│       ├── docs/
│       │   ├── RTP-MIDI-SPEC.md
│       │   └── AUDIO-ROUTING.md
│       └── README.md
│
└── automotive/                      # (Already covered in MIA)
    └── (OBD-II in mia/sparetools-obd-sim/)
```

---

## 🛠️ Part 3: Shared Scripts & Recipe Architecture

### 3.1 Shared Scripts Organization

```
scripts/                            # Shared automation
├── bootstrap/
│   ├── complete-bootstrap.py       # Main entry point
│   ├── platform-detect.py          # OS/arch detection
│   ├── cpython-fetch.py            # Download CPython
│   ├── environment-validate.py     # Validation harness
│   └── recovery-agents.py          # A/B/C/D failure patterns
│
├── build/
│   ├── build-orchestrator.py       # Multi-consumer build
│   ├── build-matrix.py             # Generate build matrix
│   ├── parallel-executor.py        # Parallel build runner
│   └── artifact-organizer.py       # Organize build outputs
│
├── validation/
│   ├── security-scan.py            # Trivy integration
│   ├── sbom-generator.py           # Syft/CycloneDX
│   ├── compliance-checker.py       # FIPS, supply chain
│   └── test-runner.py              # Unified test harness
│
├── ci-cd/
│   ├── matrix-generator.py         # GitHub Actions matrix
│   ├── artifact-uploader.py        # Cloudsmith push
│   ├── report-generator.py         # HTML/Markdown reports
│   └── dependency-tracker.py       # Track cross-consumer deps
│
├── deployment/
│   ├── package-installer.py        # Installation automation
│   ├── environment-setup.sh        # Post-install setup
│   └── health-check.py             # Verify deployments
│
├── utilities/
│   ├── workspace-generator.py      # Auto-generate VS Code workspaces
│   ├── doc-linker.py               # Cross-link consumer docs
│   ├── version-bumper.py           # Version management
│   └── changelog-generator.py      # Auto-generate CHANGELOG
│
├── testing/
│   ├── integration-tester.py       # Cross-consumer tests
│   ├── regression-suite.py         # Regression detection
│   └── coverage-analyzer.py        # Code coverage
│
└── README.md
```

### 3.2 Recipe Base Classes (Python Inheritance)

Create `scripts/recipe_base.py`:

```python
# Foundation for all conanfiles
class SpareToolsBaseConan(ConanFile):
    """Base class for all SpareTools packages."""
    
    def configure_platform_profile(self):
        """Auto-detect and apply platform profile."""
        # Platform detection logic
        pass
    
    def apply_security_gates(self):
        """Run security scanning (Trivy, Syft)."""
        # Security validation
        pass
    
    def generate_sbom(self):
        """Auto-generate SBOM (CycloneDX/SPDX)."""
        # SBOM generation
        pass
    
    def validate_build_environment(self):
        """Ensure build environment meets requirements."""
        # Environment checks
        pass

class OpenSSLBaseConan(SpareToolsBaseConan):
    """Specialized base for OpenSSL packages."""
    
    def configure_openssl_settings(self):
        """Handle OpenSSL-specific configuration."""
        pass
    
    def select_build_method(self):
        """Choose optimal build method."""
        pass

class ConsumerPackageConan(SpareToolsBaseConan):
    """Specialized base for consumer packages."""
    
    def declare_consumer_context(self):
        """Register which consumer domain this serves."""
        pass
```

Consumer conanfiles inherit:

```python
from scripts.recipe_base import OpenSSLBaseConan

class SpareToolsOpenSSLConan(OpenSSLBaseConan):
    name = "sparetools-openssl"
    version = "3.3.2"
    
    def configure(self):
        self.configure_openssl_settings()
        self.apply_security_gates()
```

---

## 📚 Part 4: Documentation Strategy

### 4.1 Central Documentation Hub

```
docs/                                           # Central hub
├── README.md                                    # Entry point
├── INDEX.md                                     # Master index (auto-generated)
├── ARCHITECTURE.md                              # Overall design
├── QUICK-START.md                               # Getting started
├── CONTRIBUTING.md                              # Contribution guidelines
├── GLOSSARY.md                                  # Terminology
│
├── foundation/                                  # Shared package docs
│   ├── SPARETOOLS-BASE.md
│   ├── SPARETOOLS-BOOTSTRAP.md
│   ├── SPARETOOLS-CPYTHON.md
│   └── SPARETOOLS-SHARED-DEV-TOOLS.md
│
├── consumers/                                   # Consumer-specific docs
│   ├── openssl/
│   │   ├── README.md
│   │   ├── BUILD-MATRIX.md
│   │   ├── FIPS-GUIDE.md
│   │   ├── PROVIDER-ORDERING.md
│   │   └── SECURITY-GATES.md
│   │
│   ├── mia/
│   │   ├── README.md
│   │   ├── MIA-INTEGRATION.md
│   │   ├── OBD-SIMULATION.md
│   │   ├── DEVICE-DRIVERS.md
│   │   └── CLOUD-INTEGRATION.md
│   │
│   ├── mcp/
│   │   ├── README.md
│   │   ├── MCP-ARCHITECTURE.md
│   │   ├── FASTMCP-INTEGRATION.md
│   │   └── PROMPT-ENGINEERING.md
│   │
│   ├── audio/
│   │   ├── README.md
│   │   ├── RTP-MIDI-GUIDE.md
│   │   └── AUDIO-ROUTING.md
│   │
│   └── automotive/
│       ├── README.md
│       └── OBD-PROTOCOL-REFERENCE.md
│
├── operations/                                  # Operations guides
│   ├── CI-CD-GUIDE.md
│   ├── RELEASE-PROCESS.md
│   ├── DEPLOYMENT-GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── MONITORING-GUIDE.md
│
├── integration/                                 # Integration examples
│   ├── OPENSSL-CONSUMER-EXAMPLE.md
│   ├── MIA-CONSUMER-EXAMPLE.md
│   ├── MCP-CONSUMER-EXAMPLE.md
│   └── CROSS-CONSUMER-INTEGRATION.md
│
├── security/                                    # Security documentation
│   ├── SECURITY-GATES.md
│   ├── FIPS-COMPLIANCE.md
│   ├── SBOM-STRATEGY.md
│   ├── SUPPLY-CHAIN-VERIFICATION.md
│   └── VULNERABILITY-RESPONSE.md
│
├── development/                                 # Development guides
│   ├── WORKSPACE-SETUP.md
│   ├── LOCAL-DEVELOPMENT.md
│   ├── TESTING-STRATEGY.md
│   └── DEBUGGING-GUIDE.md
│
├── api/                                         # Auto-generated API docs
│   ├── SPARETOOLS-BASE-API.md
│   ├── OPENSSL-TOOLS-API.md
│   └── MCP-ORCHESTRATOR-API.md
│
├── examples/                                    # Code examples
│   ├── basic-conan-usage.py
│   ├── cross-consumer-build.py
│   ├── security-integration.py
│   └── mcp-integration.py
│
├── glossary/                                    # Terminology
│   ├── CONAN-TERMINOLOGY.md
│   ├── OPENSSL-TERMINOLOGY.md
│   ├── MCP-TERMINOLOGY.md
│   └── ABBREVIATIONS.md
│
└── templates/                                   # Documentation templates
    ├── PACKAGE-README-TEMPLATE.md
    ├── CONSUMER-INTEGRATION-TEMPLATE.md
    ├── CHANGELOG-TEMPLATE.md
    └── API-REFERENCE-TEMPLATE.md
```

### 4.2 Documentation Automation

Create `scripts/utilities/doc-linker.py`:

```python
class DocumentationLinker:
    """Auto-generate cross-links between docs."""
    
    def generate_master_index(self):
        """Create INDEX.md with TOC from all files."""
        pass
    
    def link_related_docs(self):
        """Insert 'See also:' sections."""
        pass
    
    def validate_links(self):
        """Check all cross-references exist."""
        pass
    
    def generate_api_docs(self):
        """Extract docstrings and generate API reference."""
        pass
    
    def create_consumer_guide(self, consumer_name):
        """Generate consumer-specific onboarding guide."""
        pass
```

---

## 🔄 Part 5: Consumer-Specific Configuration

### 5.1 Consumer Configuration Files

```
packages/consumers/<domain>/.consumer.yaml       # Consumer metadata

# Example: openssl/.consumer.yaml
name: openssl
display_name: "OpenSSL Package Suite"
description: "Production-grade OpenSSL with multiple build methods"
dependencies:
  foundation:
    - sparetools-base
    - sparetools-cpython
  utilities:
    - sparetools-shared-dev-tools

packages:
  - sparetools-openssl
  - sparetools-openssl-tools

examples:
  - ../examples/openssl-basic
  - ../examples/openssl-advanced

documentation:
  main: ../../docs/consumers/openssl/
  integration: ../../docs/consumers/openssl/BUILD-MATRIX.md

ci_workflows:
  - build-openssl
  - test-openssl-variants
  - security-scan-openssl

platforms:
  linux: ["x86_64", "aarch64", "armv7"]
  macos: ["x86_64", "arm64"]
  windows: ["x86_64", "x86"]

supported_versions:
  cpython: ["3.12.7"]
  conan: ["2.21.0+"]
```

---

## 🚀 Part 6: Workflow & Build Automation

### 6.1 Multi-Consumer CI/CD Matrix

```
.github/workflows/build-matrix.yml              # Dynamic matrix workflow

jobs:
  generate-matrix:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4
      - name: Generate build matrix
        id: set-matrix
        run: |
          python scripts/ci-cd/matrix-generator.py \
            --consumers openssl,mia,mcp,audio \
            --platforms linux,macos,windows \
            --output matrix.json
          echo "matrix=$(cat matrix.json)" >> $GITHUB_OUTPUT
  
  build:
    needs: generate-matrix
    strategy:
      matrix: ${{ fromJson(needs.generate-matrix.outputs.matrix) }}
    runs-on: ${{ matrix.runs-on }}
    steps:
      - uses: actions/checkout@v4
      - name: Build ${{ matrix.consumer }}/${{ matrix.package }}
        run: |
          python scripts/ci-cd/build-orchestrator.py \
            --consumer ${{ matrix.consumer }} \
            --package ${{ matrix.package }} \
            --platform ${{ matrix.platform }}
      
      - name: Run security gates
        run: |
          python scripts/validation/security-scan.py
          python scripts/validation/sbom-generator.py
      
      - name: Upload artifacts
        run: |
          python scripts/ci-cd/artifact-uploader.py \
            --target cloudsmith \
            --repo sparesparrow-conan
```

### 6.2 Per-Consumer Workflows

```
.github/workflows/consumer-openssl.yml          # OpenSSL-specific
.github/workflows/consumer-mia.yml              # MIA-specific
.github/workflows/consumer-mcp.yml              # MCP-specific
.github/workflows/consumer-audio.yml            # Audio-specific
.github/workflows/consumer-automotive.yml      # Automotive-specific
```

Each includes:
- Consumer-specific test suites
- Domain-specific security checks
- Consumer-specific artifact handling
- Cross-consumer integration tests

---

## 🎯 Part 7: Workspace Structure & Developer Experience

### 7.1 Nested Workspaces

```
workspaces/
├── root.code-workspace              # Full monorepo (all consumers)
│
├── foundation.code-workspace        # All foundation packages
│
├── consumers/
│   ├── openssl.code-workspace       # OpenSSL domain only
│   ├── mia.code-workspace           # MIA domain only
│   ├── mcp.code-workspace           # MCP domain only
│   ├── audio.code-workspace         # Audio domain only
│   └── automotive.code-workspace    # Automotive domain only
│
├── development/
│   ├── recipe-dev.code-workspace    # conanfile.py focused
│   ├── python-dev.code-workspace    # Python package focused
│   └── cpp-dev.code-workspace       # C++ package focused
│
└── ci-cd/
    ├── testing.code-workspace       # Test development
    ├── security.code-workspace      # Security tooling
    └── documentation.code-workspace # Docs development
```

Each workspace includes:
- Appropriate VS Code extensions
- Pre-configured tasks
- Launch configurations
- Search patterns

---

## 🔍 Part 8: Validation & Testing Framework

### 8.1 Multi-Tier Validation

```
scripts/validation/
├── tier1-syntax.py                  # Basic validation (syntax, files)
├── tier2-dependencies.py            # Dependency resolution
├── tier3-cross-consumer.py          # Cross-consumer compatibility
├── tier4-integration.py             # Full integration tests
└── tier5-security.py                # Security and compliance
```

### 8.2 Per-Consumer Validation Profiles

```
validation/
├── openssl.validation.yaml          # OpenSSL validation config
├── mia.validation.yaml              # MIA validation config
├── mcp.validation.yaml              # MCP validation config
├── audio.validation.yaml            # Audio validation config
└── automotive.validation.yaml       # Automotive validation config
```

Each specifies:
- Required tests
- Security gates
- Performance benchmarks
- Documentation requirements

---

## 📋 Part 9: Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Create new directory structure
- [ ] Extract shared scripts
- [ ] Build recipe base classes
- [ ] Set up central documentation hub
- [ ] Create consumer configuration files

### Phase 2: Foundation Packages (Weeks 3-4)
- [ ] Migrate sparetools-base
- [ ] Migrate sparetools-bootstrap
- [ ] Migrate sparetools-shared-dev-tools
- [ ] Migrate sparetools-cpython
- [ ] Update all conanfile.py references

### Phase 3: Consumer Packages (Weeks 5-8)
- [ ] Migrate OpenSSL consumer
- [ ] Migrate MIA consumer
- [ ] Migrate MCP consumer
- [ ] Migrate Audio consumer
- [ ] Set up consumer configurations

### Phase 4: Automation & CI/CD (Weeks 9-12)
- [ ] Build orchestration scripts
- [ ] Implement validation framework
- [ ] Set up matrix-driven CI/CD
- [ ] Per-consumer workflows
- [ ] Documentation automation

### Phase 5: Developer Experience (Weeks 13-16)
- [ ] Create nested workspaces
- [ ] Documentation linking
- [ ] Integration examples
- [ ] Developer guides
- [ ] Training materials

---

## 🎓 Part 10: Key Principles & Best Practices

### 10.1 Design Principles

1. **Consumer-Centric**: Each consumer is self-contained with shared foundation
2. **Single Responsibility**: Each package has one clear purpose
3. **Inheritance Not Duplication**: Use recipe base classes to reduce boilerplate
4. **Documentation as Code**: Docs generated from code and configs
5. **Hermetic Builds**: No system dependencies beyond sparetools
6. **Security First**: Gates and validation built into every layer
7. **Multi-Platform**: All tooling works across Linux, macOS, Windows

### 10.2 Best Practices

```python
# Recipe structure
class SpareToolsPackageConan(SpareToolsBaseConan):
    """Consumer package following SpareTools patterns."""
    
    python_requires = "sparetools-base/2.0.0"
    python_requires_extend = "sparetools-base.SpareToolsBase"
    
    def configure(self):
        super().configure()  # Apply base security gates
        self.declare_consumer_context()  # Register consumer
    
    def build(self):
        self.validate_build_environment()  # Ensure setup
        self.run_build_logic()
        self.apply_security_gates()
    
    def package(self):
        self.package_artifacts()
        self.generate_sbom()  # Always
```

---

## 🔗 Part 11: Cross-Consumer Integration

### 11.1 Dependency Patterns

```
sparetools-openssl
  ├── python_requires: sparetools-base, sparetools-openssl-tools
  └── tool_requires: sparetools-cpython

sparetools-mia
  ├── requires: sparetools-openssl/3.3.2
  ├── tool_requires: sparetools-cpython
  └── python_requires: sparetools-base

sparetools-mcp-orchestrator
  ├── requires: sparetools-openssl/3.3.2  (optional)
  ├── tool_requires: sparetools-cpython
  └── python_requires: sparetools-base, sparetools-bootstrap

sparetools-rtp-midi
  ├── tool_requires: sparetools-cpython
  └── python_requires: sparetools-base
```

### 11.2 Cross-Consumer Testing

```
scripts/validation/cross-consumer-integration.py

Test Cases:
- OpenSSL → MIA (verify OBD-II over encrypted channel)
- OpenSSL → MCP (verify secure MCP protocol)
- MIA → MCP (verify orchestration)
- All → CPython (verify runtime isolation)
```

---

## 📊 Part 12: Metrics & Success Criteria

### Build Performance
- [ ] Full monorepo build: < 15 minutes
- [ ] Single consumer build: < 5 minutes
- [ ] Incremental rebuild: < 2 minutes

### Coverage
- [ ] Python code coverage: > 85%
- [ ] Documentation coverage: 100%
- [ ] Example coverage: All 4+ scenarios

### Reliability
- [ ] CI/CD success rate: > 99%
- [ ] Security gate pass rate: 100%
- [ ] Cross-consumer compatibility: 100%

---

## 🚀 Quick Reference: Command Examples

After migration:

```bash
# Build all packages
./scripts/build/build-orchestrator.py --all

# Build single consumer
./scripts/build/build-orchestrator.py --consumer openssl

# Validate cross-consumer deps
./scripts/validation/tier3-cross-consumer.py

# Generate docs
python scripts/utilities/doc-linker.py --regenerate

# Open consumer workspace
code workspaces/consumers/openssl.code-workspace

# Run consumer-specific tests
./scripts/ci-cd/test-consumer.sh mia

# Generate SBOM for all packages
./scripts/validation/sbom-generator.py --all --format cyclonedx
```

---

## 📝 Appendix: File Template Examples

### A1: Consumer .consumer.yaml Template

```yaml
# packages/consumers/<domain>/.consumer.yaml
name: my-consumer
display_name: "My Consumer Domain"
description: "Consumer domain for ..."
repository: "https://github.com/sparesparrow/<consumer-repo>"

# Shared dependencies all consumers use
dependencies:
  foundation:
    - sparetools-base/2.0.0
    - sparetools-cpython/3.12.7
    - sparetools-bootstrap/2.0.0
  shared:
    - sparetools-shared-dev-tools/2.0.0
  # Optional: domain-specific dependencies
  specific: []

# Packages in this consumer
packages:
  - sparetools-<consumer>-main
  - sparetools-<consumer>-tools

# Documentation locations
documentation:
  root: ../../docs/consumers/<domain>/
  integration: ../../docs/consumers/<domain>/INTEGRATION.md
  api: ../../docs/consumers/<domain>/API.md

# CI/CD workflows
ci_workflows:
  - build-<consumer>
  - test-<consumer>
  - security-scan-<consumer>

# Platform matrix
platforms:
  linux: ["x86_64", "aarch64"]
  macos: ["x86_64", "arm64"]
  windows: ["x86_64"]

# Minimum supported versions
minimum_versions:
  conan: "2.21.0"
  python: "3.12"
  
# Health checks
health_checks:
  - validate_dependencies
  - run_security_scans
  - check_documentation
```

### A2: Conan Recipe Template

```python
# packages/consumers/<domain>/sparetools-<name>/conanfile.py

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from sys import modules

# Import base class from shared scripts
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..', 'scripts'))
from recipe_base import ConsumerPackageConan

class SpareToolsPackageConan(ConsumerPackageConan):
    name = "sparetools-<name>"
    version = "<version>"
    
    # Declare consumer context
    consumer_domain = "<domain>"
    
    # Use base class features
    python_requires = "sparetools-base/2.0.0"
    
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    defaults = {
        "shared": False,
        "fPIC": True,
    }
    
    def declare_consumer_context(self):
        """Register this package with SpareTools."""
        self.output.info(f"Registering {self.name}/{self.version} for {self.consumer_domain}")
    
    def configure(self):
        """Apply base configuration and security."""
        self.declare_consumer_context()
        self.apply_security_gates()
    
    def layout(self):
        cmake_layout(self)
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def package(self):
        cmake = CMake(self)
        cmake.install()
        self.generate_sbom()
    
    def package_info(self):
        self.cpp_info.libs = ["<lib>"]
```

---

## 📞 Support & Next Steps

**Questions about this plan?** Review the sections:
1. **Structure** (Part 2) - Directory organization
2. **Automation** (Part 3) - Shared scripts and inheritance
3. **CI/CD** (Part 6) - Build and validation workflows
4. **Developer Experience** (Part 7) - Workspace and tooling

**Ready to migrate?** Start with Part 9 (Implementation Roadmap).

---

**Document Version:** 2.0 Enhanced  
**Last Updated:** December 13, 2025  
**Status:** Ready for Implementation
