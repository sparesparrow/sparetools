# SpareTools Package Ecosystem - Index & Quick Links

## Three-Level Documentation

This ecosystem is documented at three levels for different use cases:

### Level 1: Quick Reference (5 minutes)
**File:** [PACKAGE-QUICK-REFERENCE.md](PACKAGE-QUICK-REFERENCE.md)  
**Size:** 12 KB | **Lines:** 353

For quick lookups, one-liners, and architecture overview.

**Contains:**
- Package architecture diagram
- Quick build commands
- Dependency map
- Build profiles reference
- Platform support matrix
- Known issues summary
- Migration guide (old → new)

**Start here if:** You need a command, want to understand the architecture at a glance, or need to migrate from deprecated packages.

---

### Level 2: Complete Reference (1-2 hours)
**File:** [PACKAGE-ECOSYSTEM-SUMMARY.md](PACKAGE-ECOSYSTEM-SUMMARY.md)  
**Size:** 29 KB | **Lines:** 958

Comprehensive documentation of all 11 packages with complete details.

**Contains:**
- Detailed specs for each of 7 production packages
- Specifications for 4 deprecated packages
- Purpose, dependencies, exports for each
- Full dependency graphs
- Configuration options (15+ build profiles)
- Zero-copy deployment pattern explanation
- Security features overview
- 5 critical known issues with details
- Migration guide with code examples
- Build order and prerequisites

**Start here if:** You're new to the ecosystem, want to understand dependencies, need to add a package, or troubleshooting issues.

---

### Level 3: Developer Guide (20+ hours)
**File:** [CLAUDE.md](CLAUDE.md) (in repo root)  
**Size:** 50+ KB | **Contains:** Architecture diagrams, deep technical analysis

For architecture deep-dives, OpenSSL 3.6.0 complexity analysis, and development workflow.

**Contains:**
- Complete project overview
- Essential build/test commands
- Architecture and dependency graphs (Mermaid)
- Zero-copy symlink strategy details
- Security integration architecture
- Bootstrap orchestration patterns
- OpenSSL 3.6.0 build complexity analysis (5000+ words)
- Common gotchas and troubleshooting
- Conan 2.x pattern reference

**Start here if:** You're contributing to core systems, implementing new orchestration, or debugging OpenSSL builds.

---

## Quick Navigation by Task

### "I want to understand the ecosystem"
1. Read this file (you are here)
2. Check the [architecture diagram](PACKAGE-QUICK-REFERENCE.md#at-a-glance)
3. Review [package list](PACKAGE-ECOSYSTEM-SUMMARY.md#summary-table)

### "I want to build everything"
1. See [Quick Build Commands](PACKAGE-QUICK-REFERENCE.md#quick-build-commands)
2. Reference [Build Order](PACKAGE-ECOSYSTEM-SUMMARY.md#dependency-graph-foundational-order)
3. Check [Known Issues](PACKAGE-ECOSYSTEM-SUMMARY.md#known-issues--critical-notes)

### "I want to migrate from old packages"
1. Check [Migration Guide](PACKAGE-QUICK-REFERENCE.md#migration-from-deprecated-packages)
2. See detailed examples in [Ecosystem Summary](PACKAGE-ECOSYSTEM-SUMMARY.md#migration-guide-from-deprecated-packages)

### "I want to build OpenSSL with specific options"
1. Review [Build Methods](PACKAGE-QUICK-REFERENCE.md#openssl-build-methods)
2. Check [Configuration Options](PACKAGE-QUICK-REFERENCE.md#openssl-configuration-options)
3. See [Build Profiles](PACKAGE-QUICK-REFERENCE.md#build-profiles-15)

### "I found a bug or issue"
1. Check [Known Issues](PACKAGE-ECOSYSTEM-SUMMARY.md#known-issues--critical-notes)
2. Search [CLAUDE.md](CLAUDE.md) for detailed analysis
3. Report to: https://github.com/sparesparrow/sparetools/issues

### "I want to understand security features"
1. See [Security Features](PACKAGE-QUICK-REFERENCE.md#security-features)
2. Read [Security Integration](CLAUDE.md#security-integration)
3. Review [sparetools-base](PACKAGE-ECOSYSTEM-SUMMARY.md#1-sparetoolsbase20-production)

### "I want to understand zero-copy deployment"
1. Overview: [Zero-Copy Deployment](PACKAGE-QUICK-REFERENCE.md#zero-copy-deployment)
2. Deep dive: [CLAUDE.md Zero-Copy Section](CLAUDE.md#zero-copy-symlink-strategy)
3. Code: [symlink-helpers.py](packages/sparetools-base/symlink-helpers.py)

---

## Package List (All 11)

### Production Packages (7) ✅

| # | Name | Version | Type | Purpose |
|---|------|---------|------|---------|
| 1 | **sparetools-base** | 2.0.0 | python-require | Foundation (symlink, security) |
| 2 | **sparetools-cpython** | 3.12.7 | application | Prebuilt Python runtime |
| 3 | **sparetools-shared-dev-tools** | 2.0.0 | python-require | Generic dev utilities |
| 4 | **sparetools-openssl-tools** | 2.0.0 | python-require | OpenSSL build tools (15+ profiles) |
| 5 | **sparetools-bootstrap** | 2.0.0 | python-require | Orchestration (3-agent) |
| 6 | **sparetools-mcp-orchestrator** | 2.0.0 | python-require | AI/MCP/Mermaid tools |
| 7 | **sparetools-openssl** | 3.3.2 | library | MAIN DELIVERABLE (4 build methods) |

### Deprecated Packages (4) ⚠️

| # | Name | Version | Replacement |
|---|------|---------|-------------|
| 8 | sparetools-openssl-cmake | 3.3.2 | Use `-o build_method=cmake` |
| 9 | sparetools-openssl-autotools | 3.3.2 | Use `-o build_method=autotools` |
| 10 | sparetools-openssl-hybrid | 3.3.2 | Use `-o build_method=python` |
| 11 | sparetools-openssl-tools-mini | 1.0.0 | Use sparetools-openssl-tools |

---

## Key Information at a Glance

### Build Order (Critical!)
```
1. sparetools-base
   ↓
2. sparetools-cpython + sparetools-shared-dev-tools
   ↓
3. sparetools-openssl-tools
   ↓
4. sparetools-bootstrap + sparetools-mcp-orchestrator
   ↓
5. sparetools-openssl ⭐
```

### Main Deliverable
**sparetools-openssl/3.3.2** with 4 build methods:
- **Perl Configure** (default, production) ✅
- **CMake** (modern, optional) ✅
- **Autotools** (cross-compile) ✅
- **Python configure.py** (experimental, 65% complete) ⚠️

### OpenSSL Features (Configurable)
```
Build type:    shared/static
Performance:   threads, asm, AVX/AVX2, NEON, SVE
Features:      zlib, legacy algorithms
Compliance:    FIPS 140-3 mode
```

### Platforms Supported
- Linux (x86_64, ARM64) ✅
- macOS (x86_64, ARM64) ✅
- Windows (x86_64) ✅
- FreeBSD, Android, iOS (experimental) ⚠️

### Security Built-In
- ✅ Trivy vulnerability scanning
- ✅ Syft SBOM generation (CycloneDX/SPDX)
- ✅ FIPS 140-3 validation (570-line module)
- ✅ Automatic integration in build process

---

## Critical Known Issues

| # | Issue | Status | Action |
|---|-------|--------|--------|
| 1 | OpenSSL 3.6.0 complexity | ⚠️ Known | Stick with 3.3.2 |
| 2 | Test coverage <5% | ⚠️ Needs work | Target 60% |
| 3 | 4 deprecated packages | ⚠️ Ready | Remove soon |
| 4 | **bootstrap missing python_requires** | 🔴 CRITICAL | FIX NOW |
| 5 | Hardcoded staging paths | ⚠️ Low | Use env vars |

See [detailed issues](PACKAGE-ECOSYSTEM-SUMMARY.md#known-issues--critical-notes) for more info.

---

## Quick Commands

```bash
# Build everything in order
for pkg in base shared-dev-tools openssl-tools openssl; do
  conan create packages/sparetools-$pkg --version=2.0.0 --build=missing
done

# Build with FIPS
conan create packages/sparetools-openssl --version=3.3.2 \
  -o \*:fips=True --build=missing

# Build with CMake
conan create packages/sparetools-openssl --version=3.3.2 \
  -o \*:build_method=cmake --build=missing

# Run tests
conan test packages/sparetools-openssl/test_package \
  sparetools-openssl/3.3.2@
```

See [Quick Build Commands](PACKAGE-QUICK-REFERENCE.md#quick-build-commands) for more.

---

## File Structure

```
/home/sparrow/sparetools/
├── PACKAGE-ECOSYSTEM-INDEX.md      ← You are here
├── PACKAGE-QUICK-REFERENCE.md      ← 5-minute overview
├── PACKAGE-ECOSYSTEM-SUMMARY.md    ← Complete reference (1-2 hours)
├── CLAUDE.md                       ← Developer guide (20+ hours)
├── README.md                       ← Project overview
│
└── packages/
    ├── sparetools-base/             (7 KB, 2 modules)
    ├── sparetools-cpython/          (prebuilt Python)
    ├── sparetools-shared-dev-tools/ (utilities)
    ├── sparetools-openssl-tools/    (15+ profiles, FIPS validator)
    │   └── profiles/
    │       ├── base/               (platform/compiler)
    │       ├── build-methods/      (perl, cmake, autotools, python)
    │       └── features/           (fips, shared, static, minimal)
    ├── sparetools-bootstrap/        (orchestration)
    ├── sparetools-mcp-orchestrator/ (AI, Mermaid, MCP)
    ├── sparetools-openssl/          (MAIN - 4 build methods)
    │   ├── conanfile.py
    │   └── test_package/
    │
    ├── [DEPRECATED]
    ├── sparetools-openssl-cmake/
    ├── sparetools-openssl-autotools/
    ├── sparetools-openssl-hybrid/
    └── sparetools-openssl-tools-mini/
```

---

## Resources

### Official
- **Repository:** https://github.com/sparesparrow/sparetools
- **Distribution:** https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/

### External
- **Conan 2.x Docs:** https://docs.conan.io/2/
- **OpenSSL Project:** https://www.openssl.org
- **FIPS 140-3:** https://csrc.nist.gov/publications/detail/fips/140/3/final
- **Trivy:** https://aquasecurity.github.io/trivy/
- **Syft:** https://github.com/anchore/syft

---

## Document Versions

| Document | Version | Updated | Status |
|----------|---------|---------|--------|
| PACKAGE-ECOSYSTEM-SUMMARY.md | 1.0 | 2025-11-01 | Current |
| PACKAGE-QUICK-REFERENCE.md | 1.0 | 2025-11-01 | Current |
| PACKAGE-ECOSYSTEM-INDEX.md | 1.0 | 2025-11-01 | Current |
| CLAUDE.md | 2.0+ | Regular | See file |

---

## Getting Help

1. **For quick questions:** Check [PACKAGE-QUICK-REFERENCE.md](PACKAGE-QUICK-REFERENCE.md)
2. **For detailed info:** See [PACKAGE-ECOSYSTEM-SUMMARY.md](PACKAGE-ECOSYSTEM-SUMMARY.md)
3. **For architecture/design:** Read [CLAUDE.md](CLAUDE.md)
4. **For bug reports:** https://github.com/sparesparrow/sparetools/issues
5. **For discussions:** GitHub discussions (if enabled)

---

**SpareTools Package Ecosystem Documentation**  
Last Updated: 2025-11-01  
Repository: https://github.com/sparesparrow/sparetools
