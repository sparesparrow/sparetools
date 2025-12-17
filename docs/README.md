# SpareTools Documentation

Welcome to the SpareTools documentation. This directory contains comprehensive guides, references, and documentation for the SpareTools OpenSSL DevOps ecosystem.

## 📚 Documentation Index

### Getting Started

- **[Quick Reference](QUICK-REFERENCE.md)** - Quick reference card for package ecosystem, commands, and common workflows
- **[Packages](PACKAGES.md)** - Complete inventory and documentation of all packages
- **[Testing Guide](TESTING-GUIDE.md)** - How to test packages and run validation scripts
- **[Workspace Guide](WORKSPACE-GUIDE.md)** - VS Code workspace configuration and usage

### CI/CD & Operations

- **[CI/CD Guide](CI-CD-GUIDE.md)** - Complete guide to CI/CD pipelines and workflows
- **[CI/CD Troubleshooting](CI-CD-TROUBLESHOOTING.md)** - Common issues and solutions for CI/CD
- **[GitHub Secrets Setup](GITHUB-SECRETS-SETUP.md)** - Configuration guide for GitHub Actions secrets

### Migration & Compatibility

- **[Migration Guide](MIGRATION-GUIDE.md)** - Migration from Conan 1.x to 2.x and package updates
- **[OpenSSL 3.6.0 Build Analysis](OPENSSL-360-BUILD-ANALYSIS.md)** - Analysis of OpenSSL 3.6.0 builds

### Package Development

- **[Package README Template](PACKAGE-README-TEMPLATE.md)** - Template for package documentation
- **[Assembly Optimizations](ASSEMBLY-OPTIMIZATIONS.md)** - Build optimization strategies

### Audit & Validation Reports

- **[Audit Results](AUDIT-RESULTS.md)** - Conan recipe audit report (generated)
- **[OpenSSL 3.3.2 Compatibility](OPENSSL-332-COMPATIBILITY.md)** - OpenSSL compatibility validation report (generated)
- **[Consolidation Summary](CONSOLIDATION-SUMMARY.md)** - Documentation consolidation summary

### Archived Documentation

Historical and deprecated documentation is available in the [archive/](archive/) directory:

- `BASELINE.md` - Baseline architecture documentation
- `CI-CD-ARCHITECTURE.md` - Legacy CI/CD architecture
- `CI-CD-IMPLEMENTATION-COMPLETE.md` - Implementation completion notes
- `CI-CD-OPERATIONS-GUIDE.md` - Legacy operations guide
- `CI-CD-QUICK-START.md` - Legacy quick start guide
- `PACKAGE-ECOSYSTEM-INDEX.md` - Legacy package index
- `RELEASE-NOTES-v2.0.0.md` - Release notes for v2.0.0
- `ZERO-COPY-IMPLEMENTATION.md` - Zero-copy implementation details

## 🚀 Quick Start

### For Existing Projects
1. **Install Conan 2.x**: `pip install conan==2.21.0`
2. **Configure remote**: See [Quick Reference](QUICK-REFERENCE.md)
3. **Install packages**: `conan install --requires=sparetools-openssl/3.3.2`
4. **Build from source**: See [CI/CD Guide](CI-CD-GUIDE.md)

### For New Projects
1. **Use project templates**: `python bootstrap-obd.py --template=mia`
2. **Choose template type**: generic, mia, mcp, or android
3. **Follow template README**: Each template includes complete setup instructions
4. **Bootstrap environment**: Templates include bootstrap scripts for hermetic builds

## 📦 Package Ecosystem

The SpareTools ecosystem consists of:

- **Foundation**: `sparetools-base/2.0.0` - Core utilities
- **Tools**: `sparetools-cpython/3.12.7` - Prebuilt Python
- **Utilities**: `sparetools-openssl-tools/2.0.0` - Build tools and profiles
- **Main**: `sparetools-openssl/3.3.2` - OpenSSL library

See [Packages](PACKAGES.md) for complete details.

## 🎯 Project Templates

SpareTools now includes project templates for different use cases:

| Template | Purpose | Key Features |
|----------|---------|--------------|
| **Generic** | C++ libraries | CMake, Conan, testing, CI/CD |
| **MIA** | Python applications | Hermetic Python, OpenSSL integration, pytest |
| **MCP** | AI assistants | MCP protocol server, Docker, stdio/http transport |
| **Android** | Mobile apps | JNI, native libraries, Gradle, cross-platform |

### Using Templates

```bash
# Create new project from template
python bootstrap-obd.py --template=mia --name=my-project

# Templates include:
# - Complete project structure
# - CI/CD workflows (.github/workflows/)
# - Documentation templates
# - Testing frameworks
# - Bootstrap scripts
```

See [Template Usage Documentation](TEMPLATE-USAGE.md) for detailed instructions.

## 🔍 Validation & Testing

- Run audit: `python3 scripts/audit-conan-recipes.py`
- Validate compatibility: `python3 scripts/validate-openssl-compatibility.py`
- Run tests: `pytest test/`

See [Testing Guide](TESTING-GUIDE.md) for more information.

## 🤝 Contributing

1. Read the [Quick Reference](QUICK-REFERENCE.md)
2. Follow the [Package README Template](PACKAGE-README-TEMPLATE.md)
3. Run validation scripts before submitting PRs
4. Check [CI/CD Guide](CI-CD-GUIDE.md) for workflow requirements

## 📝 Documentation Updates

This documentation is maintained alongside the codebase. When making changes:

1. Update relevant documentation files
2. Regenerate audit reports: `python3 scripts/audit-conan-recipes.py`
3. Update this README if adding new documentation

## 🔗 Related Resources

- **MIA Integration**: See MIA integration documentation (coming soon)
- **GitHub Repository**: https://github.com/sparesparrow/sparetools
- **Cloudsmith Registry**: https://cloudsmith.io/~sparesparrow-conan/repos/openssl-conan/

## 📅 Last Updated

Documentation last consolidated: 2025-12-03
