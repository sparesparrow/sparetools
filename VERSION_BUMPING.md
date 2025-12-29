# SpareTools Version Bumping Guide

This document explains how to automatically bump versions for SpareTools packages.

## Overview

SpareTools uses a centralized version management system that automatically updates both the central `versions.yaml` file and individual `conanfile.py` files when versions are bumped.

## Version Bumping Script

The `version_bump.py` script provides automatic version management:

### Usage

```bash
# Bump a specific package
python version_bump.py --package <package_name> --type <major|minor|patch>

# Bump all packages
python version_bump.py --all --type <major|minor|patch>

# Set a specific version
python version_bump.py --set <package_name> <version>
```

### Examples

```bash
# Bump sparetools-base minor version (2.0.3 → 2.1.0)
python version_bump.py --package sparetools-base --type minor

# Bump all packages patch version
python version_bump.py --all --type patch

# Set sparetools-cpython to a specific version
python version_bump.py --set sparetools-cpython 3.12.8
```

### What it does

1. **Updates versions.yaml**: Modifies the central version configuration file
2. **Updates conanfile.py**: Updates the `version = "x.y.z"` line in each package's conanfile.py
3. **Maintains consistency**: Ensures all references to package versions are synchronized

### Supported Packages

The script automatically detects and updates packages defined in `versions.yaml`:

- **Foundation packages**: base, bootstrap, cpython, test-framework, etc.
- **Embedded packages**: lvgl, hal-sunton, embedded, etc.
- **Aerospace packages**: aerospace
- **Security packages**: crypto-suite

## Version Format

SpareTools uses [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes (1.0.0 → 2.0.0)
- **MINOR**: New features, backward compatible (1.0.0 → 1.1.0)
- **PATCH**: Bug fixes, backward compatible (1.0.0 → 1.0.1)

## Workflow for Releasing

1. **Development**: Work on features/fixes
2. **Test**: Ensure all packages build correctly
3. **Version Bump**: Use the script to bump appropriate versions
4. **Commit**: Commit the version changes
5. **Build & Upload**: Build and upload packages to Cloudsmith
6. **Tag**: Create a git tag for the release

### Example Release Workflow

```bash
# After completing development work
python version_bump.py --package sparetools-base --type minor
python version_bump.py --package sparetools-cpython --type patch

# Build and test all packages
./build_all.sh

# Upload to Cloudsmith
./publish_with_cloudsmith_cli.sh

# Commit and tag
git add .
git commit -m "Bump versions: base to 2.1.0, cpython to 3.12.8"
git tag v2.1.0
git push && git push --tags
```

## Integration with CI/CD

The version bumping script can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Bump Version
  run: python version_bump.py --all --type patch

- name: Build and Upload
  run: ./publish_with_cloudsmith_cli.sh
```

## Troubleshooting

### Package not found
- Ensure the package name matches exactly as defined in `versions.yaml`
- Use `sparetools-` prefix for consistency

### Conanfile not updated
- Check that the conanfile.py has a `version = "x.y.z"` line
- The script searches for the pattern `version = "..."` to update

### Version format errors
- Versions must follow semantic versioning (x.y.z)
- Complex versions like "3.12.7+dev1" are supported

## Benefits

- **Consistency**: All version references stay synchronized
- **Automation**: Eliminates manual version updates across multiple files
- **Safety**: Reduces risk of version mismatches
- **Speed**: Quickly bump versions for releases
- **Traceability**: Clear version history in git
