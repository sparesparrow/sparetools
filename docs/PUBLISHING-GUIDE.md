# SpareTools Publishing Guide

This guide explains how to publish SpareTools packages and artifacts to Cloudsmith and GitHub Packages, including the different publishing modes and workflows.

## 📋 Overview

SpareTools uses a multi-channel publishing strategy with safety controls:

- **Cloudsmith**: Primary binary distribution for Conan packages
- **GitHub Packages**: Secondary mirror for Conan packages
- **GitHub Releases**: Distribution of zipapps and release artifacts

Publishing follows a **mixed dry-run + production** model to ensure safety:

- **PR/feature branches**: Dry-run validation only
- **Main branch**: Build validation (no publishing)
- **Tagged releases**: Full production publishing

## 🔑 Required Secrets

### Repository Secrets (GitHub Settings → Secrets and variables → Actions)

| Secret | Purpose | Required For |
|--------|---------|--------------|
| `CLOUDSMITH_API_KEY` | Authentication for Cloudsmith publishing | Cloudsmith publishing |
| `GITHUB_TOKEN` | Automatic token for GitHub operations | GitHub Packages + Releases |

### Setting Up Secrets

1. **Cloudsmith API Key**:
   ```bash
   # Get your API key from https://cloudsmith.io/user/settings/api-keys/
   # Add as CLOUDSMITH_API_KEY in repository secrets
   ```

2. **GitHub Token**: Automatically provided by GitHub Actions (no setup needed)

## 📦 Artifacts and Channels

### Conan Packages

| Package | Channel | Version Sync | Description |
|---------|---------|--------------|-------------|
| `sparetools-base` | Production | ✅ Main version | Core utilities and security gates |
| `sparetools-cpython` | Production | ❌ Independent (3.12.7) | Python runtime |
| `sparetools-shared-dev-tools` | Production | ✅ Main version | Development tools |
| `sparetools-bootstrap` | Production | ✅ Main version | Bootstrap utilities |
| `sparetools-openssl-tools` | Production | ✅ Main version | OpenSSL build tools |
| `sparetools-obd-sim` | Production | ✅ Main version | OBD-II simulation |
| `sparetools-mcp-orchestrator` | Production | ✅ Main version | MCP orchestration |
| `sparetools-openssl` | Production | ❌ Independent (versioned) | OpenSSL builds |

### Zipapps (CLI Tools)

All 15+ zipapps defined in `scripts/build/zipapps.yaml` are published to GitHub Releases.

## 🚀 Publishing Workflows

### 1. Pull Request / Feature Branch (Dry-Run Only)

**Trigger**: Any PR or push to non-main branches affecting publishable code

**What Happens**:
- ✅ Builds all Conan packages
- ✅ Runs version validation
- ✅ Dry-run upload to both registries (no actual publishing)
- ✅ Builds zipapps and uploads as artifacts (no release attachment)
- ❌ No actual publishing to registries
- ❌ No GitHub release creation

**Purpose**: Validate that code builds and would publish successfully

### 2. Main Branch Push (Validation Only)

**Trigger**: Push to `main` or `develop` branch

**What Happens**:
- ✅ Builds all Conan packages
- ✅ Runs version validation
- ✅ Dry-run upload validation
- ✅ Builds zipapps
- ❌ No actual publishing
- ❌ No release creation

**Purpose**: Ensure main branch is always publish-ready

### 3. Tagged Release (Full Production)

**Trigger**: Git tag push (e.g., `git tag v2.0.1 && git push origin v2.0.1`)

**What Happens**:
- ✅ Full build of all packages
- ✅ Version validation against tag
- ✅ **ACTUAL PUBLISHING** to Cloudsmith
- ✅ **ACTUAL PUBLISHING** to GitHub Packages
- ✅ Zipapp building and attachment to GitHub Release
- ✅ GitHub Release creation with changelog

**Purpose**: Official releases to production registries

### 4. Manual Publishing (Workflow Dispatch)

**Trigger**: Manual trigger via GitHub Actions UI

**Parameters**:
- `version`: OpenSSL version (e.g., "3.3.2")
- `registry`: "cloudsmith", "github", or "both"
- `mode`: "production" or "dry-run"

**Purpose**: Emergency publishing or testing specific versions

## 🛠️ Version Management

### Version Synchronization

SpareTools maintains version synchronization across multiple files:

- `VERSION.txt`: Main version (e.g., "2.0.1")
- Foundation package `conanfile.py` files: Match main version
- Independent packages: Have their own versioning schemes

### Version Bumping

Use the version management script for coordinated updates:

```bash
# Validate current versions
python scripts/release/bump-version.py validate

# Bump patch version (2.0.0 -> 2.0.1)
python scripts/release/bump-version.py patch

# Bump minor version (2.0.0 -> 2.1.0)
python scripts/release/bump-version.py minor

# Bump major version (2.0.0 -> 3.0.0)
python scripts/release/bump-version.py major

# Dry-run version bump
python scripts/release/bump-version.py patch --dry-run
```

### Release Process

1. **Prepare Release**:
   ```bash
   # Validate versions are consistent
   python scripts/release/bump-version.py validate

   # Bump version if needed
   python scripts/release/bump-version.py patch

   # Commit changes
   git add .
   git commit -m "Bump version to X.Y.Z"
   ```

2. **Create Git Tag**:
   ```bash
   # Create annotated tag
   git tag -a vX.Y.Z -m "Release version X.Y.Z"

   # Push tag to trigger release
   git push origin vX.Y.Z
   ```

3. **Monitor Release**:
   - Check GitHub Actions for publish workflow completion
   - Verify packages appear in Cloudsmith and GitHub Packages
   - Confirm GitHub Release is created with zipapps attached

## 🔍 Verification and Troubleshooting

### Check Published Packages

**Cloudsmith**:
```bash
# List all SpareTools packages
conan list "sparetools-*/*" -r sparesparrow-conan

# Check specific package
conan list "sparetools-base/2.0.0" -r sparesparrow-conan
```

**GitHub Packages**:
```bash
# Add GitHub Packages remote
conan remote add github-packages \
  https://maven.pkg.github.com/YOUR_USERNAME/sparetools \
  --force || true

# List packages
conan list "sparetools-*/*" -r github-packages
```

### Common Issues

#### ❌ CLOUDSMITH_API_KEY not configured
**Solution**: Add the secret in GitHub repository settings

#### ❌ Version mismatch
**Solution**:
```bash
# Check version consistency
python scripts/release/bump-version.py validate

# Fix inconsistencies
python scripts/release/bump-version.py patch --dry-run  # See what would change
python scripts/release/bump-version.py patch            # Apply changes
```

#### ❌ Package build fails
**Solution**: Check the build logs in GitHub Actions and fix build issues locally

#### ❌ Upload fails
**Solution**: Check credentials and network connectivity

## 📋 Registry URLs

### Cloudsmith
- **Base URL**: https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/
- **Web UI**: https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/

### GitHub Packages
- **Base URL**: https://maven.pkg.github.com/YOUR_USERNAME/sparetools
- **Web UI**: https://github.com/YOUR_USERNAME/sparetools/packages

## 🔄 CI/CD Integration

### Workflows

1. **`publish.yml`**: Main publishing workflow for Conan packages
2. **`zipapps.yml`**: Zipapp building and distribution
3. **`release.yml`**: Version management and release automation (planned)

### Triggers

| Event | Workflow | Action |
|-------|----------|--------|
| PR/Push (non-main) | publish.yml | Dry-run validation |
| Push (main) | publish.yml | Build validation |
| Tag (v*) | publish.yml | Production publish |
| Tag (v*) | zipapps.yml | Build + attach zipapps |
| Manual | publish.yml | Configurable publish |

## 📚 Related Documentation

- [Package Reference](PACKAGES.md) - All available packages
- [Zipapp Distribution](ZIPAPP-DISTRIBUTION.md) - CLI tool distribution
- [CI/CD Guide](../docs/CI-CD-GUIDE.md) - Build and test automation
- [README.md](../README.md) - Quick start and overview

## 🆘 Support

For publishing issues:
1. Check GitHub Actions logs for detailed error messages
2. Validate local builds before pushing
3. Ensure all required secrets are configured
4. Check registry status and network connectivity

**Repository**: https://github.com/sparesparrow/sparetools
**Issues**: https://github.com/sparesparrow/sparetools/issues
