# Unified Testing Environment - Quick Reference

## One-Command Setup

```bash
# Download and run bootstrap
curl -O https://raw.githubusercontent.com/sparesparrow/sparetools/main/scripts/bootstrap.py
python bootstrap.py --project-type generic

# Activate environment
source .venv/bin/activate

# Run tests
python scripts/test_runner.py
```

## Project Types

| Type | Dependencies | Use Case |
|------|--------------|----------|
| `generic` | pytest, black, ruff, mypy | General Python projects |
| `mia` | + python-can, elm327-emulator | MIA automotive projects |
| `android` | + adb-shell, python-adb | Android development |
| `mcp` | + mcp, anthropic | MCP/AI integration projects |

## Test Harness API (ngapy-compatible)

```python
from sparetools_test_harness import SpareToolsTestHarness

th = SpareToolsTestHarness()

# Basic verification
th.verify(actual, expected, msg="Description", test_num=1)

# Tolerance verification
th.verify_tol(actual, expected, tolerance, msg="Description", test_num=2)

# Range verification
th.verify_range(actual, min_value, max_value, msg="Description", test_num=3)

# String verification
th.verify_string(actual, expected, case_sensitive=True, msg="Description", test_num=4)
```

## Test Runner Commands

```bash
# Run all tests
python scripts/test_runner.py

# Run only unit tests
python scripts/test_runner.py --unit-only

# Run only integration tests
python scripts/test_runner.py --integration-only

# Run only linters
python scripts/test_runner.py --lint-only

# Include security scan
python scripts/test_runner.py --security
```

## Bootstrap Options

```bash
# Generic project
python bootstrap.py --project-type generic

# MIA project
python bootstrap.py --project-type mia

# Development mode (local SpareTools repo)
python bootstrap.py --project-type generic --sparetools-repo /path/to/sparetools
```

## File Structure After Bootstrap

```
your-project/
├── .venv/                    # Virtual environment (bundled Python)
├── .conan/                    # Conan cache
├── pytest.ini                 # Test configuration
├── .ruff.toml                 # Linter configuration
├── test-results/              # Test output
│   ├── junit-unit.xml
│   ├── junit-integration.xml
│   ├── coverage/
│   └── summary.json
├── test/
│   ├── unit/
│   └── integration/
└── scripts/
    └── test_runner.py
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Bootstrap SpareTools
        run: |
          curl -O https://raw.githubusercontent.com/sparesparrow/sparetools/main/scripts/bootstrap.py
          python bootstrap.py --project-type generic
      - name: Run tests
        run: |
          source .venv/bin/activate
          python scripts/test_runner.py
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: test-results/
```

## Conan Integration

### In your conanfile.py

```python
from conan import ConanFile

class MyProjectConan(ConanFile):
    tool_requires = (
        "sparetools-cpython/3.12.7",      # Bundled Python
        "sparetools-test-harness/2.0.0",  # Test framework
    )
    python_requires = "sparetools-base/2.0.0"
```

## Troubleshooting

### Python not found
```bash
# Check Conan cache
conan cache path sparetools-cpython/3.12.7

# Reinstall bundled Python
conan install --tool-requires=sparetools-cpython/3.12.7 --build=missing
```

### Test harness import error
```bash
# Install test harness
conan install --requires=sparetools-test-harness/2.0.0 --build=missing

# Check PYTHONPATH
echo $PYTHONPATH
```

### Bootstrap fails
```bash
# Check Conan installation
conan --version

# Try with local repo
python bootstrap.py --project-type generic --sparetools-repo /path/to/sparetools
```

## Key Features

✅ **Bundled CPython 3.12.7** - No system Python required
✅ **ngapy-compatible API** - Familiar verification methods
✅ **JUnit XML output** - CI/CD integration
✅ **Parallel execution** - Faster test runs
✅ **Security scanning** - Trivy integration
✅ **Cross-platform** - Linux, macOS, Windows

## Links

- [Full Documentation](UNIFIED-TESTING-ENVIRONMENT.md)
- [Improvements Summary](UNIFIED-TESTING-IMPROVEMENTS.md)
- [SpareTools Main README](../README.md)
