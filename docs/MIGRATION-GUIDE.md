# Migration Guide: v1.x → v2.0.0

**Last Updated**: 2025-10-31  
**Target Audience**: Existing SpareTools users upgrading from v1.x to v2.0.0

---

## 📋 Overview

Version 2.0.0 represents a major architectural shift in the SpareTools ecosystem, focusing on consolidation, standardization, and improved usability. This guide will help you migrate your existing projects to the new version.

### Key Changes Summary

| Aspect | v1.x | v2.0.0 |
|--------|------|--------|
| **OpenSSL Packages** | 4 separate packages | 1 unified package |
| **Build Method Selection** | Package name | Conan option or profile |
| **Mini Package** | Separate package | Consolidated |
| **Profiles** | None | 15 comprehensive profiles |
| **Version** | 1.0.0 | 2.0.0 (breaking) |

---

## 🚨 Breaking Changes

### 1. Removed Packages

The following packages no longer exist as separate entities:

❌ **sparetools-openssl-cmake** → Use `sparetools-openssl` with `-o build_method=cmake`  
❌ **sparetools-openssl-autotools** → Use `sparetools-openssl` with `-o build_method=autotools`  
❌ **sparetools-openssl-hybrid** → Use `sparetools-openssl` with `-o build_method=python_configure`  
❌ **sparetools-openssl-tools-mini** → Scripts moved to appropriate packages

### 2. Script Locations Changed

| Script Type | v1.x Location | v2.0.0 Location |
|-------------|---------------|-----------------|
| **Generic Dev Scripts** | `sparetools-openssl-tools-mini/scripts/` | `sparetools-shared-dev-tools/scripts/` |
| **OpenSSL-Specific Scripts** | `sparetools-openssl-tools-mini/scripts/` | `sparetools-openssl-tools/scripts/` |
| **Build Automation** | `sparetools-openssl-tools-mini/openssl_tools/` | `sparetools-openssl-tools/automation/` |

### 3. Profile-Based Configuration

Build variants are now configured through Conan profiles instead of separate packages.

---

## 🔄 Migration Steps

### Step 1: Update Your conanfile.txt or conanfile.py

#### Before (v1.x):

```ini
# conanfile.txt
[requires]
sparetools-openssl-cmake/3.3.2

[tool_requires]
sparetools-openssl-tools/1.0.0
sparetools-openssl-tools-mini/1.0.0
```

#### After (v2.0.0):

```ini
# conanfile.txt
[requires]
sparetools-openssl/2.0.0

[tool_requires]
sparetools-openssl-tools/2.0.0
sparetools-shared-dev-tools/2.0.0
```

### Step 2: Specify Build Method

#### Option A: Using Conan Options

```bash
# Install with specific build method
conan install . \
  -o sparetools-openssl/*:build_method=cmake \
  --build=missing
```

Available build methods:
- `perl_configure` (default, most stable)
- `cmake` (modern, IDE-friendly)
- `autotools` (Unix standard)
- `python_configure` (experimental, Python-based)

#### Option B: Using Conan Profiles

```bash
# Install with build profiles
conan install . \
  -pr:b ~/.conan2/profiles/default \
  -pr:b packages/sparetools-openssl-tools/profiles/build-methods/cmake-build \
  --build=missing
```

### Step 3: Update Script References

If you're using scripts from the mini package, update the paths:

#### Before (v1.x):

```bash
# Generic scripts
~/.conan2/p/sparetools-openssl-tools-mini/*/p/scripts/setup-conan-env.sh

# OpenSSL scripts
~/.conan2/p/sparetools-openssl-tools-mini/*/p/scripts/enhanced-sbom-generator.py
```

#### After (v2.0.0):

```bash
# Generic scripts
~/.conan2/p/sparetools-shared-dev-tools/*/p/scripts/setup-conan-env.sh

# OpenSSL scripts
~/.conan2/p/sparetools-openssl-tools/*/p/scripts/enhanced-sbom-generator.py
```

### Step 4: Update Build Commands

#### Before (v1.x - CMake Variant):

```bash
conan create packages/sparetools-openssl-cmake \
  --version=3.3.2 \
  --build=missing
```

#### After (v2.0.0 - Unified with Option):

```bash
conan create packages/sparetools-openssl \
  --version=2.0.0 \
  -o sparetools-openssl/*:build_method=cmake \
  --build=missing
```

#### After (v2.0.0 - Unified with Profiles):

```bash
conan create packages/sparetools-openssl \
  --version=2.0.0 \
  -pr:b packages/sparetools-openssl-tools/profiles/build-methods/cmake-build \
  --build=missing
```

---

## 📚 Profile System Guide

### Understanding Profiles

v2.0.0 introduces a comprehensive profile system organized into three categories:

```
profiles/
├── base/               # Platform + compiler combinations
├── build-methods/      # Build system selection
└── features/           # Feature toggles (FIPS, shared/static, etc.)
```

### Common Profile Combinations

#### 1. Standard Linux Build

```bash
conan install . \
  -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b sparetools-openssl-tools/profiles/build-methods/perl-configure
```

#### 2. Windows Build

```bash
conan install . \
  -pr:b sparetools-openssl-tools/profiles/base/windows-msvc2022 \
  -pr:b sparetools-openssl-tools/profiles/build-methods/perl-configure
```

#### 3. FIPS-Enabled Build

```bash
conan install . \
  -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b sparetools-openssl-tools/profiles/build-methods/perl-configure \
  -pr:b sparetools-openssl-tools/profiles/features/fips-enabled
```

#### 4. Minimal Static Build

```bash
conan install . \
  -pr:b sparetools-openssl-tools/profiles/features/static-only \
  -pr:b sparetools-openssl-tools/profiles/features/minimal
```

#### 5. Performance-Optimized Build

```bash
conan install . \
  -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b sparetools-openssl-tools/profiles/build-methods/perl-configure \
  -pr:b sparetools-openssl-tools/profiles/features/performance
```

---

## 🎯 Use Case Examples

### Use Case 1: Simple CMake Project

**Goal**: Use SpareTools OpenSSL in a CMake project with default settings.

#### v1.x Approach:

```bash
conan install --requires=sparetools-openssl-cmake/3.3.2 \
  --build=missing
```

#### v2.0.0 Approach:

```bash
# Using option
conan install --requires=sparetools-openssl/2.0.0 \
  -o sparetools-openssl/*:build_method=cmake \
  --build=missing

# Or using profile
conan install --requires=sparetools-openssl/2.0.0 \
  -pr:b sparetools-openssl-tools/profiles/build-methods/cmake-build \
  --build=missing
```

### Use Case 2: FIPS-Compliant Application

**Goal**: Build OpenSSL with FIPS 140-3 module enabled.

#### v1.x Approach:

```bash
# Manual FIPS configuration required
conan install --requires=sparetools-openssl/3.3.2 \
  -o fips=True \
  --build=missing
```

#### v2.0.0 Approach:

```bash
# Profile makes it explicit and repeatable
conan install --requires=sparetools-openssl/2.0.0 \
  -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b sparetools-openssl-tools/profiles/features/fips-enabled \
  --build=missing
```

### Use Case 3: Cross-Platform CI/CD

**Goal**: Build for multiple platforms in GitHub Actions.

#### v1.x Approach:

```yaml
# Separate package per platform
- name: Install (Linux)
  run: conan install --requires=sparetools-openssl/3.3.2

- name: Install (Windows)
  run: conan install --requires=sparetools-openssl/3.3.2
```

#### v2.0.0 Approach:

```yaml
# Matrix with profiles
strategy:
  matrix:
    include:
      - os: ubuntu-latest
        profile: base/linux-gcc11
      - os: windows-latest
        profile: base/windows-msvc2022
      - os: macos-latest
        profile: base/darwin-clang-arm64

steps:
  - name: Install
    run: |
      conan install --requires=sparetools-openssl/2.0.0 \
        -pr:b sparetools-openssl-tools/profiles/${{ matrix.profile }} \
        --build=missing
```

---

## 🔧 Troubleshooting

### Issue 1: "Package 'sparetools-openssl-cmake' not found"

**Cause**: You're trying to use a removed package.

**Solution**: Use the unified package with build method option:

```bash
# Instead of
conan install --requires=sparetools-openssl-cmake/3.3.2

# Use
conan install --requires=sparetools-openssl/2.0.0 \
  -o sparetools-openssl/*:build_method=cmake
```

### Issue 2: Scripts Not Found

**Cause**: Script locations changed.

**Solution**: Check the new locations:

```bash
# For generic scripts
conan install --tool-requires=sparetools-shared-dev-tools/2.0.0

# For OpenSSL-specific scripts
conan install --tool-requires=sparetools-openssl-tools/2.0.0
```

### Issue 3: Build Method Not Recognized

**Cause**: Invalid build_method option.

**Solution**: Use one of the valid build methods:

```bash
# Valid options
-o sparetools-openssl/*:build_method=perl_configure  # Default
-o sparetools-openssl/*:build_method=cmake
-o sparetools-openssl/*:build_method=autotools
-o sparetools-openssl/*:build_method=python_configure  # Experimental
```

### Issue 4: Profile Not Found

**Cause**: Profile path incorrect or profiles not installed.

**Solution**: Ensure sparetools-openssl-tools is installed:

```bash
# Export the tools package (contains profiles)
conan export packages/sparetools-openssl-tools --version=2.0.0

# Then use profiles
conan install . \
  -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11
```

---

## 📊 Feature Comparison

| Feature | v1.x | v2.0.0 | Notes |
|---------|------|--------|-------|
| **Unified Package** | ❌ No | ✅ Yes | Single package, multiple methods |
| **Profile System** | ❌ No | ✅ Yes | 15 comprehensive profiles |
| **Build Methods** | Package-based | Option/Profile | More flexible |
| **FIPS Support** | Option only | Option + Profile | Better CI/CD integration |
| **Script Organization** | Mixed | Separated | Clearer separation |
| **Python configure.py** | ❌ No | ✅ Experimental | 65% feature parity |
| **GitHub Actions** | ❌ No | ✅ Yes | 4 workflows included |
| **Documentation** | Basic | Comprehensive | 600+ line READMEs |

---

## 🎓 Best Practices

### 1. Use Profiles in CI/CD

Profiles make your builds reproducible and explicit:

```yaml
# .github/workflows/build.yml
- name: Build with Profile
  run: |
    conan create . \
      -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11 \
      -pr:b sparetools-openssl-tools/profiles/features/fips-enabled
```

### 2. Lock Your Dependencies

Use `conan lock` to ensure reproducible builds:

```bash
# Create lock file
conan lock create . --lockfile-out=conan.lock

# Use in CI/CD
conan install . --lockfile=conan.lock
```

### 3. Version Your Profiles

If you customize profiles, version them in your repository:

```
my-project/
├── conan/
│   └── profiles/
│       ├── production.profile
│       ├── development.profile
│       └── testing.profile
└── conanfile.txt
```

### 4. Document Your Build Configuration

Include build instructions in your README:

```markdown
## Building

### Development Build
\`\`\`bash
conan install . \
  -pr:b sparetools-openssl-tools/profiles/features/shared-libs
\`\`\`

### Production Build (FIPS)
\`\`\`bash
conan install . \
  -pr:b sparetools-openssl-tools/profiles/base/linux-gcc11 \
  -pr:b sparetools-openssl-tools/profiles/features/fips-enabled
\`\`\`
```

---

## 📞 Getting Help

### Resources

- **Documentation**: https://github.com/sparesparrow/sparetools/tree/main/docs
- **Issues**: https://github.com/sparesparrow/sparetools/issues
- **Discussions**: https://github.com/sparesparrow/sparetools/discussions
- **Changelog**: https://github.com/sparesparrow/sparetools/blob/main/CHANGELOG.md

### Common Questions

**Q: Can I still use the old package names?**  
A: No, they've been removed. Use the unified package with options or profiles.

**Q: Are my v1.x packages still available?**  
A: Yes, v1.0.0 packages remain available on Cloudsmith, but won't receive updates.

**Q: How do I report migration issues?**  
A: Open an issue on GitHub with the "migration" label.

**Q: Is there a deprecation period?**  
A: v1.x is end-of-life as of 2025-10-31. Upgrade to v2.0.0 recommended.

---

## ✅ Migration Checklist

Use this checklist to track your migration:

- [ ] Read this migration guide completely
- [ ] Update conanfile.txt or conanfile.py with v2.0.0 packages
- [ ] Replace separate package references with unified package
- [ ] Update build method selection (option or profile)
- [ ] Update script references to new locations
- [ ] Test builds locally with new configuration
- [ ] Update CI/CD workflows
- [ ] Update documentation
- [ ] Test on all target platforms
- [ ] Deploy and validate in staging environment
- [ ] Deploy to production

---

**Migration Support**: If you encounter issues not covered in this guide, please open an issue on GitHub.

**Last Updated**: 2025-10-31  
**Version**: 2.0.0

