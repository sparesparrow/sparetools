# MIA Contributor Guide: Using SpareTools Packages

This guide helps MIA contributors set up their development environment to use sparetools Conan packages.

## Prerequisites

### Required Software

- **Conan 2.x**: Version 2.21.0 or later
  ```bash
  pip install conan==2.21.0
  ```

- **Python 3.12+**: Required for some sparetools packages
  ```bash
  python --version  # Should be 3.12 or later
  ```

- **Git**: For cloning repositories
- **CMake** (optional): If building C++ projects

### System Requirements

- **Linux**: Ubuntu 22.04+, Debian 11+, or similar
- **macOS**: macOS 13+ (Apple Silicon or Intel)
- **Windows**: Windows 10+ with WSL2 recommended

## Initial Setup

### 1. Install Conan

```bash
pip install --upgrade pip
pip install conan==2.21.0
```

Verify installation:

```bash
conan --version
# Should output: Conan version 2.21.0
```

### 2. Configure Conan Profile

Detect and create your system profile:

```bash
conan profile detect --force
```

This creates a default profile based on your system. Verify:

```bash
conan profile show default
```

### 3. Add Cloudsmith Remote

Add the sparetools package repository:

```bash
conan remote add sparesparrow-conan \
  https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/ \
  --force
```

Verify remote is configured:

```bash
conan remote list
```

You should see `sparesparrow-conan` in the list.

### 4. Authenticate (if needed)

If packages are private, authenticate with Cloudsmith:

```bash
conan remote login sparesparrow-conan sparesparrow --password YOUR_API_KEY
```

**Note**: Get API key from Cloudsmith dashboard if needed.

## Using SpareTools Packages

### Basic Usage in conanfile.py

Add sparetools packages to your project's `conanfile.py`:

```python
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout

class MIAProjectConan(ConanFile):
    name = "mia-project"
    version = "1.0.0"
    
    settings = "os", "arch", "compiler", "build_type"
    
    # Dependencies on sparetools packages
    requires = [
        "sparetools-openssl/3.3.2",
    ]
    
    # Tool dependencies (build-time only)
    tool_requires = [
        "cmake/[>=3.20]",
        "sparetools-cpython/3.12.7",  # If you need Python
    ]
    
    # Python utilities (for build scripts)
    python_requires = "sparetools-base/2.0.0"
    
    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
```

### Installing Dependencies

Install all dependencies for your project:

```bash
conan install . --build=missing
```

This will:
- Download packages from Cloudsmith
- Build missing packages locally if needed
- Generate build files (CMake, etc.)

### Building Your Project

Build your project:

```bash
conan build .
```

Or use your build system directly:

```bash
conan install . --build=missing
cmake --build build
```

## Common Usage Patterns

### Pattern 1: Using OpenSSL

```python
requires = [
    "sparetools-openssl/3.3.2",
]
```

In your CMakeLists.txt:

```cmake
find_package(OpenSSL REQUIRED)
target_link_libraries(your_target OpenSSL::SSL OpenSSL::Crypto)
```

### Pattern 2: Using Python Tools

```python
tool_requires = [
    "sparetools-cpython/3.12.7",
]
```

Access Python in build scripts:

```python
def build(self):
    python = self.dependencies.build["sparetools-cpython"].conf_info.get("user.cpython:executable")
    self.run(f"{python} your_script.py")
```

### Pattern 3: Using Utilities

```python
python_requires = "sparetools-base/2.0.0"
```

Use utilities in your conanfile:

```python
def build(self):
    base = self.python_requires["sparetools-base"]
    # Use utilities from base
    base.conanfile.run_trivy_scan(self.source_folder)
```

## Troubleshooting

### Issue: Package Not Found

**Error**: `ERROR: Package 'sparetools-openssl/3.3.2' not found`

**Solutions**:
1. Verify remote is configured: `conan remote list`
2. Check package exists: `conan search sparetools-openssl -r sparesparrow-conan`
3. Verify authentication if packages are private
4. Check network connectivity

### Issue: Version Conflict

**Error**: `ERROR: Version conflict`

**Solutions**:
1. Check your `conanfile.py` for version constraints
2. Use `conan graph explain` to see dependency graph
3. Update to compatible versions
4. Clear cache: `conan remove "sparetools-*/*" --force`

### Issue: Build Fails

**Error**: Build errors or missing dependencies

**Solutions**:
1. Check prerequisites: `conan profile detect --force`
2. Verify build requirements: `conan install . --build=missing -v`
3. Check logs for specific errors
4. Ensure all tool_requires are specified

### Issue: Authentication Required

**Error**: Authentication errors

**Solutions**:
1. Check if packages are private
2. Authenticate: `conan remote login sparesparrow-conan USERNAME --password API_KEY`
3. Verify API key permissions

## Best Practices

### 1. Pin Versions in Production

For production code, pin exact versions:

```python
requires = [
    "sparetools-openssl/3.3.2",  # Exact version
]
```

### 2. Use Version Ranges for Development

For development, use version ranges:

```python
requires = [
    "sparetools-openssl/[>=3.3.0,<4.0.0]",  # Allow patch updates
]
```

### 3. Cache Management

Conan caches packages locally. To clear cache:

```bash
# Clear specific packages
conan remove "sparetools-openssl/*" --force

# Clear all sparetools packages
conan remove "sparetools-*/*" --force

# Clear entire cache (use with caution)
conan cache clean "*"
```

### 4. Profile Management

Create custom profiles for different build configurations:

```bash
# Create a new profile
conan profile new myprofile --detect

# Edit profile
conan profile show myprofile > myprofile.txt
# Edit myprofile.txt
conan profile update myprofile myprofile.txt

# Use profile
conan install . --profile myprofile
```

### 5. CI/CD Integration

In CI/CD pipelines:

1. Configure remote in workflow
2. Cache Conan cache directory
3. Use `--build=missing` for first-time builds
4. Pin versions for reproducibility

## Development Workflow

### 1. Clone MIA Repository

```bash
git clone https://github.com/sparesparrow/mia.git
cd mia
```

### 2. Set Up Conan

```bash
conan profile detect --force
conan remote add sparesparrow-conan \
  https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/ \
  --force
```

### 3. Install Dependencies

```bash
conan install . --build=missing
```

### 4. Build Project

```bash
conan build .
```

### 5. Test

Run tests as defined in your project.

## Advanced Topics

### Custom Profiles

Create profiles for specific build configurations:

```bash
# Create profile for release builds
conan profile new release --detect
conan profile update settings.build_type=Release release
```

### Version Resolution

Understand how Conan resolves versions:

```bash
# Explain dependency graph
conan graph explain conanfile.py

# Show resolved versions
conan graph info conanfile.py
```

### Lock Files

Use lock files for reproducible builds:

```bash
# Generate lock file
conan lock create conanfile.py --lockfile conan.lock

# Use lock file
conan install . --lockfile conan.lock
```

## Related Documentation

- [MIA Integration Guide](MIA-INTEGRATION.md) - Complete integration guide
- [Cross-Repo Testing](CROSS-REPO-TESTING.md) - Testing cross-repo dependencies
- [Quick Reference](QUICK-REFERENCE.md) - Quick reference for sparetools
- [Packages](PACKAGES.md) - Complete package documentation

## Getting Help

### Resources

1. **Documentation**: Check this guide and related docs
2. **Examples**: See `examples/mia-consumer/` for example usage
3. **GitHub Issues**: Open an issue for bugs or questions
4. **Conan Documentation**: https://docs.conan.io/

### Common Questions

**Q: Do I need to build sparetools packages locally?**  
A: No, packages are pre-built and available from Cloudsmith. Use `--build=missing` to build only if needed.

**Q: Can I use different OpenSSL versions?**  
A: Currently, sparetools-openssl/3.3.2 is the supported version. Check package documentation for other versions.

**Q: How do I update packages?**  
A: Update version in `conanfile.py` and run `conan install . --build=missing`.

**Q: Can I contribute to sparetools?**  
A: Yes! See the sparetools repository for contribution guidelines.

## Updates

This guide is maintained alongside the codebase. Last updated: 2025-12-03
