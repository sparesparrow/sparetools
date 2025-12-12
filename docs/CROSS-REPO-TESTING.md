# Cross-Repository Dependency Resolution Testing

This document describes how to test cross-repository dependency resolution for sparetools packages.

## Overview

SpareTools packages are published to Cloudsmith and can be consumed by projects in other repositories (like MIA). This document explains how to test that dependency resolution works correctly across repositories.

## Prerequisites

- Conan 2.x installed: `pip install conan==2.21.0`
- Network access to Cloudsmith
- (Optional) Cloudsmith API key for private repositories

## Running Tests

### Automated Test Script

Run the cross-repo resolution test script:

```bash
python3 scripts/test-cross-repo-resolution.py
```

This script tests:

1. **Remote Configuration**: Verifies Cloudsmith remote can be added
2. **Package Discovery**: Tests searching for packages in remote
3. **Version Resolution**: Tests resolving specific versions
4. **Dependency Graph**: Tests building dependency graphs
5. **Build with Remote Dependencies**: Tests building with remote packages

### Manual Testing

#### 1. Configure Remote

```bash
conan remote add sparesparrow-conan \
  https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/ \
  --force
```

#### 2. Verify Remote

```bash
conan remote list
```

You should see `sparesparrow-conan` in the output.

#### 3. Search for Packages

```bash
conan search sparetools-openssl -r sparesparrow-conan
```

This should list available versions of `sparetools-openssl`.

#### 4. Test Dependency Resolution

Create a test `conanfile.py`:

```python
from conan import ConanFile

class TestConan(ConanFile):
    name = "test-consumer"
    version = "1.0.0"
    
    requires = [
        "sparetools-openssl/3.3.2",
    ]
```

Then test resolution:

```bash
conan graph explain conanfile.py
```

#### 5. Test Installation

```bash
conan install conanfile.py --build=missing
```

This should download and install `sparetools-openssl/3.3.2` from Cloudsmith.

## Test Scenarios

### Scenario 1: Basic Package Resolution

**Goal**: Verify packages can be resolved from remote

**Steps**:
1. Configure Cloudsmith remote
2. Search for `sparetools-openssl`
3. Verify version `3.3.2` is available

**Expected Result**: Package found and version available

### Scenario 2: Dependency Chain Resolution

**Goal**: Verify dependency chains resolve correctly

**Steps**:
1. Create consumer requiring `sparetools-openssl/3.3.2`
2. Run `conan graph explain`
3. Verify all dependencies resolve

**Expected Result**: Complete dependency graph resolved

### Scenario 3: Version Range Resolution

**Goal**: Test version range resolution

**Steps**:
1. Create consumer with version range: `sparetools-openssl/[>=3.3.0]`
2. Run dependency resolution
3. Verify correct version selected

**Expected Result**: Latest compatible version selected

### Scenario 4: Build with Remote Dependencies

**Goal**: Test building with remote dependencies

**Steps**:
1. Create consumer project
2. Install dependencies: `conan install . --build=missing`
3. Build project: `conan build .`

**Expected Result**: Project builds successfully with remote dependencies

## Troubleshooting

### Package Not Found

**Issue**: `conan search` doesn't find packages

**Solutions**:
1. Verify remote is configured: `conan remote list`
2. Check remote URL is correct
3. Verify packages are published to Cloudsmith
4. Check network connectivity

### Authentication Required

**Issue**: Authentication errors when accessing packages

**Solutions**:
1. Check if packages are private
2. Authenticate: `conan remote login sparesparrow-conan USERNAME --password API_KEY`
3. Verify API key has correct permissions

### Version Resolution Fails

**Issue**: Specific version not found

**Solutions**:
1. Verify version exists: `conan search sparetools-openssl -r sparesparrow-conan`
2. Check version format (should be `3.3.2`, not `v3.3.2`)
3. Try version range instead: `sparetools-openssl/[>=3.3.0]`

### Network Issues

**Issue**: Timeouts or connection errors

**Solutions**:
1. Check network connectivity
2. Verify Cloudsmith is accessible
3. Check firewall/proxy settings
4. Try with `--timeout` flag: `conan install . --timeout=300`

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Configure Conan Remote
  run: |
    conan remote add sparesparrow-conan \
      https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/ \
      --force

- name: Test Dependency Resolution
  run: |
    conan graph explain conanfile.py

- name: Install Dependencies
  run: |
    conan install . --build=missing
```

### Caching

Cache Conan cache directory in CI/CD:

```yaml
- name: Cache Conan
  uses: actions/cache@v4
  with:
    path: ~/.conan2
    key: conan-${{ runner.os }}-${{ hashFiles('conanfile.py') }}
```

## Best Practices

### 1. Pin Versions in Production

Use exact versions in production:

```python
requires = [
    "sparetools-openssl/3.3.2",  # Exact version
]
```

### 2. Use Version Ranges in Development

Use version ranges for flexibility:

```python
requires = [
    "sparetools-openssl/[>=3.3.0,<4.0.0]",  # Version range
]
```

### 3. Test Resolution Regularly

Run resolution tests:
- Before releases
- After dependency updates
- In CI/CD pipelines

### 4. Document Dependencies

Document all external dependencies and their sources in your project documentation.

## Related Documentation

- [MIA Integration Guide](MIA-INTEGRATION.md) - Integration guide for MIA
- [MIA Contributor Guide](MIA-CONTRIBUTOR-GUIDE.md) - Guide for contributors
- [Packages](PACKAGES.md) - Package documentation

## Test Script Reference

The test script `scripts/test-cross-repo-resolution.py` provides automated testing:

```bash
# Run all tests
python3 scripts/test-cross-repo-resolution.py

# Tests run:
# - Remote configuration
# - Package discovery
# - Version resolution
# - Dependency graph
# - Build with remote dependencies
```

## Support

For issues with cross-repo dependency resolution:

1. Check [MIA Integration Guide](MIA-INTEGRATION.md)
2. Review [CI/CD Troubleshooting](CI-CD-TROUBLESHOOTING.md)
3. Verify packages are published to Cloudsmith
4. Open an issue on GitHub

## Updates

This testing guide is maintained alongside the codebase. Last updated: 2025-12-03
