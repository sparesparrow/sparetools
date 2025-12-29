# NucleusESP32 Test Suite

This directory contains the test suite for NucleusESP32, following OMS project patterns.

## Structure

Following the pattern from `oms-dev/Src/Tests/OmsUnitTests/`:

```
src/Tests/
├── NucleusUnitTests/      # C++ unit tests (similar to OmsUnitTests/)
│   ├── main.cpp          # Test entry point
│   ├── pch.h             # Precompiled header
│   ├── pch.cpp           # Precompiled header implementation
│   ├── NfcModuleTests.cpp
│   ├── RfModuleTests.cpp
│   ├── IrModuleTests.cpp
│   └── DataProcessingTests.cpp
└── CommonMocks/          # Common mock objects (similar to oms-dev/CommonMocks/)
    ├── CommonMocks.h
    └── CommonMocks.cpp
```

## Test Environment

### Python Test Environment

Following the `ngapy-dev` pattern, the Python test environment is provided by **SpareTools**:

- **sparetools-cpython/3.12.7**: Bundled Python 3.12.7 runtime
- **sparetools-test-harness/2.0.0**: Test harness with ngapy-compatible API
- **sparetools-shared-dev-tools/2.0.0**: Shared development utilities

This is configured in `conanfile.py` via `build_requirements()`.

### C++ Unit Tests

C++ unit tests use GoogleTest and are built via CMake. Tests are located in `src/Tests/NucleusUnitTests/` following the `oms-dev` pattern.

## Running Tests

### C++ Unit Tests

```bash
# Build and run unit tests
./run_nucleus_unit_tests.sh

# Or on Windows
run_nucleus_unit_tests.bat
```

### Python Integration Tests

```bash
# Run Python integration tests (requires SpareTools environment)
python test_harness/run_nucleus_unit_tests.py
```

### Using Conan

```bash
# Install dependencies
conan install . --build=missing

# Build tests
cmake --preset conan-release
cmake --build build-release --target unit_tests

# Run tests
./build-release/unit_tests
```

## Test Patterns

### Unit Tests (C++)

Unit tests follow the `oms-dev` pattern:
- Located in `src/Tests/NucleusUnitTests/`
- Use GoogleTest framework
- Include precompiled headers (`pch.h`)
- Use common mocks from `CommonMocks/`

### Integration Tests (Python)

Integration tests follow the `ngapy-dev` pattern:
- Located in `test_harness/`
- Use SpareTools test harness (ngapy-compatible API)
- Python environment provided by SpareTools
- Generate JUnit XML reports

## Component Decoupling

Following `oms-dev` and `ngaims-icd-dev` patterns:
- Components are decoupled and testable independently
- Mock interfaces for hardware dependencies
- Clear separation between unit and integration tests

## Test Coverage

- **Unit Tests**: Test individual modules in isolation
- **Integration Tests**: Test module interactions and hardware integration
- **Hardware Tests**: Test actual hardware interactions (when available)

## Dependencies

### Build Dependencies (via Conan)
- `gtest/1.14.0`: Google Test framework
- `sparetools-cpython/3.12.7`: Python runtime
- `sparetools-test-harness/2.0.0`: Test harness
- `sparetools-shared-dev-tools/2.0.0`: Development tools

## References

- OMS Unit Tests: `/home/sparrow/Desktop/oms/oms-dev/Src/Tests/OmsUnitTests/`
- Ngapy Test Harness: `/home/sparrow/Desktop/oms/ngapy-dev/test_harness/`
- SpareTools: `~/sparetools`
