# sparetools-cpy-hil

Hardware-in-the-Loop (HIL) testing environment for Lennox firmware validation.

## Overview

`sparetools-cpy-hil` provides a complete testing environment for embedded firmware HIL testing, specifically designed for the Lennox furnace control system based on the ES-1856 specification.

### Included Packages

Based on `~/Downloads/testing_approaches.txt` requirements:

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | 8.0.0 | Test framework for requirements-based testing |
| pytest-timeout | 2.2.0 | Timeout support for long-running tests |
| python-can | 4.3.1 | RSBus/CAN protocol testing (CAN 2.0B, 29-bit IDs) |
| pyserial | 3.5 | A2L UART testing (4800 bps, 8N1, CRC-16) |
| pyyaml | 6.0.1 | Requirements traceability matrix |
| hypothesis | 6.98.0 | Property-based testing for safety invariants |
| pandas | 2.2.0 | Test data analysis and reporting |
| crcmod | 1.7 | ANSI IBM CRC-16 validation for A2L packets |
| behave | 1.2.6 | BDD/Gherkin testing matching ES-1856 requirements |

## Testing Capabilities

### 1. RSBus/CAN Protocol Testing
- CAN 2.0B with 29-bit identifiers
- Message timing validation (5-60 second intervals)
- Commissioning workflow testing
- Data ID streams (flame current, blower RPM, voltages)

### 2. A2L Safety Validation
- UART 4800 bps, 8N1 protocol
- ANSI IBM CRC-16 packet validation
- Blower mitigation response timing (<15s requirement)

### 3. ANSI Z21.20 Timing Compliance
- Pre-purge timing (15.0s ± 0.5s)
- Flame failure response (<2.0s)
- Ignition sequence validation
- Safety interlock testing

### 4. Requirements Traceability
- Map tests to ES-1856 specification sections
- BDD/Gherkin scenarios for requirement validation
- Automated coverage reporting

## Usage

### Building

```bash
conan create packages/testing/sparetools-cpy-hil --build=missing
```

### With setup-cpy-environment.py

```bash
# Setup HIL environment
python scripts/setup-cpy-environment.py --env hil

# Activate
source ~/CPY/scripts/activate-hil.sh

# Verify installation
python --version      # Python 3.12.7
pytest --version      # pytest 8.0.0
python -c "import can; print(can.__version__)"  # python-can 4.3.1
```

### Example HIL Test

```python
# tests/hil/test_rsbus.py
import pytest
from can import Bus

@pytest.fixture
def rsbus_network():
    """RSBus CAN interface fixture"""
    return Bus(interface='socketcan', channel='vcan0', bitrate=125000)

def test_network_startup_timing(rsbus_network):
    """Verify RSBus network startup per ES-1856 requirements"""
    start_time = time.time()

    rsbus_network.start()
    msg = rsbus_network.wait_for_message(
        node_id=0x10,
        msg_type="NetworkAnnounce",
        timeout=60.0
    )

    elapsed = time.time() - start_time
    assert elapsed < 60.0, f"Network startup too slow: {elapsed}s"
    assert msg.data["equipment_type"] == "IFC-2Stage"
```

## Dependencies

- `sparetools-cpy-base/1.0.0`: Base CPython + shared-dev-tools
- `sparetools-base/2.0.3`: Security gates (python_requires)

## Architecture

```
sparetools-cpy-hil/1.0.0
└── requires: sparetools-cpy-base/1.0.0
    ├── requires: sparetools-cpython/3.12.7
    └── requires: sparetools-shared-dev-tools/2.0.4
```

## Package Info

The package exposes:
- `user.cpy-hil:site_packages`: Path to HIL Python packages
- `user.cpy-hil:packages`: Comma-separated list of installed packages

## Testing Workflow

1. **Setup**: Install HIL environment
2. **Activate**: Source activation script
3. **Develop**: Write pytest tests for firmware validation
4. **Execute**: Run tests against hardware or simulator
5. **Report**: Generate coverage and requirements traceability reports

## License

Apache-2.0
