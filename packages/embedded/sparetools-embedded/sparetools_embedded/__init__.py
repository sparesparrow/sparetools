"""
SpareTools Embedded Package

This package contains embedded systems testing capabilities for SpareTools,
including ESP32 and other microcontroller platform support.

Features:
- ESP32 test environments with firmware flashing
- Serial communication components
- GPIO testing and control
- Embedded system integration testing
"""

from sparetools.test_environments.providers.embedded import ESP32Environment, ESP32Config, FirmwareInfo
from sparetools.core.components.providers.embedded import SerialComponent, SerialConfig, GPIOComponent, GPIOConfig
from sparetools.test_environments.providers.embedded.factory import create_embedded_environment

__version__ = "0.1.0"

__all__ = [
    # Environments
    'ESP32Environment',
    'ESP32Config',
    'FirmwareInfo',

    # Components
    'SerialComponent',
    'SerialConfig',
    'GPIOComponent',
    'GPIOConfig',

    # Factory
    'create_embedded_environment'
]


def register_embedded_plugins(plugin_manager):
    """
    Register all embedded systems plugins with the plugin manager.

    Args:
        plugin_manager: The SpareTools plugin manager instance
    """
    # Import here to avoid circular imports
    from sparetools.core.plugins.plugin_manager import PluginManager

    # Register environments
    plugin_manager.register_environment("esp32", ESP32Environment)
    plugin_manager.register_environment("esp32s2", ESP32Environment)
    plugin_manager.register_environment("esp32s3", ESP32Environment)
    plugin_manager.register_environment("esp32c3", ESP32Environment)

    # Note: Components are typically used within environments
    # rather than registered as plugins directly