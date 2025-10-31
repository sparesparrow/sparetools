# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**SpareTools** is a Conan 2.x-based DevOps ecosystem for building OpenSSL with multiple build methods (Perl Configure, CMake, Autotools, Python), integrated security scanning (Trivy, Syft, FIPS), and zero-copy deployment patterns.

**Repository:** https://github.com/sparesparrow/sparetools
**Cloudsmith:** https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/

---

## Essential Commands

### Package Development

```bash
# Build a package locally (OpenSSL example)
cd packages/sparetools-openssl
conan create . --version=3.3.2 --build=missing

# Build with specific profile and build method
conan create . --version=3.3.2 \
  -pr:b ../sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b ../sparetools-openssl-tools/profiles/build-methods/perl-configure \
  -pr:b ../sparetools-openssl-tools/profiles/features/fips-enabled

# Test a built package
conan test test_package sparetools-openssl/3.3.2@

# Install from Cloudsmith (consumer workflow)
conan remote add sparesparrow-conan \
  https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/
conan install --requires=sparetools-openssl/3.3.2 -r sparesparrow-conan
```

### Building All Packages

```bash
# Build base packages first (order matters due to dependencies)
cd packages/sparetools-base
conan create . --version=2.0.0

cd ../sparetools-cpython
conan create . --version=3.12.7

cd ../sparetools-shared-dev-tools
conan create . --version=2.0.0

cd ../sparetools-openssl-tools
conan create . --version=2.0.0

cd ../sparetools-openssl
conan create . --version=3.3.2 --build=missing
```

### Security Scanning

```bash
# Run Trivy vulnerability scan
trivy fs --security-checks vuln .

# Generate SBOM with Syft
syft packages . -o cyclonedx-json > sbom.json
syft packages . -o spdx-json > sbom-spdx.json

# FIPS validation (if module present)
python3 -c "from sparetools.openssl_tools.fips_validator import FIPSValidator; \
  FIPSValidator().validate_module('/path/to/fips/module')"
```

### Testing

```bash
# NOTE: Unit tests are currently MISSING (<5% coverage)
# Only integration tests exist via Conan test_package

# Run integration test for OpenSSL
cd packages/sparetools-openssl
conan test test_package sparetools-openssl/3.3.2@

# Validate installation script
bash scripts/validate-install.sh
```

### CI/CD Workflows

```bash
# Manually trigger publish workflow
gh workflow run publish.yml

# View workflow runs
gh run list --workflow=ci.yml

# Check security scan results
gh run list --workflow=security.yml
```

---

## Architecture

### Package Ecosystem (7 Production Packages)

**Current Versions (v2.0.0 ecosystem):**
- `sparetools-base/2.0.0` - Foundation utilities (security gates, symlink helpers)
- `sparetools-cpython/3.12.7` - Prebuilt Python runtime
- `sparetools-shared-dev-tools/2.0.0` - Generic development utilities
- `sparetools-openssl-tools/2.0.0` - OpenSSL-specific tooling (profiles, FIPS validator)
- `sparetools-bootstrap/2.0.0` - 3-agent orchestration system
- `sparetools-mcp-orchestrator/2.0.0` - MCP/AI integration
- `sparetools-openssl/3.3.2` - **Main deliverable** - OpenSSL library with 4 build methods

**Deprecated Packages (to be removed):**
- `sparetools-openssl-cmake` (consolidated into main package)
- `sparetools-openssl-autotools` (consolidated into main package)
- `sparetools-openssl-hybrid` (experimental Python configure.py)
- `sparetools-openssl-tools-mini` (merged into sparetools-openssl-tools)

### Dependency Graph

```
sparetools-openssl/3.3.2 (MAIN DELIVERABLE)
├── tool_requires: sparetools-openssl-tools/2.0.0
├── tool_requires: sparetools-cpython/3.12.7 (optional)
└── python_requires: sparetools-base/2.0.0

sparetools-openssl-tools/2.0.0
└── python_requires: sparetools-base/2.0.0 (should be declared but isn't)

sparetools-shared-dev-tools/2.0.0
└── python_requires: sparetools-base/2.0.0 (should be declared but isn't)

sparetools-cpython/3.12.7
└── python_requires: sparetools-base/1.0.0 (WRONG - should be 2.0.0)

sparetools-base/2.0.0 (FOUNDATION)
└── (no dependencies)
```

### Multi-Build System (Core Innovation)

`sparetools-openssl` supports 4 build methods via `build_method` option:

1. **perl** (default, proven, 100% reliable)
   - Uses OpenSSL's standard `./Configure` Perl script
   - Profile: `profiles/build-methods/perl-configure`
   - Implementation: `_build_with_perl()` in conanfile.py:148-167

2. **cmake** (modern, IDE-friendly)
   - Uses CMake-based build
   - Profile: `profiles/build-methods/cmake-build`
   - Implementation: `_build_with_cmake()` in conanfile.py:169-187

3. **autotools** (Unix standard)
   - Uses Autotools (configure/make)
   - Profile: `profiles/build-methods/autotools`
   - Implementation: `_build_with_autotools()` in conanfile.py:189-193

4. **python** (experimental)
   - Intended for Python configure.py (not fully integrated)
   - Implementation: `_build_with_python()` in conanfile.py:195-215
   - **STATUS:** Falls back to Perl - Python configure.py is in deprecated hybrid package

Build method selection in conanfile.py:217-233:
```python
def build(self):
    build_methods = {
        "perl": self._build_with_perl,
        "cmake": self._build_with_cmake,
        "autotools": self._build_with_autotools,
        "python": self._build_with_python,
    }
    build_func = build_methods.get(str(self.options.build_method))
    if build_func:
        build_func()
```

### Profile System (15 Composable Profiles)

Profiles are in `packages/sparetools-openssl-tools/profiles/`:

**3 Categories:**
1. **Base (6):** Platform + compiler (linux-gcc11, darwin-clang, windows-msvc2022, etc.)
2. **Build Methods (4):** perl-configure, cmake-build, autotools, python-configure
3. **Features (5):** fips-enabled, shared-libs, static-only, minimal, performance

**Composition Example:**
```bash
# FIPS-enabled build on Linux with GCC using Perl Configure
conan create . --version=3.3.2 \
  -pr:b profiles/base/linux-gcc11 \
  -pr:b profiles/build-methods/perl-configure \
  -pr:b profiles/features/fips-enabled
```

Profile inheritance uses Conan's `include()` directive.

### Zero-Copy Pattern

**Implementation:** `packages/sparetools-base/symlink-helpers.py` (228 lines)

**Pattern:** NGA aerospace-inspired symlink strategy
- Symlink-based deployment instead of copying files
- 80% disk space savings claimed
- Fast project setup
- Functions: `create_zero_copy_deployment()`, `verify_zero_copy_integrity()`

### Security Integration

**Location:** `packages/sparetools-base/security-gates.py` (199 lines)

**Integrated Tools:**
- **Trivy:** Filesystem vulnerability scanning (`run_trivy_scan()`)
- **Syft:** SBOM generation (`generate_sbom()`)
- **FIPS Validator:** Compliance checking (`packages/sparetools-bootstrap/bootstrap/openssl/fips_validator.py`, 570 lines)

**Usage in builds:**
Security gates called in conanfile.py:237-249 during package step.

### Bootstrap Orchestration

**Location:** `packages/sparetools-bootstrap/bootstrap/`

**3-Agent System:**
1. **EXECUTOR** - Executes build tasks
2. **VALIDATOR** - Validates build outputs
3. **ORCHESTRATOR** - Coordinates multi-package builds

Documentation in `docs/BOOTSTRAP_PROMPT-*.md`

---

## Critical Known Issues

### 1. Version Inconsistencies (HIGH PRIORITY)

**Issue:** Documentation says 1.0.0 but code is at 2.0.0

**Fixes needed:**
```python
# packages/sparetools-cpython/conanfile.py:17
# CURRENT (WRONG):
python_requires = "sparetools-base/1.0.0"
# SHOULD BE:
python_requires = "sparetools-base/2.0.0"
```

Also need to update `.github/workflows/publish.yml` version references.

### 2. Missing python_requires Declarations

Several packages use sparetools-base utilities but don't declare the dependency:
- `sparetools-openssl-tools/conanfile.py` should add: `python_requires = "sparetools-base/2.0.0"`
- `sparetools-shared-dev-tools/conanfile.py` should add: `python_requires = "sparetools-base/2.0.0"`

### 3. Testing Gap (CRITICAL)

**Current state:** <5% test coverage
- No pytest tests found
- No unittest tests found
- Only 1 Conan integration test in `packages/sparetools-openssl/test_package/`
- 41,720 lines of Python code with minimal testing

**README.md claims** (line 202): `pytest tests/` but `tests/` directory doesn't exist.

### 4. Python configure.py Not Integrated

**Status:** Experimental only, not production-ready
- Located in deprecated `sparetools-openssl-hybrid` package only
- Not exported to main `sparetools-openssl` package
- `build_method="python"` may fall back to Perl
- Referenced extensively in docs but not actually functional in main package

### 5. Hardcoded Paths

`packages/sparetools-cpython/conanfile.py:27` has hardcoded staging path:
```python
"/tmp/cpython-3.12.7-staging/usr/local"
```
Not portable across build environments.

### 6. Deprecated Packages Not Removed

These packages are marked "deprecated" but still in repo:
- `packages/sparetools-openssl-cmake/`
- `packages/sparetools-openssl-autotools/`
- `packages/sparetools-openssl-hybrid/`
- `packages/sparetools-openssl-tools-mini/` (still at version 1.0.0)

Should either be removed or clearly marked as "experimental/research".

---

## Important Code Locations

### Core Utilities (sparetools-base)
- **Security Gates:** `packages/sparetools-base/security-gates.py` (Trivy, Syft, type-hinted, production-quality)
- **Symlink Helpers:** `packages/sparetools-base/symlink-helpers.py` (Zero-copy pattern, well-documented)
- **Conanfile:** `packages/sparetools-base/conanfile.py` (20 lines, python-require package)

### OpenSSL Main Package
- **Conanfile:** `packages/sparetools-openssl/conanfile.py` (302 lines, unified build system)
- **Test Package:** `packages/sparetools-openssl/test_package/test_openssl.c` (SHA-256 validation test)
- **Component Setup:** conanfile.py:278-300 (SSL/Crypto libraries, headers)

### OpenSSL Tools
- **FIPS Validator:** `packages/sparetools-bootstrap/bootstrap/openssl/fips_validator.py` (570 lines, dataclasses, production-grade)
- **Profiles:** `packages/sparetools-openssl-tools/profiles/` (15 composable profiles)
- **Build Scripts:** `packages/sparetools-openssl-tools/openssl_tools/scripts/`

### CI/CD
- **Main CI:** `.github/workflows/ci.yml` (multi-platform matrix)
- **Security:** `.github/workflows/security.yml` (Trivy, Syft, CodeQL, dependency review)
- **Release:** `.github/workflows/release.yml` (automated releases)
- **Publish:** `.github/workflows/publish.yml` (Cloudsmith deployment - has version issues)

### Scripts
- **Validate Install:** `scripts/validate-install.sh` (comprehensive validation checks)
- **Aggregate Logs:** `scripts/aggregate-build-logs.py` (debugging helper)
- **Cloudsmith Dry Run:** `scripts/cloudsmith-dry-run.sh` (test uploads)

---

## Build System Gotchas

### 1. Build Order Matters

Due to dependencies, build packages in this order:
1. sparetools-base
2. sparetools-cpython
3. sparetools-shared-dev-tools
4. sparetools-openssl-tools
5. sparetools-openssl (main deliverable)

### 2. Profile Composition

Profiles stack - later profiles override earlier ones:
```bash
# Correct: base → build-method → features
-pr:b profiles/base/linux-gcc11 \
-pr:b profiles/build-methods/perl-configure \
-pr:b profiles/features/fips-enabled

# Wrong: features first (will be overridden)
-pr:b profiles/features/fips-enabled \
-pr:b profiles/base/linux-gcc11
```

### 3. FIPS Builds Require Special Handling

FIPS module has specific build requirements:
- Must use `fips=True` option
- Requires specific compiler flags (in profiles/features/fips-enabled)
- Validation via `bootstrap/openssl/fips_validator.py`

### 4. Python configure.py Location

The experimental Python configure.py is in:
- `packages/sparetools-openssl-hybrid/configure.py` (27KB, 700+ lines)
- NOT in `packages/sparetools-openssl/` (main package)
- Reference at conanfile.py:88-92 shows it's intended to be exported but isn't

### 5. OpenSSL 3.6.0+ Provider Issues

Avoid OpenSSL 3.6.0+ for now:
- Provider compilation has dependency ordering issues
- Stick with 3.3.2 (proven stable)
- See Technical Debt notes in original CLAUDE.md

---

## Conan 2.x Patterns Used

### python_requires Pattern
```python
# Foundation package pattern
class SparetoolsBase(ConanFile):
    name = "sparetools-base"
    package_type = "python-require"
    # Provides utilities to other packages

# Consumer pattern
class SomePackage(ConanFile):
    python_requires = "sparetools-base/2.0.0"
    # Can use base utilities
```

### tool_requires Pattern
```python
# Build tool pattern (OpenSSL needs tools to build)
class SparetoolsOpenssl(ConanFile):
    tool_requires = [
        "sparetools-openssl-tools/2.0.0",  # Profiles, validators
        "sparetools-cpython/3.12.7"        # Python runtime
    ]
```

### Modern Layouts
- `cmake_layout()` for CMake-based packages
- `basic_layout()` for non-CMake packages
- Replaces old `self.cpp_info.libdirs` patterns

### Components
OpenSSL package exports two components (conanfile.py:278-300):
```python
self.cpp_info.components["ssl"].libs = ["ssl"]
self.cpp_info.components["crypto"].libs = ["crypto"]
```
Consumers can require specific components: `--requires=sparetools-openssl/3.3.2:ssl`

---

## Development Workflow

### Adding a New Package

1. Create package directory: `mkdir packages/sparetools-newpackage`
2. Create conanfile.py with proper dependencies
3. Declare `python_requires = "sparetools-base/2.0.0"` if using base utilities
4. Create test_package/ with integration test
5. Add package README.md
6. Update root README.md
7. Test locally: `conan create . --version=X.Y.Z`
8. Add to CI workflows

### Modifying OpenSSL Build

The main build logic is in `packages/sparetools-openssl/conanfile.py`:
- Configure options: lines 24-45
- Build methods: lines 148-215
- Build dispatcher: lines 217-233
- Security gates: lines 237-249
- Package step: lines 251-276

To add a new build method:
1. Add to `build_method` option enum
2. Create `_build_with_<method>()` function
3. Add to `build_methods` dict
4. Create profile in `profiles/build-methods/<method>`
5. Test with: `conan create . --version=3.3.2 -o build_method=<method>`

### Running Security Scans Locally

Before pushing changes:
```bash
# Vulnerability scan
trivy fs --security-checks vuln --severity CRITICAL,HIGH .

# Generate SBOM
syft packages . -o cyclonedx-json > sbom.json

# Validate (if output is present)
syft packages . -o spdx-json | jq '.packages | length'
```

---

## Documentation Structure

- **README.md** - User-facing documentation, quick start
- **CLAUDE.md** - This file, for Claude Code instances
- **CHANGELOG.md** - v2.0.0 changes documented
- **BASELINE.md** - Current state snapshot (may be outdated)
- **docs/MIGRATION-GUIDE.md** - Migration from v1.x
- **docs/TODO.json** - Tracked work items
- **Package READMEs** - Each package has its own README with specific usage

---

## GitHub Actions Workflows

### ci.yml
Multi-platform matrix builds (Linux, macOS, Windows) with 4 build configurations.
Uses profiles from openssl-tools.

### security.yml
Comprehensive security scanning:
- Trivy vulnerability scanning
- Syft SBOM generation (CycloneDX + SPDX)
- CodeQL static analysis
- Dependency review

### build-test.yml
Comprehensive build testing across platforms.

### integration.yml
Consumer project testing and FIPS validation.

### release.yml
Automated release creation with changelogs and assets.

### publish.yml
Cloudsmith deployment (manual trigger).
**⚠️ Contains version inconsistencies - references 1.0.0 instead of 2.0.0**

---

## Resources

- **Conan Documentation:** https://docs.conan.io/
- **OpenSSL Source:** https://github.com/openssl/openssl
- **OpenSSL Documentation:** https://www.openssl.org/docs/
- **FIPS 140-3:** https://csrc.nist.gov/publications/detail/fips/140/3/final
- **Trivy:** https://aquasecurity.github.io/trivy/
- **Syft:** https://github.com/anchore/syft

---

## What's Next (From Original Handover)

See original CLAUDE.md sections for:
- Week 1: GitHub Actions Perfection
- Week 2: FIPS Automation
- Week 3-4: Kubernetes Integration

**However**, recommend addressing critical issues first:
1. Fix version inconsistencies
2. Implement testing (target 60% coverage)
3. Remove deprecated packages
4. Add missing python_requires declarations

---

## Key Learnings

1. **OpenSSL Provider Architecture:** OpenSSL 3.x providers have complex build dependencies - use 3.3.2 (stable)
2. **Multi-Build Approach:** Flexible build system provides options for different environments
3. **Zero-Copy Pattern:** Symlink-based deployment significantly reduces disk usage
4. **Security-First:** Integrated scanning (Trivy, Syft) catches issues early
5. **Conan 2.x Migration:** python_requires and tool_requires replace older patterns
6. **Profile Composition:** Layered profiles enable reusable build configurations
