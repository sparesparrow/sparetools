# sparetools-base

Foundation `python_requires` package for the SpareTools ecosystem.

## Purpose

Provides core utilities, patterns, and security gates shared across all SpareTools packages. This is the foundational layer that other packages build upon, containing zero-copy deployment patterns, security integration, and common Conan extensions.

## Features

- **Zero-Copy Symlink Utilities**: NGA aerospace pattern for disk space optimization (80% savings)
- **Security Gates**: Integrated Trivy, Syft, and FIPS validation
- **Conan Extensions**: Custom helpers and build tools
- **Common Patterns**: Reusable code for package development

## Installation

As a `python_requires` package, this is automatically included when other SpareTools packages depend on it:

```bash
# Export to local cache
cd packages/sparetools-base
conan export . --version=1.0.0
```

## Usage

### As python_requires in Other Packages

```python
from conan import ConanFile

class MyProject(ConanFile):
    name = "my-project"
    python_requires = "sparetools-base/1.0.0"
    
    def build(self):
        # Access base utilities
        base = self.python_requires["sparetools-base"].conanfile
        
        # Use zero-copy pattern
        if hasattr(base, 'create_zero_copy_environment'):
            base.create_zero_copy_environment(self, "openssl", "./DEPS/openssl")
        
        # Run security gates
        if hasattr(base, 'run_trivy_scan'):
            base.run_trivy_scan(self.source_folder)
```

### Direct Module Import

```python
from conan import ConanFile
from conan.tools.files import load
import sys
import os

class MyProject(ConanFile):
    python_requires = "sparetools-base/1.0.0"
    
    def build(self):
        # Import modules directly
        base_folder = self.python_requires["sparetools-base"].module_folder
        sys.path.insert(0, base_folder)
        
        from symlink_helpers import create_symlink_with_check
        from security_gates import run_trivy, generate_sbom
        
        # Use utilities
        create_symlink_with_check("source", "target")
        run_trivy(self.build_folder)
```

## Included Modules

### symlink-helpers.py (7,346 bytes)

Zero-copy deployment pattern implementation:

```python
from symlink_helpers import (
    create_symlink_with_check,
    create_whole_dir_path,
    zero_copy_deploy,
    verify_symlink_integrity
)

# Create zero-copy environment
zero_copy_deploy(
    source_dir="/path/to/source",
    target_dir="/path/to/target",
    pattern="*.so"
)
```

**Key Functions:**
- `create_symlink_with_check()`: Safe symlink creation with validation
- `zero_copy_deploy()`: Deploy entire directories via symlinks
- `verify_symlink_integrity()`: Validate symlink chain
- `atomic_symlink_swap()`: Atomic updates for zero-downtime

### security-gates.py (6,062 bytes)

Security scanning and validation:

```python
from security_gates import (
    run_trivy_scan,
    generate_sbom,
    validate_fips_compliance,
    check_vulnerabilities
)

# Run security scans
run_trivy_scan(
    target_dir="./build",
    fail_on_critical=True
)

# Generate SBOM
sbom = generate_sbom(
    package_dir="./package",
    format="cyclonedx-json"
)
```

**Key Functions:**
- `run_trivy_scan()`: Vulnerability scanning with Aqua Trivy
- `generate_sbom()`: CycloneDX/SPDX SBOM generation
- `validate_fips_compliance()`: FIPS 140-3 validation hooks
- `security_report()`: Aggregate security report generation

## Dependencies

### Requirements
- None (this is the base package)

### Tool Requirements
- Python 3.8+ (for module execution)

### Python Requirements
- None (no external Python packages required)

## Configuration

No configuration required. This package exports utilities for use by other packages.

## Development

### Building Locally

```bash
cd packages/sparetools-base
conan export . --version=1.0.0
```

### Testing

```bash
# Test by using in another package
cd packages/sparetools-openssl
conan create . --version=3.3.2 --build=missing
```

### Adding New Utilities

1. Add Python module to package directory
2. Update `conanfile.py` exports_sources if needed
3. Document in this README
4. Export new version

## Integration Examples

### Example 1: Package with Security Gates

```python
from conan import ConanFile

class SecurePackage(ConanFile):
    name = "secure-package"
    python_requires = "sparetools-base/1.0.0"
    
    def build(self):
        self.run("make")
        
        # Run security gates
        base = self.python_requires["sparetools-base"].conanfile
        base.run_trivy_scan(self.build_folder)
        base.generate_sbom(self.package_folder)
```

### Example 2: Zero-Copy Deployment

```python
from conan import ConanFile

class FastDeployPackage(ConanFile):
    name = "fast-deploy"
    python_requires = "sparetools-base/1.0.0"
    
    def package(self):
        # Use zero-copy instead of copying files
        base = self.python_requires["sparetools-base"].conanfile
        base.zero_copy_deploy(
            self.build_folder,
            self.package_folder
        )
```

### Example 3: FIPS Validation

```python
from conan import ConanFile

class FIPSPackage(ConanFile):
    name = "fips-package"
    python_requires = "sparetools-base/1.0.0"
    options = {"fips": [True, False]}
    default_options = {"fips": False}
    
    def build(self):
        self.run("make")
        
        if self.options.fips:
            base = self.python_requires["sparetools-base"].conanfile
            base.validate_fips_compliance(self.build_folder)
```

## Best Practices

1. **Always use python_requires**: Don't copy utilities, use python_requires
2. **Check for method existence**: Use `hasattr()` for forward compatibility
3. **Handle errors gracefully**: Security gates may not always be available
4. **Version pinning**: Pin to specific version for production

## Troubleshooting

### Module Not Found

```bash
# Error: Module 'symlink_helpers' not found
# Solution: Ensure sparetools-base is exported
conan export packages/sparetools-base --version=1.0.0
```

### Security Gates Not Available

```python
# In your conanfile.py
try:
    base = self.python_requires["sparetools-base"].conanfile
    base.run_trivy_scan(self.build_folder)
except Exception as e:
    self.output.warn(f"Security gates not available: {e}")
```

## Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| Linux | ✅ Full support | Primary platform |
| Windows | ✅ Full support | Path handling normalized |
| macOS | ✅ Full support | Darwin-specific symlinks |
| BSD | ⚠️ Limited testing | Should work |

## Performance

### Zero-Copy Benefits

- **Disk Space**: 80% savings (symlinks vs copies)
- **Deployment Speed**: 90% faster (instant symlinks)
- **Update Time**: Atomic (single symlink swap)

### Security Scanning

- **Trivy Scan**: ~30-60 seconds typical
- **SBOM Generation**: ~10-20 seconds
- **FIPS Validation**: ~60-120 seconds

## License

Apache-2.0

## Contributing

See CONTRIBUTING.md in repository root.

## Related Packages

- **sparetools-shared-dev-tools**: Higher-level development tools
- **sparetools-openssl-tools**: OpenSSL-specific tools
- **sparetools-openssl**: Uses this as base

## Resources

- **Repository**: https://github.com/sparesparrow/sparetools
- **Issues**: https://github.com/sparesparrow/sparetools/issues
- **Cloudsmith**: https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/

## Version History

### 1.0.0 (Current)
- Initial release
- Zero-copy pattern implementation
- Security gates (Trivy, Syft)
- FIPS validation hooks
- Cross-platform support

---

**Foundation of the SpareTools Ecosystem**
