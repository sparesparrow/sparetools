# SpareTools Aerospace

Aerospace domain extensions for SpareTools, migrated from ngapy framework.

## Overview

This package provides aerospace-specific test environments, components, and domain logic migrated from the ngapy framework while preserving all existing functionality.

## Components

### Test Environments
- **ASEEnvironment**: ASE (Aerospace Systems Environment) test bench
- **JETSEnvironment**: JETS test bench integration
- **SITSEnvironment**: SITS test bench integration

### Components
- **ASEComponent**: ASE-specific communication and file operations
- **DEOSComponent**: DEOS platform component interface
- **JETSComponent**: JETS platform component interface

### Products
- **ngaafcs**: NGAA FCS GUI and workflow implementations
- **ngaims**: NGA IMS extensive domain logic and business rules

## Usage

### Environment Setup

```python
from sparetools_aerospace.environments.ase_environment import ASEEnvironment

# Create ASE test environment
env = ASEEnvironment()
env.start()

# Run health checks
if env.health_check():
    print("ASE environment ready")
```

### Component Integration

```python
from sparetools_aerospace.components.ase_component import ASEComponent

# Create ASE component
component = ASEComponent()
component.connect()

# File operations
component.upload_file("local_file.txt", "remote_path.txt")
```

### Plugin Registration

```python
from sparetools_aerospace import register_aerospace_plugins
from sparetools.core.plugins.plugin_manager import PluginManager

# Register aerospace plugins
pm = PluginManager()
register_aerospace_plugins(pm)

# Use registered environments
ase_env = pm.get_environment("ase")()
```

## Migration Notes

This package was created through systematic migration from ngapy:

- **100% Logic Preservation**: All algorithms and business logic intact
- **Interface Compatibility**: Drop-in replacement for ngapy aerospace modules
- **Domain Separation**: Aerospace code isolated from generic framework
- **Plugin Architecture**: Extensible for future aerospace platforms

### Breaking Changes
- Import paths changed from `ngapy.*` to `sparetools_aerospace.*`
- Class names updated (ASEBench → ASEEnvironment, etc.)
- Configuration providers abstracted

## Dependencies

- `sparetools-test-framework`: Core test framework components
- `sparetools-base`: Foundation utilities and configuration

## Integration

Works seamlessly with:
- **sparetools-test-harness**: Test execution and result collection
- **sparetools-cpython**: Python environment management
- **Existing ngapy workflows**: Drop-in compatibility maintained

## Development

### Adding New Aerospace Environments

1. Extend `TestEnvironment` from `sparetools-test-framework`
2. Implement platform-specific communication protocols
3. Add to `environments/` directory
4. Register in `__init__.py` plugin function

### Domain Logic Preservation

When modifying aerospace components:
- Preserve all existing algorithms and business rules
- Maintain backward compatibility with ngapy interfaces
- Document any logic changes with migration records
- Test against existing ngapy test suites