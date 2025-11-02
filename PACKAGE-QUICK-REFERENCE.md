# SpareTools Package Ecosystem - Quick Reference Card

## At a Glance

**11 packages** | **7 production** | **4 deprecated** | **v2.0.0** | **Conan 2.x**

```
┌─────────────────────────────────────────────────────────────────┐
│                    PACKAGE ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Layer 1: FOUNDATION                                             │
│  ┗━ sparetools-base/2.0.0 ✅                                     │
│     (symlink-helpers, security-gates)                            │
│                                                                   │
│  Layer 2: PREBUILT TOOLS                                         │
│  ┗━ sparetools-cpython/3.12.7 ✅                                 │
│     (Python 3.12.7 binary)                                       │
│                                                                   │
│  Layer 3: UTILITIES                                              │
│  ┣━ sparetools-shared-dev-tools/2.0.0 ✅                         │
│  ┗━ sparetools-openssl-tools/2.0.0 ✅                            │
│     (15+ profiles, FIPS validator, security tools)              │
│                                                                   │
│  Layer 4: ORCHESTRATION                                          │
│  ┣━ sparetools-bootstrap/2.0.0 ✅ ⚠️ ISSUE #4                    │
│  ┗━ sparetools-mcp-orchestrator/2.0.0 ✅                         │
│     (AI, Mermaid, MCP)                                           │
│                                                                   │
│  Layer 5: MAIN DELIVERABLE                                       │
│  ┗━ sparetools-openssl/3.3.2 ✅                                  │
│     (Perl, CMake, Autotools, Python build methods)              │
│                                                                   │
│  DEPRECATED (4 - to be removed)                                  │
│  ┣━ sparetools-openssl-cmake/3.3.2 ⚠️                            │
│  ┣━ sparetools-openssl-autotools/3.3.2 ⚠️                        │
│  ┣━ sparetools-openssl-hybrid/3.3.2 ⚠️                           │
│  ┗━ sparetools-openssl-tools-mini/1.0.0 ⚠️                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Package Type Legend

| Type | Meaning | Use Case |
|------|---------|----------|
| `python-require` | Recipe dependency | Shared utilities, tools |
| `application` | Standalone binary | Prebuilt runtime tools |
| `library` | C/C++ library | OpenSSL deliverable |

---

## Quick Build Commands

```bash
# Build foundation first
conan create packages/sparetools-base --version=2.0.0

# Then utilities
conan create packages/sparetools-shared-dev-tools --version=2.0.0
conan create packages/sparetools-openssl-tools --version=2.0.0

# Then main deliverable
conan create packages/sparetools-openssl --version=3.3.2 --build=missing

# Build with options
conan create packages/sparetools-openssl --version=3.3.2 \
  -o sparetools-openssl/*:build_method=perl \
  -o sparetools-openssl/*:fips=True

# Test
conan test packages/sparetools-openssl/test_package sparetools-openssl/3.3.2@
```

---

## Package Dependencies Quick Map

```
sparetools-base/2.0.0
  └─ NOTHING (foundation)

sparetools-cpython/3.12.7
  └─ python_requires: base

sparetools-shared-dev-tools/2.0.0
  └─ python_requires: base

sparetools-openssl-tools/2.0.0
  └─ python_requires: base

sparetools-bootstrap/2.0.0
  └─ ⚠️ MISSING: should have python_requires: base

sparetools-mcp-orchestrator/2.0.0
  └─ python_requires: base

sparetools-openssl/3.3.2 ⭐ MAIN
  ├─ python_requires: base
  ├─ tool_requires: openssl-tools/2.0.0
  └─ tool_requires: cpython/3.12.7
```

---

## OpenSSL Build Methods

| Method | Status | Best For |
|--------|--------|----------|
| **Perl Configure** (default) | ✅ Production | Most compatible, proven |
| **CMake** | ✅ Modern | IDE integration, development |
| **Autotools** | ✅ Cross-compile | Embedded, ARM targets |
| **Python configure.py** | ⚠️ Experimental | Pure Python (65% complete) |

**Usage:**
```bash
-o sparetools-openssl/*:build_method=perl       # Default
-o sparetools-openssl/*:build_method=cmake
-o sparetools-openssl/*:build_method=autotools
-o sparetools-openssl/*:build_method=python     # Falls back to perl
```

---

## Key Exports by Package

### sparetools-base
- `symlink-helpers.py` - Zero-copy deployment (create_symlink_with_check, zero_copy_deploy, atomic_symlink_swap)
- `security-gates.py` - Security scanning (run_trivy_scan, generate_sbom, validate_fips_compliance)

### sparetools-cpython
- `bin/python3.12` - Primary Python executable
- `bin/python3` - Symlink to python3.12
- `bin/python` - Symlink to python3.12
- Library path: `lib/`

### sparetools-openssl-tools
- `openssl_tools/` - Python modules for build automation
- `profiles/` - 15+ Conan build profiles
  - base/ - Platform/compiler profiles
  - build-methods/ - Build system selection
  - features/ - Feature toggles
- Scripts - 20+ automation scripts
- FIPS validator (570+ lines)
- SBOM generator

### sparetools-bootstrap
- Build orchestration (3-agent pattern)
- Build matrix generation
- FIPS validation helpers
- SBOM generation

### sparetools-mcp-orchestrator
- MCP server (FastMCP)
- Mermaid diagram generation (700+ templates)
- Prompt management
- AI-assisted development tools
- Ecosystem monitoring

### sparetools-openssl
- `OpenSSL::SSL` - libssl library
- `OpenSSL::Crypto` - libcrypto library
- CMake targets, pkg-config support

---

## Platform Support

| Platform | x86_64 | ARM64 | Status |
|----------|--------|-------|--------|
| Linux | ✅ | ✅ | Tested |
| macOS | ✅ | ✅ | Supported |
| Windows | ✅ | — | Supported |
| FreeBSD | ✅ | ⚠️ | Experimental |
| Android | — | ✅ | Experimental |
| iOS | — | ✅ | Experimental |

---

## OpenSSL Configuration Options

```
build_method: [perl, cmake, autotools, python]  → default: perl
shared:       [True, False]                     → default: False
fPIC:         [True, False]                     → default: True
fips:         [True, False]                     → default: False
enable_threads: [True, False]                   → default: True
enable_asm:   [True, False]                     → default: True
enable_zlib:  [True, False]                     → default: True
enable_legacy: [True, False]                    → default: False
enable_avx:   [True, False]                     → default: True
enable_avx2:  [True, False]                     → default: True
enable_neon:  [True, False]                     → default: True
enable_sve:   [True, False]                     → default: False
```

---

## Build Profiles (15+)

### Base Profiles
- `linux-gcc11`, `linux-clang14`
- `darwin-clang-x86_64`, `darwin-clang-arm64`
- `windows-msvc2022`

### Build Method Profiles
- `perl-configure` (production)
- `cmake-build` (modern)
- `autotools` (cross-compile)
- `python-configure` (experimental)

### Feature Profiles
- `fips-enabled` - FIPS 140-3 mode
- `shared-libs` - Shared libraries
- `static-only` - Static only
- `minimal` - Minimal features
- `performance` - Performance opts

**Stack them:**
```bash
-pr:b profiles/base/linux-gcc11 \
-pr:b profiles/build-methods/perl-configure \
-pr:b profiles/features/fips-enabled
```

---

## Known Issues

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | OpenSSL 3.6.0 complex build | HIGH | ⚠️ Stick with 3.3.2 |
| 2 | Testing deficit (<5% coverage) | MEDIUM | ⚠️ Target 60% |
| 3 | 4 deprecated packages | MEDIUM | ⚠️ Ready to remove |
| 4 | **sparetools-bootstrap missing python_requires** | **HIGH** | 🔴 NEEDS FIX |
| 5 | Hardcoded staging paths | LOW | ⚠️ Use env vars |

---

## File Locations

```
/home/sparrow/sparetools/
├── packages/
│   ├── sparetools-base/
│   ├── sparetools-cpython/
│   ├── sparetools-shared-dev-tools/
│   ├── sparetools-openssl-tools/
│   │   └── profiles/           # 15+ build profiles
│   ├── sparetools-bootstrap/
│   ├── sparetools-mcp-orchestrator/
│   ├── sparetools-openssl/
│   │   └── test_package/       # Integration tests
│   ├── sparetools-openssl-cmake/     (deprecated)
│   ├── sparetools-openssl-autotools/ (deprecated)
│   ├── sparetools-openssl-hybrid/    (deprecated)
│   └── sparetools-openssl-tools-mini/ (deprecated)
├── PACKAGE-ECOSYSTEM-SUMMARY.md ← Full reference
├── PACKAGE-QUICK-REFERENCE.md   ← This file
└── CLAUDE.md                    ← Developer guide
```

---

## Resources

- **Repository:** https://github.com/sparesparrow/sparetools
- **Distribution:** https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/
- **Conan Docs:** https://docs.conan.io/2/
- **OpenSSL:** https://www.openssl.org
- **FIPS 140-3:** https://csrc.nist.gov/publications/detail/fips/140/3/final

---

## Migration from Deprecated Packages

```bash
# OLD → NEW

# CMake build
conan install --requires=sparetools-openssl-cmake/3.3.2
→ conan install --requires=sparetools-openssl/3.3.2 -o build_method=cmake

# Autotools build
conan install --requires=sparetools-openssl-autotools/3.3.2
→ conan install --requires=sparetools-openssl/3.3.2 -o build_method=autotools

# Hybrid/Python build
conan install --requires=sparetools-openssl-hybrid/3.3.2
→ conan install --requires=sparetools-openssl/3.3.2 -o build_method=python

# Mini tools
python_requires = "sparetools-openssl-tools-mini/1.0.0"
→ python_requires = "sparetools-openssl-tools/2.0.0"
```

---

## Zero-Copy Deployment

Save 80% disk space using OS-level symlinks:

```
~/.conan2/p/                          # Actual files (once)
  └── sparetools-openssl/.../p/

_Build/packages/
  └── sparetools-openssl → ~/.conan2/p/.../sparetools-openssl/p

Projects/
  └── lib/ → _Build/packages/sparetools-openssl/lib/
```

---

## Security Features

✅ **Integrated in sparetools-base & sparetools-openssl:**
- Trivy vulnerability scanning
- Syft SBOM generation (CycloneDX/SPDX)
- FIPS 140-3 validation (570-line module)
- Automatic during build

```bash
# Runs automatically:
conan create packages/sparetools-openssl --version=3.3.2
# → Trivy scan + SBOM generation included
```

---

## One-Liner Reference

```bash
# Full build (foundation → tools → openssl)
for pkg in base shared-dev-tools openssl-tools openssl; do
  conan create packages/sparetools-$pkg --version=2.0.0 --build=missing
done

# Quick FIPS test
conan create packages/sparetools-openssl --version=3.3.2 -o \*:fips=True --build=missing

# Run all tests
conan test packages/sparetools-openssl/test_package sparetools-openssl/3.3.2@
```

---

**Quick Reference v1.0**  
Last Updated: 2025-11-01  
See PACKAGE-ECOSYSTEM-SUMMARY.md for complete reference
