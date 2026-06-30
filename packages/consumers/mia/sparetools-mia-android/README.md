# SpareTools MIA Android

MIA Android-specific utilities, device workspace configurations, and demo scripts for mobile integration.

## Components

### Device Workspace
- **Android Device Workspace** (`android-device-workspace/`) - Configuration and setup utilities for Android device integration
- Device-specific configurations and connection utilities

### Demo Scripts
- **Citroen C4 Demo** (`android_citroen_c4_demo.py`) - Android integration demo for Citroen C4 vehicle systems
- Example scripts for Android device communication and control

### Mobile Integration
- Android-specific utilities for MIA ecosystem integration
- Mobile device management and communication tools
- Bluetooth Low Energy (BLE) integration helpers

## Installation

### Via SpareTools (Recommended)

```bash
# Using Conan
conan install sparetools-mia-android/2.0.0@
```

### Direct Installation

```bash
pip install sparetools-mia-android
```

## Usage

```python
from mia.android import android_citroen_c4_demo
from mia.android.android_device_workspace import DeviceManager

# Initialize Android device workspace
device_mgr = DeviceManager()
device_mgr.configure_device("citroen_c4")

# Run Android integration demo
demo = android_citroen_c4_demo.CitroenC4Demo()
demo.start_integration()
```

## Configuration

The package includes configuration files for various Android devices and integration scenarios:

- Device workspace configurations in `android-device-workspace/`
- Demo script configurations for different vehicle systems
- Integration settings for mobile communication protocols

## Dependencies

- `sparetools-mia` - Core MIA functionality
- `sparetools-base` - SpareTools foundation
- `pydantic` - Data validation
- `pyyaml` - Configuration file handling

## Development

### Building from Source

```bash
# Clone the repository
git clone https://github.com/sparesparrow/sparetools.git
cd sparetools/packages/consumers/mia/sparetools-mia-android

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Adding New Android Devices

1. Create device configuration in `android-device-workspace/`
2. Add device-specific utilities in appropriate modules
3. Update demo scripts with new device support
4. Add configuration examples to documentation

## License

Apache 2.0 License - see LICENSE file for details.

## Support

For issues and questions:
- GitHub Issues: [sparesparrow/sparetools](https://github.com/sparesparrow/sparetools/issues)
- Documentation: [MIA Android Documentation](https://github.com/sparesparrow/sparetools/tree/main/packages/consumers/mia/sparetools-mia-android)