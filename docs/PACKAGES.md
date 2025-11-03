# SpareTools Package Ecosystem - Complete Inventory

**Repository:** https://github.com/sparesparrow/sparetools  
**Version:** v2.0.0  
**Conan Version:** 2.x  
**Base Distribution:** Cloudsmith (https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/)

---

## Executive Summary

SpareTools is a production-grade Conan 2.x ecosystem for building OpenSSL with multiple build methods (Perl Configure, CMake, Autotools, Python), integrated security scanning, and a zero-copy deployment pattern. The ecosystem consists of **11 packages** organized in foundational layers:

1. **Foundation Layer**: sparetools-base (python_requires)
2. **Prebuilt Tools Layer**: sparetools-cpython (tool_requires)
3. **Utilities Layer**: sparetools-shared-dev-tools, sparetools-openssl-tools (python_requires)
4. **Orchestration Layer**: sparetools-bootstrap, sparetools-mcp-orchestrator (python_requires)
5. **Main Deliverable**: sparetools-openssl/3.3.2 (library)
6. **Deprecated (to be removed)**: 4 legacy packages

---

## FOUNDATIONAL PACKAGES (Layer 1)

### 1. sparetools-base/2.0.0 ✅ PRODUCTION

**Status:** Production  
**Type:** `python-require`  
**Description:** Foundation utilities and security gates shared across all packages

**Purpose:**
- Core utilities for zero-copy deployment patterns
- Security integration (Trivy, Syft SBOM, FIPS validation)
- Conan extensions and common patterns
- Foundation that all other packages depend on

**Exports (Python Modules):**
- `symlink-helpers.py` (7,346 bytes)
  - `create_symlink_with_check()` - Safe symlink creation
  - `zero_copy_deploy()` - Deploy via symlinks
  - `verify_symlink_integrity()` - Validate symlink chains
  - `atomic_symlink_swap()` - Atomic zero-downtime updates

- `security-gates.py` (6,062 bytes)
  - `run_trivy_scan()` - Vulnerability scanning
  - `generate_sbom()` - CycloneDX/SPDX SBOM generation
  - `validate_fips_compliance()` - FIPS validation hooks
  - `security_report()` - Aggregate security reporting

**Dependencies:**
- python_requires: None (this is the base)
- tool_requires: None
- System: Python 3.8+

**Key Features:**
- Zero-copy symlink utilities (80% disk savings)
- Cross-platform support (Linux, macOS, Windows)
- Security gates integrated with Trivy, Syft, FIPS
- Conan helper extensions

**Usage Pattern:**
```python
python_requires = "sparetools-base/2.0.0"

def build(self):
    base = self.python_requires["sparetools-base"].conanfile
    base.run_trivy_scan(self.source_folder)
    base.generate_sbom(self.package_folder)
```

**Development Setup:**
```bash
cd packages/sparetools-base
conan export . --version=2.0.0
```

---

## PREBUILT TOOLS LAYER (Layer 2)

### 2. sparetools-cpython/3.12.7 ✅ PRODUCTION

**Status:** Production  
**Type:** `application` (tool_requires)  
**Description:** Prebuilt Python 3.12.7 runtime for DevOps ecosystem

**Purpose:**
- Consistent Python runtime across all build environments
- Eliminates system Python version conflicts
- Used by OpenSSL hybrid builds and Python-based tools

**Build Configuration:**
```
--enable-optimizations --with-lto --enable-shared
```

**Exports (Binaries):**
- `bin/python3.12` (primary)
- `bin/python3` (symlink)
- `bin/python` (symlink)
- Library path: `lib/`
- Version file: `VERSION` (contains "3.12.7")

**Dependencies:**
- python_requires: "sparetools-base/2.0.0"
- tool_requires: None
- System: Prebuilt - no compilation required

**Key Features:**
- Prebuilt (no compilation needed)
- Cross-platform (Linux, Windows, macOS)
- Self-contained runtime
- Optimized with LTO

**Usage Pattern:**
```python
tool_requires = "sparetools-cpython/3.12.7"

def build(self):
    self.run("python3 --version")
    self.run("python3 my_script.py")
```

**Configuration:**
```bash
CPYTHON_STAGING_DIR=/tmp/cpython-3.12.7-staging/usr/local \
conan create packages/sparetools-cpython --version=3.12.7
```

---

## UTILITIES LAYER (Layer 3)

### 3. sparetools-shared-dev-tools/2.0.0 ✅ PRODUCTION

**Status:** Production  
**Type:** `python-require`  
**Description:** Generic development utilities and CLI tools

**Purpose:**
- Reusable development scripts across packages
- Conan helpers and utilities
- Configuration management
- File operations

**Exports (Python Modules):**
- `shared_dev_tools/` - Development tool modules
- `scripts/` - Automation scripts
  - `setup-conan-env.sh` - Conan environment setup
  - `setup-dev-env.sh` - Development environment setup
  - `validate-conan-packages.py` - Package validation

**Dependencies:**
- python_requires: "sparetools-base/2.0.0"
- tool_requires: None

**Key Features:**
- CLI tools for common operations
- Conan integration helpers
- YAML configuration support
- File operation utilities

**Usage Pattern:**
```python
python_requires = "sparetools-shared-dev-tools/2.0.0"
```

---

### 4. sparetools-openssl-tools/2.0.0 ✅ PRODUCTION

**Status:** Production  
**Type:** `python-require`  
**Description:** Complete OpenSSL build automation, FIPS validation, and security tools

**Purpose:**
- OpenSSL-specific build orchestration
- FIPS 140-3 validation and compliance
- Conan build profiles (15+ configurations)
- Security scanning and SBOM generation
- Build matrix generation

**Exports (Python Modules + Profiles):**
- Core Modules:
  - `openssl_tools/build.py` - Build orchestration
  - `openssl_tools/cli.py` - Command-line interface
  - `openssl_tools/conan_functions.py` - Conan integration

- Automation:
  - `openssl_tools/automation/build_orchestrator.py` - Pipeline automation

- Security:
  - `openssl_tools/security/fips_validator.py` - FIPS validation (570+ lines)
  - `openssl_tools/security/sbom_generator.py` - SBOM generation

- Core Utilities:
  - `openssl_tools/core/version_manager.py` - Version management

- Build Profiles (15+ configurations):
  - **base/** - Platform/compiler profiles (linux-gcc11, windows-msvc2022, darwin-clang, etc.)
  - **build-methods/** - perl-configure, cmake-build, autotools, python-configure
  - **features/** - fips-enabled, shared-libs, static-only, minimal, performance
  - **matrix/** - Build matrix documentation

- Scripts (15+ automation scripts):
  - `test-openssl-*.py` - OpenSSL testing scripts
  - `enhanced-sbom-generator.py` - Advanced SBOM generation
  - `implement-parallel-tracks.sh` - Parallel build orchestration
  - `monitor-*.sh` - Performance/security monitoring
  - `verify-bootstrap.sh` - Bootstrap verification

**Dependencies:**
- python_requires: "sparetools-base/2.0.0"
- tool_requires: None

**Key Features:**
- 15+ Conan build profiles for platform/compiler/feature combinations
- FIPS 140-3 validation (570+ lines dedicated module)
- Security scanning integration (Trivy, Syft)
- Build matrix generation for CI/CD
- Version management
- Performance monitoring
- Parallel build orchestration

**Usage Pattern:**
```bash
# Using profiles
conan create packages/sparetools-openssl --version=3.3.2 \
  -pr:b profiles/base/linux-gcc11 \
  -pr:b profiles/build-methods/perl-configure \
  -pr:b profiles/features/fips-enabled

# FIPS validation
python -m openssl_tools.fips_validator --module fips-3.0.8 --strict

# SBOM generation
python -m openssl_tools.sbom_generator --format cyclonedx
```

---

## ORCHESTRATION LAYER (Layer 4)

### 5. sparetools-bootstrap/2.0.0 ✅ PRODUCTION

**Status:** Production (Critical Issue: Missing python_requires declaration - see Issue 4)  
**Type:** `python-require`  
**Description:** Bootstrap automation and 3-agent orchestration system

**Purpose:**
- Automated environment setup and validation
- Three-agent orchestration (EXECUTOR → VALIDATOR → ORCHESTRATOR)
- Build matrix generation
- Cryptographic configuration management
- FIPS validation helpers
- SBOM generation

**Exports (Python Modules):**
- Core:
  - `bootstrap/conan_functions.py` - Conan operation helpers

- Orchestration:
  - `bootstrap/openssl/build_matrix.py` - Build matrix generation
  - `bootstrap/openssl/crypto_config.py` - Crypto configuration
  - `bootstrap/openssl/fips_validator.py` - FIPS validation
  - `bootstrap/openssl/sbom_generator.py` - SBOM generation

- Scripts:
  - Automation scripts for orchestration

**Dependencies:**
```
ISSUE #4: Missing Declaration!
Current code shows no python_requires, but README suggests:
  - python_requires: "sparetools-shared-dev-tools/2.0.0"
  - python_requires: "sparetools-base/2.0.0"
SHOULD BE FIXED: Add python_requires declarations
```

**Key Features:**
- Three-agent orchestration pattern
- Automated build matrix generation
- Crypto configuration management
- FIPS validation
- SBOM generation
- Environment bootstrap

**Architecture:**
```
ORCHESTRATOR (Coordinates)
  ├── EXECUTOR (Builds & Packages)
  │   ├── Build OpenSSL
  │   ├── Package with Conan
  │   └── Generate Artifacts
  └── VALIDATOR (Verifies)
      ├── Run Tests
      ├── Security Scans (Trivy/Syft)
      ├── Generate SBOM
      └── FIPS Validation
```

---

### 6. sparetools-mcp-orchestrator/2.0.0 ✅ PRODUCTION

**Status:** Production (General-purpose, not OpenSSL-specific)  
**Type:** `python-require`  
**Description:** MCP (Model Context Protocol) integration and AI-assisted development

**Purpose:**
- MCP server integration (FastMCP and custom servers)
- AI-assisted development (Cursor IDE integration)
- Mermaid diagram generation and rendering
- Prompt management (700+ templates)
- Project orchestration
- Ecosystem monitoring
- AWS integration

**Exports (Python Modules):**
- Core MCP:
  - `mcp_project_orchestrator/core/` - Core MCP functionality
  - `mcp_project_orchestrator/fastmcp.py` - FastMCP integration
  - `mcp_project_orchestrator/server.py` - MCP server

- AI & Orchestration:
  - `mcp_project_orchestrator/project_orchestration.py` - Project orchestration
  - `mcp_project_orchestrator/fan_out_orchestrator.py` - Fan-out patterns
  - `mcp_project_orchestrator/ecosystem_monitor.py` - Ecosystem monitoring
  - `mcp_project_orchestrator/cli.py` - Command-line interface

- Mermaid Diagramming:
  - `mcp_project_orchestrator/mermaid/generator.py` - Diagram generation
  - `mcp_project_orchestrator/mermaid/renderer.py` - Diagram rendering
  - `mcp_project_orchestrator/mermaid/` - Complete tooling

- Prompt Management:
  - `mcp_project_orchestrator/prompts/` - 700+ prompt templates
  - `mcp_project_orchestrator/prompt_manager/` - Prompt management

- Scripts:
  - Automation scripts for MCP operations

**Dependencies:**
- python_requires: "sparetools-base/2.0.0"
- tool_requires: None

**Key Features:**
- MCP server with FastMCP integration
- AI-powered code generation (Cursor IDE)
- Mermaid architecture diagram automation
- 700+ prompt templates
- Multi-repository orchestration
- Ecosystem health monitoring
- AWS service integration

**Note:** This is general-purpose tooling, not specific to OpenSSL. Should be considered for extraction into separate repository (sparesparrow/mcp-orchestrator) for broader reuse.

**Usage Pattern:**
```bash
# Start MCP server
python -m mcp_project_orchestrator.server

# Generate diagram
python -m mcp_project_orchestrator.cli diagram --type architecture
```

---

## MAIN DELIVERABLE (Layer 5)

### 7. sparetools-openssl/3.3.2 ✅ PRODUCTION

**Status:** Production  
**Type:** `library`  
**Description:** Unified OpenSSL package with multiple build method support

**Purpose:**
- Primary deliverable - production-grade OpenSSL library
- Consolidated package replacing 4 deprecated variants
- Support for 4 build methods (Perl Configure, CMake, Autotools, Python)
- FIPS 140-3 compliance support
- Security integration (Trivy scanning, SBOM generation)
- Cross-platform (Linux, Windows, macOS, FreeBSD, Android, iOS)

**Settings:**
```
os, arch, compiler, build_type
```

**Options:**
```
build_method:  [perl, cmake, autotools, python]  (default: perl)
shared:        [True, False]                      (default: False)
fPIC:          [True, False]                      (default: True)
fips:          [True, False]                      (default: False)
enable_threads:[True, False]                      (default: True)
enable_asm:    [True, False]                      (default: True)
enable_zlib:   [True, False]                      (default: True)
enable_legacy: [True, False]                      (default: False)
enable_avx:    [True, False]                      (default: True)
enable_avx2:   [True, False]                      (default: True)
enable_neon:   [True, False]                      (default: True)
enable_sve:    [True, False]                      (default: False)
```

**Dependencies:**
```
tool_requires:
  - sparetools-openssl-tools/2.0.0
  - sparetools-cpython/3.12.7

python_requires:
  - sparetools-base/2.0.0
```

**Build Methods:**
1. **Perl Configure** (DEFAULT - Production)
   - Most stable and feature-complete
   - Full OpenSSL feature support
   - Proven in production
   - Supports Unix-like (make) and Windows (nmake/MSVC)

2. **CMake** (Modern - Optional)
   - Better IDE integration
   - Native Conan CMake support
   - Faster configuration
   - Falls back to Perl if CMake not available

3. **Autotools** (Cross-compilation)
   - Conan Autotools integration wrapper
   - Standardized patterns
   - Cross-compilation support
   - Embedded target support

4. **Python configure.py** (Experimental - 65% feature parity)
   - Pure Python implementation
   - No Perl dependency
   - Extensible and maintainable
   - Falls back to Perl on failure
   - Note: Currently incomplete (see CLAUDE.md Issue 1)

**Exports:**
```cpp
Libraries:
  - OpenSSL::SSL (libssl)
  - OpenSSL::Crypto (libcrypto)
  
CMake Targets:
  - OpenSSL::OpenSSL (unified)
  - OpenSSL::SSL (component)
  - OpenSSL::Crypto (component)

pkg-config:
  - openssl
  - libssl
  - libcrypto
```

**Source Code:**
- Downloads from: https://github.com/openssl/openssl/releases/tag/openssl-3.3.2
- Includes: configure.py (Python helper script)

**Test Package:**
```cpp
Integration tests:
  - test_openssl - Basic functionality test
  - test_provider_ordering - Provider configuration test (3.x specific)
  - test_fips_smoke - FIPS smoke test (optional)
```

**Security Integration:**
```
During build():
  - run_trivy_scan() - Vulnerability scanning
  - generate_sbom() - CycloneDX/SPDX SBOM generation
  - If FIPS enabled: FIPS validation
```

**Platform Support:**
| Platform | Architecture | Status |
|----------|-------------|--------|
| Linux | x86_64 | ✅ Tested |
| Linux | ARM64 | ✅ Supported |
| Windows | x86_64 | ✅ Supported |
| macOS | x86_64 | ✅ Supported |
| macOS | ARM64 | ✅ Supported |
| FreeBSD | x86_64 | ⚠️ Experimental |

**Configuration Targets:**
- Linux: linux-x86_64, linux-x86, linux-aarch64, linux-armv4, linux-mips, linux-mips64, linux-ppc64le
- Windows: VC-WIN64A (x86_64), VC-WIN32 (x86), VC-WIN-ARM64
- macOS: darwin64-x86_64-cc, darwin64-arm64-cc
- FreeBSD: BSD-x86_64, BSD-x86, BSD-aarch64
- Android: android-x86_64, android-x86, android-arm64, android-arm
- iOS: ios64-cross

**Usage Examples:**
```bash
# Basic
conan install --requires=sparetools-openssl/3.3.2

# With CMake build
conan install --requires=sparetools-openssl/3.3.2 \
  -o sparetools-openssl/*:build_method=cmake

# With FIPS
conan install --requires=sparetools-openssl/3.3.2 \
  -o sparetools-openssl/*:fips=True

# With profiles
conan create packages/sparetools-openssl --version=3.3.2 \
  -pr:b profiles/base/linux-gcc11 \
  -pr:b profiles/build-methods/perl-configure \
  -pr:b profiles/features/fips-enabled
```

**Development Setup:**
```bash
cd packages/sparetools-openssl
conan create . --version=3.3.2 --build=missing
conan test test_package sparetools-openssl/3.3.2@
```

---

## DEPRECATED PACKAGES (To Be Removed)

These packages are consolidated into `sparetools-openssl` and should be removed:

### 8. sparetools-openssl-cmake/3.3.2 ⚠️ DEPRECATED

**Status:** Deprecated (consolidated into main package)  
**Type:** `library`  
**Description:** OpenSSL built with CMake build system

**Why Deprecated:**
- Functionality now available via `sparetools-openssl -o build_method=cmake`
- Use unified package instead

**Replacement:**
```bash
# OLD (deprecated)
conan install --requires=sparetools-openssl-cmake/3.3.2

# NEW (use this)
conan install --requires=sparetools-openssl/3.3.2 \
  -o sparetools-openssl/*:build_method=cmake
```

---

### 9. sparetools-openssl-autotools/3.3.2 ⚠️ DEPRECATED

**Status:** Deprecated (consolidated into main package)  
**Type:** `library`  
**Description:** OpenSSL built with Conan Autotools integration

**Why Deprecated:**
- Functionality now available via `sparetools-openssl -o build_method=autotools`
- Use unified package instead

**Replacement:**
```bash
# OLD (deprecated)
conan install --requires=sparetools-openssl-autotools/3.3.2

# NEW (use this)
conan install --requires=sparetools-openssl/3.3.2 \
  -o sparetools-openssl/*:build_method=autotools
```

---

### 10. sparetools-openssl-hybrid/3.3.2 ⚠️ DEPRECATED

**Status:** Deprecated (consolidated into main package)  
**Type:** `library`  
**Description:** OpenSSL with hybrid Python-enhanced approach

**Why Deprecated:**
- Functionality now available via `sparetools-openssl -o build_method=python`
- Python configure.py moved to main package
- Experimental status carries over to unified package

**Replacement:**
```bash
# OLD (deprecated)
conan install --requires=sparetools-openssl-hybrid/3.3.2

# NEW (use this)
conan install --requires=sparetools-openssl/3.3.2 \
  -o sparetools-openssl/*:build_method=python
```

---

### 11. sparetools-openssl-tools-mini/1.0.0 ⚠️ DEPRECATED

**Status:** Deprecated (merged into sparetools-openssl-tools)  
**Type:** `python-require`  
**Description:** Minimal OpenSSL tools (now full-featured)

**Why Deprecated:**
- Merged into `sparetools-openssl-tools/2.0.0`
- Full tools package now provides all needed functionality
- No longer necessary to maintain separate minimal version

**Replacement:**
```bash
# OLD (deprecated)
python_requires = "sparetools-openssl-tools-mini/1.0.0"

# NEW (use this)
python_requires = "sparetools-openssl-tools/2.0.0"
```

---

## DEPENDENCY GRAPH (Foundational Order)

```
Build Order (Critical - depends on dependencies):

1. sparetools-base/2.0.0
   ↓
2. sparetools-cpython/3.12.7
   sparetools-shared-dev-tools/2.0.0
   ↓
3. sparetools-openssl-tools/2.0.0
   ↓
4. sparetools-bootstrap/2.0.0
   sparetools-mcp-orchestrator/2.0.0
   ↓
5. sparetools-openssl/3.3.2 (MAIN DELIVERABLE)
```

**Dependency Matrix:**

| Package | python_requires | tool_requires | Purpose |
|---------|---|---|---|
| sparetools-base | ❌ None | ❌ None | Foundation |
| sparetools-cpython | ✅ base | ❌ None | Prebuilt Python |
| sparetools-shared-dev-tools | ✅ base | ❌ None | Utilities |
| sparetools-openssl-tools | ✅ base | ❌ None | OpenSSL Tools |
| sparetools-bootstrap | ⚠️ MISSING (should be base + shared-dev-tools) | ❌ None | Orchestration |
| sparetools-mcp-orchestrator | ✅ base | ❌ None | MCP Integration |
| **sparetools-openssl** | **✅ base** | **✅ tools, cpython** | **MAIN** |

---

## KNOWN ISSUES & CRITICAL NOTES

### Issue #1: OpenSSL 3.6.0 Build Complexity ⚠️ OPEN

**Status:** Known limitation - stick with 3.3.2 for production  
**Severity:** High  
**Details:**
- OpenSSL 3.6.0 has complex provider architecture with dynamic dependencies
- Python configure.py is only 65% feature-complete
- Perl Configure works but requires Perl 5.10+
- CMake support incomplete in upstream OpenSSL
- **Recommendation:** Use OpenSSL 3.3.2 for SpareTools primary builds
- See `CLAUDE.md` Issue 1 for deep technical analysis

### Issue #2: Testing Deficit ⚠️ OPEN

**Status:** Unit test coverage <5%  
**Severity:** Medium  
**Target:** 60% coverage using pytest  
**Action:** Integrate pytest framework and expand test suite

### Issue #3: Deprecated Packages Cleanup ⚠️ OPEN

**Status:** 4 packages ready for removal  
**Severity:** Medium  
**Packages to remove:**
- sparetools-openssl-cmake/3.3.2
- sparetools-openssl-autotools/3.3.2
- sparetools-openssl-hybrid/3.3.2
- sparetools-openssl-tools-mini/1.0.0

**Action:** Remove after transition period and update CI/docs

### Issue #4: Missing python_requires Declaration ⚠️ CRITICAL

**Status:** sparetools-bootstrap missing declarations  
**Severity:** High  
**Details:**
```python
# CURRENT (incorrect - missing dependencies!)
class SpareToolsBootstrapConan(ConanFile):
    name = "sparetools-bootstrap"
    version = "2.0.0"
    # NO python_requires!

# SHOULD BE:
class SpareToolsBootstrapConan(ConanFile):
    name = "sparetools-bootstrap"
    version = "2.0.0"
    python_requires = "sparetools-base/2.0.0"
    # ALSO should depend on shared-dev-tools if used
```

**Action:** Add `python_requires = "sparetools-base/2.0.0"` to conanfile.py

### Issue #5: Hardcoded Paths ⚠️ OPEN

**Status:** Environment variable support needed  
**Severity:** Low  
**Details:** Some paths are hardcoded (e.g., CPYTHON_STAGING_DIR)  
**Action:** Use environment variables for staging paths with sensible defaults

---

## PACKAGE STATISTICS

| Category | Count | Details |
|----------|-------|---------|
| **Total Packages** | 11 | All variants |
| **Production Packages** | 7 | Ready for use |
| **Deprecated Packages** | 4 | To be removed |
| **Python-Require Packages** | 6 | Utilities and tools |
| **Application Packages** | 1 | sparetools-cpython |
| **Library Packages** | 4 | OpenSSL variants (1 active + 3 deprecated) |
| | | |
| **Total Python Modules** | 30+ | Core functionality |
| **Build Profiles** | 15+ | Platform/compiler/feature combos |
| **Automation Scripts** | 20+ | CI/CD and orchestration |
| **Documentation Files** | 11+ | READMEs and guides |

---

## BUILD PROFILES REFERENCE

Located in: `packages/sparetools-openssl-tools/profiles/`

### Base Profiles (Platform + Compiler)
- `linux-gcc11` - Linux with GCC 11
- `linux-clang14` - Linux with Clang 14
- `darwin-clang-arm64` - macOS ARM64 (Apple Silicon)
- `darwin-clang-x86_64` - macOS x86_64
- `windows-msvc2022` - Windows with MSVC 2022
- Additional platform-specific profiles

### Build Method Profiles
- `perl-configure` - Standard Perl Configure (default, production)
- `cmake-build` - CMake build system
- `autotools` - Autotools wrapper
- `python-configure` - Python configure.py (experimental)

### Feature Profiles
- `fips-enabled` - FIPS 140-3 compliance mode
- `shared-libs` - Build shared libraries
- `static-only` - Static libraries only
- `minimal` - Minimal feature set
- `performance` - Performance optimizations

### Usage
```bash
# Stack profiles: base → build-method → features
conan create packages/sparetools-openssl --version=3.3.2 \
  -pr:b profiles/base/linux-gcc11 \
  -pr:b profiles/build-methods/perl-configure \
  -pr:b profiles/features/fips-enabled
```

---

## QUICK START GUIDE

### 1. Build All Packages (Production Order)
```bash
cd /home/sparrow/sparetools

# Foundation
conan create packages/sparetools-base --version=2.0.0

# Prebuilt Python (requires CPYTHON_STAGING_DIR)
CPYTHON_STAGING_DIR=/tmp/cpython-3.12.7-staging/usr/local \
conan create packages/sparetools-cpython --version=3.12.7

# Utilities
conan create packages/sparetools-shared-dev-tools --version=2.0.0
conan create packages/sparetools-openssl-tools --version=2.0.0

# Orchestration
conan create packages/sparetools-bootstrap --version=2.0.0
conan create packages/sparetools-mcp-orchestrator --version=2.0.0

# Main deliverable
conan create packages/sparetools-openssl --version=3.3.2 --build=missing
```

### 2. Build with Specific Configuration
```bash
# FIPS-enabled with Perl Configure
conan create packages/sparetools-openssl --version=3.3.2 \
  -o sparetools-openssl/*:fips=True

# CMake build
conan create packages/sparetools-openssl --version=3.3.2 \
  -o sparetools-openssl/*:build_method=cmake

# Shared libraries
conan create packages/sparetools-openssl --version=3.3.2 \
  -o sparetools-openssl/*:shared=True
```

### 3. Run Integration Tests
```bash
conan test packages/sparetools-openssl/test_package \
  sparetools-openssl/3.3.2@

# With FIPS tests
conan test packages/sparetools-openssl/test_package \
  sparetools-openssl/3.3.2@ \
  -o test_fips=True
```

### 4. Security Scanning
```bash
# Vulnerability scan (requires Trivy)
trivy fs --security-checks vuln /home/sparrow/sparetools

# SBOM generation (requires Syft)
syft packages /home/sparrow/sparetools -o cyclonedx-json > sbom.json

# FIPS validation
python -m openssl_tools.fips_validator --module fips-3.0.8 --strict
```

---

## RELATED REPOSITORIES

### Official
- **Main:** https://github.com/sparesparrow/sparetools (this repository)
- **Distribution:** https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/

### External Resources
- **OpenSSL:** https://github.com/openssl/openssl
- **OpenSSL Docs:** https://www.openssl.org/docs/
- **FIPS 140-3:** https://csrc.nist.gov/publications/detail/fips/140/3/final
- **Conan:** https://docs.conan.io/2/
- **Trivy:** https://aquasecurity.github.io/trivy/
- **Syft:** https://github.com/anchore/syft

### Future Separation Candidates
- **sparetools-mcp-orchestrator** - Consider separating into sparesparrow/mcp-orchestrator for broader use

---

## MIGRATION GUIDE (From Deprecated Packages)

### From Separate Packages to Unified
```bash
# OLD: Using separate packages
conan install --requires=sparetools-openssl-cmake/3.3.2
conan install --requires=sparetools-openssl-autotools/3.3.2
conan install --requires=sparetools-openssl-hybrid/3.3.2

# NEW: Using unified package with options
conan install --requires=sparetools-openssl/3.3.2 \
  -o sparetools-openssl/*:build_method=cmake

conan install --requires=sparetools-openssl/3.3.2 \
  -o sparetools-openssl/*:build_method=autotools

conan install --requires=sparetools-openssl/3.3.2 \
  -o sparetools-openssl/*:build_method=python
```

### From Mini to Full Tools
```bash
# OLD: Using minimal tools
python_requires = "sparetools-openssl-tools-mini/1.0.0"

# NEW: Using complete tools
python_requires = "sparetools-openssl-tools/2.0.0"
```

---

## ZERO-COPY DEPLOYMENT PATTERN

### Concept
Artifacts stored once in Conan cache, exposed via OS-level symlinks. Saves 80% disk space and enables atomic updates.

### Layout Example
```
Conan Cache (~/.conan2/p/):
  ├── sparetools-base/...
  ├── sparetools-cpython/.../p/ (ACTUAL FILES)
  └── sparetools-openssl/.../p/ (ACTUAL FILES)

Workspace (_Build/packages/):
  ├── sparetools-base → ~/.conan2/p/.../sparetools-base/p
  ├── sparetools-cpython → ~/.conan2/p/.../sparetools-cpython/p
  └── sparetools-openssl → ~/.conan2/p/.../sparetools-openssl/p

Consumer Projects:
  ├── bin → _Build/packages/sparetools-cpython/bin
  ├── lib → _Build/packages/sparetools-openssl/lib
  └── include → _Build/packages/sparetools-openssl/include
```

### Usage via sparetools-base
```python
from symlink_helpers import zero_copy_deploy

zero_copy_deploy(
    source_dir="~/.conan2/p/openssl/p",
    target_dir="./my-workspace/openssl",
    pattern="*.so"
)
```

---

## VERSION MATRIX

| Package | Version | Status | Release |
|---------|---------|--------|---------|
| sparetools-base | 2.0.0 | ✅ Production | v2.0.0 |
| sparetools-cpython | 3.12.7 | ✅ Production | v2.0.0 |
| sparetools-shared-dev-tools | 2.0.0 | ✅ Production | v2.0.0 |
| sparetools-openssl-tools | 2.0.0 | ✅ Production | v2.0.0 |
| sparetools-bootstrap | 2.0.0 | ✅ Production | v2.0.0 |
| sparetools-mcp-orchestrator | 2.0.0 | ✅ Production | v2.0.0 |
| **sparetools-openssl** | **3.3.2** | **✅ Production** | **v2.0.0** |
| sparetools-openssl-cmake | 3.3.2 | ⚠️ Deprecated | v1.x |
| sparetools-openssl-autotools | 3.3.2 | ⚠️ Deprecated | v1.x |
| sparetools-openssl-hybrid | 3.3.2 | ⚠️ Deprecated | v1.x |
| sparetools-openssl-tools-mini | 1.0.0 | ⚠️ Deprecated | v1.x |

---

## SUMMARY TABLE

| # | Package Name | Version | Type | Status | Depends On | Exports |
|---|---|---|---|---|---|---|
| 1 | sparetools-base | 2.0.0 | python-require | ✅ Prod | — | symlink-helpers, security-gates |
| 2 | sparetools-cpython | 3.12.7 | application | ✅ Prod | base | python3.12 binary |
| 3 | sparetools-shared-dev-tools | 2.0.0 | python-require | ✅ Prod | base | dev utilities, scripts |
| 4 | sparetools-openssl-tools | 2.0.0 | python-require | ✅ Prod | base | openssl_tools, 15+ profiles |
| 5 | sparetools-bootstrap | 2.0.0 | python-require | ✅ Prod | ⚠️ MISSING | orchestration, FIPS validator |
| 6 | sparetools-mcp-orchestrator | 2.0.0 | python-require | ✅ Prod | base | MCP, Mermaid, prompts |
| 7 | **sparetools-openssl** | **3.3.2** | **library** | **✅ Prod** | **base, tools, cpython** | **OpenSSL libs + tools** |
| 8 | sparetools-openssl-cmake | 3.3.2 | library | ⚠️ Deprecated | — | (use unified package) |
| 9 | sparetools-openssl-autotools | 3.3.2 | library | ⚠️ Deprecated | — | (use unified package) |
| 10 | sparetools-openssl-hybrid | 3.3.2 | library | ⚠️ Deprecated | — | (use unified package) |
| 11 | sparetools-openssl-tools-mini | 1.0.0 | python-require | ⚠️ Deprecated | — | (use full tools) |

---

**End of SpareTools Package Ecosystem Summary**  
Generated: 2025-11-01  
Repository: https://github.com/sparesparrow/sparetools
