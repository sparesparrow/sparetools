# SpareTools: OpenSSL DevOps Ecosystem

## Project Overview
SpareTools provides comprehensive DevOps tooling for OpenSSL ecosystem management, build automation, and deployment orchestration. This repo contains Conan package recipes, build scripts, CI/CD configurations, and validation tools.

## Quick Reference
Related Architecture: See [MIA](https://github.com/sparesparrow/mia) for the main IoT control system.

## Tasks

### Phase 1: Consolidation & Cleanup
- [ ] Audit all existing Conan recipes in `packages/`
- [ ] Validate OpenSSL 3.3.2 compatibility across all recipes
- [ ] Update CI/CD workflows in `.github/workflows/`
- [ ] Consolidate documentation in `docs/`
- [ ] Remove obsolete build configurations

### Phase 2: Integration with MIA
- [ ] Ensure sparetools Conan packages are importable from MIA's `conanfile.py`
- [ ] Test cross-repo dependency resolution
- [ ] Document Conan setup for MIA contributors

### Phase 3: Quality & Testing
- [ ] Unit tests for all build scripts
- [ ] Integration tests with real OpenSSL builds
- [ ] Validation suite (`validate-*.py` scripts)

## Key Files
- `packages/`: Conan recipe definitions
- `scripts/`: Build and deployment scripts
- `test/`: Test suite and validation tools
- `_Build/`: Build artifacts directory
- `.github/workflows/`: CI/CD pipeline definitions

## Contributors
- DevOps maintainer: TBD

## Notes
- All recipes must pass `pytest` validation
- OpenSSL 3.x targets only (legacy support via separate branch if needed)
- Conan 2.x+ required
