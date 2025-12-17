# OBD-II Simulation Guide

This guide explains how to set up and use the OBD-II simulation environment using the ELM327-emulator.

## Overview

The OBD-II simulation setup provides a hermetic Python environment with an ELM327-compatible emulator for testing OBD-II applications without physical hardware. The bootstrap script automatically downloads CPython 3.12.7 from Cloudsmith and configures the emulator to simulate a vehicle's OBD-II interface.

## Prerequisites

- **System Python 3.x**: Required for initial bootstrap execution
- **Network Access**: Access to Cloudsmith (`dl.cloudsmith.io`)
- **Disk Space**: ~100-200MB for CPython runtime and packages
- **Permissions**: Write access to project root directory

### Linux-Specific Requirements

- **Serial Port Access**: User must be in `dialout` group for serial port access
  ```bash
  sudo usermod -a -G dialout $USER
  # Log out and back in for changes to take effect
  ```
- **socat** (optional): May be required for some serial port operations
  ```bash
  sudo apt-get install socat  # Debian/Ubuntu
  ```

## Quick Start

### 1. Run Bootstrap Script

```bash
./bootstrap-obd.py
```

Or with system Python:

```bash
python3 bootstrap-obd.py
```

### 2. Expected Behavior

The script will:

1. **Check for existing installation**: If `.mia/python` exists and is valid, skip download
2. **Download CPython**: Fetch CPython 3.12.7 from Cloudsmith for your platform
3. **Extract runtime**: Extract to `.mia/python` directory atomically
4. **Verify installation**: Check that Python and pip executables work
5. **Install packages**: Install `ELM327-emulator` and `obd` packages via pip
6. **Launch emulator**: Start ELM327-emulator in car scenario mode

### 3. Emulator Output

The emulator will:
- Start in foreground mode
- Display connection information (virtual serial port)
- Simulate a Toyota Auris Hybrid by default
- Accept OBD-II commands and respond with simulated data

Example output:
```
[BOOTSTRAP] Starting emulator (this will run in foreground)...
[BOOTSTRAP] Press Ctrl+C to stop the emulator
============================================================
ELM327 Emulator vX.X.X
Virtual serial port: /dev/pts/3
Scenario: car (Toyota Auris Hybrid)
Ready for connections...
```

## Architecture

### Directory Structure

```
.mia/
└── python/              # Hermetic CPython 3.12.7 installation
    ├── bin/            # Executables (Linux/macOS)
    │   ├── python3
    │   └── pip3
    └── lib/            # Python standard library
```

### Environment Isolation

The bootstrap script uses `PYTHONHOME` to ensure complete isolation:

- **PYTHONHOME**: Set to `.mia/python` directory
- **PATH**: Prepended with `.mia/python/bin` (or `Scripts` on Windows)
- **No system dependencies**: All Python packages installed in hermetic environment

### Platform Support

| Platform | Architecture | Status |
|----------|-------------|--------|
| Linux    | x86_64      | ✅ Supported |
| macOS    | arm64       | ✅ Supported |
| Windows  | x86_64      | ✅ Supported |

## Usage

### Running the Emulator

```bash
# Run bootstrap (downloads and launches emulator)
./bootstrap-obd.py

# The emulator runs in foreground
# Press Ctrl+C to stop
```

### Connecting to the Emulator

Once running, the emulator exposes a virtual serial port:

**Linux/macOS:**
```bash
# Example: /dev/pts/3
screen /dev/pts/3 9600
# Or use your OBD-II library
```

**Windows:**
```powershell
# Example: COM4
# Use your OBD-II library to connect
```

### Using with OBD-II Libraries

The `obd` Python package is pre-installed. Example usage:

```python
import obd

# Connect to virtual serial port
connection = obd.OBD("/dev/pts/3")  # Linux/macOS
# connection = obd.OBD("COM4")      # Windows

# Query vehicle speed
cmd = obd.commands.SPEED
response = connection.query(cmd)
print(f"Speed: {response.value}")
```

## Troubleshooting

### HTTPError 404: Package Not Found

**Symptom**: `HTTP error 404: Not Found`

**Cause**: CPython version or platform architecture mismatch

**Remediation**:
1. Verify `CPY_VER` in `bootstrap-obd.py` matches Cloudsmith manifest
2. Check platform detection: `platform.system()` should return "Linux", "Darwin", or "Windows"
3. Verify Cloudsmith repository path: `sparesparrow/cpy`

**Check available versions**:
```bash
# Visit Cloudsmith repository
https://cloudsmith.io/~sparesparrow/repos/cpy/packages/
```

### ModuleNotFoundError

**Symptom**: `ModuleNotFoundError: No module named 'elm327_emulator'`

**Cause**: Package installation failed or script not run from project root

**Remediation**:
1. Ensure script runs from project root directory
2. Purge `.mia` directory and re-run:
   ```bash
   rm -rf .mia
   ./bootstrap-obd.py
   ```
3. Check network connectivity for pip install
4. Verify pip installation succeeded (check script output)

### PermissionError: /dev/pts/X

**Symptom**: `PermissionError: [Errno 13] Permission denied: '/dev/pts/3'`

**Cause**: User lacks serial port permissions (Linux)

**Remediation**:
1. Add user to `dialout` group:
   ```bash
   sudo usermod -a -G dialout $USER
   ```
2. Log out and back in (or use `newgrp dialout`)
3. Verify group membership:
   ```bash
   groups
   ```
4. Check `socat` availability if needed:
   ```bash
   which socat
   ```

### Address Already in Use

**Symptom**: `OSError: [Errno 98] Address already in use` or port conflict

**Cause**: Previous emulator instance still running or port conflict

**Remediation**:
1. Find and kill zombie Python processes:
   ```bash
   ps aux | grep elm327
   kill <PID>
   ```
2. Specify different port via emulator flags (if supported)
3. Check for other processes using the serial port:
   ```bash
   lsof /dev/pts/3  # Linux/macOS
   ```

### Extraction Failed

**Symptom**: `File operation failed` or `OSError: [Errno 28] No space left on device`

**Cause**: Insufficient disk space or permissions

**Remediation**:
1. Check available disk space:
   ```bash
   df -h .
   ```
2. Ensure write permissions in project root:
   ```bash
   ls -ld .
   ```
3. Clean up temporary files:
   ```bash
   rm -rf /tmp/cpython-*
   ```

### Network Connectivity Issues

**Symptom**: `Network error: [Errno 101] Network is unreachable`

**Cause**: No internet access or Cloudsmith unreachable

**Remediation**:
1. Verify internet connectivity:
   ```bash
   ping dl.cloudsmith.io
   ```
2. Check firewall/proxy settings
3. Verify Cloudsmith repository is accessible:
   ```bash
   curl -I https://dl.cloudsmith.io/public/sparesparrow/cpy/raw/files/
   ```

## Advanced Usage

### Custom Emulator Configuration

Modify `bootstrap-obd.py` to customize emulator launch:

```python
# In launch_emulator() function
cmd = [
    PYTHON_EXE, "-m", "elm327_emulator",
    "--scenario", "car",
    "--port", "35000",  # Custom port
    "--baud", "38400"   # Custom baud rate
]
```

### Running Emulator in Background

To run emulator in background, modify `launch_emulator()`:

```python
# Use subprocess.Popen instead of subprocess.run
process = subprocess.Popen(cmd, env=env)
print_status(f"Emulator started in background (PID: {process.pid})")
```

### Using Different Python Version

To use a different CPython version:

1. Update `CPY_VER` in `bootstrap-obd.py`
2. Verify version exists in Cloudsmith repository
3. Re-run bootstrap script

## Integration with MIA

The OBD-II simulation environment integrates with MIA projects:

1. **Hermetic Environment**: No system-wide dependencies
2. **Cloudsmith Integration**: Uses same Cloudsmith infrastructure as MIA packages
3. **Conan Compatibility**: Can be used alongside Conan-managed dependencies

See [MIA Integration Guide](MIA-INTEGRATION.md) for details.

## References

- **ELM327-emulator**: [GitHub Repository](https://github.com/Ircama/ELM327-emulator)
- **Python-OBD**: [Documentation](https://python-obd.readthedocs.io/)
- **OBD-II Protocol**: [Wikipedia](https://en.wikipedia.org/wiki/On-board_diagnostics)

## Best Practices

1. **Version Pinning**: Pin CPython version in `bootstrap-obd.py` for reproducibility
2. **Cache Management**: `.mia/` directory is gitignored; purge if corrupted
3. **Isolation**: Never modify `.mia/python` manually; always use bootstrap script
4. **Testing**: Test emulator connection before integrating with production code

## Support

For issues or questions:

1. Check this troubleshooting guide
2. Review [MIA Integration Guide](MIA-INTEGRATION.md)
3. Check ELM327-emulator documentation
4. Open an issue on GitHub

## Version History

- **2025-01-XX**: Initial OBD-II simulation setup with CPython 3.12.7
