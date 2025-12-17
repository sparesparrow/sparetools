"""
ESP32 Bootstrap Support

Provides ESP32-specific bootstrap functionality including:
- PlatformIO setup and configuration
- ESP32 toolchain management
- Board-specific configuration
- Hardware simulation setup
"""

from .platformio_setup import PlatformIOSetup
from .esp32_config import ESP32ConfigManager
from .board_config import ESP32BoardConfig

__all__ = [
    'PlatformIOSetup',
    'ESP32ConfigManager',
    'ESP32BoardConfig'
]