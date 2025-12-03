# Conan Recipes Audit Report

Generated: 2025-12-03 11:54:08

## Summary

- **Total packages audited**: 10
- **Compliant packages**: 6
- **Packages with issues**: 4
- **Packages with warnings**: 4

## Detailed Results

### sparetools-base

- **Path**: `packages/sparetools-base/conanfile.py`
- **Version**: 2.0.0
- **Package Type**: `python-require`
- **Description**: Foundation utilities for SpareTools ecosystem
- **License**: Apache-2.0
- **Has test_package**: ❌
- **Conan API**: ✅ Uses Conan 2.x API (`buildenv_info`/`runenv_info`)

**Status**: ✅ Compliant

### sparetools-bootstrap

- **Path**: `packages/sparetools-bootstrap/conanfile.py`
- **Version**: 2.0.0
- **Package Type**: `python-require`
- **Description**: Bootstrap utilities for SpareTools ecosystem
- **License**: Apache-2.0
- **Dependencies**:
  - python_requires: sparetools-base/2.0.0
- **Has test_package**: ✅
- **Conan API**: ✅ Uses Conan 2.x API (`buildenv_info`/`runenv_info`)

**Status**: ✅ Compliant

### packages/sparetools-bootstrap/test_package/conanfile.py

- **Path**: `packages/sparetools-bootstrap/test_package/conanfile.py`
- **Dependencies**:
  - python_requires: sparetools-bootstrap/[>=2.0.0]
- **Has test_package**: ❌
- **Conan API**: ℹ️ No environment info (may be library-only)

**Issues:**
- ❌ Missing required field: name
- ❌ Missing required field: version

**Warnings:**
- ⚠️ Missing recommended field: description
- ⚠️ Missing recommended field: license
- ⚠️ Missing package_type field (recommended for Conan 2.x)

**Status**: ❌ Has issues

### sparetools-cpython

- **Path**: `packages/sparetools-cpython/conanfile.py`
- **Version**: 3.12.7
- **Package Type**: `application`
- **Description**: Prebuilt CPython 3.12.7 with OpenSSL support for DevOps
- **License**: Python-2.0
- **Dependencies**:
  - python_requires: sparetools-base/2.0.0
- **Has test_package**: ✅
- **Conan API**: ✅ Uses Conan 2.x API (`buildenv_info`/`runenv_info`)

**Status**: ✅ Compliant

### packages/sparetools-cpython/test_package/conanfile.py

- **Path**: `packages/sparetools-cpython/test_package/conanfile.py`
- **Has test_package**: ❌
- **Conan API**: ℹ️ No environment info (may be library-only)

**Issues:**
- ❌ Missing required field: name
- ❌ Missing required field: version

**Warnings:**
- ⚠️ Missing recommended field: description
- ⚠️ Missing recommended field: license
- ⚠️ Missing package_type field (recommended for Conan 2.x)

**Status**: ❌ Has issues

### sparetools-openssl-tools

- **Path**: `packages/sparetools-openssl-tools/conanfile.py`
- **Version**: 2.0.0
- **Package Type**: `python-require`
- **Description**: Complete OpenSSL tools for SpareTools ecosystem
- **License**: Apache-2.0
- **Dependencies**:
  - python_requires: sparetools-base/2.0.0
- **Has test_package**: ❌
- **Conan API**: ✅ Uses Conan 2.x API (`buildenv_info`/`runenv_info`)

**Status**: ✅ Compliant

### sparetools-openssl

- **Path**: `packages/sparetools-openssl/conanfile.py`
- **Version**: 3.3.2
- **Package Type**: `library`
- **Description**: Unified OpenSSL package with multiple build method support
- **License**: Apache-2.0
- **Dependencies**:
  - tool_requires: sparetools-openssl-tools/2.0.0, sparetools-cpython/3.12.7
  - python_requires: sparetools-base/2.0.0
  - requires: sparetools-openssl-tools/2.0.0, sparetools-cpython/3.12.7
- **Has test_package**: ✅
- **Conan API**: ⚠️ Has `package_info` but no environment info

**Status**: ✅ Compliant

### packages/sparetools-openssl/test_package/conanfile.py

- **Path**: `packages/sparetools-openssl/test_package/conanfile.py`
- **Has test_package**: ❌
- **Conan API**: ℹ️ No environment info (may be library-only)

**Issues:**
- ❌ Missing required field: name
- ❌ Missing required field: version

**Warnings:**
- ⚠️ Missing recommended field: description
- ⚠️ Missing recommended field: license
- ⚠️ Missing package_type field (recommended for Conan 2.x)

**Status**: ❌ Has issues

### sparetools-shared-dev-tools

- **Path**: `packages/sparetools-shared-dev-tools/conanfile.py`
- **Version**: 2.0.0
- **Package Type**: `python-require`
- **Description**: Shared development tools for SpareTools ecosystem
- **License**: Apache-2.0
- **Dependencies**:
  - python_requires: sparetools-base/2.0.0
- **Has test_package**: ✅
- **Conan API**: ✅ Uses Conan 2.x API (`buildenv_info`/`runenv_info`)

**Status**: ✅ Compliant

### packages/sparetools-shared-dev-tools/test_package/conanfile.py

- **Path**: `packages/sparetools-shared-dev-tools/test_package/conanfile.py`
- **Dependencies**:
  - python_requires: sparetools-shared-dev-tools/[>=2.0.0]
- **Has test_package**: ❌
- **Conan API**: ℹ️ No environment info (may be library-only)

**Issues:**
- ❌ Missing required field: name
- ❌ Missing required field: version

**Warnings:**
- ⚠️ Missing recommended field: description
- ⚠️ Missing recommended field: license
- ⚠️ Missing package_type field (recommended for Conan 2.x)

**Status**: ❌ Has issues

## Recommendations

### Test Package Coverage

Packages missing test_package directories:
- `` (packages/sparetools-bootstrap/test_package/conanfile.py)
- `` (packages/sparetools-shared-dev-tools/test_package/conanfile.py)
- `` (packages/sparetools-openssl/test_package/conanfile.py)
- `` (packages/sparetools-cpython/test_package/conanfile.py)
