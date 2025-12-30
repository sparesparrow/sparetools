# SpareTools Version Management

Comprehensive version management system for Conan packages with automatic increment validation, conflict prevention, and semantic versioning enforcement.

## Overview

This system ensures that Conan package versions are properly managed across the entire SpareTools ecosystem. It prevents version conflicts, enforces semantic versioning, and provides automated version bumping capabilities.

## Key Features

- **🔒 Version Increment Enforcement**: Pre-commit hooks prevent commits without version bumps
- **🚫 Conflict Prevention**: PR validation blocks duplicate versions across branches
- **🤖 Automatic Bumping**: Intelligent version increment based on commit messages
- **📊 Semantic Versioning**: Strict adherence to MAJOR.MINOR.PATCH format
- **🔍 Validation**: Multi-layer validation at commit, PR, and CI levels

## Version Increment Rules

### When Versions MUST Be Incremented

| Scenario | Branch Type | Action | Reason |
|----------|-------------|--------|--------|
| **Feature Development** | `feature/*` | Increment required | Each feature branch represents new development |
| **Bug Fixes** | Any branch | Increment required | Bug fixes change package behavior |
| **API Changes** | Any branch | Increment required | API changes affect consumers |
| **Release Preparation** | `release/*`, `hotfix/*` | Increment required | Releases need unique version |
| **Main Branch** | `main`, `develop` | Increment required | Protected branches require version progression |

### When Versions Can Stay The Same

| Scenario | Branch Type | Action | Reason |
|----------|-------------|--------|--------|
| **Documentation** | Any branch | No increment needed | Docs don't affect package functionality |
| **CI/CD Changes** | Any branch | No increment needed | Build changes don't affect package |
| **Test Updates** | Any branch | No increment needed | Tests don't affect package interface |

## Usage

### Automatic Version Bumping

```bash
# Bump patch version (1.0.0 → 1.0.1)
python3 scripts/bump_version.py patch

# Bump minor version (1.0.0 → 1.1.0)
python3 scripts/bump_version.py minor

# Bump major version (1.0.0 → 2.0.0)
python3 scripts/bump_version.py major

# Auto-detect bump type from commits
python3 scripts/bump_version.py auto
```

### Manual Version Management

```bash
# Edit conanfile.py directly
version = "1.0.1"

# Update VERSION file
echo "1.0.1" > VERSION
```

### Validation Commands

```bash
# Validate all version increments
python3 scripts/check_version_increment.py --all

# Validate specific conanfile
python3 scripts/check_version_increment.py --conanfile packages/foundation/sparetools-base/conanfile.py

# Dry-run version bump
python3 scripts/bump_version.py patch --dry-run
```

## Commit Message Conventions

The auto-bumping feature analyzes commit messages to determine version increment type:

### Major Version (X.0.0)
```bash
git commit -m "breaking: remove deprecated API endpoint

- Removes /api/v1/legacy endpoint
- Breaks backward compatibility
- Update client code required
"
```

### Minor Version (X.Y.0)
```bash
git commit -m "feat: add user authentication system

- Implements OAuth2 flow
- Adds JWT token validation
- Backward compatible API
"
```

### Patch Version (X.Y.Z)
```bash
git commit -m "fix: resolve memory leak in connection pool

- Fix resource cleanup in ConnectionPool.close()
- Add proper exception handling
- No API changes
"
```

## Quality Gates

### 1. Pre-Commit Hook
Runs automatically on `git commit`:

```bash
🔍 Running pre-commit checks...
📦 Checking Conan package version increments...
🔧 Validating Conan structure...
🔐 Checking for potential secret leaks...
✅ All pre-commit checks passed!
```

**Blocks commits that:**
- Don't increment versions when required
- Have invalid version formats
- Contain potential secrets

### 2. PR Validation
GitHub Actions workflow validates PRs:

```yaml
# .github/workflows/pr-version-validation.yml
- Validates version increment requirements
- Checks for conflicts with main branch
- Enforces semantic versioning format
- Suggests appropriate bump types
```

**Blocks PR merges that:**
- Have version conflicts with target branch
- Use invalid semantic version format
- Don't follow version increment rules

### 3. CI/CD Enforcement
Post-merge validation on protected branches:

```yaml
# .github/workflows/version-enforcement.yml
- Enforces version progression on main/develop
- Creates version tags automatically
- Updates version documentation
- Prevents conflicts across branches
```

## Version Format Standards

### Valid Formats
```
1.0.0          # Release version
1.0.1          # Patch release
1.1.0          # Minor release
2.0.0          # Major release
1.0.0-alpha    # Pre-release
1.0.0-beta.1   # Pre-release with build
```

### Invalid Formats
```
1.0             # Missing patch version
1.0.0.0         # Too many components
1.0.0-SNAPSHOT  # Non-standard pre-release
v1.0.0          # Version prefix not allowed
```

## Branch-Specific Rules

### Feature Branches (`feature/*`)
- **Version Increment**: Required
- **Validation**: Strict increment checking
- **Merge**: Blocked if version not incremented

### Release Branches (`release/*`, `hotfix/*`)
- **Version Increment**: Required
- **Validation**: Strict increment checking
- **Merge**: Automatic version tag creation

### Main Branch (`main`)
- **Version Increment**: Required for all changes
- **Validation**: Strict increment checking
- **Merge**: Automatic documentation updates

### Develop Branch (`develop`)
- **Version Increment**: Required for all changes
- **Validation**: Strict increment checking
- **Merge**: Integration testing required

## Conflict Resolution

### Version Conflicts
When multiple branches have the same version:

```bash
# Check for conflicts
python3 scripts/check_version_increment.py --all

# Resolve by incrementing
python3 scripts/bump_version.py patch

# Verify resolution
python3 scripts/check_version_increment.py --all
```

### Merge Conflicts
When merging branches with version changes:

```bash
# After merge conflict resolution
python3 scripts/check_version_increment.py --all

# Re-bump if needed
python3 scripts/bump_version.py patch
```

## Automated Version Bumping

### Commit-Based Auto-Bumping
The system analyzes commit messages to determine bump type:

| Commit Pattern | Bump Type | Example |
|----------------|-----------|---------|
| `breaking:`, `break:` | Major | `breaking: remove old API` |
| `feat:`, `feature:` | Minor | `feat: add new endpoint` |
| `fix:`, `bug:` | Patch | `fix: resolve crash` |
| Other | Patch | `refactor: cleanup code` |

### Manual Override
Override auto-detection with explicit bump commands:

```bash
# Force major bump regardless of commits
python3 scripts/bump_version.py major

# Force minor bump for feature additions
python3 scripts/bump_version.py minor
```

## Integration with CI/CD

### GitHub Actions Integration

```yaml
# PR validation
- name: Validate version increments
  run: python3 scripts/check_version_increment.py --all

# Release automation
- name: Create version tag
  if: contains(github.event.head_commit.message, 'release:')
  run: |
    VERSION=$(cat VERSION)
    git tag "v$VERSION"
    git push origin "v$VERSION"
```

### Pre-commit Integration

```yaml
# .pre-commit-config.yaml
- id: validate-version-increment
  name: Validate Conan package version increments
  entry: python3 scripts/check_version_increment.py --all
  language: system
  files: conanfile\.py$
```

## Troubleshooting

### Common Issues

**"Version increment validation failed"**
```bash
# Solution: Bump version and commit
python3 scripts/bump_version.py patch
git add conanfile.py
git commit -m "bump: version to X.Y.Z"
```

**"Version conflict with main branch"**
```bash
# Solution: Check what version main has and increment beyond it
git log --oneline origin/main -- conanfile.py
python3 scripts/bump_version.py patch
```

**"Invalid semantic version format"**
```bash
# Solution: Fix version format in conanfile.py
# Valid: version = "1.0.0"
# Invalid: version = "1.0", version = "v1.0.0"
```

### Debug Commands

```bash
# Check current version status
python3 scripts/check_version_increment.py --all --verbose

# See version history
git log --oneline -- conanfile.py

# Check for version conflicts
python3 scripts/check_version_increment.py --all
```

## Advanced Configuration

### Custom Bump Rules

Modify `scripts/bump_version.py` to customize bump logic:

```python
def determine_bump_type_from_commits(self, commits: List[str]) -> str:
    """Customize bump type determination."""
    # Your custom logic here
    pass
```

### Version Validation Rules

Modify `scripts/check_version_increment.py` for custom validation:

```python
def should_increment_version(self, conanfile_path: Path, current_version: str) -> Tuple[bool, str]:
    """Customize increment requirements."""
    # Your custom logic here
    pass
```

## Best Practices

### Development Workflow
1. **Feature branches**: Always bump version before PR
2. **Commit messages**: Use conventional commit format
3. **PR validation**: Address version validation failures
4. **Merge to main**: Ensure clean version progression

### Version Planning
1. **Major releases**: Plan breaking changes carefully
2. **Minor releases**: Group feature additions
3. **Patch releases**: Regular bug fix deployments

### Team Coordination
1. **Version ownership**: Assign version bump responsibility
2. **Release planning**: Coordinate version increments
3. **Branch management**: Keep branches version-conflict-free

## Migration Guide

### From Manual Versioning
1. Install pre-commit hooks: `pre-commit install`
2. Run initial validation: `python3 scripts/check_version_increment.py --all`
3. Fix any issues found
4. Enable version enforcement workflows

### From Different Versioning Scheme
1. Audit current versions
2. Plan migration path
3. Update all packages to semantic versions
4. Enable validation system

## Support

### Getting Help
- Check validation output for specific error messages
- Review commit history for version patterns
- Run debug commands for detailed information

### Common Solutions
- **Version stuck**: Check branch protection rules
- **Conflicts**: Coordinate with team on version increments
- **Validation fails**: Review commit message conventions

This version management system ensures reliable, conflict-free package versioning across the entire SpareTools ecosystem while maintaining semantic versioning standards and preventing deployment issues.