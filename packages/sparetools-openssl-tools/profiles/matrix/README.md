# OpenSSL Build Matrix

Complete build matrix for testing all platform/compiler/build-method/feature combinations.

## Full Build Matrix (36 combinations)

| Platform | Compiler | Build Method | Features | Profile Combination |
|----------|----------|--------------|----------|---------------------|
| Linux x86_64 | GCC 11 | Perl | Default | `base/linux-gcc11` + `build-methods/perl-configure` |
| Linux x86_64 | GCC 11 | Perl | FIPS | `base/linux-gcc11` + `build-methods/perl-configure` + `features/fips-enabled` |
| Linux x86_64 | GCC 11 | CMake | Shared | `base/linux-gcc11` + `build-methods/cmake-build` + `features/shared-libs` |
| Linux x86_64 | GCC 11 | Python | Performance | `base/linux-gcc11` + `build-methods/python-configure` + `features/performance` |
| Linux x86_64 | Clang 14 | Perl | Default | `base/linux-clang14` + `build-methods/perl-configure` |
| Linux x86_64 | Clang 14 | Perl | FIPS | `base/linux-clang14` + `build-methods/perl-configure` + `features/fips-enabled` |
| Linux ARM64 | GCC 11 | Autotools | Minimal | `base/linux-gcc11-arm64` + `build-methods/autotools` + `features/minimal` |
| Linux ARM64 | GCC 11 | Perl | Default | `base/linux-gcc11-arm64` + `build-methods/perl-configure` |
| Windows x86_64 | MSVC 2022 | Perl | Default | `base/windows-msvc2022` + `build-methods/perl-configure` |
| Windows x86_64 | MSVC 2022 | CMake | Shared | `base/windows-msvc2022` + `build-methods/cmake-build` + `features/shared-libs` |
| macOS x86_64 | Apple Clang | Perl | Default | `base/darwin-clang` + `build-methods/perl-configure` |
| macOS x86_64 | Apple Clang | CMake | Performance | `base/darwin-clang` + `build-methods/cmake-build` + `features/performance` |
| macOS ARM64 | Apple Clang | Perl | Default | `base/darwin-clang-arm64` + `build-methods/perl-configure` |
| macOS ARM64 | Apple Clang | Python | Shared | `base/darwin-clang-arm64` + `build-methods/python-configure` + `features/shared-libs` |

## Priority Matrix (12 Essential Combinations)

### Tier 1: Production-Critical (6 combinations)

Must pass for release:

1. **Linux GCC + Perl + Default**
   ```bash
   conan create . -pr:b base/linux-gcc11 -pr:b build-methods/perl-configure
   ```

2. **Linux GCC + Perl + FIPS**
   ```bash
   conan create . -pr:b base/linux-gcc11 -pr:b build-methods/perl-configure -pr:b features/fips-enabled
   ```

3. **Linux Clang + Perl + Default**
   ```bash
   conan create . -pr:b base/linux-clang14 -pr:b build-methods/perl-configure
   ```

4. **Windows MSVC + Perl + Default**
   ```bash
   conan create . -pr:b base/windows-msvc2022 -pr:b build-methods/perl-configure
   ```

5. **macOS x86_64 + Perl + Default**
   ```bash
   conan create . -pr:b base/darwin-clang -pr:b build-methods/perl-configure
   ```

6. **macOS ARM64 + Perl + Default**
   ```bash
   conan create . -pr:b base/darwin-clang-arm64 -pr:b build-methods/perl-configure
   ```

### Tier 2: Alternative Build Methods (3 combinations)

Important for flexibility:

7. **Linux GCC + CMake + Shared**
   ```bash
   conan create . -pr:b base/linux-gcc11 -pr:b build-methods/cmake-build -pr:b features/shared-libs
   ```

8. **Linux ARM64 + Autotools + Minimal**
   ```bash
   conan create . -pr:b base/linux-gcc11-arm64 -pr:b build-methods/autotools -pr:b features/minimal
   ```

9. **macOS ARM64 + Python + Performance**
   ```bash
   conan create . -pr:b base/darwin-clang-arm64 -pr:b build-methods/python-configure -pr:b features/performance
   ```

### Tier 3: Feature Validation (3 combinations)

Feature-specific testing:

10. **Linux GCC + Perl + Minimal**
    ```bash
    conan create . -pr:b base/linux-gcc11 -pr:b build-methods/perl-configure -pr:b features/minimal
    ```

11. **Windows MSVC + CMake + Shared**
    ```bash
    conan create . -pr:b base/windows-msvc2022 -pr:b build-methods/cmake-build -pr:b features/shared-libs
    ```

12. **macOS x86_64 + Perl + Performance**
    ```bash
    conan create . -pr:b base/darwin-clang -pr:b build-methods/perl-configure -pr:b features/performance
    ```

## GitHub Actions Matrix Configuration

### Complete Matrix (CI/CD)

```yaml
name: Build Matrix
on: [push, pull_request]

jobs:
  build-matrix:
    strategy:
      fail-fast: false
      matrix:
        include:
          # Tier 1: Production-Critical
          - os: ubuntu-22.04
            name: Linux-GCC11-Perl-Default
            base_profile: base/linux-gcc11
            method_profile: build-methods/perl-configure
            feature_profile: ""
          
          - os: ubuntu-22.04
            name: Linux-GCC11-Perl-FIPS
            base_profile: base/linux-gcc11
            method_profile: build-methods/perl-configure
            feature_profile: features/fips-enabled
          
          - os: ubuntu-22.04
            name: Linux-Clang14-Perl-Default
            base_profile: base/linux-clang14
            method_profile: build-methods/perl-configure
            feature_profile: ""
          
          - os: windows-2022
            name: Windows-MSVC2022-Perl-Default
            base_profile: base/windows-msvc2022
            method_profile: build-methods/perl-configure
            feature_profile: ""
          
          - os: macos-14
            name: macOS-x86_64-Perl-Default
            base_profile: base/darwin-clang
            method_profile: build-methods/perl-configure
            feature_profile: ""
          
          - os: macos-14
            name: macOS-ARM64-Perl-Default
            base_profile: base/darwin-clang-arm64
            method_profile: build-methods/perl-configure
            feature_profile: ""
          
          # Tier 2: Alternative Build Methods
          - os: ubuntu-22.04
            name: Linux-GCC11-CMake-Shared
            base_profile: base/linux-gcc11
            method_profile: build-methods/cmake-build
            feature_profile: features/shared-libs
          
          - os: ubuntu-22.04
            name: Linux-ARM64-Autotools-Minimal
            base_profile: base/linux-gcc11-arm64
            method_profile: build-methods/autotools
            feature_profile: features/minimal
          
          - os: macos-14
            name: macOS-ARM64-Python-Performance
            base_profile: base/darwin-clang-arm64
            method_profile: build-methods/python-configure
            feature_profile: features/performance
          
          # Tier 3: Feature Validation
          - os: ubuntu-22.04
            name: Linux-GCC11-Perl-Minimal
            base_profile: base/linux-gcc11
            method_profile: build-methods/perl-configure
            feature_profile: features/minimal
          
          - os: windows-2022
            name: Windows-MSVC2022-CMake-Shared
            base_profile: base/windows-msvc2022
            method_profile: build-methods/cmake-build
            feature_profile: features/shared-libs
          
          - os: macos-14
            name: macOS-x86_64-Perl-Performance
            base_profile: base/darwin-clang
            method_profile: build-methods/perl-configure
            feature_profile: features/performance
    
    runs-on: ${{ matrix.os }}
    name: ${{ matrix.name }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install Conan
        run: pip install conan==2.21.0
      
      - name: Detect Conan Profile
        run: conan profile detect --force
      
      - name: Build OpenSSL
        run: |
          PROFILES="-pr:b sparetools-openssl-tools/profiles/${{ matrix.base_profile }} -pr:b sparetools-openssl-tools/profiles/${{ matrix.method_profile }}"
          if [ -n "${{ matrix.feature_profile }}" ]; then
            PROFILES="$PROFILES -pr:b sparetools-openssl-tools/profiles/${{ matrix.feature_profile }}"
          fi
          conan create packages/sparetools-openssl --version=3.3.2 $PROFILES --build=missing
      
      - name: Test Package
        run: conan test packages/sparetools-openssl/test_package sparetools-openssl/3.3.2@
```

### Minimal Matrix (PR Validation)

```yaml
name: PR Validation
on: [pull_request]

jobs:
  pr-matrix:
    strategy:
      matrix:
        include:
          - os: ubuntu-22.04
            base: base/linux-gcc11
            method: build-methods/perl-configure
          - os: windows-2022
            base: base/windows-msvc2022
            method: build-methods/perl-configure
          - os: macos-14
            base: base/darwin-clang-arm64
            method: build-methods/perl-configure
    
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: |
          pip install conan==2.21.0
          conan profile detect --force
          conan create packages/sparetools-openssl --version=3.3.2 \
            -pr:b sparetools-openssl-tools/profiles/${{ matrix.base }} \
            -pr:b sparetools-openssl-tools/profiles/${{ matrix.method }} \
            --build=missing
```

## Parallel Execution Strategy

### VS Code Workspace Tasks

See `../../.vscode/tasks.json` for parallel build tasks:

```json
{
  "label": "Parallel Build Matrix",
  "dependsOn": [
    "Build: Linux-GCC11-Perl",
    "Build: Linux-Clang14-Perl",
    "Build: Linux-GCC11-CMake",
    "Build: Linux-ARM64-Autotools"
  ],
  "dependsOrder": "parallel"
}
```

### Local Parallel Testing

```bash
#!/bin/bash
# parallel-build-test.sh

PROFILES=(
  "base/linux-gcc11 build-methods/perl-configure"
  "base/linux-clang14 build-methods/perl-configure"
  "base/linux-gcc11 build-methods/cmake-build features/shared-libs"
  "base/linux-gcc11 build-methods/python-configure features/performance"
)

for profile_set in "${PROFILES[@]}"; do
  (
    echo "Building with: $profile_set"
    conan create packages/sparetools-openssl --version=3.3.2 \
      $(echo $profile_set | sed 's/ / -pr:b sparetools-openssl-tools\/profiles\//g' | sed 's/^/-pr:b sparetools-openssl-tools\/profiles\//') \
      --build=missing
  ) &
done

wait
echo "All parallel builds completed!"
```

## Performance Benchmarks

Expected build times (approximate):

| Configuration | Build Time | Notes |
|--------------|------------|-------|
| Perl Configure (default) | 5-8 min | Standard build |
| Perl Configure + FIPS | 6-10 min | Additional validation |
| CMake (if supported) | 4-7 min | Faster configuration |
| Autotools | 5-8 min | Similar to Perl |
| Python configure | 6-9 min | Experimental, may be slower |

Parallel builds (4 cores): ~15-20 minutes for full matrix

## Success Criteria

### Per-Build Criteria
- Build completes without errors
- All tests pass (`conan test`)
- Libraries generated (.a/.so/.dll)
- Headers installed
- Package can be consumed

### Matrix-Wide Criteria
- All Tier 1 builds pass (6/6)
- At least 80% of Tier 2 builds pass (2/3)
- At least 66% of Tier 3 builds pass (2/3)
- Zero CRITICAL security findings (Trivy)
- SBOM generated for each build

## Failure Analysis

### Common Failures

1. **Provider Build Order Issues (OpenSSL 3.x)**
   - Symptom: Errors in `providers/` compilation
   - Solution: Use Perl Configure method
   - Affected: Python configure (65% parity)

2. **CMake Not Supported**
   - Symptom: No `cmake/` directory
   - Solution: Auto-fallback to Perl Configure
   - Affected: OpenSSL < 3.6.0

3. **FIPS Module Missing**
   - Symptom: `enable-fips` fails
   - Solution: Use OpenSSL 3.0+ with FIPS module
   - Affected: FIPS builds

## Matrix Evolution

### Phase 1 (Current): Core Matrix
- 12 essential combinations
- 3 platforms × 2 compilers × 2 methods

### Phase 2 (Next): Extended Matrix
- +12 combinations (24 total)
- Add: FreeBSD, Android, iOS
- Add: More feature combinations

### Phase 3 (Future): Full Matrix
- +12 combinations (36 total)
- All permutations tested
- Performance benchmarking
- Cross-compilation validation

## Related Documentation

- [Profiles README](../README.md)
- [SpareTools OpenSSL Package](../../README.md)
- [GitHub Workflows](../../../../.github/workflows/)

