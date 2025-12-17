# ESP32 Consumer Integration Guide

## Overview

This guide provides detailed instructions for integrating ESP32 projects with the SpareTools ecosystem. The ESP32 consumer enables seamless development, testing, and deployment of ESP32-based embedded systems.

## Prerequisites

- Python 3.8+ (SpareTools provides 3.12.7 hermetically)
- Git
- Internet connection for dependency downloads
- ESP32 development board (optional, simulation available)

## Integration Steps

### 1. Add SpareTools Submodule

```bash
git submodule add https://github.com/sparesparrow/sparetools.git .sparetools
git submodule update --init --recursive
```

Update `.gitignore`:
```
.sparetools/
```

### 2. Update Project Configuration

#### pyproject.toml
Ensure SpareTools paths are excluded from formatting/linting:

```toml
[tool.black]
extend-exclude = '''
/(
  \.sparetools
)/
'''

[tool.isort]
skip = [".platformio", ".pio", ".sparetools", "build", "dist"]
```

#### GitHub Workflows
Update CI/CD workflows to use SpareTools reusable workflows:

```yaml
jobs:
  quality:
    uses: ./.sparetools/.github/workflows/reusable/esp32-quality.yml
    # ... configuration

  test:
    uses: ./.sparetools/.github/workflows/reusable/esp32-testing.yml
    # ... configuration

  build:
    uses: ./.sparetools/.github/workflows/reusable/esp32-build.yml
    # ... configuration
```

### 3. Update Conan Configuration

```python
class MyESP32ProjectConan(ConanFile):
    python_requires = "sparetools-base/2.0.0"

    def build_requirements(self):
        self.tool_requires("sparetools-cpython/3.12.7")
        self.tool_requires("sparetools-bootstrap/2.0.0")
        self.tool_requires("sparetools-test-harness/2.0.0")
        self.tool_requires("sparetools-shared-dev-tools/2.0.0")
```

### 4. Update Development Scripts

#### bootstrap.py
Modify to delegate to SpareTools:

```python
def setup_esp32_tools(self) -> bool:
    try:
        if self.sparetools_python and self.sparetools_python.exists():
            cmd = [
                str(self.sparetools_python),
                "-m", "sparetools_shared_dev_tools.cli",
                "bootstrap", "esp32"
            ]
            self.run_command(cmd)
            return True
    except ImportError:
        pass

    # Fallback implementation
    return self._setup_platformio_fallback()
```

#### test_runner.py
Delegate test execution to SpareTools:

```python
def run_unit_tests(self, parallel=True, coverage=True):
    if self.sparetools_runner:
        return self.sparetools_runner.run_unit_tests(parallel, coverage)
    # Fallback implementation
```

### 5. Update Test Configuration

#### pytest Integration
Use SpareTools ESP32 test fixtures:

```python
import pytest

def test_nfc_functionality(esp32_hardware_harness):
    """Test NFC functionality with hardware simulation."""
    harness = esp32_hardware_harness

    # Simulate NFC communication
    expected = b"hello_nfc"
    actual = b"hello_nfc"  # Simulated response

    assert harness.verify_nfc_communication(expected, actual)

@pytest.fixture(autouse=True)
def esp32_setup_test_environment():
    """Auto-setup ESP32 test environment."""
    # Environment setup handled by SpareTools
    yield
```

#### Hardware Simulation
Configure hardware simulation in tests:

```python
from sparetools_test_harness import ESP32TestHarness

def test_rf_transmission():
    harness = ESP32TestHarness(hardware_simulation=True)

    # Test RF transmission simulation
    result = harness.verify_rf_transmission(
        frequency=433920000,  # 433.92 MHz
        data=b"test_data"
    )
    assert result
```

## Project Templates

Use SpareTools ESP32 templates as starting points:

- `~/.sparetools/templates/esp32/conanfile.py.template`
- `~/.sparetools/templates/esp32/CMakeLists.txt.template`
- `~/.sparetools/templates/esp32/platformio.ini.template`
- `~/.sparetools/templates/esp32/pyproject.toml.template`

## Development Workflow

### Local Development

1. **Bootstrap Environment**
   ```bash
   python scripts/bootstrap.py
   ```

2. **Build Firmware**
   ```bash
   pio run -e esp32dev
   ```

3. **Run Tests**
   ```bash
   python scripts/test_runner.py
   ```

4. **Flash Device** (optional)
   ```bash
   pio run -e esp32dev -t upload
   ```

### CI/CD Pipeline

The integrated CI/CD pipeline includes:

1. **Quality Checks**: Linting, formatting, type checking
2. **Unit Tests**: C++ unit tests with hardware simulation
3. **Integration Tests**: Python integration tests
4. **ESP32 Builds**: Multi-board firmware compilation
5. **Security Scanning**: Vulnerability and license checks

### Testing Strategy

#### Unit Tests (C++)
- Test individual modules without hardware
- Use GoogleTest framework
- Run on host system (Linux/Windows/macOS)

#### Integration Tests (Python)
- Test module interactions
- Hardware simulation available
- pytest framework with custom fixtures

#### Hardware Tests
- Require physical ESP32 device
- Optional in CI (simulation preferred)
- Marked with `hardware` marker

## Configuration Reference

### ESP32 Board Configurations

Common board configurations in `platformio.ini`:

```ini
[env:esp32dev]
board = esp32dev
build_flags = -Ofast -D BOARD_NAME="esp32dev"

[env:esp32-s3-devkitc-1]
board = esp32-s3-devkitc-1
build_flags = -Ofast -D BOARD_NAME="esp32-s3-devkitc-1"
```

### Environment Variables

SpareTools sets these environment variables:

- `ESP32_PROJECT_NAME`: Project name
- `ESP32_PROJECT_TYPE`: Project type (embedded/esp32)
- `PLATFORMIO_CORE_DIR`: PlatformIO core directory
- `ESP32_HARDWARE_SIMULATION`: Hardware simulation flag

## Troubleshooting

### Common Issues

#### Import Errors
```
ImportError: No module named 'sparetools_*'
```
**Solution**: Ensure `.sparetools` submodule is initialized:
```bash
git submodule update --init --recursive
```

#### PlatformIO Not Found
```
pio: command not found
```
**Solution**: Run bootstrap to install PlatformIO:
```bash
python scripts/bootstrap.py
```

#### Hardware Simulation Fails
**Solution**: Check Python path includes SpareTools:
```bash
export PYTHONPATH="$PWD/.sparetools:$PYTHONPATH"
```

### Debug Mode

Enable debug logging:
```bash
export SPARETOOLS_DEBUG=1
python scripts/bootstrap.py --verbose
```

## Migration from Standalone ESP32 Projects

When migrating existing ESP32 projects to SpareTools:

1. **Backup Project**: Create a backup before migration
2. **Add Submodule**: Follow integration steps above
3. **Update Scripts**: Modify bootstrap.py and test_runner.py
4. **Update Workflows**: Change to SpareTools reusable workflows
5. **Test Integration**: Run full test suite to verify
6. **Update Documentation**: Reference SpareTools in README

## Best Practices

### Code Organization
- Keep ESP32-specific code in `src/` directory
- Place test files in `test/` directory
- Use `test_harness/` for simulation components
- Store scripts in `scripts/` directory

### Testing
- Write unit tests for all C++ modules
- Include hardware simulation tests
- Use descriptive test names
- Mark hardware-dependent tests appropriately

### CI/CD
- Use matrix builds for multiple ESP32 boards
- Enable caching for faster builds
- Include security scanning in pipelines
- Generate artifacts for firmware releases

### Documentation
- Keep README updated with SpareTools integration
- Document custom board configurations
- Include troubleshooting guides
- Reference SpareTools documentation

## Support

For ESP32 consumer-specific issues:
- Check SpareTools ESP32 documentation
- Review NucleusESP32 as reference implementation
- Open issues in SpareTools repository for framework issues
- Open issues in project repository for project-specific issues