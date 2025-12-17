# mia-project

{{project_description}}

## Overview

This is a MIA (Modular Integration Architecture) project template that leverages SpareTools packages for hermetic, cross-platform development.

## Features

- Hermetic Python environment via SpareTools CPython
- Conan-based dependency management
- OpenSSL integration through SpareTools
- Cross-platform build support
- CI/CD pipeline ready
- Comprehensive testing setup

## Prerequisites

- Conan 2.x
- Python 3.12+ (system Python for bootstrapping only)
- Git

## Quick Start

1. Clone this template:
```bash
git clone https://github.com/yourusername/mia-project
cd mia-project
```

2. Install dependencies and build:
```bash
conan install . --build=missing
conan build .
```

3. Run tests:
```bash
conan test test_package
```

## Project Structure

```
mia-project/
├── conanfile.py           # Conan recipe
├── pyproject.toml         # Python package configuration
├── src/mia_project/   # Source code
├── test/                  # Unit tests
├── docs/                  # Documentation
├── scripts/               # Utility scripts
└── test_package/          # Conan test package
```

## Dependencies

This project uses SpareTools packages:

- `sparetools-cpython/3.12.7` - Hermetic Python runtime
- `sparetools-openssl/3.3.2` - OpenSSL library
- `sparetools-base/2.0.0` - Shared utilities

## Development

### Environment Setup

```bash
# Create isolated environment
conan install . --build=missing

# Activate environment
conan build .
```

### Running Tests

```bash
# Run unit tests
pytest

# Run integration tests
pytest test/integration/

# Run with coverage
pytest --cov=mia_project --cov-report=html
```

### Code Quality

```bash
# Lint code
ruff check .

# Format code
black .

# Type check
mypy src/
```

## Contributing

See the main SpareTools documentation for contribution guidelines and coding standards.