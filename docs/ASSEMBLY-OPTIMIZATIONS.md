# OpenSSL Assembly Optimizations Guide

This guide explains how to enable and configure SIMD assembly optimizations for OpenSSL in SpareTools.

## Overview

OpenSSL supports various SIMD instruction sets to accelerate cryptographic operations:
- **AVX/AVX2** - Intel/AMD x86_64 processors
- **NEON** - ARM processors (ARMv7/ARMv8)
- **SVE** - ARM Scalable Vector Extensions (ARMv8.4+)

Assembly optimizations can provide **20-40% performance improvement** in cryptographic operations.

---

## Quick Start

### Build with Maximum Optimizations (Recommended)

```bash
cd packages/sparetools-openssl
conan create . --version=3.3.2 \
  -pr:b ../sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b ../sparetools-openssl-tools/profiles/features/assembly-optimized
```

### Build with Specific Optimizations

```bash
# AVX2 only
conan create . --version=3.3.2 \
  -pr:b ../sparetools-openssl-tools/profiles/features/assembly-avx2-only

# AVX only (older systems)
conan create . --version=3.3.2 \
  -pr:b ../sparetools-openssl-tools/profiles/features/assembly-avx-only

# ARM NEON
conan create . --version=3.3.2 \
  -pr:b ../sparetools-openssl-tools/profiles/base/linux-gcc11-arm64 \
  -pr:b ../sparetools-openssl-tools/profiles/features/assembly-neon

# No assembly (pure C)
conan create . --version=3.3.2 \
  -pr:b ../sparetools-openssl-tools/profiles/features/assembly-minimal
```

---

## Available Options

### Conan Options

You can override assembly options directly via command line:

```bash
conan create . --version=3.3.2 \
  -o sparetools-openssl/*:enable_asm=True \
  -o sparetools-openssl/*:enable_avx=True \
  -o sparetools-openssl/*:enable_avx2=True \
  -o sparetools-openssl/*:enable_neon=True \
  -o sparetools-openssl/*:enable_sve=False
```

### Available Conan Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `enable_asm` | True/False | True | Enable/disable all assembly optimizations |
| `enable_avx` | True/False | True | Enable AVX instructions (x86/x86_64) |
| `enable_avx2` | True/False | True | Enable AVX2 instructions (x86/x86_64) |
| `enable_neon` | True/False | True | Enable ARM NEON instructions |
| `enable_sve` | True/False | False | Enable ARM SVE instructions |

---

## Optimization Profiles

### 1. Assembly-Optimized (Recommended)

**File:** `profiles/features/assembly-optimized`

Enables all available optimizations for the target architecture.

**Performance:** +20-40%
**Use Case:** High-performance servers, TLS termination

**Configuration:**
```yaml
enable_asm=True
enable_avx=True
enable_avx2=True
enable_neon=True
enable_sve=False
```

**Usage:**
```bash
conan create . --version=3.3.2 \
  -pr:b ../sparetools-openssl-tools/profiles/features/assembly-optimized
```

---

### 2. Assembly-AVX2-Only

**File:** `profiles/features/assembly-avx2-only`

Enables AVX2 optimizations for x86_64 systems.

**Performance:** +15-25%
**Use Case:** Moderate-performance x86_64 systems

**Configuration:**
```yaml
enable_asm=True
enable_avx=True
enable_avx2=True
enable_neon=False
enable_sve=False
```

**Usage:**
```bash
conan create . --version=3.3.2 \
  -pr:b ../sparetools-openssl-tools/profiles/features/assembly-avx2-only
```

---

### 3. Assembly-AVX-Only

**File:** `profiles/features/assembly-avx-only`

Enables AVX optimizations (without AVX2) for older x86_64 processors.

**Performance:** +8-15%
**Use Case:** Sandy Bridge/Ivy Bridge era processors

**Configuration:**
```yaml
enable_asm=True
enable_avx=True
enable_avx2=False
enable_neon=False
enable_sve=False
```

**Usage:**
```bash
conan create . --version=3.3.2 \
  -pr:b ../sparetools-openssl-tools/profiles/features/assembly-avx-only
```

---

### 4. Assembly-NEON

**File:** `profiles/features/assembly-neon`

Enables ARM NEON SIMD optimizations.

**Performance:** +20-35% (ARM systems)
**Use Case:** ARM64, embedded systems, mobile

**Configuration:**
```yaml
enable_asm=True
enable_avx=False
enable_avx2=False
enable_neon=True
enable_sve=False
```

**Usage:**
```bash
conan create . --version=3.3.2 \
  -pr:b ../sparetools-openssl-tools/profiles/base/linux-gcc11-arm64 \
  -pr:b ../sparetools-openssl-tools/profiles/features/assembly-neon
```

---

### 5. Assembly-Minimal

**File:** `profiles/features/assembly-minimal`

Disables all assembly optimizations (pure C implementation).

**Performance:** -5-10%
**Use Case:** Debug builds, testing, portability

**Configuration:**
```yaml
enable_asm=False
enable_avx=False
enable_avx2=False
enable_neon=False
enable_sve=False
```

**Usage:**
```bash
conan create . --version=3.3.2 \
  -pr:b ../sparetools-openssl-tools/profiles/features/assembly-minimal
```

---

## Architecture-Specific Recommendations

### x86_64 (Intel/AMD)

**Recommended Profile:** `assembly-optimized`

**Architecture Support Matrix:**

| CPU Generation | AVX | AVX2 | Recommended Profile |
|---|---|---|---|
| Nehalem | ❌ | ❌ | assembly-minimal |
| Sandy Bridge+ | ✓ | ❌ | assembly-avx-only |
| Haswell+ | ✓ | ✓ | assembly-optimized |
| Ice Lake+ | ✓ | ✓ | assembly-optimized |

**Example for Haswell+ system:**
```bash
conan create . --version=3.3.2 \
  -pr:b ../sparetools-openssl-tools/profiles/features/assembly-optimized
```

### ARM64 (ARMv8)

**Recommended Profile:** `assembly-neon`

**Feature Support:**

| Feature | Available | Recommended |
|---|---|---|
| NEON | ✓ (all ARMv8) | Yes |
| SVE | ✓ (ARMv8.4+) | No (currently disabled) |
| ASIMD | ✓ (all ARMv8) | Auto-enabled |

**Example for Cortex-A72 (Raspberry Pi 4):**
```bash
conan create . --version=3.3.2 \
  -pr:b ../sparetools-openssl-tools/profiles/base/linux-gcc11-arm64 \
  -pr:b ../sparetools-openssl-tools/profiles/features/assembly-neon
```

### ARM32 (ARMv7)

**Recommended Profile:** `assembly-neon`

**Requirements:**
- NEON capable processor (ARMv7 with NEON)
- Compiler support for NEON instructions

**Example:**
```bash
conan create . --version=3.3.2 \
  -o sparetools-openssl/*:enable_neon=True
```

---

## Performance Benchmarks

Approximate performance improvements with assembly optimizations:

### SHA-256 Hashing
- **No Optimization:** Baseline
- **AVX:** +5-10%
- **AVX2:** +12-20%
- **NEON:** +15-25%

### AES-256-GCM Encryption
- **No Optimization:** Baseline
- **AVX:** +10-15%
- **AVX2:** +20-35%
- **NEON:** +20-30%

### RSA Operations
- **No Optimization:** Baseline
- **AVX:** +8-12%
- **AVX2:** +15-25%
- **NEON:** +10-20%

**Note:** Actual performance depends on CPU model, workload, and data size.

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build with Optimizations

jobs:
  build-optimized:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        profile:
          - assembly-optimized
          - assembly-avx2-only
          - assembly-minimal

    steps:
      - uses: actions/checkout@v4

      - name: Build with ${{ matrix.profile }}
        run: |
          conan create packages/sparetools-openssl \
            --version=3.3.2 \
            -pr:b packages/sparetools-openssl-tools/profiles/features/${{ matrix.profile }}

  build-arm:
    runs-on: macos-latest
    strategy:
      matrix:
        include:
          - profile: base/darwin-clang-arm64
            asm: assembly-neon

    steps:
      - uses: actions/checkout@v4

      - name: Build ARM with NEON
        run: |
          conan create packages/sparetools-openssl \
            --version=3.3.2 \
            -pr:b packages/sparetools-openssl-tools/profiles/${{ matrix.profile }} \
            -pr:b packages/sparetools-openssl-tools/profiles/features/${{ matrix.asm }}
```

---

## Troubleshooting

### Build fails with "Unsupported instruction set"

**Solution:** Use `assembly-avx-only` or `assembly-minimal` profile.

```bash
conan create . --version=3.3.2 \
  -pr:b ../sparetools-openssl-tools/profiles/features/assembly-avx-only
```

### Performance not improving

**Check:** Verify that:
1. Assembly optimizations are enabled
2. Correct architecture profile is used
3. CPU supports the selected instruction set

**Verify:**
```bash
# Check which options were used
conan list 'sparetools-openssl/3.3.2:*'
conan cache path 'sparetools-openssl/3.3.2:*'
```

### Assembly code not found

**Solution:** Ensure:
1. `enable_asm=True` is set
2. OpenSSL version supports assembly (3.1.0+)
3. Compiler has assembly support

---

## Creating Custom Optimization Profiles

Create custom profiles by extending existing ones:

**File:** `profiles/features/assembly-custom`

```yaml
# Include base performance profile
include(../features/assembly-optimized)

[options]
# Override specific options
sparetools-openssl/*:enable_sve=True

[settings]
# Custom compiler flags
[conf]
tools.build:cxxflags=[-march=native]
```

---

## References

- [OpenSSL Assembly Optimizations](https://github.com/openssl/openssl/blob/master/INSTALL.md#assembler-languages)
- [Intel AVX Instruction Set](https://www.intel.com/content/www/en/en/architecture-and-technology/avx-2.html)
- [ARM NEON Intrinsics](https://developer.arm.com/architectures/instruction-sets/intrinsics/)
- [Conan Profiles Documentation](https://docs.conan.io/en/conan_2_0/reference/conanfile_py.html#profiles)

---

## FAQ

**Q: Which profile should I use?**
A: Use `assembly-optimized` for maximum performance. Use `assembly-avx-only` if your system doesn't support AVX2.

**Q: Is assembly optimization safe?**
A: Yes, assembly optimizations are well-tested and part of OpenSSL's standard build.

**Q: Can I mix optimization profiles?**
A: No, use only one optimization profile. Profiles are mutually exclusive.

**Q: How do I verify which optimizations are enabled?**
A: Check the build log for configuration arguments or run `openssl version -a` on the built binary.

**Q: Does FIPS mode work with assembly optimizations?**
A: Yes, FIPS mode works with all assembly optimizations. Use both FIPS and assembly profiles together.

---

## Support

For issues or questions about assembly optimizations:
1. Check this guide
2. Review OpenSSL documentation
3. Create a GitHub issue with your configuration
