# sparetools-bootstrap

Bootstrap automation and orchestration for SpareTools ecosystem.

## Purpose

Provides automated setup and validation for SpareTools development environments. Implements a three-agent orchestration system (EXECUTOR → VALIDATOR → ORCHESTRATOR) for reliable environment bootstrap.

## Installation

```bash
conan export packages/sparetools-bootstrap --version=1.0.0
```

## Features

- **Three-Agent Orchestration**: Automated, validated setup
- **Build Matrix Generation**: Smart build matrix for CI/CD
- **Crypto Configuration**: Cryptographic configuration management
- **FIPS Validation**: FIPS 140-3 compliance validation
- **SBOM Generation**: Software Bill of Materials creation

## Usage

```python
from conan import ConanFile

class MyPackage(ConanFile):
    python_requires = "sparetools-bootstrap/1.0.0"
```

## Modules

- `bootstrap/conan_functions.py` - Conan operation helpers
- `bootstrap/openssl/build_matrix.py` - Build matrix generation
- `bootstrap/openssl/crypto_config.py` - Crypto configuration
- `bootstrap/openssl/fips_validator.py` - FIPS validation
- `bootstrap/openssl/sbom_generator.py` - SBOM generation

## Dependencies

- sparetools-shared-dev-tools/1.0.0
- sparetools-base/1.0.0

## License

Apache-2.0

