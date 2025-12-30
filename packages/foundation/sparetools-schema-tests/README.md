# SpareTools Schema Tests

Automated testing framework for FlatBuffers schema compatibility and validation.

## Overview

This package provides comprehensive testing tools for ensuring FlatBuffers schema compatibility across platforms, versions, and use cases. It includes both C++ and Python test suites that validate:

- Message serialization/deserialization
- Cross-platform compatibility (endianness)
- Schema evolution (forward/backward compatibility)
- Performance characteristics
- Error handling and fuzz testing

## Features

### Comprehensive Test Coverage

- **Cross-Platform Compatibility**: Ensures messages work across ESP32, Android, Linux, macOS
- **Schema Evolution**: Tests forward/backward compatibility when schemas change
- **Performance Benchmarking**: Measures serialization/deserialization speed
- **Error Handling**: Validates robust error handling with invalid/malformed data
- **Fuzz Testing**: Tests parsing with random data to find edge cases

### Multi-Language Support

- **C++ Tests**: High-performance native testing using Google Test
- **Python Tests**: Cross-platform scripting and validation
- **Integration Tests**: Combined C++/Python workflow testing

## Usage

### Running Tests

```bash
# Build and run all tests
conan create . --build=missing
conan test . --profile=linux-x86_64

# Run specific test suites
./bin/schema_tests --gtest_filter="*CrossPlatform*"
./bin/schema_tests --gtest_filter="*Performance*"

# Run Python tests
python tests/test_schema_compatibility.py
```

### CI/CD Integration

In GitHub Actions workflows:

```yaml
- name: Run Schema Compatibility Tests
  run: |
    conan create packages/foundation/sparetools-schema-tests --build=missing
    conan test packages/foundation/sparetools-schema-tests
```

## Test Categories

### Cross-Platform Tests

Ensures messages created on one platform parse correctly on others:

```cpp
TEST_F(CrossPlatformTest, BPMSerialization) {
    // Create message on "ESP32"
    auto bpm_update = sparetools::bpm::CreateBPMUpdate(builder_, ...);
    builder_.Finish(bpm_update);

    // Verify it parses on "Android/MCP"
    auto parsed = sparetools::bpm::GetBPMUpdate(builder_.GetBufferPointer());
    ASSERT_FLOAT_EQ(parsed->bpm(), expected_bpm_);
}
```

### Schema Evolution Tests

Tests compatibility when schemas are updated:

```cpp
TEST_F(SchemaEvolutionTest, ForwardCompatibility) {
    // Create message with new fields
    auto message = CreateMessageWithNewFields(builder_, ...);

    // Old parser should ignore new fields gracefully
    auto parsed = ParseWithOldSchema(message);
    ASSERT_TRUE(OldFieldsAreValid(parsed));
}
```

### Performance Tests

Benchmarks serialization and parsing performance:

```cpp
TEST_F(PerformanceTest, BenchmarkOperations) {
    benchmarkSerialization(10000);  // Time 10k serializations
    benchmarkDeserialization(buffers_);  // Time parsing
}
```

### Fuzz Tests

Tests parsing with random/invalid data:

```cpp
TEST_F(FuzzTest, RandomDataParsing) {
    auto random_data = generateRandomData(128);
    // Should not crash, should reject invalid data
    fuzzTestBPM(random_data.data(), random_data.size());
}
```

## Integration with SpareTools

### Automatic Schema Testing

The testing framework integrates with SpareTools workflows:

1. **Schema Changes**: Automatically detected in CI/CD
2. **Compatibility Validation**: Tests run against all platforms
3. **Performance Regression**: Performance tests catch slowdowns
4. **Cross-Version Testing**: Validates against previous schema versions

### Workflow Integration

```yaml
# In .github/workflows/schema-validation.yml
jobs:
  test-schemas:
    steps:
    - name: Run Schema Tests
      run: |
        conan create packages/foundation/sparetools-schema-tests
        conan test packages/foundation/sparetools-schema-tests \
          --profile=linux-x86_64 \
          --profile=esp32-xtensa \
          --profile=android-armv8
```

## Test Results

### Output Format

Tests produce detailed output showing:

```
SpareTools FlatBuffers Schema Compatibility Tests
=================================================
Testing BPM message serialization... ✅ PASSED
Testing GPIO command serialization... ✅ PASSED
Testing cross-platform endianness... ✅ PASSED
...

=================================================
TEST SUMMARY
=================================================
Total: 8/8 tests passed
🎉 All schema compatibility tests passed!
```

### Performance Metrics

Performance tests report timing information:

```
Serialization: 10000 messages in 1234 microseconds (0.123 μs per message)
Deserialization: 10000 messages in 567 microseconds (0.056 μs per message)
```

### JSON Results

Detailed results saved to `schema_test_results.json`:

```json
[
  {
    "test": "test_bpm_message_serialization",
    "passed": true,
    "timestamp": 1234567890000
  },
  {
    "test": "test_performance_comparison",
    "passed": true,
    "metrics": {
      "flatbuffers_avg": 0.000123,
      "json_avg": 0.001456
    }
  }
]
```

## Adding New Tests

### C++ Tests

1. **Extend Test Classes**:
```cpp
class MyCustomTest : public CrossPlatformTest {
protected:
    void testMyCustomLogic() {
        // Custom test implementation
    }
};
```

2. **Add Test Cases**:
```cpp
TEST_F(MyCustomTest, CustomLogic) {
    testMyCustomLogic();
}
```

### Python Tests

1. **Add Test Methods**:
```python
def test_my_custom_logic(self) -> bool:
    # Custom test implementation
    return True
```

2. **Register Tests**:
```python
tests = [
    # ... existing tests
    self.test_my_custom_logic,
]
```

## Dependencies

- `sparetools-protocols/1.0.0`: Schema definitions
- `flatbuffers/24.3.25`: Runtime library
- `gtest/1.14.0`: C++ testing framework
- `sparetools-flatbuffers/24.3.25`: Compiler tools

## Building

```bash
# Standard build
conan create . --build=missing

# With test execution
conan create . --build=missing
ctest --output-on-failure

# Cross-platform build
conan create . --profile=esp32-xtensa
conan create . --profile=android-armv8
```

## Best Practices

### Test Organization
- Group related tests in classes
- Use descriptive test names
- Include performance baselines
- Test error conditions thoroughly

### CI/CD Integration
- Run tests on all target platforms
- Fail builds on test failures
- Archive test results
- Monitor performance trends

### Schema Evolution
- Test compatibility when adding fields
- Validate default values
- Test with real device data
- Document breaking changes

## Troubleshooting

### Common Issues

**Tests Fail on Different Platforms**
- Check endianness handling
- Verify compiler compatibility
- Test with real device data

**Performance Regressions**
- Compare against baseline metrics
- Profile memory usage
- Check for memory leaks

**Schema Parsing Errors**
- Validate schema syntax with `flatc`
- Check include paths
- Verify namespace usage

### Debug Tools

```bash
# Validate schema syntax
flatc --schema --strict-json schema.fbs

# Inspect binary messages
flatc --json --raw-binary -o /dev/stdout binary_data.fbs

# Run specific tests
./bin/schema_tests --gtest_filter="*BPM*"
```

## Contributing

Follow SpareTools testing guidelines:
- Add tests for new schema changes
- Include performance benchmarks
- Test on all supported platforms
- Document test requirements