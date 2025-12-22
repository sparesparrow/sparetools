# SpareTools Ecosystem Versioning Strategy

## Overview
The SpareTools ecosystem uses semantic versioning (MAJOR.MINOR.PATCH) with a unified release cycle across all projects. This ensures consistent dependency management and predictable release schedules.

## Version Schema

### Ecosystem Version (sparetools/VERSION.txt)
- **Format**: `MAJOR.MINOR.PATCH`
- **Current**: `2.0.0`
- **Purpose**: Defines the overall ecosystem release version
- **Scope**: Applies to all projects in the MIA ecosystem

### Project Versions
All projects align their major and minor versions with the ecosystem version:

| Project | Version File | Version | Alignment |
|---------|-------------|---------|-----------|
| sparetools | VERSION.txt | 2.0.0 | Master version |
| mia | VERSION.txt | 2.0.0 | Ecosystem aligned |
| mia-project | pyproject.toml | 2.0.0 | Ecosystem aligned |

### Package Versions
Individual Conan packages follow semantic versioning based on their specific functionality:

| Package | Version | Reason |
|---------|---------|--------|
| sparetools-cpython | 3.12.7 | Python runtime version |
| sparetools-openssl | 3.3.2 | OpenSSL library version |
| sparetools-base | 2.0.0 | Ecosystem aligned |
| sparetools-obd-sim | 2.0.0 | Ecosystem aligned |
| sparetools-mcp-orchestrator | 2.0.0 | Ecosystem aligned |

## Release Cycle

### Major Releases (X.0.0)
- Breaking changes across the ecosystem
- Major architectural changes
- Updated when ecosystem compatibility changes

### Minor Releases (2.X.0)
- New features added to existing projects
- Backward-compatible API changes
- Updated when new functionality is added

### Patch Releases (2.0.X)
- Bug fixes and security patches
- No breaking changes
- Updated for critical fixes and improvements

## Version Update Process

1. **Ecosystem Release**: Update `sparetools/VERSION.txt`
2. **Project Alignment**: Update all project VERSION.txt files
3. **Package Updates**: Update Conan packages as needed
4. **CI/CD**: Automated version propagation through pipelines
5. **Documentation**: Update version references in docs

## Dependencies

### Internal Dependencies
- All MIA projects depend on SpareTools packages
- Version ranges allow patch-level updates: `sparetools-base/[>=2.0.0 <3.0.0]`

### External Dependencies
- OpenSSL: Follows upstream version (3.3.2)
- Python: Follows runtime version (3.12.7)
- Other libraries: Semantic versioning as appropriate

## Migration Guide

### From v1.x to v2.0.0
- Update all Conan package references
- Review breaking changes in release notes
- Update CI/CD pipelines for new version schema

## Version Validation

### Automated Checks
- CI/CD validates version consistency across projects
- Conan package resolution tests version compatibility
- Integration tests verify end-to-end version alignment

### Manual Verification
```bash
# Check version alignment
./scripts/validate-versions.sh

# Verify package compatibility
conan install . --build=missing
```

## Future Considerations

- Consider calendar versioning for patch releases
- Implement automated version bumping in CI/CD
- Add version metadata to packages for better traceability