# Deprecated Workflows

This directory contains GitHub Actions workflows that have been deprecated due to consolidation and optimization efforts.

## Deprecated Workflow List

### build-test.yml
**Deprecated:** 2025-11-03
**Reason:** Duplicate functionality with `ci.yml`
**Replacement:** Use `ci.yml` which provides comprehensive multi-platform testing with better caching

### build-and-test.yml
**Deprecated:** 2025-11-03
**Reason:** Duplicate functionality with `ci.yml`
**Replacement:** Use `ci.yml` for all PR and main branch testing

### deploy-cloudsmith.yml
**Deprecated:** 2025-11-03
**Reason:** Functionality merged into `publish.yml`
**Replacement:** Use `publish.yml` which supports both Cloudsmith and GitHub Packages with dependency ordering

### integration.yml
**Deprecated:** 2025-11-03
**Reason:** Complex workflow with overlapping responsibilities; integration tests now in `ci.yml`
**Replacement:** Use `ci.yml` for PR testing and `nightly.yml` for comprehensive regression testing

### build-cpython-matrix.yml
**Deprecated:** 2025-11-03
**Reason:** CPython builds now handled by main CI workflows
**Replacement:** Use `ci.yml` or `nightly.yml` which include CPython package builds in dependency chain

## Active Production Workflows

The following workflows remain active and are the canonical implementations:

1. **ci.yml** - Continuous Integration (PR validation, main branch testing)
2. **publish.yml** - Package publishing to Cloudsmith and GitHub Packages
3. **security.yml** - Security scanning (Trivy, Syft, CodeQL, FIPS)
4. **nightly.yml** - Comprehensive nightly regression testing
5. **release.yml** - Release management and version tagging
6. **openssl-perl-preconfigure.yml** - OpenSSL Perl Configure preprocessing (experimental)
7. **openssl-upstream-preconfigure.yml** - OpenSSL upstream validation (experimental)

## Workflow Documentation

For complete workflow documentation, see:
- [docs/CI-CD-DOCUMENTATION-INDEX.md](../../../docs/CI-CD-DOCUMENTATION-INDEX.md)
- [docs/CI-CD-IMPLEMENTATION-COMPLETE.md](../../../docs/CI-CD-IMPLEMENTATION-COMPLETE.md)
- [docs/CI-CD-OPERATIONS-GUIDE.md](../../../docs/CI-CD-OPERATIONS-GUIDE.md)

## Removal Timeline

These workflows will remain in the `deprecated/` directory until:
- All documentation references updated (target: 2025-11-10)
- Validation of active workflows complete (target: 2025-11-10)
- No workflow triggers or dependencies remain (verification: 2025-11-30)

After this grace period, they will be removed entirely.
