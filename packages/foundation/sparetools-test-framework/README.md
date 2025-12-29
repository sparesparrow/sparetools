# SpareTools Test Framework

Core test framework components migrated from ngapy, providing reusable test environments, components, and harness integration.

## Overview

This package contains the foundational test framework architecture that supports:

- **Test Environments**: Abstract base classes for hardware test environments
- **Core Components**: Reusable component interfaces for communication and control
- **Test Framework**: Procedures, verification, and reporting infrastructure
- **Embedded Support**: ESP32 and other microcontroller test environments
- **Aerospace Integration**: Legacy aerospace test environment support

## Architecture

### Test Environments
- `test_environments/`: Abstract TestEnvironment base class and implementations
- `test_environments/providers/embedded/`: ESP32 and embedded system environments
- `test_environments/providers/aerospace/`: ASE, JETS, SITS environments

### Core Components
- `core/components/`: Component base classes and implementations
- `core/components/providers/embedded/`: Serial and GPIO components
- `core/components/providers/aerospace/`: Aerospace-specific components
- `core/configuration/`: Configuration management and providers

### Test Framework
- `test_framework/procedures/`: Test procedure execution
- `test_framework/harness/`: Test harness integration
- `test_framework/verification/`: Result verification
- `test_framework/execution/`: Parallel test execution
- `test_framework/reporting/`: HTML reporting

### Tools
- `cli/`: Command-line interface for test execution
- `migration/`: Tools for migrating from ngapy to SpareTools

## Usage

### Basic Test Environment

```python
from sparetools.test_environments.providers.embedded import ESP32Environment, ESP32Config

config = ESP32Config(port="/dev/ttyUSB0", chip="esp32")
env = ESP32Environment(config=config)

# Health check
healthy = env.health_check()

# Firmware flashing
env.flash_firmware("firmware.bin")

# GPIO testing
result = env.run_gpio_test(pin=2, mode="output")
```

### Component Usage

```python
from sparetools.core.components.providers.embedded import SerialComponent, GPIOComponent

# Serial communication
serial = SerialComponent(SerialConfig(port="/dev/ttyUSB0"))
serial.connect()
response = serial.send_and_receive("AT\r\n")

# GPIO testing
gpio = GPIOComponent(serial_component=serial)
result = gpio.test_digital_output(pin=2, test_value=1)
```

### CLI Usage

```bash
# Run test procedure
python -m sparetools.cli.main run test_procedure.py

# Validate environment
python -m sparetools.cli.main validate
```

## Migration from ngapy

This package was created by systematically migrating ngapy components while preserving 100% of existing logic:

- **TestEnvironment**: Migrated from Bench class with full interface compatibility
- **Component**: Migrated from Module class with communication protocol preservation
- **Configuration**: Migrated config_loader with environment provider abstraction
- **Verification**: Extracted verification logic with wrapper classes

## Dependencies

- `sparetools-base`: Core utilities and configuration
- `sparetools-cpython`: Bundled Python environment
- `pyserial`: Serial communication (for embedded components)

## Integration

This package integrates with:

- **sparetools-test-harness**: Pytest integration and result collection
- **sparetools-embedded**: ESP32-specific firmware and hardware testing
- **sparetools-aerospace**: Aerospace test environments and components

## Development

### Adding New Test Environments

1. Extend `TestEnvironment` base class
2. Implement all abstract methods
3. Add to appropriate provider directory
4. Update factory functions

### Adding New Components

1. Extend `Component` base class or create simple components
2. Implement required interfaces
3. Add to provider directories
4. Update imports and documentation