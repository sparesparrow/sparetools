# SpareTools OpenSSL Test Package

This directory contains comprehensive tests for the OpenSSL package built with SpareTools.

## Test Files

### 1. `test_openssl.c` - Basic Functionality Tests

Tests fundamental OpenSSL operations:
- OpenSSL initialization and library loading
- Version information reporting
- SHA-256 digest algorithm availability
- Basic hashing operation

**Run:**
```bash
conan test test_package sparetools-openssl/3.3.2@
```

### 2. `test_provider_ordering.c` - Provider Tests

Tests OpenSSL 3.x provider system and algorithm availability:

**Features:**
- Default provider availability
- Legacy provider loading and operation
- Provider ordering and preference
- Algorithm availability across providers
- Modern algorithms (SHA-256, SHA-512, AES-256-GCM, ChaCha20-Poly1305)

**Tested Algorithms:**
- Digest: SHA-256, SHA-384, SHA-512, SHA3-256, SHA3-512
- Ciphers: AES-128-CBC, AES-256-CBC, AES-256-GCM, ChaCha20-Poly1305

**Run:**
```bash
# Basic test with provider tests
conan test test_package sparetools-openssl/3.3.2@ \
  -o "*:test_provider=default"

# Test with legacy provider
conan test test_package sparetools-openssl/3.3.2@ \
  -o "*:test_provider=all"
```

### 3. `test_fips_smoke.c` - FIPS Smoke Tests

Validates FIPS-approved cryptographic operations:

**Features:**
- FIPS mode detection
- FIPS-approved algorithm availability
- SHA-256 hash operation with test vectors
- AES-256-CBC encryption/decryption
- Round-trip encryption verification
- Basic FIPS compliance checks

**FIPS-Approved Algorithms:**
- Digests: SHA-256, SHA-384, SHA-512, SHA3-256, SHA3-384
- Ciphers: AES-128-CBC, AES-192-CBC, AES-256-CBC, AES-128-GCM, AES-256-GCM

**Run:**
```bash
# Test with FIPS validation
conan test test_package sparetools-openssl/3.3.2@ \
  -o "*:test_fips=True"

# Both provider and FIPS tests
conan test test_package sparetools-openssl/3.3.2@ \
  -o "*:test_provider=default" \
  -o "*:test_fips=True"
```

## Test Configuration Options

The test package supports the following options:

### `test_provider`
- `default` (default): Run provider ordering tests with default provider
- `legacy`: Test legacy provider compatibility
- `all`: Test both default and legacy providers

### `test_fips`
- `False` (default): Skip FIPS smoke tests
- `True`: Run FIPS smoke tests

## Usage Examples

### Run all tests with default configuration:
```bash
cd packages/sparetools-openssl
conan test test_package sparetools-openssl/3.3.2@
```

### Run with provider testing enabled:
```bash
conan test test_package sparetools-openssl/3.3.2@ \
  -o "*:test_provider=default"
```

### Run with FIPS testing enabled:
```bash
conan test test_package sparetools-openssl/3.3.2@ \
  -o "*:test_fips=True"
```

### Run with all tests enabled:
```bash
conan test test_package sparetools-openssl/3.3.2@ \
  -o "*:test_provider=all" \
  -o "*:test_fips=True"
```

### Run with specific profile and all tests:
```bash
conan test test_package sparetools-openssl/3.3.2@ \
  -pr:b ../sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b ../sparetools-openssl-tools/profiles/features/fips-enabled \
  -o "*:test_provider=default" \
  -o "*:test_fips=True"
```

## Building Manually

### Build all test executables:
```bash
mkdir build && cd build
cmake ..
cmake --build .
```

### Run individual tests:
```bash
./test_openssl
./test_provider_ordering
./test_fips_smoke
```

### Run via ctest:
```bash
ctest --output-on-failure
```

## Test Output Examples

### Successful provider test:
```
=================================
OpenSSL Provider Ordering Tests
=================================

Testing default provider availability...
✓ SHA2-256 available from default provider
✓ AES-256-CBC available from default provider

...

=================================
✅ All provider tests PASSED!
```

### Successful FIPS test:
```
===================================
OpenSSL FIPS Smoke Tests
===================================

Testing FIPS mode...
⚠ FIPS mode is DISABLED (build may not include FIPS)

Testing FIPS-approved algorithms...
✓ SHA2-256 available
✓ SHA2-384 available
...
✓ All 5 FIPS-approved digests available

...

===================================
✅ All FIPS smoke tests PASSED!
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run Provider Tests
  run: |
    conan test test_package sparetools-openssl/3.3.2@ \
      -o "*:test_provider=default"

- name: Run FIPS Tests
  run: |
    conan test test_package sparetools-openssl/3.3.2@ \
      -o "*:test_fips=True"
```

## Requirements

- OpenSSL 3.1.0 or later (provider system required)
- CMake 3.15+
- C compiler (gcc, clang, or MSVC)
- Conan 2.0+

## Known Issues

### FIPS tests on non-FIPS builds
- FIPS smoke tests will pass if FIPS is not enabled (non-fatal)
- Set `-o "*:test_fips=True"` only when building with FIPS profile

### Legacy provider not available
- Legacy provider test reports warning if not available
- This is expected on default builds

## Troubleshooting

### Test fails: "Provider X not available"
- Ensure the correct profile is used when building OpenSSL
- Check if the feature profile (FIPS, etc.) is applied

### CMake configuration fails
- Ensure `find_package(OpenSSL)` can find the Conan-generated files
- Check that CMakeDeps and CMakeToolchain generators are enabled

### Test executables not found
- Run `cmake --build .` in the build directory
- Verify build completed successfully

## Adding New Tests

To add a new test:

1. Create `test_*.c` file with test code
2. Add executable to `CMakeLists.txt`
3. Add test case with `add_test()`
4. Update test option in `conanfile.py` if needed
5. Document in this README

Example:
```cmake
# CMakeLists.txt
add_executable(test_new test_new.c)
target_link_libraries(test_new OpenSSL::SSL OpenSSL::Crypto)
add_test(NAME new_test COMMAND test_new)
```

## References

- [OpenSSL Provider Documentation](https://www.openssl.org/docs/manmaster/man7/provider.html)
- [OpenSSL FIPS Module](https://www.openssl.org/docs/manmaster/man7/fips.html)
- [Conan Test Package](https://docs.conan.io/en/conan_2_0/reference/conanfile_py.html#test)
