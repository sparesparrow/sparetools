# SpareTools Quick Start Guide

Get up and running with SpareTools in under 15 minutes.

## 🎯 Prerequisites

### Required Tools
```bash
# Install Conan package manager
pip install conan==2.21.0

# Verify installation
conan --version  # Should show 2.21.0

# Install Git (if not already installed)
git --version
```

### System Requirements
- **Python**: 3.8+ (system Python for bootstrapping)
- **Git**: 2.30+
- **Disk Space**: 5GB+ for package cache
- **Platforms**: Linux, macOS, Windows

## 🚀 Quick Start (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/sparesparrow/sparetools.git
cd sparetools
```

### 2. Bootstrap Environment
```bash
# Bootstrap CPython and OpenSSL
python bootstrap-obd.py

# This will:
# - Download and build CPython 3.12.7
# - Build OpenSSL with SpareTools configuration
# - Set up hermetic Python environment
```

### 3. Verify Installation
```bash
# List all available packages
conan list "sparetools-*"

# Should show:
# sparetools-base/2.0.0
# sparetools-cpython/3.12.7
# sparetools-openssl/3.3.2
# And more...
```

### 4. Create Your First Project
```bash
# Create a new project from template
python bootstrap-obd.py --template=mia --name=my-first-project

# This creates a complete Python project with:
# - Project structure
# - CI/CD workflows
# - Testing framework
# - Documentation
```

## 📦 Using SpareTools Packages

### Basic Package Usage
```bash
# Install a package
conan install --requires=sparetools-openssl/3.3.2

# Use in your project
conan install . --build=missing
conan build .
```

### Python Integration
```python
# Your Python code can now use SpareTools packages
import ssl

# This automatically uses SpareTools OpenSSL
context = ssl.create_default_context()
print(f"OpenSSL version: {ssl.OPENSSL_VERSION}")
```

## 🏗️ Building from Source

### Build All Packages
```bash
# Build entire monorepo (takes ~15-30 minutes)
python scripts/build/build-orchestrator.py --all
```

### Build Specific Consumer
```bash
# Build only OpenSSL packages
python scripts/build/build-orchestrator.py --consumers openssl
```

### Parallel Builds
```bash
# Use multiple cores for faster builds
python scripts/build/build-orchestrator.py --all --parallel=4
```

## 🧪 Validation & Testing

### Run Validation Suite
```bash
# Validate all packages
python scripts/validation/tier1-syntax.py

# Check OpenSSL compatibility
python scripts/validation/validate-openssl-compatibility.py

# Audit recipes
python scripts/validation/audit-conan-recipes.py
```

### Run Tests
```bash
# Run test suite
pytest test/

# Test specific consumer
python scripts/testing/integration-tester.py --consumer mia
```

## 🔧 Development Workflow

### Setting Up Development Environment
```bash
# Configure Conan remotes
conan remote add sparesparrow-conan \
    https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/

# Enable development mode
conan profile detect --force

# For development, you can also:
pip install -e packages/sparetools-base
```

### Working with Templates
```bash
# List available templates
python bootstrap-obd.py --list-templates

# Create project with custom settings
python bootstrap-obd.py --template=mcp \
    --name=my-mcp-server \
    --variables='{"author": "Your Name", "version": "1.0.0"}'
```

### CI/CD Integration
```bash
# Templates include CI/CD workflows
# Just push to GitHub and CI/CD runs automatically
git add .
git commit -m "feat: my new feature"
git push origin main
```

## 🔍 Troubleshooting

### Common Issues

#### Conan Remote Issues
```bash
# If remote is not accessible
conan remote remove sparesparrow-conan
conan remote add sparesparrow-conan \
    https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/

# Test remote
conan remote list
```

#### Build Failures
```bash
# Clear cache and retry
conan remove "*" -c
python scripts/build/build-orchestrator.py --consumers openssl
```

#### Python Path Issues
```bash
# Ensure proper Python environment
python bootstrap-obd.py  # Re-run bootstrap if needed

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Permission Issues
```bash
# On Linux/macOS, you might need:
chmod +x scripts/*.py
chmod +x bootstrap-obd.py
```

### Getting Help

1. **Check existing documentation**:
   - [CI/CD Guide](operations/CI-CD-GUIDE.md)
   - [Troubleshooting](operations/TROUBLESHOOTING.md)
   - [Integration Examples](../docs/integration/)

2. **Run diagnostics**:
   ```bash
   # Comprehensive validation
   python scripts/validation/tier1-syntax.py -v
   python scripts/validation/validate-openssl-compatibility.py
   ```

3. **Community support**:
   - GitHub Issues: Report bugs and request features
   - GitHub Discussions: Ask questions and share knowledge

## 🎯 Next Steps

### For Package Consumers
- Explore [Integration Examples](../docs/integration/)
- Learn about [Consumer Documentation](../docs/consumers/)
- Understand [CI/CD Integration](operations/CI-CD-GUIDE.md)

### For Package Developers
- Read [Contributing Guidelines](CONTRIBUTING.md)
- Study [Recipe Base Classes](../scripts/recipe_base.py)
- Learn [Package Development](../docs/consumers/openssl/)

### For Platform Integrators
- Review [Cross-Platform Builds](../docs/consumers/openssl/BUILD-MATRIX.md)
- Understand [Security Gates](../docs/security/SECURITY-GATES.md)
- Explore [Deployment Options](operations/DEPLOYMENT-GUIDE.md)

## 📚 Additional Resources

- **[Package Ecosystem](../PACKAGES.md)**: Complete package inventory
- **[Architecture Overview](ARCHITECTURE.md)**: System design principles
- **[Template Usage](../TEMPLATE-USAGE.md)**: Project template guide
- **[API Reference](../docs/api/)**: Package APIs and interfaces

---

**Time to complete**: 5-15 minutes | **Skills required**: Basic command line | **Next**: [Integration Examples](../docs/integration/) or [Package Documentation](../PACKAGES.md)