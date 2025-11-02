# SpareTools Testing Guide

Comprehensive testing guide for SpareTools Conan packages, workflows, and CI/CD pipelines.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Local Testing](#local-testing)
3. [Package Testing](#package-testing)
4. [Integration Testing](#integration-testing)
5. [Workflow Testing](#workflow-testing)
6. [Security Testing](#security-testing)
7. [Performance Testing](#performance-testing)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

```bash
# Install Conan 2.x
pip install conan==2.21.0

# Verify installation
conan --version  # Should show 2.21.0

# Configure Conan
conan profile detect --force
```

### Quick Test Command

```bash
# Test OpenSSL package
cd packages/sparetools-openssl
conan create . --version=3.3.2 --build=missing
conan test test_package --requires=sparetools-openssl/3.3.2
```

---

## Local Testing

### 1. Test Foundation Packages

#### Test sparetools-base

```bash
cd packages/sparetools-base

# Export (python_requires)
conan export . --version=2.0.0

# Verify export
conan list "sparetools-base/*"
```

#### Test sparetools-openssl-tools

```bash
cd packages/sparetools-openssl-tools

# Export
conan export . --version=2.0.0

# Verify profiles exist
ls -la profiles/base/
ls -la profiles/build-methods/
ls -la profiles/features/

# Test profile validation
conan profile show packages/sparetools-openssl-tools/profiles/base/linux-gcc11
```

### 2. Test CPython Package

```bash
cd packages/sparetools-cpython

# Build CPython
conan create . \
  --version=3.12.7 \
  --build=missing \
  -s build_type=Release

# Verify installation
PKG_PATH=$(conan cache path "sparetools-cpython/3.12.7:*" | head -1)
"$PKG_PATH/bin/python3" --version
"$PKG_PATH/bin/python3" -c "import ssl; print(ssl.OPENSSL_VERSION)"
```

### 3. Test OpenSSL Package

#### Basic Build Test

```bash
cd packages/sparetools-openssl

# Build with default profile (Perl Configure)
conan create . \
  --version=3.3.2 \
  -pr:b packages/sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b packages/sparetools-openssl-tools/profiles/build-methods/perl-configure \
  --build=missing
```

#### Test with FIPS Enabled

```bash
conan create . \
  --version=3.3.2 \
  -pr:b packages/sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b packages/sparetools-openssl-tools/profiles/build-methods/perl-configure \
  -pr:b packages/sparetools-openssl-tools/profiles/features/fips-enabled \
  --build=missing
```

#### Test Multiple Build Methods

```bash
# Test CMake build (if supported)
conan create . \
  --version=3.3.2 \
  -pr:b packages/sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b packages/sparetools-openssl-tools/profiles/build-methods/cmake-build \
  --build=missing

# Test Autotools build
conan create . \
  --version=3.3.2 \
  -pr:b packages/sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b packages/sparetools-openssl-tools/profiles/build-methods/autotools \
  --build=missing
```

---

## Package Testing

### Running test_package

All packages include `test_package/` directories with integration tests.

#### Test Foundation Package

```bash
cd packages/sparetools-base

# Create package first
conan export . --version=2.0.0

# Run test_package (if exists)
cd test_package
conan test . --requires=sparetools-base/2.0.0
```

#### Test OpenSSL Package

```bash
cd packages/sparetools-openssl

# Build package
conan create . \
  --version=3.3.2 \
  -pr:b packages/sparetools-openssl-tools/profiles/base/linux-gcc11 \
  --build=missing

# Run test_package
conan test test_package \
  --requires=sparetools-openssl/3.3.2 \
  -pr:b packages/sparetools-openssl-tools/profiles/base/linux-gcc11
```

### Custom Test Scripts

Create custom test scripts for additional validation:

```python
# test_custom.py
import os
import subprocess
from pathlib import Path

def test_openssl_installation():
    """Test OpenSSL installation"""
    # Get package path from Conan cache
    result = subprocess.run(
        ["conan", "cache", "path", "sparetools-openssl/3.3.2:*"],
        capture_output=True,
        text=True
    )
    pkg_path = Path(result.stdout.strip().split('\n')[0])
    
    # Test openssl binary
    openssl_bin = pkg_path / "bin" / "openssl"
    assert openssl_bin.exists(), f"OpenSSL binary not found at {openssl_bin}"
    
    # Test version
    result = subprocess.run([str(openssl_bin), "version"], capture_output=True, text=True)
    assert "OpenSSL" in result.stdout, "OpenSSL version command failed"
    
    print(f"✅ OpenSSL installation verified: {result.stdout.strip()}")

if __name__ == "__main__":
    test_openssl_installation()
```

Run custom test:
```bash
python test_custom.py
```

---

## Integration Testing

### Multi-Package Dependency Test

Test the complete dependency chain:

```bash
#!/bin/bash
# test-full-chain.sh

set -e

VERSION_BASE="2.0.0"
VERSION_CPYTHON="3.12.7"
VERSION_OPENSSL="3.3.2"

echo "🔨 Testing full package dependency chain..."

# Stage 1: Foundation packages
echo "📦 Stage 1: Foundation packages"
conan export packages/sparetools-base --version=$VERSION_BASE
conan export packages/sparetools-openssl-tools --version=$VERSION_BASE

# Stage 2: CPython
echo "📦 Stage 2: CPython"
conan create packages/sparetools-cpython \
  --version=$VERSION_CPYTHON \
  --build=missing

# Stage 3: OpenSSL
echo "📦 Stage 3: OpenSSL"
conan create packages/sparetools-openssl \
  --version=$VERSION_OPENSSL \
  -pr:b packages/sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b packages/sparetools-openssl-tools/profiles/build-methods/perl-configure \
  --build=missing

# Stage 4: Integration test
echo "🧪 Stage 4: Integration test"
cd packages/sparetools-openssl
conan test test_package \
  --requires=sparetools-openssl/$VERSION_OPENSSL

echo "✅ Full chain test passed!"
```

### Cross-Platform Testing Matrix

```bash
#!/bin/bash
# test-cross-platform.sh

PLATFORMS=(
  "linux-gcc11:ubuntu-22.04"
  "linux-clang18:ubuntu-22.04"
  "darwin-clang:macos-13"
  "windows-msvc2022:windows-2022"
)

for PLATFORM in "${PLATFORMS[@]}"; do
  PROFILE=$(echo $PLATFORM | cut -d: -f1)
  OS=$(echo $PLATFORM | cut -d: -f2)
  
  echo "🧪 Testing $PROFILE on $OS"
  
  # Use Docker or GitHub Actions for cross-platform
  # Or test locally on each platform
  
  conan create packages/sparetools-openssl \
    --version=3.3.2 \
    -pr:b packages/sparetools-openssl-tools/profiles/base/$PROFILE \
    -pr:b packages/sparetools-openssl-tools/profiles/build-methods/perl-configure \
    --build=missing || echo "❌ Failed on $PROFILE"
done
```

---

## Workflow Testing

### Test GitHub Actions Locally

Install `act` (GitHub Actions local runner):

```bash
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

#### Test CI Workflow

```bash
# Dry run
act push -W .github/workflows/ci.yml --dry-run

# Run specific job
act push -W .github/workflows/ci.yml -j build-test

# Run with matrix
act push -W .github/workflows/ci.yml \
  -j build-test \
  -s matrix.profile=linux-gcc11
```

#### Test Build Workflow

```bash
# Test build-and-test workflow
act workflow_dispatch -W .github/workflows/build-and-test.yml

# Test with inputs
act workflow_dispatch -W .github/workflows/build-and-test.yml \
  --input skip_tests=false
```

### Validate Workflow Syntax

```bash
# Install actionlint (workflow validator)
brew install actionlint  # macOS
# or download from: https://github.com/rhymond/actionlint/releases

# Validate all workflows
actionlint .github/workflows/*.yml

# Validate specific workflow
actionlint .github/workflows/ci.yml
```

### Test Workflow with Docker

```bash
# Use act with Docker
act push -W .github/workflows/ci.yml \
  -P ubuntu-latest=catthehacker/ubuntu:act-22.04 \
  -P macos-latest=catthehacker/macos:big-sur-latest
```

---

## Security Testing

### Trivy Vulnerability Scanning

```bash
# Install Trivy
brew install trivy  # macOS
# or: https://aquasecurity.github.io/trivy/latest/getting-started/installation/

# Scan packages
trivy fs --security-checks vuln ~/.conan2/p/spareto*openssl*/p

# Scan with specific severity
trivy fs --security-checks vuln \
  --severity CRITICAL,HIGH \
  ~/.conan2/p/spareto*openssl*/p

# Generate SARIF report
trivy fs --security-checks vuln \
  --format sarif \
  --output trivy-results.sarif \
  ~/.conan2/p/spareto*openssl*/p
```

### Syft SBOM Generation

```bash
# Install Syft
brew install syft  # macOS
# or: https://github.com/anchore/syft#installation

# Generate CycloneDX SBOM
syft packages ~/.conan2/p/spareto*openssl*/p \
  -o cyclonedx-json \
  > sbom-cyclonedx.json

# Generate SPDX SBOM
syft packages ~/.conan2/p/spareto*openssl*/p \
  -o spdx-json \
  > sbom-spdx.json

# Validate SBOM
cat sbom-cyclonedx.json | jq '.'
```

### FIPS Validation

```bash
# Test FIPS-enabled build
conan create packages/sparetools-openssl \
  --version=3.3.2 \
  -pr:b packages/sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b packages/sparetools-openssl-tools/profiles/build-methods/perl-configure \
  -pr:b packages/sparetools-openssl-tools/profiles/features/fips-enabled \
  --build=missing

# Validate FIPS module (if available)
python3 -c "
from sparetools.bootstrap.openssl.fips_validator import FIPSValidator
validator = FIPSValidator()
result = validator.validate_module('/path/to/fips/module')
print(f'FIPS Validation: {result}')
"
```

---

## Performance Testing

### Build Time Benchmarking

```bash
#!/bin/bash
# benchmark-build-time.sh

echo "⏱️  Benchmarking build times..."

# Time foundation packages
echo "📦 Foundation packages..."
time (
  conan export packages/sparetools-base --version=2.0.0
  conan export packages/sparetools-openssl-tools --version=2.0.0
)

# Time CPython build
echo "📦 CPython build..."
time (
  conan create packages/sparetools-cpython \
    --version=3.12.7 \
    --build=missing
)

# Time OpenSSL build
echo "📦 OpenSSL build..."
time (
  conan create packages/sparetools-openssl \
    --version=3.3.2 \
    -pr:b packages/sparetools-openssl-tools/profiles/base/linux-gcc11 \
    --build=missing
)
```

### Package Size Analysis

```bash
#!/bin/bash
# analyze-package-size.sh

echo "📊 Package size analysis..."

for PKG in "sparetools-base" "sparetools-cpython" "sparetools-openssl"; do
  PKG_PATH=$(conan cache path "$PKG/*:*" | head -1)
  if [ -n "$PKG_PATH" ]; then
    SIZE=$(du -sh "$PKG_PATH" | cut -f1)
    echo "$PKG: $SIZE"
    echo "  Contents:"
    du -h "$PKG_PATH"/* 2>/dev/null | head -10
  fi
done
```

---

## Troubleshooting

### Common Issues

#### Issue: Conan 1.x Syntax Errors

**Error:**
```
ERROR: Invalid reference 'sparetools-openssl/3.3.2@'
```

**Solution:**
```bash
# Use Conan 2.x syntax
conan test test_package --requires=sparetools-openssl/3.3.2
# NOT: conan test test_package sparetools-openssl/3.3.2@
```

#### Issue: Profile Not Found

**Error:**
```
ERROR: Profile not found: 'packages/sparetools-openssl-tools/profiles/base/linux-gcc11'
```

**Solution:**
```bash
# Use absolute path or verify profile exists
ls -la packages/sparetools-openssl-tools/profiles/base/linux-gcc11

# Or use relative path from package directory
cd packages/sparetools-openssl
conan create . \
  -pr:b ../sparetools-openssl-tools/profiles/base/linux-gcc11
```

#### Issue: Missing Dependencies

**Error:**
```
ERROR: 'sparetools-base/2.0.0' not found
```

**Solution:**
```bash
# Export foundation packages first
conan export packages/sparetools-base --version=2.0.0

# Or download from remote
conan download "sparetools-base/2.0.0" -r sparesparrow-conan
```

#### Issue: Build Cache Conflicts

**Error:**
```
ERROR: Cache conflict or corrupted package
```

**Solution:**
```bash
# Clear cache
conan cache clean "*"

# Or remove specific package
conan cache path "sparetools-openssl/3.3.2:*" | xargs rm -rf
```

### Debug Commands

```bash
# Verbose Conan output
conan create . --version=3.3.2 --build=missing -v

# Show package information
conan list "sparetools-openssl/*" --format=json | jq

# Show cache location
conan cache path "sparetools-openssl/3.3.2:*"

# Show profile contents
conan profile show packages/sparetools-openssl-tools/profiles/base/linux-gcc11

# Show package dependencies
conan graph info --requires=sparetools-openssl/3.3.2
```

### Test Logs

Save test logs for debugging:

```bash
# Run test with logging
conan create . \
  --version=3.3.2 \
  --build=missing \
  2>&1 | tee build.log

# Analyze log
grep -i "error\|warning\|failed" build.log
```

---

## Test Automation

### Continuous Testing Script

```bash
#!/bin/bash
# continuous-test.sh

set -e

while true; do
  echo "🔄 Running continuous tests..."
  
  # Run test suite
  bash test-full-chain.sh
  
  # Wait before next run
  echo "✅ Tests passed. Waiting 60s..."
  sleep 60
done
```

### Pre-Commit Testing

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🧪 Running pre-commit tests..."

# Quick syntax check
find packages -name "*.py" -exec python -m py_compile {} \;

# Validate conanfiles
find packages -name "conanfile.py" -exec conan graph info {} \; || exit 1

echo "✅ Pre-commit tests passed"
```

---

## Best Practices

1. **Always test locally before pushing**
   ```bash
   conan create . --version=3.3.2 --build=missing
   conan test test_package --requires=sparetools-openssl/3.3.2
   ```

2. **Test with multiple profiles**
   - Test with FIPS enabled
   - Test with different build methods
   - Test on multiple platforms

3. **Validate dependencies**
   - Export foundation packages first
   - Verify profile paths are correct
   - Check Conan version compatibility

4. **Use verbose logging for debugging**
   ```bash
   conan create . --version=3.3.2 --build=missing -v
   ```

5. **Test security scans**
   ```bash
   trivy fs --security-checks vuln ~/.conan2/p/spareto*openssl*/p
   ```

---

## Additional Resources

- [Conan 2.x Testing Documentation](https://docs.conan.io/2/creating_packages/testing_packages.html)
- [SpareTools Profiles Guide](../packages/sparetools-openssl-tools/profiles/README.md)
- [CI/CD Operations Guide](CI-CD-OPERATIONS-GUIDE.md)
- [Troubleshooting Guide](CI-CD-TROUBLESHOOTING.md)
