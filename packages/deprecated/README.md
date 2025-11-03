# Deprecated Packages

This directory contains packages that have been deprecated and are no longer maintained.

## Deprecated Package List

### sparetools-openssl-cmake (v3.3.2)
**Deprecated:** 2025-11-03
**Reason:** Consolidated into `sparetools-openssl` package with `build_method=cmake` option
**Replacement:** Use `sparetools-openssl/3.3.2` with CMake profile from `sparetools-openssl-tools/profiles/build-methods/cmake-build`

### sparetools-openssl-autotools (v3.3.2)
**Deprecated:** 2025-11-03
**Reason:** Consolidated into `sparetools-openssl` package with `build_method=autotools` option
**Replacement:** Use `sparetools-openssl/3.3.2` with Autotools profile from `sparetools-openssl-tools/profiles/build-methods/autotools`

### sparetools-openssl-hybrid (v3.3.2)
**Deprecated:** 2025-11-03
**Reason:** Experimental Python configure.py implementation (~65% feature parity) - not production-ready
**Replacement:** Use `sparetools-openssl/3.3.2` with Perl Configure (default) or CMake build method
**Note:** Python configure.py requires significant work to support OpenSSL 3.6.0+ features

### sparetools-openssl-tools-mini (v1.0.0)
**Deprecated:** 2025-11-03
**Reason:** Merged into `sparetools-openssl-tools/2.0.0` package
**Replacement:** Use `sparetools-openssl-tools/2.0.0` (contains all functionality from mini)

## Migration Guide

If you have dependencies on these packages in your `conanfile.py`, update as follows:

**Before:**
```python
requires = "sparetools-openssl-cmake/3.3.2"
```

**After:**
```python
requires = "sparetools-openssl/3.3.2"
# Use profile: packages/sparetools-openssl-tools/profiles/build-methods/cmake-build
```

**Before:**
```python
tool_requires = "sparetools-openssl-tools-mini/1.0.0"
```

**After:**
```python
tool_requires = "sparetools-openssl-tools/2.0.0"
```

## Removal Timeline

These packages will remain in the `deprecated/` directory until:
- All CI/CD workflows have been updated (target: 2025-11-10)
- Documentation references updated (target: 2025-11-10)
- No active consumers remain (verification: 2025-11-30)

After this grace period, they will be removed entirely.

## Contact

For migration assistance, see [CLAUDE.md](../../CLAUDE.md) or open an issue at https://github.com/sparesparrow/sparetools/issues
