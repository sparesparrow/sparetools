# Enhanced Version Management System

A hybrid version management system combining the flexibility of OMS with the rigor of SpareTools, providing comprehensive version control, automated validation, and CI/CD integration.

## Overview

This enhanced system addresses the limitations of both traditional approaches:

- **OMS Approach**: Flexible git-based versioning but lacks validation and enforcement
- **SpareTools Approach**: Strict semantic versioning but lacks flexibility for complex builds

The hybrid system provides:
- **Flexible versioning** with git-based metadata (OMS-inspired)
- **Strict validation** and semantic versioning (SpareTools approach)
- **Automated enforcement** at multiple levels
- **CI/CD integration** with intelligent workflows

## Core Components

### 1. Improved Version Manager (`scripts/improved_version_management.py`)

```bash
# Check current version
python3 scripts/improved_version_management.py current

# Generate git-based version (OMS-style)
python3 scripts/improved_version_management.py git-version

# Auto-analyze commits and suggest bump
python3 scripts/improved_version_management.py analyze

# Validate consistency across all files
python3 scripts/improved_version_management.py validate

# Generate comprehensive report
python3 scripts/improved_version_management.py report
```

### 2. Version Increment Validator (`scripts/check_version_increment.py`)

Maintains SpareTools' rigorous validation while adding flexibility:

```bash
# Validate all conanfile versions
python3 scripts/check_version_increment.py --all

# Check specific file
python3 scripts/check_version_increment.py --conanfile path/to/conanfile.py
```

### 3. Automated Version Bumping (`scripts/bump_version.py`)

Intelligent version bumping based on conventional commits:

```bash
# Auto-detect bump type from commits
python3 scripts/bump_version.py auto

# Manual bump types
python3 scripts/bump_version.py major
python3 scripts/bump_version.py minor
python3 scripts/bump_version.py patch
```

## Version Formats

### Static Semantic Versions (SpareTools-style)
```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
2.0.3                    # Release version
2.0.3-alpha              # Pre-release
2.0.3-alpha.1            # Pre-release with build
```

### Dynamic Git-based Versions (OMS-inspired)
```
BASE_VERSION+git.COMMIT_COUNT.gHASH[.dirty]
2.0.3+git.42.gabc1234           # Clean working directory
2.0.3+git.42.gabc1234.dirty     # Modified files present
```

## Quality Gates

### 1. Pre-commit Hooks
Comprehensive validation before commits:

```yaml
# .pre-commit-config.yaml
- id: version-management
  name: Comprehensive version management validation
- id: enforce-version-increment
  name: Enforce version increments for changes
- id: suggest-version-bump
  name: Suggest appropriate version bump
```

### 2. CI/CD Validation
Multi-level validation in GitHub Actions:

```yaml
# PR Validation
- Version increment enforcement
- Conflict detection with target branch
- Semantic versioning validation

# Main Branch Protection
- Version progression validation
- Automatic tagging for releases
- Documentation updates
```

### 3. Automated Version Bumping
Intelligent commit analysis:

```python
# Conventional commit analysis
breaking: message    → Major bump
feat: message        → Minor bump
fix: message         → Patch bump
other                → Patch bump
```

## Branch-Specific Rules

### Feature Branches (`feature/*`)
```yaml
# Rules
- Version increment: Required
- Validation: Strict
- Merge blocking: Yes (if version not incremented)

# Example workflow
1. Make changes
2. Run: python3 scripts/bump_version.py auto
3. Commit changes
4. Create PR (validation passes)
```

### Release Branches (`release/*`, `hotfix/*`)
```yaml
# Rules
- Version increment: Required
- Validation: Strict semantic versioning
- Automatic tagging: Yes

# Example workflow
1. Create release branch
2. Increment version manually
3. Test thoroughly
4. Merge to main (creates tag automatically)
```

### Main Branch (`main`)
```yaml
# Rules
- Version increment: Required for all changes
- Validation: Strict progression
- Automatic processes: Tagging, documentation

# Protection
- Direct pushes blocked
- PRs must pass version validation
- Releases create automatic tags
```

## Automated Workflows

### PR Version Validation
```yaml
name: PR Version Validation
on: pull_request

jobs:
  validate:
    steps:
      - name: Validate version increment
        run: python3 scripts/check_version_increment.py --all

      - name: Check conflicts with main
        run: # Conflict detection logic

      - name: Suggest bump type
        run: python3 scripts/improved_version_management.py analyze
```

### Release Management
```yaml
name: Release Version Management
on:
  push:
    branches: [main]
    paths: [VERSION]

jobs:
  release:
    steps:
      - name: Create version tag
        run: # Automatic tagging

      - name: Generate release notes
        run: # Commit analysis for release notes
```

## Integration Examples

### Development Workflow

```bash
# 1. Make changes
git add .
git commit -m "feat: add new authentication system"

# 2. Pre-commit hook validates version
# (automatically runs version validation)

# 3. Create PR
# CI validates version increment and suggests bump type

# 4. If validation fails, bump version
python3 scripts/improved_version_management.py bump --auto

# 5. Commit and push
git add conanfile.py
git commit -m "bump: version to 2.1.0"
git push
```

### Release Process

```bash
# 1. Finalize changes on develop
git checkout develop
python3 scripts/improved_version_management.py bump --type minor

# 2. Create release branch
git checkout -b release/2.1.0
git commit -m "release: version 2.1.0"

# 3. Merge to main (creates tag automatically)
# CI validates and tags the release
```

## Advanced Features

### Git-based Version Metadata
```python
# Generate versions with build metadata
version = generate_git_based_version("2.0.3")
# Result: "2.0.3+git.42.gabc1234.dirty"

# Useful for:
# - Development builds
# - CI/CD artifact versioning
# - Debugging version provenance
```

### Commit Analysis Engine
```python
# Analyze conventional commits
analysis = analyze_commit_messages()
{
    'bump_type': 'minor',
    'confidence': 0.85,
    'breaking_changes': 0,
    'features': 3,
    'fixes': 2
}
```

### Version Conflict Detection
```python
# Detect conflicts across branches
conflicts = validate_version_consistency()
# Returns detailed conflict report with resolution suggestions
```

## Comparison: OMS vs SpareTools vs Enhanced

| Feature | OMS | SpareTools | Enhanced |
|---------|-----|------------|----------|
| **Version Format** | Git-based only | Semantic only | Both |
| **Validation** | None | Strict | Comprehensive |
| **Automation** | Manual | Basic | Intelligent |
| **CI/CD Integration** | Minimal | Basic | Advanced |
| **Conflict Detection** | None | PR-level | Multi-branch |
| **Commit Analysis** | None | None | Advanced |
| **Pre-commit Hooks** | None | Basic | Comprehensive |

## Migration Guide

### From Pure OMS Approach
```bash
# 1. Add semantic version base
echo "2.0.3" > VERSION

# 2. Enable validation hooks
pre-commit install

# 3. Add CI/CD workflows
# Copy .github/workflows/version-management.yml

# 4. Update existing conanfiles
python3 scripts/improved_version_management.py validate
```

### From Pure SpareTools Approach
```bash
# 1. Enable git-based metadata
# Edit conanfile.py to support +git suffixes

# 2. Add intelligent bumping
# Update workflows to use improved_version_management.py

# 3. Add commit analysis
# Enable conventional commit parsing
```

## Best Practices

### Development
1. **Use conventional commits** for automatic bump detection
2. **Run validation locally** before pushing
3. **Keep feature branches short-lived** to avoid conflicts
4. **Test version bumps** in isolation

### Release Management
1. **Use release branches** for stable releases
2. **Tag releases automatically** from CI/CD
3. **Generate release notes** from commit analysis
4. **Maintain semantic versioning** strictly

### CI/CD Integration
1. **Fail fast** on version validation errors
2. **Cache validation results** for performance
3. **Notify teams** of version conflicts
4. **Audit version changes** regularly

## Troubleshooting

### Common Issues

**"Version increment validation failed"**
```bash
# Check what changed
git diff HEAD~1 -- conanfile.py

# Auto-bump version
python3 scripts/improved_version_management.py bump --auto

# Manual bump if needed
python3 scripts/improved_version_management.py bump --type patch
```

**"Version conflict with target branch"**
```bash
# Check target branch version
git show origin/main:VERSION

# Bump to resolve conflict
python3 scripts/bump_version.py patch
```

**Low confidence in auto-bump**
```bash
# Check commit analysis
python3 scripts/improved_version_management.py analyze --json

# Override manually if needed
python3 scripts/bump_version.py --type minor
```

## Future Enhancements

### Planned Features
- **Dependency version locking** based on compatibility
- **Automated changelog generation** from commits
- **Version drift detection** across microservices
- **Security patch tracking** in version metadata

### Integration Opportunities
- **Container registry** version tagging
- **Artifact repository** version management
- **Deployment pipeline** version validation
- **Compliance reporting** for version audits

This enhanced version management system provides the perfect balance of flexibility and rigor, ensuring reliable releases while supporting modern development workflows.