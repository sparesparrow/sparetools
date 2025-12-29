# SpareTools MCP Prompts Reference

## Overview

This document lists all MCP prompts available for SpareTools development, including both existing prompts that are reused and SpareTools-specific prompts.

## Existing Prompts (Reused)

### conan-toolchain-package-creation
**Purpose**: Creating Conan toolchain packages for cross-compilation
**Variables**:
- None (interactive prompt)
**Use Case**: Setting up ARM GCC toolchains, cross-platform development

### conan-toolchain-package-id
**Purpose**: Package ID management for Conan toolchains
**Variables**:
- None (interactive prompt)
**Use Case**: Managing package IDs for different build configurations

### conan-toolchain-testing
**Purpose**: Testing workflows for Conan toolchain packages
**Variables**:
- None (interactive prompt)
**Use Case**: Testing toolchain packages across different platforms

### code-review-assistant
**Purpose**: Code review assistance for Python/C++ code
**Variables**:
- `language`: Programming language (python/cpp)
- `code`: Code to review
- `context`: Additional context
**Use Case**: Reviewing SpareTools package recipes and build scripts

### architecture-design-assistant
**Purpose**: Architecture design thinking for package ecosystem
**Variables**:
- None (interactive prompt)
**Use Case**: Designing new package architectures and dependency management

## SpareTools-Specific Prompts

### sparetools-package-bootstrap
**Purpose**: Bootstrap new SpareTools packages with proper structure and dependencies
**Variables**:
- `package_name` (required): Name of the new package (e.g., "sparetools-new-package")
- `package_type` (required): Type of package - "library", "tool-require", "application"
- `dependencies` (optional): Comma-separated list of dependencies (e.g., "sparetools-base/2.0.0")
**Use Case**: Creating new packages like sparetools-openssl, sparetools-cpython, etc.
**Example Usage**:
```bash
/sparetools-package-bootstrap
# package_name: sparetools-new-tool
# package_type: tool-require
# dependencies: sparetools-base/2.0.0, sparetools-cpython/3.12.7
```

### sparetools-zero-copy-deployment
**Purpose**: Guide implementation of zero-copy deployment pattern using symlinks
**Variables**:
- `workspace_path` (required): Relative path to workspace package (e.g., "packages/sparetools-openssl")
- `conan_cache_path` (required): Path to Conan cache (default: "~/.conan2/p")
**Use Case**: Setting up efficient development environments with symlinked binaries
**Example Usage**:
```bash
/sparetools-zero-copy-deployment
# workspace_path: packages/sparetools-openssl
# conan_cache_path: ~/.conan2/p
```

### sparetools-security-scan
**Purpose**: Security scanning workflow using Trivy, Syft, CodeQL, and FIPS validation
**Variables**:
- `package_name` (required): Full package reference (e.g., "sparetools-openssl/3.3.2")
- `scan_type` (required): Type of scan - "quick", "full", "fips-only"
**Use Case**: Running security scans before package publishing to Cloudsmith
**Example Usage**:
```bash
/sparetools-security-scan
# package_name: sparetools-openssl/3.3.2
# scan_type: full
```

### sparetools-ci-cd-workflow
**Purpose**: GitHub Actions workflow creation for multi-platform package builds
**Variables**:
- `package_name` (required): Package name without version (e.g., "sparetools-openssl")
- `build_matrix` (required): Comma-separated build targets (e.g., "linux-gcc11,linux-clang14,macos-clang,darwin-arm64")
**Use Case**: Setting up CI/CD pipelines for new packages
**Example Usage**:
```bash
/sparetools-ci-cd-workflow
# package_name: sparetools-openssl
# build_matrix: linux-gcc11,linux-clang14,macos-clang,darwin-arm64,windows-msvc2022
```

### sparetools-profile-composition
**Purpose**: Creating and composing Conan profiles for different build scenarios
**Variables**:
- `platform` (required): Target platform (e.g., "linux", "macos", "windows")
- `compiler` (required): Compiler type and version (e.g., "gcc11", "clang14", "msvc2022")
- `build_method` (required): Build method (e.g., "perl-configure", "cmake", "autotools")
- `features` (optional): Comma-separated features (e.g., "fips-enabled,shared-libs,performance")
**Use Case**: Building packages with specific platform/compiler/feature combinations
**Example Usage**:
```bash
/sparetools-profile-composition
# platform: linux
# compiler: gcc11
# build_method: perl-configure
# features: fips-enabled,performance
```

## Usage Patterns

### Package Development Workflow
1. **Bootstrap**: Use `sparetools-package-bootstrap` to create new package structure
2. **Profile Setup**: Use `sparetools-profile-composition` to configure build profiles
3. **Code Review**: Use `code-review-assistant` for recipe reviews
4. **Security**: Use `sparetools-security-scan` before publishing
5. **CI/CD**: Use `sparetools-ci-cd-workflow` for automation setup

### Deployment Workflow
1. **Zero-Copy Setup**: Use `sparetools-zero-copy-deployment` for efficient development
2. **Integration Testing**: Use existing prompts for code review and testing
3. **Security Validation**: Run security scans on all artifacts
4. **Publishing**: Ensure all scans pass before Cloudsmith upload

## Best Practices

### Variable Usage
- Always provide required variables
- Use descriptive values that match your actual package names
- Test prompts with sample values first

### Context Awareness
- Prompts automatically detect SpareTools repository context
- Package names should follow `sparetools-*` convention
- Dependencies should reference other SpareTools packages when possible

### Iterative Development
- Start with basic prompt usage and refine variables as needed
- Update prompt templates based on common usage patterns
- Add new prompts for frequently repeated tasks

## Troubleshooting

### Prompt Variables Not Working
- Check exact variable names (case-sensitive)
- Ensure all required variables are provided
- Verify variable values don't contain special characters that break JSON

### Context Not Detected
- Ensure you're in the correct workspace directory
- Check that MCP server is running and accessible
- Verify prompt files exist in `/home/sparrow/mcp/data/prompts/`

### New Prompts Not Appearing
- Restart Cursor after adding new prompt files
- Check MCP server logs for errors
- Verify JSON syntax in new prompt files

## Contributing

To add new SpareTools-specific prompts:

1. Create JSON file following the established format
2. Use `sparetools-` prefix for prompt ID
3. Include comprehensive description and variable documentation
4. Add to this reference document
5. Test in Cursor MCP interface
6. Update as needed based on usage feedback

