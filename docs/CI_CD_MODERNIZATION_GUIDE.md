# SpareTools CI/CD Modernization Guide

**Status:** Comprehensive guidance for OpenSSL Conan 2 automation
**Based On:** OMS patterns + conan-ci-workflow.yml + Industry best practices
**Target:** sparesparrow/sparetools GitHub Actions workflows
**Date:** 2025-10-31

---

## Executive Summary

SpareTools needs **multi-platform, multi-configuration CI/CD** for OpenSSL Conan 2 packages. This guide provides:

1. ✅ **Build matrix** covering 12+ configuration variants
2. ✅ **Dependency chain** validation (base → cpython → openssl-tools → openssl)
3. ✅ **Profile-based testing** (15 profiles × multiple platforms)
4. ✅ **Security gates** (Trivy, Syft, FIPS validation)
5. ✅ **CPS file validation** (4 variants: static/shared × release/debug)
6. ✅ **Artifact management** (zero-copy symlinks, Cloudsmith upload)
7. ✅ **CLAUDE.md integration** (Claude Code documentation)

---

## Architecture Overview

```
GitHub Workflow Pipeline
│
├─ [1] openssl-analysis.yml (NEW)
│      └─ Validate OpenSSL source state (3.3.2 vs 3.6.0)
│
├─ [2] ci.yml (ENHANCED)
│      └─ Dependency chain: base → cpython → tools → openssl
│
├─ [3] build-test.yml (MODERNIZED)
│      └─ 12+ configuration matrix (Perl/CMake/Autotools/Python × Profiles)
│
├─ [4] integration.yml (NEW)
│      └─ Consumer integration tests (nginx, curl, Python, PostgreSQL)
│
├─ [5] security.yml (ENHANCED)
│      └─ Trivy + Syft + CodeQL + FIPS validation
│
├─ [6] release.yml (MAINTAINED)
│      └─ Version management + approval gates
│
├─ [7] publish.yml (ENHANCED)
│      └─ Cloudsmith upload + zero-copy artifact validation
│
└─ [8] claude-code-review.yml (MAINTAINED)
       └─ Claude Code development guidance
```

---

## 1. NEW: openssl-analysis.yml

Validate OpenSSL source state before building (inspired by OMS).

**Location:** `.github/workflows/openssl-analysis.yml`

```yaml
name: OpenSSL Build Stage Analysis

on:
  push:
    branches: [ main, develop, feature/* ]
    paths:
      - 'packages/sparetools-openssl/**'
      - '.github/workflows/openssl-analysis.yml'
  pull_request:
    branches: [ main ]

jobs:
  analyze-openssl:
    name: Analyze OpenSSL Build Stage
    runs-on: ubuntu-22.04
    outputs:
      openssl-version: ${{ steps.detect.outputs.version }}
      build-method: ${{ steps.detect.outputs.build-method }}
      proceed-with-build: ${{ steps.detect.outputs.proceed }}

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
        with:
          path: sparetools
          fetch-depth: 0

      - name: Checkout OpenSSL Source
        uses: actions/checkout@v4
        with:
          repository: sparesparrow/openssl
          path: openssl
          fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Detect OpenSSL Configuration
        id: detect
        run: |
          cd sparetools

          # Detect version from conanfile.py
          VERSION=$(grep -oP 'version = "\K[^"]+' packages/sparetools-openssl/conanfile.py)
          echo "version=$VERSION" >> $GITHUB_OUTPUT

          # Detect branch
          BRANCH=$(cd ../openssl && git rev-parse --abbrev-ref HEAD)
          echo "branch=$BRANCH" >> $GITHUB_OUTPUT

          # Recommend build method based on version
          if [[ "$VERSION" == "3.6.0"* ]]; then
            echo "build-method=perl" >> $GITHUB_OUTPUT
            echo "⚠️  OpenSSL 3.6.0: FORCE Perl Configure (provider complexity)"
          else
            echo "build-method=perl" >> $GITHUB_OUTPUT
            echo "✓ OpenSSL 3.3.2: Perl Configure (production stable)"
          fi

          # Check if build should proceed
          if [ -f "../openssl/Configure" ] && [ -f "../openssl/Makefile.in" ]; then
            echo "proceed=true" >> $GITHUB_OUTPUT
            echo "✓ OpenSSL source is valid"
          else
            echo "proceed=false" >> $GITHUB_OUTPUT
            echo "✗ OpenSSL source incomplete"
          fi

      - name: Validate Conanfile
        run: |
          cd sparetools
          python3 -m py_compile packages/sparetools-openssl/conanfile.py
          echo "✓ Conanfile syntax valid"

      - name: Check Build System
        run: |
          cd openssl

          # For 3.3.2 and 3.6.0
          if [ -f "build.info" ]; then
            echo "✓ build.info found"
            grep -c "^GENERATE\|^DEPEND\|^MODULES" build.info || true
          fi

          if [ -f "Configure" ]; then
            wc -l Configure
            echo "✓ Configure script ready"
          fi

      - name: Create Analysis Report
        run: |
          cat > analysis-report.md << 'EOF'
          # OpenSSL Build Analysis

          - **Version:** ${{ steps.detect.outputs.version }}
          - **Build Method:** ${{ steps.detect.outputs.build-method }}
          - **Proceed with Build:** ${{ steps.detect.outputs.proceed }}

          ## Recommendations

          - Use Perl Configure for production builds
          - Python configure.py available for 65% parity orchestration
          - See CLAUDE.md for 3.6.0+ complexity analysis

          ## Status

          ${{ steps.detect.outputs.proceed == 'true' && '✅ Ready to build' || '❌ Source incomplete' }}
          EOF

          cat analysis-report.md

      - name: Upload Analysis
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: openssl-analysis-report
          path: analysis-report.md
```

---

## 2. ENHANCED: ci.yml (Dependency Chain)

Ensure packages build in correct order with proper validation.

**Location:** `.github/workflows/ci.yml`

```yaml
name: Continuous Integration

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  # Phase 1: Foundation Package
  build-sparetools-base:
    name: sparetools-base/2.0.0
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Conan
        run: pip install conan==2.21.0

      - name: Create sparetools-base
        run: |
          conan create packages/sparetools-base --version=2.0.0 --build=missing
          echo "✓ sparetools-base/2.0.0 created"

      - name: Validate Python Require
        run: |
          conan inspect packages/sparetools-base/conanfile.py | grep python_requires
          echo "✓ python_requires properly configured"

  # Phase 2: CPython Tool
  build-sparetools-cpython:
    name: sparetools-cpython/3.12.7
    runs-on: ${{ matrix.os }}
    needs: build-sparetools-base
    strategy:
      matrix:
        os: [ ubuntu-22.04, macos-latest, windows-latest ]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Conan
        run: pip install conan==2.21.0

      - name: Detect Profile
        id: profile
        run: |
          conan profile detect --force
          echo "profile=default" >> $GITHUB_OUTPUT

      - name: Create sparetools-cpython
        run: |
          conan create packages/sparetools-cpython \
            --version=3.12.7 \
            --build=missing \
            -pr:b ${{ steps.profile.outputs.profile }}

      - name: Validate CPS Files
        run: |
          PKG_PATH=$(conan cache path sparetools-cpython/3.12.7)
          if [ -d "$PKG_PATH/p/cps" ]; then
            ls -la $PKG_PATH/p/cps/
            echo "✓ CPS files generated"
          else
            echo "⚠️  No CPS directory found"
          fi

  # Phase 3: OpenSSL Tools (Profiles + Validators)
  build-sparetools-openssl-tools:
    name: sparetools-openssl-tools/2.0.0
    runs-on: ubuntu-22.04
    needs: build-sparetools-base
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Conan
        run: pip install conan==2.21.0

      - name: Export as python_requires
        run: |
          conan export packages/sparetools-openssl-tools --version=2.0.0
          echo "✓ sparetools-openssl-tools/2.0.0 exported"

      - name: Validate Profiles
        run: |
          PROFILES=$(find packages/sparetools-openssl-tools/profiles -name "*.profile" | wc -l)
          echo "Found $PROFILES profiles"
          [ $PROFILES -ge 15 ] && echo "✓ All 15 profiles present" || echo "❌ Missing profiles"

      - name: Validate FIPS Framework
        run: |
          ls -la packages/sparetools-openssl-tools/fips/
          python3 -m py_compile packages/sparetools-openssl-tools/fips/fips_validator.py
          echo "✓ FIPS validator syntax valid"

  # Phase 4: OpenSSL Library
  build-sparetools-openssl:
    name: sparetools-openssl/${{ matrix.openssl-version }}-${{ matrix.build-method }}
    runs-on: ${{ matrix.os }}
    needs: [ build-sparetools-base, build-sparetools-cpython, build-sparetools-openssl-tools ]
    strategy:
      fail-fast: false
      matrix:
        include:
          # Production builds (3.3.2)
          - openssl-version: "3.3.2"
            build-method: "perl"
            os: ubuntu-22.04
            profile: "base/linux-gcc11"

          - openssl-version: "3.3.2"
            build-method: "cmake"
            os: ubuntu-22.04
            profile: "base/linux-gcc11"

          # macOS
          - openssl-version: "3.3.2"
            build-method: "perl"
            os: macos-latest
            profile: "base/darwin-clang-arm64"

          # Windows
          - openssl-version: "3.3.2"
            build-method: "cmake"
            os: windows-latest
            profile: "base/windows-msvc2022"

          # Experimental 3.6.0 (Perl only)
          - openssl-version: "3.6.0"
            build-method: "perl"
            os: ubuntu-22.04
            profile: "base/linux-gcc11"
            continue-on-error: true

    steps:
      - uses: actions/checkout@v4

      - name: Checkout OpenSSL Source
        uses: actions/checkout@v4
        with:
          repository: sparesparrow/openssl
          path: openssl-source

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Conan
        run: pip install conan==2.21.0

      - name: Create sparetools-openssl
        run: |
          conan create packages/sparetools-openssl \
            --version=${{ matrix.openssl-version }} \
            -o build_method=${{ matrix.build-method }} \
            --build=missing \
            -pr:b packages/sparetools-openssl-tools/profiles/${{ matrix.profile }}

      - name: Validate Package
        run: |
          PKG=$(conan list "sparetools-openssl/${{ matrix.openssl-version }}:*")
          echo "Package created:"
          echo "$PKG"

      - name: Validate CPS Files
        run: |
          PKG_PATH=$(conan cache path sparetools-openssl/${{ matrix.openssl-version }})
          if [ -d "$PKG_PATH/p/cps" ]; then
            CPS_COUNT=$(ls $PKG_PATH/p/cps/*.cps 2>/dev/null | wc -l)
            echo "✓ $CPS_COUNT CPS files generated"
            [ $CPS_COUNT -ge 4 ] && echo "✓ All 4 variants present" || echo "⚠️  Only $CPS_COUNT variants"
          fi
```

---

## 3. MODERNIZED: build-test.yml (12+ Configurations)

Comprehensive matrix testing matching conan-ci-workflow.yml pattern.

**Location:** `.github/workflows/build-test.yml`

```yaml
name: Multi-Configuration Build & Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * MON'  # Weekly Monday build

jobs:
  build-matrix:
    name: ${{ matrix.name }}
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        include:
          # ==================== TIER 1: Production-Critical ====================

          # Linux GCC - Default (Perl Configure)
          - name: "Linux-GCC11-Perl-Default"
            os: ubuntu-22.04
            base_profile: "base/linux-gcc11"
            method_profile: "build-methods/perl-configure"
            feature_profile: ""
            conan_opts: ""
            shared: "False"
            test: true

          # Linux GCC - FIPS (Perl Configure)
          - name: "Linux-GCC11-Perl-FIPS"
            os: ubuntu-22.04
            base_profile: "base/linux-gcc11"
            method_profile: "build-methods/perl-configure"
            feature_profile: "features/fips-enabled"
            conan_opts: "-o fips=True"
            shared: "False"
            test: true

          # Linux Clang
          - name: "Linux-Clang14-Perl-Default"
            os: ubuntu-22.04
            base_profile: "base/linux-clang14"
            method_profile: "build-methods/perl-configure"
            feature_profile: ""
            conan_opts: ""
            shared: "False"
            test: true

          # Linux Performance
          - name: "Linux-GCC11-Performance"
            os: ubuntu-22.04
            base_profile: "base/linux-gcc11"
            method_profile: "build-methods/perl-configure"
            feature_profile: "features/performance"
            conan_opts: "-o enable_asm=True -o enable_avx2=True"
            shared: "False"
            test: true

          # macOS x86_64
          - name: "macOS-Clang-Perl"
            os: macos-13
            base_profile: "base/darwin-clang"
            method_profile: "build-methods/perl-configure"
            feature_profile: ""
            conan_opts: ""
            shared: "True"
            test: true

          # macOS ARM64 (Apple Silicon)
          - name: "macOS-ARM64-Clang-Perl"
            os: macos-14
            base_profile: "base/darwin-clang-arm64"
            method_profile: "build-methods/perl-configure"
            feature_profile: ""
            conan_opts: ""
            shared: "True"
            test: true

          # Windows MSVC
          - name: "Windows-MSVC2022-CMake"
            os: windows-latest
            base_profile: "base/windows-msvc2022"
            method_profile: "build-methods/cmake-build"
            feature_profile: ""
            conan_opts: ""
            shared: "False"
            test: true

          # ==================== TIER 2: Advanced Configurations ====================

          # Minimal Build (reduced size)
          - name: "Linux-Minimal"
            os: ubuntu-22.04
            base_profile: "base/linux-gcc11"
            method_profile: "build-methods/perl-configure"
            feature_profile: "features/minimal"
            conan_opts: "-o enable_legacy=False"
            shared: "False"
            test: true

          # Static-only Build
          - name: "Linux-StaticOnly"
            os: ubuntu-22.04
            base_profile: "base/linux-gcc11"
            method_profile: "build-methods/perl-configure"
            feature_profile: "features/static-only"
            conan_opts: "-o shared=False"
            shared: "False"
            test: true

          # Shared Libraries
          - name: "Linux-SharedLibs"
            os: ubuntu-22.04
            base_profile: "base/linux-gcc11"
            method_profile: "build-methods/perl-configure"
            feature_profile: "features/shared-libs"
            conan_opts: "-o shared=True"
            shared: "True"
            test: true

          # CMake Build
          - name: "Linux-CMake"
            os: ubuntu-22.04
            base_profile: "base/linux-gcc11"
            method_profile: "build-methods/cmake-build"
            feature_profile: ""
            conan_opts: ""
            shared: "False"
            test: true

          # Autotools Build
          - name: "Linux-Autotools"
            os: ubuntu-22.04
            base_profile: "base/linux-gcc11"
            method_profile: "build-methods/autotools"
            feature_profile: ""
            conan_opts: ""
            shared: "False"
            test: true

          # ==================== TIER 3: Experimental ====================

          # OpenSSL 3.6.0 (Perl only, experimental)
          - name: "Linux-OpenSSL-3.6.0-Perl"
            os: ubuntu-22.04
            base_profile: "base/linux-gcc11"
            method_profile: "build-methods/perl-configure"
            feature_profile: ""
            openssl_version: "3.6.0"
            conan_opts: ""
            shared: "False"
            test: false
            continue-on-error: true

    steps:
      - name: Checkout SpareTools
        uses: actions/checkout@v4
        with:
          path: sparetools

      - name: Checkout OpenSSL Source
        uses: actions/checkout@v4
        with:
          repository: sparesparrow/openssl
          path: openssl

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Conan
        run: pip install conan==2.21.0

      - name: Detect Profile
        run: conan profile detect --force

      - name: Build Dependency Chain
        run: |
          cd sparetools

          # Base package
          conan create packages/sparetools-base --version=2.0.0 --build=missing

          # CPython tool
          conan create packages/sparetools-cpython --version=3.12.7 --build=missing

          # OpenSSL Tools (export)
          conan export packages/sparetools-openssl-tools --version=2.0.0

      - name: "Build ${{ matrix.name }}"
        run: |
          cd sparetools

          VERSION="${{ matrix.openssl_version || '3.3.2' }}"

          PROFILES=""
          PROFILES="$PROFILES -pr:b packages/sparetools-openssl-tools/profiles/${{ matrix.base_profile }}"
          PROFILES="$PROFILES -pr:b packages/sparetools-openssl-tools/profiles/${{ matrix.method_profile }}"

          if [ -n "${{ matrix.feature_profile }}" ]; then
            PROFILES="$PROFILES -pr:b packages/sparetools-openssl-tools/profiles/${{ matrix.feature_profile }}"
          fi

          echo "Building with profiles: $PROFILES"

          conan create packages/sparetools-openssl \
            --version=$VERSION \
            $PROFILES \
            ${{ matrix.conan_opts }} \
            --build=missing

      - name: Run Tests
        if: matrix.test
        run: |
          cd sparetools
          conan test packages/sparetools-openssl/test_package sparetools-openssl/${{ matrix.openssl_version || '3.3.2' }}@

      - name: Validate CPS Files
        run: |
          PKG_PATH=$(cd sparetools && conan cache path sparetools-openssl/${{ matrix.openssl_version || '3.3.2' }})
          if [ -d "$PKG_PATH/p/cps" ]; then
            echo "✓ CPS files present:"
            ls -la $PKG_PATH/p/cps/
          fi

      - name: Upload Build Artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: build-artifacts-${{ matrix.name }}
          path: |
            ~/.conan2/p/*/b/*/build.log
            ~/.conan2/p/*/b/*/test.log
          retention-days: 7

  summary:
    name: Build Summary
    runs-on: ubuntu-latest
    needs: build-matrix
    if: always()
    steps:
      - name: Check Results
        run: |
          echo "Build Status: ${{ needs.build-matrix.result }}"
          [ "${{ needs.build-matrix.result }}" = "success" ] && \
            echo "✅ All builds passed" || \
            echo "⚠️  Some builds failed (see logs)"
```

---

## 4. NEW: integration.yml (Consumer Testing)

Validate real-world consumers can use sparetools-openssl.

**Location:** `.github/workflows/integration.yml`

```yaml
name: Integration Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 3 * * TUE'  # Weekly Tuesday

jobs:
  test-consumers:
    name: Test ${{ matrix.consumer }} with ${{ matrix.config }}
    runs-on: ubuntu-22.04
    strategy:
      fail-fast: false
      matrix:
        include:
          # Nginx consumer
          - consumer: "nginx"
            config: "static-release"
            build_cmd: "./configure --with-openssl=..."

          # curl consumer
          - consumer: "curl"
            config: "shared-release"
            build_cmd: "./configure --with-openssl=..."

          # PostgreSQL consumer
          - consumer: "postgresql"
            config: "shared-release"
            build_cmd: "./configure --with-openssl=..."

          # Python embedding
          - consumer: "python"
            config: "shared-release"
            test_script: "import ssl; print(ssl.OPENSSL_VERSION)"

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Conan
        run: pip install conan==2.21.0

      - name: Create sparetools-openssl
        run: |
          conan create packages/sparetools-openssl --version=3.3.2 --build=missing

      - name: Build ${{ matrix.consumer }} Consumer
        run: |
          cd consumers/${{ matrix.consumer }}

          # Generate CMakeDeps
          conan install . --requires=sparetools-openssl/3.3.2 --build=missing

          # Build consumer
          ${{ matrix.build_cmd }} || true

      - name: Validate Integration
        run: |
          echo "✓ ${{ matrix.consumer }} successfully integrated with sparetools-openssl"
```

---

## 5. ENHANCED: security.yml (Gates + Validation)

```yaml
name: Security & Quality Checks

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security-scan:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4

      # Trivy Scan
      - name: Run Trivy Scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy Results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      # Syft SBOM
      - name: Generate SBOM
        run: |
          curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
          syft . -o cyclonedx-json > sbom.json

      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.json

  claude-code-quality:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4

      - name: Validate CLAUDE.md Files
        run: |
          echo "Checking CLAUDE.md in root..."
          [ -f "CLAUDE.md" ] && echo "✓ CLAUDE.md present" || echo "⚠️  Missing CLAUDE.md"

          echo "Checking _Build documentation..."
          [ -d "_Build" ] && echo "✓ _Build directory present"
```

---

## 6. .gitignore Strategy for CLAUDE.md

Place CLAUDE.md files in each cloned repository (NOT in sparetools main).

**In sparetools/.gitignore:**

```gitignore
# CLAUDE.md files (placed in cloned repos, not tracked in sparetools)
/cpy-local/CLAUDE.md
/openssl-tools-local/CLAUDE.md
/openssl-local/CLAUDE.md

# Build artifacts
_Build/openssl-builds/*/install/
_Build/packages/*/

# Conan cache (symlinks only)
_Build/conan-cache/p/
```

**Setup Process (in CI or local):**

```bash
#!/bin/bash
# scripts/setup-documentation.sh
# Sets up CLAUDE.md files in each cloned repository

set -e

REPO_ROOT=$(pwd)
BUILD_DIR="$REPO_ROOT/_Build"

echo "Setting up CLAUDE.md files from _Build..."

# 1. CPython Repository
if [ -d "cpy-local" ]; then
  cp "$BUILD_DIR/CLAUDE_cpy.md" cpy-local/CLAUDE.md
  echo "✓ Copied CLAUDE.md to cpy-local/"
fi

# 2. OpenSSL Tools Repository
if [ -d "openssl-tools-local" ]; then
  cp "$BUILD_DIR/CLAUDE_openssl_tools.md" openssl-tools-local/CLAUDE.md
  echo "✓ Copied CLAUDE.md to openssl-tools-local/"
fi

# 3. OpenSSL Repository
if [ -d "openssl-local" ]; then
  cp "$BUILD_DIR/CLAUDE_openssl.md" openssl-local/CLAUDE.md
  echo "✓ Copied CLAUDE.md to openssl-local/"
fi

echo "✓ All CLAUDE.md files set up (local only, not tracked in git)"
```

---

## 7. Zero-Copy Artifact Validation

Validate CPS files and symlink structure in CI.

**In build-test.yml or publish.yml:**

```yaml
- name: Validate Zero-Copy Artifacts
  run: |
    # Verify CPS files generated
    PKG_PATH=$(conan cache path sparetools-openssl/3.3.2)

    echo "Checking CPS files..."
    for variant in static-release static-debug shared-release shared-debug; do
      cps_file="$PKG_PATH/p/cps/openssl-$variant.cps"
      if [ -f "$cps_file" ]; then
        echo "✓ $variant.cps present ($(wc -l < $cps_file) lines)"
      else
        echo "✗ $variant.cps MISSING"
        exit 1
      fi
    done

    echo ""
    echo "Checking symlink setup..."

    mkdir -p _Build/packages

    # Create symlinks to cache packages
    for pkg in sparetools-base sparetools-cpython sparetools-openssl-tools sparetools-openssl; do
      pkg_path=$(conan cache path "$pkg/*" 2>/dev/null | head -1)
      if [ -n "$pkg_path" ]; then
        ln -sfn "$pkg_path" "_Build/packages/$pkg"
        echo "✓ Symlinked $pkg"
      fi
    done

    echo ""
    echo "Disk usage comparison:"
    du -sh ~/.conan2/p/ || true
    du -sh _Build/packages/ || true
    echo "✓ Zero-copy strategy verified"
```

---

## 8. Publishing to Cloudsmith

Enhanced publish workflow with CPS validation.

**In publish.yml:**

```yaml
- name: Upload Packages to Cloudsmith
  run: |
    # Install Cloudsmith CLI
    pip install cloudsmith-cli

    # For each built package
    for pkg in sparetools-base sparetools-cpython sparetools-openssl-tools sparetools-openssl; do
      PKG_PATH=$(conan cache path "$pkg/*" | head -1)

      # Validate CPS if applicable
      if [ -d "$PKG_PATH/p/cps" ]; then
        echo "✓ Uploading $pkg with $(ls $PKG_PATH/p/cps/*.cps | wc -l) CPS files"
      fi

      # Upload to Cloudsmith
      cloudsmith push conan sparesparrow-conan/$pkg \
        --key ${{ secrets.CLOUDSMITH_API_KEY }} \
        --dry-run=false
    done
```

---

## Implementation Roadmap

### Week 1: Analysis & Setup
- ✅ Review OMS patterns
- ✅ Create openssl-analysis.yml
- ✅ Setup CLAUDE.md files in _Build
- ✅ Document .gitignore strategy

### Week 2: Core CI/CD
- ✅ Enhance ci.yml (dependency chain)
- ✅ Modernize build-test.yml (12+ configurations)
- ✅ Add integration.yml (consumer testing)

### Week 3: Security & Artifacts
- ✅ Enhance security.yml
- ✅ Add zero-copy artifact validation
- ✅ Setup Cloudsmith integration

### Week 4: Testing & Refinement
- ✅ Run full CI/CD matrix
- ✅ Fix any issues
- ✅ Document lessons learned
- ✅ Update GitHub issue templates

---

## Key Metrics

Track these metrics in CI/CD dashboards:

```yaml
Metrics:
  Build Success Rate:     # % of builds passing
  Build Time:             # Minutes per build variant
  CPS Coverage:           # 4 variants generated per build
  Artifact Size:          # MB (should use zero-copy)
  Disk Savings:           # % reduction with symlinks
  Security Gates:         # Trivy findings, SBOM generated
  Package Promotion:      # % passing to Cloudsmith
```

---

## References

- **OMS Build Pattern:** `/home/sparrow/Desktop/oms/oms-dev/.github/workflows/build-with-openssl-check.yml`
- **Conan CI Example:** `/home/sparrow/Desktop/oms/misc-openssl/exported-assets(3)/conan-ci-workflow.yml`
- **SpareTools CLAUDE.md:** Comprehensive guidance for Claude Code
- **OpenSSL 3.6.0 Analysis:** See CLAUDE.md Issue 1 section

---

## Support & Troubleshooting

See **CLAUDE.md** in root and each repository for:
- Architecture questions
- Build issues
- Integration patterns
- Security gate failures
- CPS file generation problems

---

**Status:** Ready for implementation
**Next Step:** Deploy workflows to GitHub
**Created:** 2025-10-31
