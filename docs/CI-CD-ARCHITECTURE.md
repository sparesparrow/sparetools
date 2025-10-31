# CI/CD Architecture & Design

**Date:** October 31, 2025 | **Status:** Production | **Audience:** Architects, Tech Leads

---

## Design Philosophy

The SpareTools CI/CD architecture prioritizes:

1. **Simplicity** - Straightforward workflow structure, minimal complexity
2. **Reliability** - Fail-safe defaults, comprehensive error handling
3. **Flexibility** - Support multiple build methods and platforms
4. **Sustainability** - Easy to maintain, well-documented
5. **Security** - Security gates, SBOM generation, vulnerability scanning

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Repository                         │
│  (sparesparrow/sparetools)                                  │
└─────────────────────────────────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
    ┌─────────┐     ┌──────────┐    ┌──────────┐
    │  ci.yml │     │publish.  │    │security. │
    │         │     │yml       │    │yml       │
    └────┬────┘     └──┬───────┘    └──┬───────┘
         │              │                │
         │ Tests        │ Publishes      │ Scans
         │              │                │
    ┌────▼──────────────▼────────────────▼─────┐
    │         GitHub Actions Runners             │
    │  (Ubuntu, macOS, Windows)                 │
    └────┬──────────────┬────────────────┬─────┘
         │              │                │
    ┌────▼──┐    ┌──────▼─────┐   ┌─────▼────┐
    │ Conan  │    │ Cloudsmith  │   │ GitHub   │
    │ Cache  │    │ Repository  │   │ Packages │
    └────────┘    └─────────────┘   └──────────┘
```

---

## Workflow Architecture

### 1. **ci.yml** - Continuous Integration

**Purpose:** Test code on every push and PR

**Design:**
- Triggers on push to main/develop and all PRs
- Skip docs-only changes (efficiency)
- Run on 3 platforms in parallel (coverage)
- Use Conan cache for speed
- Test all 7 packages

**Flow:**
```
Event: push/PR
  ↓
Change Detection (skip docs-only)
  ↓
Setup (install deps, cache)
  ↓
Build All Packages (parallel on 3 platforms)
  ↓
Integration Tests (test_package)
  ↓
Upload Artifacts
  ↓
Report Status
```

**Tier-based approach:**
- **Tier 1 (Critical):** Must always pass
- **Tier 2 (Advanced):** Nice to have
- **Tier 3 (Experimental):** Can fail

---

### 2. **publish.yml** - Package Publishing

**Purpose:** Publish approved packages to registries

**Design:**
- Triggers on push to main and version tags
- Dual-registry strategy (Cloudsmith primary, GitHub secondary)
- Ordered builds (base → cpython → tools → openssl)
- Retry logic for reliability
- Create GitHub releases for tags

**Flow:**
```
Event: push main OR tag v*
  ↓
Build Base Package
  ↓
Build CPython (depends on base)
  ↓
Build Tools (depends on cpython)
  ↓
Build OpenSSL (depends on tools)
  ↓
Upload to Cloudsmith (primary)
  ↓
Upload to GitHub Packages (secondary)
  ↓
Create Release (if tagged)
```

**Dependency Order:**
```
sparetools-base (no deps)
  ↓
sparetools-cpython (needs base)
  ↓
sparetools-openssl-tools (needs cpython)
  ↓
sparetools-openssl (needs tools)
```

---

### 3. **security.yml** - Security Scanning

**Purpose:** Vulnerability scanning, compliance, SBOM generation

**Design:**
- Trivy for filesystem scanning (blocks on CRITICAL)
- Syft for SBOM generation (CycloneDX + SPDX)
- CodeQL for static analysis
- FIPS validation (optional)
- Dependency review on PRs

**Tools:**
| Tool | Purpose | Output |
|------|---------|--------|
| **Trivy** | Vuln scan | SARIF (→ GitHub Security) |
| **Syft** | SBOM | CycloneDX, SPDX |
| **CodeQL** | Static analysis | SARIF (→ GitHub Security) |
| **FIPS Validator** | Compliance | Pass/Fail report |

---

### 4. **nightly.yml** - Regression Testing

**Purpose:** Comprehensive testing every night

**Design:**
- Runs on schedule (02:00 UTC daily)
- Broader test matrix than ci.yml
- Multiple build methods (Perl, CMake)
- Performance baseline measurements
- Auto-creates issues on failure

**Test Scope:**
- All 7 packages
- All 3 platforms
- All build methods
- Multiple configurations

---

### 5. **reusable/build-package.yml** - Shared Build Logic

**Purpose:** DRY principle - shared build steps

**Design:**
- Called by other workflows
- Configurable profiles and build methods
- Comprehensive error handling
- Standardized artifact handling

**Caller Pattern:**
```yaml
- uses: ./.github/workflows/reusable/build-package.yml
  with:
    package: sparetools-openssl
    profile: linux-gcc11
```

---

## Platform Strategy

### Supported Platforms

| Platform | Compiler | Status | Tier |
|----------|----------|--------|------|
| Linux (Ubuntu 22.04) | GCC 11 | ✅ Production | Tier 1 |
| Linux (Ubuntu 22.04) | Clang 18 | ✅ Production | Tier 1 |
| macOS (latest) | AppleClang | ✅ Production | Tier 1 |
| Windows (2022) | MSVC 2022 | ✅ Production | Tier 1 |
| Linux (ARM64) | GCC 11 | ◐ Experimental | Tier 3 |

### Build Methods

| Method | Status | Use Case | Tier |
|--------|--------|----------|------|
| Perl Configure | ✅ Production | OpenSSL 3.6.0+ | Tier 1 |
| CMake | ✅ Production | Modern workflows | Tier 2 |
| Autotools | ◐ Planned | UNIX standard | Tier 2 |
| Python | ◐ Experimental | Orchestration | Tier 3 |

---

## Caching Strategy

### Conan Cache

```yaml
uses: actions/cache@v3
with:
  path: ~/.conan2
  key: conan-${{ matrix.os }}-${{ matrix.compiler }}
```

**Benefits:**
- Reduces build time by ~60%
- Avoids redownloading packages
- Consistent across runs

**Invalidation:**
- When conanfile.py changes
- When dependencies update
- Every 7 days (safety refresh)

---

## Artifact Management

### Storage

**GitHub Actions Storage:**
- Retention: 30 days (default)
- Location: GitHub's servers
- Cost: Unlimited for public repos

**Cloudsmith:**
- Long-term package storage
- Retention: Configurable per package
- Cost: Per plan

### Cleanup

```bash
# Artifacts older than 7 days
gh run list --status completed | tail -n +8 | \
  awk '{print $1}' | xargs -I {} gh run delete {} --confirm
```

---

## Security Architecture

### Secret Management

**Secrets Used:**
1. `CLOUDSMITH_API_KEY` - Package publishing
2. `GITHUB_TOKEN` - GitHub operations (automatic)

**Security Properties:**
- Secrets masked in logs (automatic)
- Secrets not accessible to forks
- Per-secret audit logging
- 90-day rotation recommended

### Vulnerability Scanning

**Three-layer approach:**
1. **Trivy** - Container/filesystem scanning (fast)
2. **CodeQL** - Code analysis (comprehensive)
3. **Dependency Review** - Pull request scanning (prevention)

**CRITICAL Vulnerabilities:**
- Block publish.yml on main
- Allow on PRs (visibility only)
- Auto-create issues on findings

---

## Scalability Considerations

### Current Capacity

- **Workflows:** 5 active
- **Build matrix:** 12 configurations (3 platforms × 4 methods)
- **Packages:** 7 total
- **Execution time:** ~15 minutes per config

### Future Scaling

**If needed:**

1. **More platforms:** Add rows to build matrix
2. **More build methods:** Add columns to build matrix
3. **Longer tests:** Split into nightly only
4. **Parallel jobs:** GitHub supports up to 256 jobs per workflow

**Estimated limits:**
- ~50 platforms before hitting GitHub limits
- ~100 packages before performance degradation
- ~1 hour workflows need optimization

---

## Configuration Management

### Profile-Based Approach

```yaml
# Base profile
profiles/base/linux-gcc11.profile
→ compiler: gcc
→ compiler.version: 11
→ compiler.cppstd: 17

# Build method profile
profiles/build-methods/perl-configure.profile
→ build_method: perl
→ options: [no-shared, threads]

# Feature profile
profiles/features/fips-enabled.profile
→ fips: True
→ validation: strict
```

### Profile Composition

```bash
# Stack profiles to compose configs
conan create . \
  -pr:b base/linux-gcc11.profile \
  -pr:b build-methods/perl-configure.profile \
  -pr:b features/fips-enabled.profile
```

---

## Deployment Strategy

### Release Process

```
Tag Version (v3.3.2)
  ↓
publish.yml triggered
  ↓
Build all packages
  ↓
Upload to Cloudsmith
  ↓
Upload to GitHub Packages
  ↓
Create GitHub Release
  ↓
Users can conan install v3.3.2
```

### Rollback

If version has issues:

```bash
# Delete from Cloudsmith UI or:
# conan remove -c sparetools-openssl/X.Y.Z

# Delete GitHub Release (UI only)
```

---

## Error Handling

### Retry Strategy

**publish.yml:**
```yaml
- name: Upload to Cloudsmith
  run: conan upload ...
  continue-on-error: true

- name: Retry Upload
  if: failure()
  run: sleep 60 && conan upload ...
```

**Rationale:**
- Transient network errors
- Temporary service unavailability
- Registry concurrency issues

### Notifications

- **Failures:** GitHub Actions notifications
- **Issues:** Auto-created on nightly failures
- **Slack:** Configure via GitHub Apps
- **Email:** Enable in GitHub notifications

---

## Cost Analysis

### Current Costs

| Resource | Monthly Cost | Notes |
|----------|-------------|-------|
| GitHub Actions | ~$0 | Free for public repos |
| GitHub Packages | $0 | Free storage |
| Cloudsmith | $0-$500 | Depends on plan |
| Runner Minutes | Unlimited | Public repos |

### Optimization

- Use skip-conditions to avoid unnecessary runs
- Reuse cache to reduce compute
- Consolidate parallel jobs when possible

---

## Future Enhancements

### Planned Features

1. **CMake support** - Already in design
2. **Autotools support** - Need to implement
3. **ARM64 support** - Infrastructure ready
4. **Docker builds** - Multi-arch support
5. **Performance tracking** - Benchmark suite

### Under Consideration

- GPU builds (large binaries)
- Distributed builds (cross-compilation)
- Cache federation (faster pulls)
- ML-based test selection

---

## References

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Conan Documentation](https://docs.conan.io/2/)
- [Cloudsmith Docs](https://help.cloudsmith.io/)
- [Security Best Practices](https://docs.github.com/en/actions/security-guides)

---

**Last Updated:** October 31, 2025
