# SPARETOOLS

Zero-copy dependency management and prebuilt toolchains for OpenSSL development.

## 📦 Packages

### `sparetools-base` (python_requires)
Foundation utilities providing:
- Zero-copy symlink management (NGA pattern)
- Security gates (Trivy, Syft, FIPS validation)
- Conan extensions and helpers

### `sparetools-cpython` (application)
Prebuilt CPython 3.12.7 with:
- OpenSSL support
- LTO and PGO optimizations
- Zero-dependency installation

## 🚀 Quick Start

Add Cloudsmith remoteconan remote add cloudsmith https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/index.jsonInstall prebuilt CPythonconan install --requires=sparetools-cpython/3.12.7 -r cloudsmith --deployer=full_deployActivate environmentsource full_deploy/host/sparetools-cpython/3.12.7/*/activate.sh
python3 --version  # Python 3.12.7

## 📚 Documentation

- [Bootstrap Executor](docs/BOOTSTRAP_PROMPT-EXECUTOR.md) - Automated environment setup
- [Bootstrap Validator](docs/BOOTSTRAP_PROMPT-VALIDATOR.md) - Validation checks
- [Bootstrap Orchestrator](docs/BOOTSTRAP_PROMPT-ORCHESTRATOR.md) - Recovery automation
- [Bootstrap Instructions](docs/BOOTSTRAP-INSTRUCTIONS.md) - Complete guide

## 🏗 Repository Structure
sparetools/
├── packages/
│   ├── sparetools-base/       # Python_requires utilities
│   └── sparetools-cpython/    # Prebuilt CPython
├── docs/                      # Bootstrap prompts and guides
└── scripts/                   # Automation scripts

## 🔗 Related Projects

- [mcp-prompts](https://github.com/sparesparrow/mcp-prompts) - MCP server for automation
- [openssl](https://github.com/sparesparrow/openssl) - OpenSSL with modern CI/CD

## 📄 License

Apache-2.0
EOF

# Step 7: Create package READMEs
cat > packages/sparetools-base/README.md << 'EOF'
# sparetools-base

Foundation python_requires package for SpareTools ecosystem.

## Features

- **Zero-copy symlink utilities** - NGA aerospace pattern
- **Security gates** - Trivy, Syft, FIPS validation
- **Conan extensions** - Custom helpers and tools

## Usage
from conan import ConanFileclass MyProject(ConanFile):
python_requires = "sparetools-base/1.0.0"def build(self):
    # Access utilities
    base = self.python_requires["sparetools-base"].module
    base.create_zero_copy_environment(self, "openssl", "./DEPS/openssl")
## Export
cd packages/sparetools-base
conan export . --version=1.0.0
