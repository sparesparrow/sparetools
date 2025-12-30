---
description: Git-based versioning rules for SpareTools Conan packages
alwaysApply: true
---

# SpareTools Versioning Rules

## Core Principles

### Git-Based Versioning (Primary Method)
- **All conanfile.py files MUST use git-based versioning**
- Pattern: `version = os.environ.get('CONAN_BUILD_VERSION', 'fallback_version')`
- `CONAN_BUILD_VERSION` is set by git-to-conan collector from git tags/branches
- Fallback version is used for local development

### Version Increment Requirements
- **Every change to a branch MUST result in a new version**
- Pull requests with same conanfile version as base branch MUST fail or auto-increment
- Version tracking prevents duplicate builds of the same git reference

### Version Format Standards
- **Development branches**: `develop_{timestamp}_{sha}` or raw branch name
- **Feature branches**: `feature_{name}_{timestamp}_{sha}` or raw branch name
- **Release tags**: Semantic versioning (e.g., `1.0.0`, `2.3.1`)
- **Snapshots**: `{version}+dev` or `{version}-SNAPSHOT`

## Implementation Requirements

### conanfile.py Structure
```python
from conan import ConanFile
import os  # Required for CONAN_BUILD_VERSION

class MyPackageConan(ConanFile):
    name = "my-package"
    # MUST use git-based versioning
    version = os.environ.get('CONAN_BUILD_VERSION', '1.0.0')
    # ... rest of conanfile
```

### Dependencies
- Use `sparetools-versioning/1.0.0` as `python_requires` for versioning utilities
- Use `sparetools-base/2.0.3` for foundation utilities

### Pre-commit Hooks
- Validate version increment on branch changes
- Check that conanfile.py uses git-based versioning pattern
- Fail if PR has same version as base branch

### CI/CD Integration
- Set `CONAN_BUILD_VERSION` from git reference before `conan create`
- Track processed versions in YAML skip list
- Upload packages to remote after successful build

## Versioning Tools

### Git-to-Conan Collector
- Located in `sparetools-versioning` package
- Processes git tags/branches and creates Conan packages
- Sets `CONAN_BUILD_VERSION` environment variable
- Tracks processed items to prevent duplicates

### Version Manager
- Tracks package usage and last used timestamps
- Manages YAML skip list for processed builds
- Enables cleanup of old packages

## Validation Rules

1. **Version Pattern Check**: All conanfile.py must match pattern `os.environ.get('CONAN_BUILD_VERSION', ...)`
2. **Version Increment Check**: PRs must increment version or fail validation
3. **Version Tracking**: Processed versions must be tracked in skip list
4. **Git Reference**: Version must be derived from git tag/branch/commit

