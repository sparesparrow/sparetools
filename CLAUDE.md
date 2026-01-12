# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SpareTools** is a production-grade Conan 2.x monorepo spanning embedded systems, AI/ML, cybersecurity, aerospace, and enterprise applications. It provides a hermetic, security-first ecosystem with zero-copy deployment capabilities and comprehensive CI/CD automation.

- **License:** Apache-2.0
- **Repository:** github.com/sparesparrow/sparetools
- **Package Registry:** Cloudsmith (sparesparrow-conan/sparetools)
- **Current Version:** v2.0.4
- **Minimum Requirements:** Conan 2.21.0+, Python 3.12+

## Repository Structure

```
packages/
  ├── foundation/        # 8 core packages (base, cpython, bootstrap, etc.)
  ├── consumers/         # 10+ domain-specific applications (esp32, mcp, aerospace, etc.)
  ├── deprecated/        # Legacy packages (mark for removal)
  ├── python/           # Python utilities (fs-tools, proc-tools)
  ├── testing/          # Test infrastructure
  ├── mcp/              # Model Context Protocol ecosystem
  ├── embedded/         # Embedded systems and firmware
  ├── streaming/        # Media streaming solutions
  ├── wifi/             # WiFi sensing and analysis
  ├── sdr/              # Software-defined radio
  ├── security/         # Cryptography and security
  └── pentest/          # Penetration testing toolkit

docs/                  # Comprehensive documentation (45+ files)
test/                  # Test suite (unit, integration)
scripts/               # Build and automation utilities
.github/workflows/     # GitHub Actions CI/CD pipelines
```

## Common Development Commands

### Building Packages

**Foundation layer** (required for all packages):
```bash
conan create packages/foundation/sparetools-base --version=2.0.4 --build=missing
conan create packages/foundation/sparetools-cpython --version=3.12.7 --build=missing
```

**Build any package**:
```bash
conan create packages/{category}/{package-name} --version={VERSION} --build=missing
```

**Build with specific options**:
```bash
conan create packages/foundation/sparetools-openssl --version=3.3.2 \
  -o '*:fips=True' \
  -o '*:build_method=perl'
```

**Build from Turbo** (orchestrated build across domains):
```bash
npm run build              # Full monorepo build
npm run build:embedded     # Embedded systems packages
npm run build:python       # Python packages
npm run build:schemas      # Protocol schemas (FlatBuffers)
```

### Testing

**Run full test suite**:
```bash
npm run test              # All tests via turbo
pytest test/unit/ -v      # Unit tests directly
pytest test/integration/ -v  # Integration tests
```

**Run specific tests with coverage**:
```bash
pytest test/unit/ -v --cov=packages/sparetools-base --cov-report=html
pytest test/unit/ -m "not slow"  # Exclude slow tests
```

**Test individual package** (after building):
```bash
conan test packages/{package}/test_package {package}/{VERSION}@
```

### Linting and Formatting

```bash
npm run lint              # Check all code quality
npm run format            # Auto-format code (black, etc.)
```

Pre-commit hooks (flake8, black, YAML validation) run automatically on git commit.

### Publishing Packages

```bash
npm run publish           # Publish all packages
npm run publish:conan     # Publish to Cloudsmith
npm run publish:python    # Publish Python packages
```

Cloudsmith remote (configured in `conanfile.py`):
```bash
conan remote add sparesparrow-conan \
  https://dl.cloudsmith.io/public/sparesparrow-conan/sparetools/
conan upload "sparetools-*/*" -r sparesparrow-conan --confirm --parallel=4
```

## Architecture Patterns

### Layered Package Organization

SpareTools uses a **5-layer architecture**:

1. **Foundation Layer** (sparetools-base, sparetools-versioning)
   - Shared utilities for all packages
   - Security gates (Trivy, Syft SBOM, FIPS validation)
   - Zero-copy deployment helpers

2. **Prebuilt Tools Layer** (sparetools-cpython)
   - Hermetic Python 3.12.7 runtime
   - Eliminates system Python conflicts
   - Used by build tools and DevOps

3. **Utilities Layer** (shared-dev-tools, test-harness, bootstrap)
   - Development utilities and helpers
   - Test infrastructure (gtest, gmock)
   - Project orchestration and templates

4. **Orchestration Layer** (sparetools-mcp-orchestrator, sparetools-bootstrap)
   - Multi-domain project bootstrapping
   - AI/ML Model Context Protocol ecosystem
   - Cross-domain integration

5. **Domain-Specific Consumers**
   - Embedded systems (ESP32, IoT)
   - AI/ML and MCP servers
   - Cybersecurity (pentest toolkit, crypto)
   - Aerospace applications
   - Mobile/Android integration

### Dependency Pattern

Packages use `python_requires` for shared infrastructure:

```python
# In conanfile.py
python_requires = "sparetools-base/2.0.4"

def build(self):
    base = self.python_requires["sparetools-base"].conanfile
    base.run_trivy_scan(self.source_folder)     # Security gate
    base.generate_sbom(self.package_folder)     # SBOM generation
```

This approach avoids circular dependencies and allows recipe sharing.

### Zero-Copy Development (CPY System)

For local development without building every dependency:

```bash
# Create symlinks to Conan cache instead of versioned packages
cd /path/to/consumer-project
mkdir CPY && cd CPY
ln -sf $(conan cache path sparetools-base/2.0.4) sparetools-base
ln -sf $(conan cache path sparetools-cpython/3.12.7) sparetools-cpython
export LD_LIBRARY_PATH="$PWD/sparetools-base/lib:$LD_LIBRARY_PATH"
conan build ..  # Uses symlinked packages
```

Benefits: instant updates, no duplication, isolated development. See `docs/CPY_SYSTEM.md` for details.

### Security-First Architecture

Every package includes security gates:
- **Trivy scans** for container vulnerabilities
- **Syft SBOM** generation (CycloneDX, SPDX formats)
- **FIPS 140-3 validation** for cryptography packages
- **CodeQL scanning** in CI/CD

Security gates run in `conanfile.py` during build phase.

## CI/CD Pipeline

GitHub Actions workflows (`.github/workflows/`):

- **ci.yml**: Multi-platform builds (Linux, macOS, Windows) + unit tests
- **security.yml**: Trivy/Syft scanning, CodeQL analysis, FIPS validation
- **publish.yml**: Cloudsmith package publishing (manual approval required)
- **nightly.yml**: Full integration test suite
- **release.yml**: Version management and GitHub releases

Pipeline flow:
```
Push/PR → ci.yml (build + tests)
  ↓
  All Pass? → security.yml (scanning)
  ↓
  Critical findings? → Block merge
  ↓
  Approved? → publish.yml (Cloudsmith)
```

## Version Management

### Centralized Version Tracking

All package versions are defined in `/versions.yaml`:

```yaml
foundation:
  sparetools-base: 2.0.4
  sparetools-cpython: 3.12.7

consumers:
  esp32:
    sparetools-nucleus: 2.0.0
```

### Semantic Versioning

SpareTools follows semantic versioning (MAJOR.MINOR.PATCH):
- **2.0.4**: Major API changes, minor features, patch fixes
- Version bumps trigger git tags and releases automatically
- Pre-commit hooks validate version increments

**To bump a version**, modify `/versions.yaml` and commit. The CI pipeline will:
1. Validate the increment
2. Create a git tag
3. Publish to Cloudsmith
4. Create GitHub release

## Testing Architecture

### Test Organization

```
test/
  ├── unit/                      # Fast unit tests (< 1s each)
  ├── integration/               # External dependency tests
  └── conftest.py               # pytest fixtures
```

### Running Tests

**By marker**:
```bash
pytest -m unit                  # Only unit tests
pytest -m integration           # Only integration tests
pytest -m slow                  # Slow/long-running tests
```

**By path**:
```bash
pytest test/unit/ -v            # All unit tests
pytest test/unit/test_foo.py    # Specific file
pytest test/unit/test_foo.py::test_bar -v  # Specific test
```

**With coverage**:
```bash
pytest test/unit/ --cov=packages/sparetools-base --cov-report=html
# Open htmlcov/index.html in browser
```

### Package-Level Tests

Each Conan package can include a `test_package/` directory with `conanfile.py` defining a `test()` method:

```python
# packages/my-package/test_package/conanfile.py
def test(self):
    self.run("myapp --version")
```

Test after building:
```bash
conan test packages/{package}/test_package {package}/{VERSION}@
```

## Key Files and Directories

| Path | Purpose |
|------|---------|
| `/package.json` | Turbo workspace configuration and npm scripts |
| `/pytest.ini` | pytest configuration (test discovery, markers) |
| `/versions.yaml` | Centralized version definitions for all packages |
| `/.pre-commit-config.yaml` | Pre-commit hooks (black, flake8, custom validators) |
| `/conanfile.py` | Meta-package definition and CI configuration |
| `/.github/workflows/` | GitHub Actions CI/CD pipelines |
| `/docs/QUICK-REFERENCE.md` | Command cheat sheet |
| `/docs/PACKAGES.md` | Package inventory and dependency graph |
| `/docs/ARCHITECTURE.md` | System design and implementation patterns |
| `/docs/CI-CD-GUIDE.md` | Workflow troubleshooting and operations |

## Workspace Organization

The monorepo uses **Turbo** for task orchestration:

```bash
npm install                # Install turbo and dependencies
npm run build              # Run build tasks across all packages
npm run test               # Run tests in dependency order
turbo run {script}         # Run arbitrary script in all packages
turbo run {script} --filter="sparetools-base"  # Run in specific package
```

Each package's `package.json` or `conanfile.py` defines available scripts.

## Documentation

Start with these docs for different needs:

- **Getting Started**: `/docs/QUICK-START.md`
- **Command Reference**: `/docs/QUICK-REFERENCE.md`
- **Package Overview**: `/docs/PACKAGES.md`
- **Architecture Details**: `/docs/ARCHITECTURE.md`
- **Building & Publishing**: `/docs/PUBLISHING-GUIDE.md`
- **CI/CD Operations**: `/docs/CI-CD-GUIDE.md`
- **Troubleshooting**: `/docs/CI-CD-TROUBLESHOOTING.md`
- **Embedded (ESP32)**: `/docs/consumers/esp32/README.md`
- **AI/ML (MCP)**: `/packages/mcp/README.md`
- **Zero-Copy Development**: `/docs/CPY_SYSTEM.md`

## Important Patterns

### Package Dependencies

Use `python_requires` for recipe sharing (not `requires`):

```python
python_requires = "sparetools-base/2.0.4"  # Correct: recipe dependency
# NOT: requires = "sparetools-base/2.0.4"  # Wrong: creates binary dependency
```

### Build Methods

OpenSSL supports multiple build methods via option:

```bash
-o sparetools-openssl/*:build_method=perl       # Default (production)
-o sparetools-openssl/*:build_method=cmake      # Modern IDEs
-o sparetools-openssl/*:build_method=autotools  # Cross-compile
-o sparetools-openssl/*:build_method=python     # Experimental
```

### FIPS Compliance

For cryptography packages, enable FIPS validation:

```bash
conan create packages/security/sparetools-crypto-suite \
  -o '*:fips=True' --build=missing
```

Security gates automatically validate FIPS 140-3 compliance during build.

## Pre-commit Hooks

Hooks run automatically before git commit:

- **black**: Python code formatting
- **flake8**: Python linting (PEP8)
- **yaml**: GitHub Actions workflow validation
- **sparetools-suggest-version-bump**: Recommend version increments
- **sparetools-validate-git-versioning**: Git tag format validation
- **sparetools-check-secrets**: Detect exposed credentials

Install hooks:
```bash
pre-commit install
```

Bypass hooks (not recommended):
```bash
git commit --no-verify
```

## Common Issues and Solutions

### "Package not found" errors

Ensure the Conan remote is configured:
```bash
conan remote add sparesparrow-conan \
  https://dl.cloudsmith.io/public/sparesparrow-conan/sparetools/
conan remote list
```

### Build failures with "Missing python_requires"

Ensure foundation packages are built first:
```bash
conan create packages/foundation/sparetools-base --version=2.0.4 --build=missing
```

### Test discovery issues

Check pytest.ini configuration and ensure tests follow `test_*.py` naming.

### Version mismatches

Verify all package versions are defined in `/versions.yaml`. The CI pipeline validates this automatically.

## Quick Workflow Example

**Building and testing a new feature**:

```bash
# 1. Make code changes
git checkout -b feature/my-feature

# 2. Build affected package
conan create packages/foundation/sparetools-base --version=2.0.4 --build=missing

# 3. Run tests
pytest test/unit/ -v --cov=packages/sparetools-base

# 4. Format code
npm run format

# 5. Commit (pre-commit hooks run automatically)
git add .
git commit -m "Add feature X to sparetools-base"

# 6. Push and create PR
git push origin feature/my-feature

# 7. GitHub Actions CI runs automatically:
#    - ci.yml: multi-platform build + tests
#    - security.yml: scanning
#    - Manual approval for publishing
```

## References

- **Conan Documentation**: https://docs.conan.io/
- **GitHub Repository**: https://github.com/sparesparrow/sparetools
- **Cloudsmith Registry**: https://cloudsmith.io/~sparesparrow-conan/repos/sparetools/
- **Issue Tracker**: https://github.com/sparesparrow/sparetools/issues
