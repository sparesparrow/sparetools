# CPY Modular Python Environment - Quick Start Guide

## Overview

The CPY system provides a modular Python development environment at `~/CPY` using zero-copy symlinks from Conan packages. This enables 99.99% disk savings while maintaining full functionality.

## What Was Created

### 1. Conan Packages

#### sparetools-cpy-base/1.0.0
- **Location**: `packages/foundation/sparetools-cpy-base/`
- **Purpose**: Base Python 3.12.7 + shared-dev-tools environment
- **Status**: ✅ Built and tested

#### sparetools-cpy-hil/1.0.0
- **Location**: `packages/testing/sparetools-cpy-hil/`
- **Purpose**: Hardware-in-Loop testing for Lennox firmware
- **Includes**: pytest, python-can, pyserial, hypothesis, behave, crcmod, pandas
- **Status**: 📦 Ready to build

### 2. Setup Script

**File**: `scripts/setup-cpy-environment.py`

Automates:
- Resolving Conan package paths
- Creating ~/CPY directory structure with symlinks
- Generating activation scripts
- Environment validation

### 3. Files Updated

- `versions.yaml`: Added cpy-base 1.0.0, cpy-hil 1.0.0

## Quick Start

### Step 1: Build the HIL Package (Optional, but recommended)

```bash
cd /home/sparrow/projects/dev-tools/sparetools

# Build HIL package (this will pip install all testing dependencies)
# Note: This takes ~5-10 minutes as it installs pytest, python-can, etc.
conan create packages/testing/sparetools-cpy-hil --build=missing
```

**Note**: The base package (sparetools-cpy-base/1.0.0) is already built ✅

### Step 2: Setup ~/CPY Environment

```bash
# Setup base environment only
python scripts/setup-cpy-environment.py --env base

# OR setup everything (base + HIL)
python scripts/setup-cpy-environment.py --env all
```

**What this does**:
1. Resolves sparetools-cpython/3.12.7 and sparetools-shared-dev-tools from Conan cache
2. Creates ~/CPY/base/ with symlinks to Python and shared-dev-tools
3. Generates activation scripts in ~/CPY/scripts/
4. Saves metadata in ~/CPY/.cpy-metadata/

### Step 3: Activate and Use

```bash
# Activate base environment
source ~/CPY/scripts/activate-base.sh

# Now you have Python 3.12.7 and shared-dev-tools available
python --version  # Python 3.12.7
python -c "import shared_dev_tools"  # Works!

# Deactivate when done
source ~/CPY/scripts/deactivate.sh
```

### Step 4: Use HIL Environment (After building cpy-hil)

```bash
# Activate HIL environment (automatically activates base too)
source ~/CPY/scripts/activate-hil.sh

# Now you have all HIL testing tools
pytest --version     # pytest 8.0.0
python -c "import can"      # python-can
python -c "import serial"   # pyserial
python -c "import hypothesis"  # hypothesis

# Run Lennox firmware tests
cd ~/projects/lennox-firmware-tests
pytest tests/hil/ -v
```

## Directory Structure

After setup, your ~/CPY will look like:

```
~/CPY/
├── base/                        # Symlinks to CPython + shared-dev-tools
│   ├── bin/                     # → Conan cache CPython bin/
│   ├── lib/                     # → Conan cache CPython lib/
│   ├── include/                 # → Conan cache CPython include/
│   ├── share/                   # → Conan cache CPython share/
│   └── shared_dev_tools/        # → Conan cache shared-dev-tools/
├── envs/
│   └── hil/
│       └── lib/                 # → Conan cache cpy-hil lib/
├── scripts/
│   ├── activate-base.sh         # Base activation
│   ├── activate-hil.sh          # HIL activation
│   └── deactivate.sh            # Deactivation
└── .cpy-metadata/
    ├── base.json                # Base metadata
    └── hil.json                 # HIL metadata
```

## Validation

```bash
# Validate base environment
python scripts/setup-cpy-environment.py --validate base

# Validate HIL environment (after building cpy-hil)
python scripts/setup-cpy-environment.py --validate hil
```

## Common Operations

### Clean Installation
```bash
python scripts/setup-cpy-environment.py --clean
```

### Rebuild HIL Package
```bash
# Remove old version
conan remove "sparetools-cpy-hil/1.0.0" -c

# Rebuild with new dependencies
conan create packages/testing/sparetools-cpy-hil --build=missing

# Re-setup environment
python scripts/setup-cpy-environment.py --clean
python scripts/setup-cpy-environment.py --env all
```

### Check Package Locations
```bash
# Find where packages are installed in Conan cache
conan cache path sparetools-cpy-base/1.0.0
conan cache path sparetools-cpy-hil/1.0.0
```

## Disk Space Savings

**Traditional approach** (copying files):
- CPython: ~350 MB
- shared-dev-tools: ~5 MB
- HIL packages: ~80 MB
- **Total: ~435 MB per installation**

**CPY approach** (symlinks):
- Conan cache (one-time): ~435 MB
- ~/CPY symlinks: ~28 KB
- **Disk savings: 99.99%**

## Lennox Firmware HIL Testing

The HIL environment is specifically designed for testing the Lennox furnace control firmware based on ES-1856 specification:

### Testing Capabilities

1. **RSBus/CAN Protocol**: python-can (CAN 2.0B, 29-bit identifiers)
2. **A2L UART**: pyserial (4800 bps, CRC-16 validation with crcmod)
3. **Requirements-Based**: pytest + behave (BDD/Gherkin)
4. **Safety Testing**: hypothesis (property-based testing)
5. **Data Analysis**: pandas (test results and reporting)

### Example Test

```python
# tests/hil/test_ignition_sequence.py
import pytest
from can import Bus

@pytest.fixture
def rsbus():
    return Bus(interface='socketcan', channel='vcan0', bitrate=125000)

def test_prepurge_timing(rsbus):
    """Verify pre-purge time per ES-1856 3.5.3.2"""
    # Test implementation
    pass
```

## Troubleshooting

### Package Not Found
```bash
# Build missing packages
conan create packages/foundation/sparetools-cpy-base --build=missing
conan create packages/testing/sparetools-cpy-hil --build=missing
```

### Python Not Found
```bash
# Check if symlinks are created
ls -l ~/CPY/base/bin/python3

# Re-run setup
python scripts/setup-cpy-environment.py --clean
python scripts/setup-cpy-environment.py --env all
```

### Import Errors
```bash
# Validate environment
python scripts/setup-cpy-environment.py --validate hil

# Check PYTHONPATH
echo $PYTHONPATH
```

## Next Steps

1. **Build HIL Package**: `conan create packages/testing/sparetools-cpy-hil --build=missing`
2. **Setup Environment**: `python scripts/setup-cpy-environment.py --env all`
3. **Activate**: `source ~/CPY/scripts/activate-hil.sh`
4. **Start Testing**: Write pytest tests for your Lennox firmware!

## Documentation

- **Base Package**: `packages/foundation/sparetools-cpy-base/README.md`
- **HIL Package**: `packages/testing/sparetools-cpy-hil/README.md`
- **Detailed Plan**: `/home/sparrow/.claude/plans/cozy-mixing-ladybug.md`

## Support

For issues or questions, refer to the comprehensive plan document or the package READMEs.

---

**Created**: 2026-01-06
**SpareTools Version**: 2.0.x
**CPython Version**: 3.12.7
