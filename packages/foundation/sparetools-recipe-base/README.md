# SpareTools Recipe Base Classes

This foundation package provides base classes for the SpareTools layered architecture:

## Classes

### `SpareToolsFoundationBase`
Base class for foundation packages that provide core utilities and dependencies.

**Features:**
- Common metadata (license, URL)
- Python package type configuration
- Standard packaging and environment setup

### `SpareToolsConsumerBase`
Base class for consumer packages that are end-user applications.

**Features:**
- Common metadata for applications
- Application package type
- Runtime environment configuration

## Usage

```python
from sparetools_recipe_base import SpareToolsFoundationBase

class MyFoundationPackage(SpareToolsFoundationBase):
    name = "my-foundation-package"
    version = "1.0.0"
    description = "My foundation package"
    # ... additional package-specific configuration
```

```python
from sparetools_recipe_base import SpareToolsConsumerBase

class MyConsumerApp(SpareToolsConsumerBase):
    name = "my-consumer-app"
    version = "1.0.0"
    description = "My consumer application"
    python_requires = "sparetools-base/2.0.0"
    # ... additional package-specific configuration
```

## Architecture

This package is part of the SpareTools layered architecture:
- **Foundation Layer**: Core packages (like this one)
- **Consumer Layer**: End-user applications

Foundation packages should not depend on consumer packages, but consumers can depend on foundation packages.