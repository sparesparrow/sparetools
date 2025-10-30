# SpareTools - DevOps Tooling for OpenSSL Ecosystem

Zero-copy dependency management and prebuilt toolchains for OpenSSL development.

## 📦 Packages

### `sparetools-base` (python_requires)
Foundation utilities providing:
- Zero-copy symlink management (NGA pattern)
- Security gates (Trivy, Syft, FIPS validation)
- Conan extensions and helpers

**Status:** ✅ Published to Cloudsmith (`sparetools-base/1.0.0`)

### `sparetools-cpython` (application)
Prebuilt CPython 3.12.7 with:
- OpenSSL support
- LTO and PGO optimizations
- Zero-dependency installation
- Both `python` and `python3` commands

**Status:** ✅ Published to Cloudsmith (`sparetools-cpython/3.12.7`)

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for full installation instructions.

Quick version:
```bash
# Add remote
conan remote add sparesparrow-conan https://conan.cloudsmith.io/sparesparrow-conan/openssl-conan/

# Install CPython
conan install --requires=sparetools-cpython/3.12.7 -r sparesparrow-conan --deployer=full_deploy

# Activate
source full_deploy/host/sparetools-cpython/3.12.7/*/activate.sh

# Test
python3 --version  # Python 3.12.7
```

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Installation and usage guide
- [Bootstrap Executor](docs/BOOTSTRAP_PROMPT-EXECUTOR.md) - Automated environment setup
- [Bootstrap Validator](docs/BOOTSTRAP_PROMPT-VALIDATOR.md) - Validation checks
- [Bootstrap Orchestrator](docs/BOOTSTRAP_PROMPT-ORCHESTRATOR.md) - Recovery automation
- [Bootstrap Instructions](docs/BOOTSTRAP-INSTRUCTIONS.md) - Complete guide

## 🏗 Repository Structure

```
sparetools/
├── packages/
│   ├── sparetools-base/       # Python_requires utilities
│   │   ├── conanfile.py       # Published v1.0.0 ✅
│   │   ├── symlink_helpers.py
│   │   ├── security_gates.py
│   │   └── README.md
│   └── sparetools-cpython/    # Prebuilt CPython
│       ├── conanfile.py       # Published v3.12.7 ✅
│       └── README.md
├── docs/                      # Bootstrap prompts
├── scripts/                   # Automation scripts
│   └── validate-install.sh   # Installation validator
├── QUICKSTART.md              # Installation guide
└── README.md                  # This file
```

## 🔗 Related Projects

- [mcp-prompts](https://github.com/sparesparrow/mcp-prompts) - MCP server for automation
- [openssl](https://github.com/sparesparrow/openssl) - OpenSSL with modern CI/CD

## 📄 License

Apache-2.0

## 🎯 Coming Soon

- `sparetools-openssl/3.4.0` - Prebuilt OpenSSL with FIPS
- `sparetools-conan/2.21.0` - Prebuilt Conan itself
- GitHub Actions CI/CD workflows
