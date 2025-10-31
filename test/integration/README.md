# SpareTools Integration Test Suite

## Overview

This directory contains integration tests that validate the cooperation between all SpareTools packages in the v2.0.0 ecosystem.

## Test Philosophy

**Integration over Isolation**: While unit tests verify individual components in isolation, integration tests validate that the entire ecosystem works together as designed.

### What We Test

1. **Package Dependency Resolution** - Ensures Conan correctly resolves all dependencies
2. **Bundled Python Runtime Usage** - Validates builds use `sparetools-cpython/3.12.7` not system Python
3. **Cross-Package Utility Access** - Tests that utilities from `sparetools-base` are accessible
4. **Security Gates Integration** - Validates Trivy/Syft/FIPS tools are integrated
5. **Zero-Copy Pattern** - Tests symlink-based deployment functionality
6. **Profile Composition** - Validates 15 composable profiles work correctly
7. **Cloudsmith Availability** - Tests packages are uploaded and accessible from registry

## Test Structure

```
test/integration/
├── README.md (this file)
├── test_package_cooperation.py (main integration test)
└── fixtures/ (test data, if needed)
```

## Running Tests

### Quick Start

```bash
# From workspace root
cd /home/sparrow/sparetools

# Run integration tests
python3 test/integration/test_package_cooperation.py
```

### Prerequisites

1. **Build all packages first** (in dependency order):
```bash
conan create packages/sparetools-base --version=2.0.0
conan create packages/sparetools-cpython --version=3.12.7
conan create packages/sparetools-shared-dev-tools --version=2.0.0
conan create packages/sparetools-bootstrap --version=2.0.0
conan create packages/sparetools-openssl-tools --version=2.0.0
conan create packages/sparetools-openssl --version=3.3.2 --build=missing
```

2. **Configure Conan remotes**:
```bash
conan remote add sparesparrow-conan \
  https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/ --force
```

### Test Output

Tests provide color-coded output:
- 🔵 **BLUE** - Info messages
- 🟢 **GREEN** - Successful tests
- 🔴 **RED** - Failed tests
- 🟡 **YELLOW** - Warnings

Example output:
```
================================================================================
SpareTools Integration Test Suite
================================================================================

1. Testing Package Existence
INFO: Testing existence of sparetools-base/2.0.0
SUCCESS: ✓ sparetools-base/2.0.0 found
...

================================================================================
Test Results Summary
================================================================================
✓ PASS - Package sparetools-base/2.0.0 exists
✓ PASS - Package sparetools-cpython/3.12.7 exists
...
Total: 15/15 tests passed

✓ ALL TESTS PASSED
```

## Test Details

### 1. Package Existence Tests

Validates that all packages are built and available in local Conan cache:
- `sparetools-base/2.0.0`
- `sparetools-cpython/3.12.7`
- `sparetools-shared-dev-tools/2.0.0`
- `sparetools-bootstrap/2.0.0`
- `sparetools-openssl-tools/2.0.0`
- `sparetools-openssl/3.3.2`

### 2. Dependency Resolution Tests

Creates dependency graphs and validates:
- `sparetools-openssl` correctly depends on:
  - `sparetools-base/2.0.0` (python_requires)
  - `sparetools-openssl-tools/2.0.0` (tool_requires)
  - `sparetools-cpython/3.12.7` (tool_requires)

### 3. Python Runtime Usage Test

Creates a temporary test consumer that:
1. Declares `tool_requires = "sparetools-cpython/3.12.7"`
2. Builds the package
3. Checks `sys.executable` to verify it uses bundled Python
4. Validates path contains `.conan2` (Conan package cache)

**Expected Result**: Builds use `/home/sparrow/.conan2/.../sparetools-cpython/.../bin/python3.12` not `/usr/bin/python3`

### 4. Security Gates Integration Test

Validates that `security-gates.py` from `sparetools-base` is:
- Included in the package
- Accessible to dependent packages
- Provides functions: `run_trivy_scan()`, `generate_sbom()`

### 5. Zero-Copy Helpers Test

Validates that `symlink-helpers.py` from `sparetools-base` is:
- Included in the package
- Provides functions: `create_zero_copy_deployment()`, `verify_zero_copy_integrity()`

### 6. Profile Composition Test

Validates profile structure in `packages/sparetools-openssl-tools/profiles/`:
- `base/` - 6 platform profiles (linux-gcc11, darwin-clang, etc.)
- `build-methods/` - 4 method profiles (perl-configure, cmake-build, etc.)
- `features/` - 5 feature profiles (fips-enabled, shared-libs, etc.)

### 7. Cloudsmith Availability Test

Attempts to:
1. Add Cloudsmith remote
2. Search for `sparetools-*` packages
3. Verify packages are uploaded and accessible

**Note**: This test may fail if packages haven't been uploaded yet.

### 8. Full-Stack Build Test (Optional)

Builds `sparetools-openssl/3.3.2` from scratch and validates:
- All dependencies are resolved
- Build uses bundled Python
- Security gates run during build
- Package is created successfully

**Note**: Commented out by default as it takes 5-10 minutes.

## CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/integration-tests.yml`:

```yaml
name: Integration Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Install Conan
        run: |
          python -m pip install --upgrade pip
          python -m pip install conan==2.21.0
      
      - name: Build all packages
        run: |
          conan create packages/sparetools-base --version=2.0.0
          conan create packages/sparetools-cpython --version=3.12.7
          conan create packages/sparetools-shared-dev-tools --version=2.0.0
          conan create packages/sparetools-bootstrap --version=2.0.0
          conan create packages/sparetools-openssl-tools --version=2.0.0
          conan create packages/sparetools-openssl --version=3.3.2 --build=missing
      
      - name: Run integration tests
        run: python3 test/integration/test_package_cooperation.py
```

## Debugging Failed Tests

### Package Not Found

```bash
# Check local Conan cache
conan list "sparetools-*"

# Rebuild missing package
conan create packages/sparetools-<name> --version=<version> --build=missing
```

### Dependency Resolution Failed

```bash
# Inspect dependency graph
conan graph info --requires=sparetools-openssl/3.3.2 --format=json

# Check for version mismatches
grep -r "python_requires" packages/*/conanfile.py
grep -r "tool_requires" packages/*/conanfile.py
```

### Python Runtime Not Used

```bash
# Check if sparetools-cpython is built
conan list "sparetools-cpython/3.12.7:*"

# Check CPython staging directory
ls -la /tmp/cpython-3.12.7-staging/ || echo "Staging directory missing"

# Set custom staging path
export CPYTHON_STAGING_DIR=/custom/path
conan create packages/sparetools-cpython --version=3.12.7
```

### Cloudsmith Upload Failed

```bash
# Check authentication
conan remote login sparesparrow-conan sparesparrow --password "$CLOUDSMITH_API_KEY"

# Upload packages
conan upload "sparetools-*/*" -r sparesparrow-conan --confirm
```

## Best Practices

### 1. Test Order Matters

Always run tests in this order:
1. Package existence (fast, validates setup)
2. Dependency resolution (fast, validates conanfile.py)
3. Python runtime usage (medium, validates toolchain)
4. Integration features (medium, validates functionality)
5. Full-stack build (slow, validates end-to-end)

### 2. Fail Fast

Tests are ordered to fail fast on fundamental issues before wasting time on complex builds.

### 3. Isolation

Each test creates its own temporary directories and cleans up afterwards.

### 4. Parallel Execution

Tests can run in parallel (except full-stack build):
```bash
# Run tests in parallel (if you add pytest)
pytest test/integration/ -n auto
```

## Common Integration Test Patterns

### Pattern 1: Test Consumer

Create a temporary Conan consumer package to test functionality:

```python
test_dir = tempfile.mkdtemp(prefix="sparetools_test_")
conanfile = Path(test_dir) / "conanfile.py"
conanfile.write_text('''
from conan import ConanFile

class TestConsumer(ConanFile):
    requires = "sparetools-openssl/3.3.2"
    
    def build(self):
        # Test functionality here
        self.output.info("Testing...")
''')
subprocess.run(f"conan create {test_dir}", shell=True)
```

### Pattern 2: Graph Inspection

Use `conan graph info` to validate dependency resolution:

```python
result = subprocess.run(
    "conan graph info --requires=pkg/version --format=json",
    capture_output=True,
    text=True,
    shell=True
)
graph = json.loads(result.stdout)
# Validate graph structure
```

### Pattern 3: Environment Validation

Check that build environment is set up correctly:

```python
def test_environment():
    result = subprocess.run(
        "conan install --requires=sparetools-cpython/3.12.7 && "
        "cat conanbuild.sh | grep PYTHONHOME",
        shell=True,
        capture_output=True,
        text=True
    )
    assert "sparetools-cpython" in result.stdout
```

## Extending Tests

### Adding New Tests

1. Add test method to `IntegrationTestSuite` class
2. Call from `run_all_tests()`
3. Update this README with test description

Example:

```python
def test_new_feature(self) -> bool:
    """Test description"""
    self.log("Testing new feature", "INFO")
    
    # Test implementation
    code, stdout, stderr = self.run_command("test command")
    
    if code == 0:
        self.results.append(("New feature", True, ""))
        self.log("✓ New feature works", "SUCCESS")
        return True
    else:
        self.results.append(("New feature", False, stderr))
        self.log("✗ New feature failed", "ERROR")
        return False
```

## Troubleshooting

### Issue: Tests time out

**Solution**: Increase timeout in `run_command()`:
```python
timeout=600  # 10 minutes
```

### Issue: Packages not found after build

**Solution**: Check Conan cache:
```bash
conan cache path sparetools-base/2.0.0
ls -la $(conan cache path sparetools-base/2.0.0)
```

### Issue: Python runtime not detected

**Solution**: Check environment setup:
```bash
conan install --requires=sparetools-cpython/3.12.7 --deployer=full_deploy
cat conanbuild.sh | grep -A5 "sparetools-cpython"
```

## References

- **Conan Documentation**: https://docs.conan.io/2/
- **pytest Documentation**: https://docs.pytest.org/
- **SpareTools CLAUDE.md**: Complete ecosystem documentation

## Support

For issues with integration tests:
1. Check this README
2. Review test output logs
3. Inspect Conan cache: `conan list "sparetools-*"`
4. Open issue on GitHub: https://github.com/sparesparrow/sparetools/issues
