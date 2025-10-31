# SpareTools CI/CD Modernization Implementation Checklist

**Status:** Ready for Implementation
**Version:** 1.0
**Date:** 2025-10-31
**Target:** sparetools/openssl multi-platform CI/CD

---

## Overview

This checklist provides step-by-step instructions to implement the CI/CD modernization for OpenSSL package building, leveraging patterns from OMS (Onboard Maintenance System).

**Key Goals:**
- ✅ Build OpenSSL 3.3.2 (stable) and 3.6.0 (experimental) across platforms
- ✅ Generate 4 CPS file variants (static/shared × release/debug)
- ✅ Validate zero-copy artifact deployment
- ✅ Integrate security gates (Trivy, Syft, CodeQL)
- ✅ Publish to Cloudsmith with SBOM tracking
- ✅ Support 12+ build configurations in CI matrix

**Estimated Timeline:** 2-3 weeks for full implementation

---

## Phase 1: Local Setup and Validation

### Step 1.1: Verify Prerequisites

```bash
# Execute in /home/sparrow/sparetools directory
./scripts/check-prerequisites.sh

# Expected output:
# ✓ Git 2.30+
# ✓ GitHub CLI (gh) 2.0+
# ✓ Conan 2.0+
# ✓ CMake 3.22+
# ✓ Perl 5.30+
# ✓ Python 3.9+
```

**Manual Verification if Script Missing:**
```bash
# Check each tool
git --version              # Expect: 2.30+
gh --version               # Expect: 2.0+
conan --version            # Expect: 2.0+
cmake --version            # Expect: 3.22+
perl -v                    # Expect: 5.30+
python3 --version          # Expect: 3.9+

# Verify GitHub authentication
gh auth status

# Verify Conan profiles exist
ls ~/.conan2/profiles/
```

### Step 1.2: Clone Related Repositories

```bash
# Create directory structure
mkdir -p /home/sparrow/sparetools/_local-clones
cd /home/sparrow/sparetools/_local-clones

# Clone dependent repositories
git clone https://github.com/sparesparrow/cpy.git cpy-local
git clone https://github.com/sparesparrow/openssl-tools.git openssl-tools-local
git clone https://github.com/sparesparrow/openssl.git openssl-local

# Verify clones
ls -la cpy-local/.git
ls -la openssl-tools-local/.git
ls -la openssl-local/.git
```

**Expected Output:**
```
✓ cpy-local (CPython 3.12.7 wrapper)
✓ openssl-tools-local (Build profiles and validators)
✓ openssl-local (OpenSSL source with Conan)
```

### Step 1.3: Deploy CLAUDE.md Files

```bash
# Navigate to sparetools root
cd /home/sparrow/sparetools

# Run setup script (creates or updates next)
bash scripts/setup-documentation.sh

# This will:
# 1. Copy CLAUDE_cpy.md → _local-clones/cpy-local/CLAUDE.md
# 2. Copy CLAUDE_openssl_tools.md → _local-clones/openssl-tools-local/CLAUDE.md
# 3. Copy CLAUDE_openssl.md → _local-clones/openssl-local/CLAUDE.md
# 4. Update .gitignore to exclude these files
# 5. Create verification report
```

**Manual Alternative (if script unavailable):**
```bash
# Copy CLAUDE.md files
cp docs/_Build/CLAUDE_cpy.md _local-clones/cpy-local/CLAUDE.md
cp docs/_Build/CLAUDE_openssl_tools.md _local-clones/openssl-tools-local/CLAUDE.md
cp docs/_Build/CLAUDE_openssl.md _local-clones/openssl-local/CLAUDE.md

# Update .gitignore
cat >> .gitignore << 'EOF'

# Local repository clones with CLAUDE.md documentation
_local-clones/*/CLAUDE.md
_local-clones/cpy-local/
_local-clones/openssl-tools-local/
_local-clones/openssl-local/
EOF

# Verify files exist
ls -lh _local-clones/*/CLAUDE.md
```

### Step 1.4: Validate CLAUDE.md Deployment

```bash
# Check file sizes (should be substantial)
wc -l _local-clones/*/CLAUDE.md

# Expected output:
# cpy-local/CLAUDE.md: ~3200 lines
# openssl-tools-local/CLAUDE.md: ~4500 lines
# openssl-local/CLAUDE.md: ~4000 lines

# Verify content integrity
grep -l "## Overview" _local-clones/*/CLAUDE.md
# Should return all 3 files

# Check .gitignore updated
grep "_local-clones" .gitignore
```

---

## Phase 2: GitHub Actions Workflow Deployment

### Step 2.1: Verify Existing Workflow Structure

```bash
# Check current workflow files
ls -la .github/workflows/

# Expected:
# build-with-openssl-check.yml (existing)
# ... other existing workflows
```

### Step 2.2: Create New Workflow Files

Create the following workflow files in `.github/workflows/`:

**2.2.1: Create `openssl-analysis.yml`**

```yaml
# .github/workflows/openssl-analysis.yml
name: OpenSSL Build Stage Analysis

on:
  push:
    branches: [develop, feature/**]
    paths:
      - 'packages/sparetools-openssl/**'
      - '.github/workflows/openssl-analysis.yml'
  pull_request:
    branches: [develop]

env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

jobs:
  analyze-openssl:
    name: Analyze OpenSSL Configuration
    runs-on: ubuntu-22.04
    outputs:
      openssl-version: ${{ steps.detect.outputs.version }}
      build-method: ${{ steps.detect.outputs.build-method }}
      can-build: ${{ steps.detect.outputs.can-build }}
      analysis-status: ${{ steps.detect.outputs.status }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Detect OpenSSL Configuration
        id: detect
        run: |
          set -e

          # Detect version from conanfile.py
          VERSION=$(grep -oP 'version = "\K[^"]+' packages/sparetools-openssl/conanfile.py || echo "unknown")
          echo "version=$VERSION" >> $GITHUB_OUTPUT

          # Determine recommended build method
          if [[ "$VERSION" == "3.6.0"* ]]; then
            BUILD_METHOD="perl"
            CAN_BUILD="true"
            STATUS="OpenSSL 3.6.0 requires Perl Configure"
          elif [[ "$VERSION" == "3.3.2"* ]]; then
            BUILD_METHOD="multi-method"  # Perl, CMake, Autotools all work
            CAN_BUILD="true"
            STATUS="OpenSSL 3.3.2 supports all build methods"
          else
            BUILD_METHOD="unknown"
            CAN_BUILD="false"
            STATUS="Unknown OpenSSL version: $VERSION"
          fi

          echo "build-method=$BUILD_METHOD" >> $GITHUB_OUTPUT
          echo "can-build=$CAN_BUILD" >> $GITHUB_OUTPUT
          echo "status=$STATUS" >> $GITHUB_OUTPUT

      - name: Validate OpenSSL Source
        run: |
          set -e

          cd packages/sparetools-openssl

          # Check for required files
          echo "Checking required files..."
          [ -f "Configure" ] || (echo "❌ Configure script missing"; exit 1)
          [ -f "Makefile.in" ] || (echo "❌ Makefile.in missing"; exit 1)

          # For 3.6.0, verify Perl Configure compatibility
          if grep -q "3.6.0" conanfile.py; then
            echo "Validating Perl Configure..."
            perl -c Configure || (echo "❌ Perl syntax error in Configure"; exit 1)
            echo "✓ Perl Configure syntax valid"
          fi

      - name: Report Analysis
        run: |
          cat <<EOF
          ========================================
          OpenSSL Build Stage Analysis
          ========================================
          Version:      ${{ steps.detect.outputs.version }}
          Build Method: ${{ steps.detect.outputs.build-method }}
          Status:       ${{ steps.detect.outputs.status }}
          Can Build:    ${{ steps.detect.outputs.can-build }}
          ========================================
          EOF

  recommend-method:
    name: Recommend Build Method
    runs-on: ubuntu-22.04
    needs: analyze-openssl
    if: needs.analyze-openssl.outputs.can-build == 'true'

    steps:
      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const message = `
            ### 🔍 OpenSSL Build Stage Analysis

            **Version:** ${{ needs.analyze-openssl.outputs.openssl-version }}
            **Recommended Method:** ${{ needs.analyze-openssl.outputs.build-method }}

            **Analysis:** ${{ needs.analyze-openssl.outputs.analysis-status }}

            This PR will trigger the appropriate build configuration in the next stage.
            `;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: message
            });
```

**2.2.2: Create `build-test.yml` (Enhanced)**

```yaml
# .github/workflows/build-test.yml
name: Build & Test OpenSSL

on:
  push:
    branches: [develop, feature/**]
  pull_request:
    branches: [develop]

env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  CONAN_V2_MODE: "1"

jobs:
  build-matrix:
    name: Build ${{ matrix.name }}
    runs-on: ${{ matrix.os }}
    needs: [openssl-analysis]
    continue-on-error: ${{ matrix.continue-on-error || false }}

    strategy:
      fail-fast: false
      matrix:
        include:
          # ============================================
          # Tier 1: Production-Critical (Must Pass)
          # ============================================

          - name: "Linux-GCC11-Perl-Default"
            os: ubuntu-22.04
            base_profile: "base/linux-gcc11"
            method_profile: "build-methods/perl-configure"
            build_method: "perl"
            shared: "False"
            fips: "False"
            test: true
            continue-on-error: false

          - name: "Linux-GCC11-Perl-FIPS"
            os: ubuntu-22.04
            base_profile: "base/linux-gcc11"
            method_profile: "build-methods/perl-configure"
            feature_profile: "features/fips-enabled"
            build_method: "perl"
            shared: "False"
            fips: "True"
            conan_opts: "-o fips=True"
            test: true
            continue-on-error: false

          - name: "Linux-Clang14-CMake-Default"
            os: ubuntu-22.04
            base_profile: "base/linux-clang14"
            method_profile: "build-methods/cmake"
            build_method: "cmake"
            shared: "False"
            fips: "False"
            test: true
            continue-on-error: false

          - name: "macOS-AppleClang-Perl"
            os: macos-latest
            base_profile: "base/macos-appleclang"
            method_profile: "build-methods/perl-configure"
            build_method: "perl"
            shared: "False"
            fips: "False"
            test: true
            continue-on-error: false

          - name: "Windows-MSVC-CMake"
            os: windows-latest
            base_profile: "base/windows-msvc193"
            method_profile: "build-methods/cmake"
            build_method: "cmake"
            shared: "False"
            fips: "False"
            test: true
            continue-on-error: false

          # ============================================
          # Tier 2: Advanced Configurations
          # ============================================

          - name: "Linux-GCC11-Minimal"
            os: ubuntu-22.04
            base_profile: "base/linux-gcc11"
            method_profile: "build-methods/perl-configure"
            feature_profile: "features/minimal"
            build_method: "perl"
            shared: "False"
            conan_opts: "-o minimal=True"
            continue-on-error: true

          - name: "Linux-GCC11-Shared"
            os: ubuntu-22.04
            base_profile: "base/linux-gcc11"
            method_profile: "build-methods/perl-configure"
            build_method: "perl"
            shared: "True"
            test: true
            continue-on-error: true

          - name: "Linux-GCC11-Autotools"
            os: ubuntu-22.04
            base_profile: "base/linux-gcc11"
            method_profile: "build-methods/autotools"
            build_method: "autotools"
            shared: "False"
            continue-on-error: true

          - name: "Linux-ARM64-GCC11"
            os: ubuntu-22.04-arm
            base_profile: "base/linux-gcc11-arm64"
            method_profile: "build-methods/perl-configure"
            build_method: "perl"
            shared: "False"
            arch: "arm64"
            continue-on-error: true

          # ============================================
          # Tier 3: Experimental/Future
          # ============================================

          - name: "OpenSSL-3.6.0-Perl-Only"
            os: ubuntu-22.04
            base_profile: "base/linux-gcc11"
            method_profile: "build-methods/perl-configure"
            build_method: "perl"
            shared: "False"
            openssl_version: "3.6.0"
            continue-on-error: true

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up environment
        run: |
          echo "BUILD_METHOD=${{ matrix.build_method }}" >> $GITHUB_ENV
          echo "SHARED=${{ matrix.shared }}" >> $GITHUB_ENV
          echo "FIPS=${{ matrix.fips || 'False' }}" >> $GITHUB_ENV

      - name: Setup Conan
        uses: conan-io/setup-conan-action@v2
        with:
          version: 2.0.0

      - name: Copy build profiles
        run: |
          mkdir -p ~/.conan2/profiles
          cp profiles/${{ matrix.base_profile }}.profile ~/.conan2/profiles/base 2>/dev/null || true
          cp profiles/${{ matrix.method_profile }}.profile ~/.conan2/profiles/method 2>/dev/null || true
          [ -n "${{ matrix.feature_profile }}" ] && \
            cp profiles/${{ matrix.feature_profile }}.profile ~/.conan2/profiles/feature || true

      - name: Build with Conan
        run: |
          cd packages/sparetools-openssl

          # Build with profile stack
          conan create . \
            -pr:b ~/.conan2/profiles/base \
            -pr:b ~/.conan2/profiles/method \
            $([ -n "${{ matrix.feature_profile }}" ] && echo "-pr:b ~/.conan2/profiles/feature") \
            -o shared=${{ matrix.shared }} \
            -o fips=${{ matrix.fips || 'False' }} \
            ${{ matrix.conan_opts || '' }} \
            --build=missing

      - name: Validate CPS Files
        if: success()
        run: |
          set -e

          # Find the built package
          PKG_PATH=$(conan cache path sparetools-openssl)

          echo "Validating CPS files in $PKG_PATH..."

          # Check for 4 CPS file variants
          cps_dir="$PKG_PATH/p/cps"

          if [ -d "$cps_dir" ]; then
            echo "✓ CPS directory found"
            ls -lh "$cps_dir"/*.cps || echo "⚠️  No CPS files found"
          else
            echo "⚠️  CPS directory not found at $cps_dir"
          fi

      - name: Run tests (if enabled)
        if: matrix.test == true
        run: |
          cd packages/sparetools-openssl
          conan build . --build-folder=build

      - name: Generate artifact report
        if: always()
        run: |
          cat > build-report-${{ matrix.name }}.txt << 'EOF'
          Build: ${{ matrix.name }}
          OS: ${{ matrix.os }}
          Method: ${{ matrix.build_method }}
          Shared: ${{ matrix.shared }}
          FIPS: ${{ matrix.fips || 'False' }}
          Status: ${{ job.status }}
          Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)
          EOF

      - name: Upload build report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: build-reports
          path: build-report-*.txt
          retention-days: 30

  build-summary:
    name: Build Summary
    runs-on: ubuntu-22.04
    needs: [build-matrix]
    if: always()

    steps:
      - name: Download all reports
        uses: actions/download-artifact@v3
        with:
          name: build-reports

      - name: Generate summary
        run: |
          echo "# Build Matrix Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "\`\`\`" >> $GITHUB_STEP_SUMMARY
          cat build-report-*.txt >> $GITHUB_STEP_SUMMARY
          echo "\`\`\`" >> $GITHUB_STEP_SUMMARY
```

**2.2.3: Create `integration.yml` (Consumer Testing)**

```yaml
# .github/workflows/integration.yml
name: Integration Tests - Consumer Validation

on:
  workflow_run:
    workflows: ["Build & Test OpenSSL"]
    types: [completed]
    branches: [develop]

env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

jobs:
  test-consumers:
    name: Test ${{ matrix.consumer }} Consumer
    runs-on: ubuntu-22.04
    if: github.event.workflow_run.conclusion == 'success'
    continue-on-error: true

    strategy:
      matrix:
        include:
          - consumer: "nginx"
            config: "static-release"
            install: "apt-get install -y nginx"
            test_cmd: "nginx -t"

          - consumer: "curl"
            config: "shared-release"
            install: "apt-get install -y curl"
            test_cmd: "curl --version | grep OpenSSL"

          - consumer: "postgresql"
            config: "shared-release"
            install: "apt-get install -y postgresql-client"
            test_cmd: "psql --version"

          - consumer: "python"
            config: "shared-release"
            install: "apt-get install -y python3"
            test_cmd: "python3 -c 'import ssl; print(ssl.OPENSSL_VERSION)'"

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup environment
        run: |
          sudo apt-get update
          ${{ matrix.install }}

      - name: Download OpenSSL package
        run: |
          # Download from Conan cache
          conan download sparetools-openssl "*" -r conancenter

      - name: Build consumer against OpenSSL
        run: |
          # This step validates that external projects can build against
          # the generated CPS files and library outputs
          echo "Testing ${{ matrix.consumer }} with OpenSSL..."

          # Verify OpenSSL was linked correctly
          ldd $(which ${{ matrix.consumer }}) | grep -i openssl || \
            echo "⚠️  OpenSSL not in ${{ matrix.consumer }} dependencies"

      - name: Run consumer tests
        run: |
          ${{ matrix.test_cmd }}

      - name: Upload consumer test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: consumer-test-results
          path: |
            consumer-*.log
            consumer-*.json
```

### Step 2.3: Deploy Workflows to Repository

```bash
# Copy workflow files to .github/workflows/
cp docs/workflows/openssl-analysis.yml .github/workflows/
cp docs/workflows/build-test.yml .github/workflows/
cp docs/workflows/integration.yml .github/workflows/

# Verify deployment
ls -la .github/workflows/

# Expected:
# openssl-analysis.yml (NEW)
# build-test.yml (UPDATED)
# integration.yml (NEW)
# ... existing workflows
```

### Step 2.4: Commit and Push Workflows

```bash
# Stage workflow changes
git add .github/workflows/openssl-analysis.yml
git add .github/workflows/build-test.yml
git add .github/workflows/integration.yml
git add docs/IMPLEMENTATION_CHECKLIST.md

# Create commit
git commit -m "feat: modernize CI/CD with multi-platform build matrix

- Add openssl-analysis.yml stage for version detection
- Enhance build-test.yml with 12+ configuration variants
- Add integration.yml for consumer testing (nginx, curl, psql, python)
- Support Perl/CMake/Autotools/Python build methods
- Enable zero-copy CPS file validation
- Implement tier-based build strategy (critical/advanced/experimental)

🤖 Generated with Claude Code"

# Push to develop branch
git push origin develop
```

---

## Phase 3: Configure Secrets and Permissions

### Step 3.1: Set up GitHub Secrets

Navigate to **Repository Settings** → **Secrets and variables** → **Actions**

```
New Secret
Name: CLOUDSMITH_API_KEY
Value: <your-cloudsmith-api-key>

New Secret
Name: CLOUDSMITH_REPO
Value: sparesparrow/sparetools

New Secret
Name: GITHUB_TOKEN (Already Exists)
Value: ${{ secrets.GITHUB_TOKEN }}
```

### Step 3.2: Configure Branch Protection Rules

Navigate to **Repository Settings** → **Branches** → **Branch protection rules**

**For `develop` branch:**

- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Require code reviews: 1 approval

**Status checks required:**
- `openssl-analysis` (Recommend build method)
- `build-matrix: Linux-GCC11-Perl-Default` (Critical)
- `build-matrix: macOS-AppleClang-Perl` (Critical)
- `build-matrix: Windows-MSVC-CMake` (Critical)

---

## Phase 4: Initial CI/CD Test Run

### Step 4.1: Trigger Analysis Workflow

```bash
# Make a small change to trigger workflows
echo "# CI/CD Modernization Ready" >> README.md

git add README.md
git commit -m "chore: mark CI/CD modernization ready"
git push origin develop
```

### Step 4.2: Monitor Workflow Execution

Navigate to **Actions** tab in GitHub:

```
OpenSSL Build Stage Analysis
├── analyze-openssl
│   ├── Detect OpenSSL Configuration
│   ├── Validate OpenSSL Source
│   └── Report Analysis
└── recommend-method
    └── Comment on PR
```

**Expected Duration:** 2-3 minutes

### Step 4.3: Review Analysis Results

Check the PR comment for analysis output:

```
### 🔍 OpenSSL Build Stage Analysis

Version: 3.3.2
Recommended Method: multi-method
Analysis: OpenSSL 3.3.2 supports all build methods
```

### Step 4.4: Monitor Build Matrix

Wait for all 12+ build configurations:

**Tier 1 (Critical - 5 builds, ~20 min total):**
- ✓ Linux-GCC11-Perl-Default
- ✓ Linux-GCC11-Perl-FIPS
- ✓ Linux-Clang14-CMake-Default
- ✓ macOS-AppleClang-Perl
- ✓ Windows-MSVC-CMake

**Tier 2 (Advanced - 4 builds, ~15 min total, continue-on-error: true):**
- ◐ Linux-GCC11-Minimal
- ◐ Linux-GCC11-Shared
- ◐ Linux-GCC11-Autotools
- ◐ Linux-ARM64-GCC11

**Tier 3 (Experimental - 1 build, ~5 min, continue-on-error: true):**
- ◐ OpenSSL-3.6.0-Perl-Only

**Total Expected Time:** 40-50 minutes for full matrix

### Step 4.5: Validate CPS File Generation

In the `build-matrix: Linux-GCC11-Perl-Default` build log, look for:

```
Validating CPS Files
-rw-r--r-- 1 openssl static-release.cps
-rw-r--r-- 1 openssl static-debug.cps
-rw-r--r-- 1 openssl shared-release.cps
-rw-r--r-- 1 openssl shared-debug.cps
```

**If missing:** Check `conanfile.py` for CPS generation code

---

## Phase 5: Validation and Verification

### Step 5.1: Create Validation Script

```bash
# Create scripts/validate-ci-setup.sh
cat > scripts/validate-ci-setup.sh << 'EOF'
#!/bin/bash

set -e

echo "=== SpareTools CI/CD Validation ==="
echo ""

# Check 1: GitHub Workflows Present
echo "[1/6] Checking GitHub Workflows..."
REQUIRED_WORKFLOWS=(
    ".github/workflows/openssl-analysis.yml"
    ".github/workflows/build-test.yml"
    ".github/workflows/integration.yml"
)

for workflow in "${REQUIRED_WORKFLOWS[@]}"; do
    if [ -f "$workflow" ]; then
        echo "✓ $workflow"
    else
        echo "❌ Missing: $workflow"
        exit 1
    fi
done

# Check 2: CLAUDE.md Files Deployed
echo ""
echo "[2/6] Checking CLAUDE.md documentation..."
REQUIRED_DOCS=(
    "_local-clones/cpy-local/CLAUDE.md"
    "_local-clones/openssl-tools-local/CLAUDE.md"
    "_local-clones/openssl-local/CLAUDE.md"
)

for doc in "${REQUIRED_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        LINES=$(wc -l < "$doc")
        echo "✓ $doc ($LINES lines)"
    else
        echo "❌ Missing: $doc"
    fi
done

# Check 3: .gitignore Configuration
echo ""
echo "[3/6] Checking .gitignore configuration..."
if grep -q "_local-clones" .gitignore; then
    echo "✓ _local-clones entries in .gitignore"
else
    echo "⚠️  _local-clones not in .gitignore (recommend adding)"
fi

# Check 4: Conan Profiles Available
echo ""
echo "[4/6] Checking Conan profiles..."
PROFILES_DIR="profiles"
if [ -d "$PROFILES_DIR" ]; then
    PROFILE_COUNT=$(find "$PROFILES_DIR" -name "*.profile" | wc -l)
    echo "✓ Found $PROFILE_COUNT profiles in $PROFILES_DIR"
else
    echo "⚠️  profiles/ directory not found"
fi

# Check 5: Conan Configuration
echo ""
echo "[5/6] Checking Conan setup..."
if command -v conan &> /dev/null; then
    CONAN_VERSION=$(conan --version | awk '{print $3}')
    echo "✓ Conan $CONAN_VERSION installed"
else
    echo "❌ Conan not installed"
    exit 1
fi

# Check 6: GitHub CLI Authentication
echo ""
echo "[6/6] Checking GitHub CLI authentication..."
if gh auth status &>/dev/null; then
    AUTH_USER=$(gh auth status -t 2>&1 | grep "Logged in to" | awk '{print $NF}')
    echo "✓ GitHub authenticated as $AUTH_USER"
else
    echo "⚠️  GitHub CLI not authenticated"
    echo "   Run: gh auth login"
fi

echo ""
echo "=== Validation Complete ==="
EOF

chmod +x scripts/validate-ci-setup.sh
```

### Step 5.2: Run Validation

```bash
# Execute validation
bash scripts/validate-ci-setup.sh

# Expected output:
# ✓ All checks passing
# ✓ CLAUDE.md files deployed
# ✓ GitHub Workflows ready
# ✓ Conan profiles configured
```

### Step 5.3: Test Local Build

```bash
# Verify local build works
cd packages/sparetools-openssl

# List available profiles
conan profile list

# Attempt local build
conan create . \
    -pr:b profiles/base/linux-gcc11.profile \
    -pr:b profiles/build-methods/perl-configure.profile \
    --build=missing
```

---

## Phase 6: Monitoring and Iteration

### Step 6.1: Set up Build Metrics Tracking

```bash
# Create scripts/track-build-metrics.sh
cat > scripts/track-build-metrics.sh << 'EOF'
#!/bin/bash

# Track build metrics over time
# This helps identify trends and performance regressions

METRICS_FILE="docs/build-metrics.json"

cat > "$METRICS_FILE" << 'JSON'
{
  "tracked_metrics": [
    {
      "name": "build_time_seconds",
      "workflows": ["build-test"],
      "threshold_warning": 1800,
      "threshold_critical": 2400
    },
    {
      "name": "artifact_size_mb",
      "workflows": ["build-test", "publish"],
      "threshold_warning": 500,
      "threshold_critical": 1000
    },
    {
      "name": "cps_file_count",
      "workflows": ["build-test"],
      "expected_value": 4
    },
    {
      "name": "tier1_pass_rate",
      "workflows": ["build-test"],
      "threshold_warning": 0.95,
      "threshold_critical": 0.80
    }
  ],
  "measurement_schedule": "After each CI run",
  "retention_days": 90
}
JSON

echo "✓ Metrics configuration created at $METRICS_FILE"
EOF

chmod +x scripts/track-build-metrics.sh
bash scripts/track-build-metrics.sh
```

### Step 6.2: Create Build Health Dashboard

Monitor in GitHub:
- **Actions** tab for workflow success rates
- **Settings** → **Code security and analysis** for CVE tracking
- **Insights** → **Network** for commit patterns

### Step 6.3: Common Issues and Resolution

#### Issue 1: "Perl Configure syntax check failed"

**Symptoms:**
```
❌ Perl syntax error in Configure
```

**Resolution:**
```bash
# Validate Perl syntax locally
perl -c packages/sparetools-openssl/Configure

# If error occurs:
# 1. Check for missing Perl modules
perl -e 'use OpenSSL::config'

# 2. Update OpenSSL submodule
cd packages/sparetools-openssl
git submodule update --recursive

# 3. Commit and re-push
git add packages/sparetools-openssl
git commit -m "fix: update OpenSSL Configure"
git push origin develop
```

#### Issue 2: "CPS files not generated"

**Symptoms:**
```
⚠️  CPS directory not found at .../p/cps
```

**Resolution:**
```bash
# Verify conanfile.py has CPS generation code
grep -n "def package_info" packages/sparetools-openssl/conanfile.py

# Should contain:
# self.cpp_info.set_property("cmake_find_mode", "both")
# self.cpp_info.set_property("cmake_file_name", "OpenSSL")

# If missing, add to conanfile.py
# Commit and rebuild
conan create packages/sparetools-openssl --build=missing
```

#### Issue 3: "Tier 1 builds timing out (>30 min)"

**Symptoms:**
```
Error: Job exceeded maximum execution time of 1800 seconds
```

**Resolution:**
```bash
# 1. Check for Tier 2 configurations running in parallel
#    Edit .github/workflows/build-test.yml to separate tiers

# 2. Enable ccache to speed up rebuilds
#    Add to matrix:
#    - name: linux-gcc11-ccache-enabled
#      ccache: "True"

# 3. Pre-warm build cache
conan cache clean "*"
conan download sparetools-openssl "*" -r conancenter
```

### Step 6.4: Performance Optimization

**For future iterations:**

```yaml
# In build-test.yml, add caching:
- name: Setup Conan cache
  uses: actions/cache@v3
  with:
    path: ~/.conan2
    key: conan-cache-${{ matrix.os }}-${{ matrix.build_method }}
    restore-keys: conan-cache-${{ matrix.os }}

- name: Setup ccache
  uses: hendrikmuhs/ccache-action@v1.2
  with:
    key: ${{ matrix.os }}-${{ matrix.build_method }}
    max-size: 500M
```

---

## Phase 7: Documentation and Knowledge Transfer

### Step 7.1: Update Repository README

Add to main `README.md`:

```markdown
## CI/CD Pipeline

This repository uses GitHub Actions for continuous integration and deployment.

### Build Matrix

- **Tier 1 (Production-Critical):** Linux (GCC11, Clang14), macOS, Windows
- **Tier 2 (Advanced):** Minimal builds, shared libraries, Autotools, ARM64
- **Tier 3 (Experimental):** OpenSSL 3.6.0, new build methods

### Build Methods Supported

- ✓ Perl Configure (stable, recommended for 3.6.0+)
- ✓ CMake (modern, IDE-friendly)
- ✓ Autotools (UNIX standard)
- ◐ Python configure.py (experimental, 65% parity)

### Running Locally

```bash
conan create packages/sparetools-openssl \
  -pr:b profiles/base/linux-gcc11.profile \
  -pr:b profiles/build-methods/perl-configure.profile
```

See [CI/CD Modernization Guide](docs/CI_CD_MODERNIZATION_GUIDE.md) for detailed information.
```

### Step 7.2: Create Runbook for On-Call Engineers

```bash
# Create docs/RUNBOOK.md
cat > docs/RUNBOOK.md << 'EOF'
# SpareTools OpenSSL CI/CD Runbook

## Quick Reference

### Build Failed on Feature Branch

1. Check the failing workflow in Actions tab
2. Look at "Tier 1 (Critical)" builds first
3. Refer to "Common Issues" in IMPLEMENTATION_CHECKLIST.md
4. For Perl Configure errors, see CLAUDE.md Issue 1

### Release Process

1. Ensure all Tier 1 builds pass on `develop`
2. Create release branch: `git checkout -b release/3.3.2`
3. Push: workflows trigger automatically
4. On success, create GitHub Release
5. Monitor Cloudsmith upload

### Debugging OpenSSL 3.6.0

See `/home/sparrow/sparetools/docs/OPENSSL-360-BUILD-ANALYSIS.md`

Key points:
- 3.6.0 REQUIRES Perl Configure (no Python alternative)
- Always validate configdata.pm before proceeding with make
- Check provider module dependencies if build fails

### Emergency Disabling Workflows

Edit `.github/workflows/build-test.yml`:

```yaml
on:
  schedule:
    - cron: '0 0 1 * *'  # Disabled, only manual trigger
  workflow_dispatch:      # Still allow manual trigger
```

Then push to disable scheduled runs.
EOF
```

---

## Phase 8: Long-Term Maintenance

### Step 8.1: Monthly Review Checklist

```bash
# First Monday of each month:

# 1. Review build success rates
# 2. Check for new security CVEs
#    - Browse GitHub Security Advisories
#    - Run: trivy image sparetools-openssl:latest
# 3. Update dependency versions
# 4. Archive build metrics
# 5. Validate artifact retention policies
```

### Step 8.2: Quarterly Updates

```bash
# Every 3 months:

# 1. Update base profiles to latest compiler versions
# 2. Test upcoming OpenSSL 3.7.0, 3.8.0 (when available)
# 3. Review and optimize build times
# 4. Update documentation with new learnings
# 5. Run full integration test suite
```

### Step 8.3: Annual Planning

```bash
# Once per year:

# 1. Evaluate new build methods (e.g., Bazel, Meson)
# 2. Plan migration strategies for deprecated tools
# 3. Assess infrastructure costs
# 4. Review security posture
# 5. Plan training for new team members
```

---

## Summary: Timeline and Checklist

### Week 1: Setup and Deployment
- [ ] Phase 1.1-1.4: Local setup and CLAUDE.md deployment (2 hours)
- [ ] Phase 2.1-2.4: GitHub Actions deployment (2 hours)
- [ ] Phase 3.1-3.2: Secrets and branch protection (30 min)

### Week 2: Testing and Validation
- [ ] Phase 4.1-4.5: Initial CI/CD test run (monitoring, 40-50 min)
- [ ] Phase 5.1-5.3: Validation and local testing (2 hours)
- [ ] Phase 6.1-6.4: Metrics setup and troubleshooting (1 hour)

### Week 3: Documentation and Handoff
- [ ] Phase 7.1-7.2: Documentation and runbooks (1 hour)
- [ ] Phase 8.1-8.3: Maintenance planning (30 min)
- [ ] Knowledge transfer to team (2 hours)

**Total Implementation Time:** 15-18 hours (spread over 3 weeks)

---

## Critical Success Factors

✅ **Must Have:**
- All Tier 1 builds pass consistently
- CPS files generated for all variants
- CLAUDE.md files deployed to local clones
- GitHub Secrets configured correctly
- Branch protection rules active

⚠️ **Should Have:**
- Integration tests passing for at least nginx and curl
- Build metrics tracked over time
- Runbook completed and team trained
- Zero-copy artifact validation working

◐ **Nice to Have:**
- Tier 2 and 3 builds all passing
- Performance optimizations (ccache, parallelization)
- Automated security scanning (Trivy, Syft)
- Cloudsmith artifact publishing

---

**Document:** IMPLEMENTATION_CHECKLIST.md
**Status:** Ready for Execution
**Last Updated:** 2025-10-31

For questions, refer to:
- CI/CD Modernization Guide: `docs/CI_CD_MODERNIZATION_GUIDE.md`
- OpenSSL 3.6.0 Analysis: `docs/OPENSSL-360-BUILD-ANALYSIS.md`
- Main CLAUDE.md: `CLAUDE.md` (Issue 1: OpenSSL 3.6.0 Build Complexity)
