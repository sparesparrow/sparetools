"""
Embedded Test Environment Factory

Creates and manages test environments for embedded systems,
particularly ESP32-based devices and other microcontroller platforms.
"""

from typing import Dict, Any, Optional, Type
from sparetools.test_environments.environment import TestEnvironment
from .esp32_environment import ESP32Environment, ESP32Config, FirmwareInfo


class EmbeddedEnvironmentFactory:
    """
    Factory for creating embedded test environments.

    Supports various embedded platforms with extensible architecture.
    """

    def __init__(self):
        self.environment_types: Dict[str, Type[TestEnvironment]] = {
            'esp32': ESP32Environment,
            'esp32s2': ESP32Environment,
            'esp32s3': ESP32Environment,
            'esp32c3': ESP32Environment,
            # Add more platforms as needed
        }

    def create_environment(self, platform: str, **kwargs) -> Optional[TestEnvironment]:
        """
        Create a test environment for the specified platform.

        Args:
            platform: Platform type ('esp32', 'esp32s2', etc.)
            **kwargs: Platform-specific configuration parameters

        Returns:
            Configured test environment or None if platform not supported
        """
        env_class = self.environment_types.get(platform.lower())
        if not env_class:
            return None

        if platform.startswith('esp32'):
            # ESP32-specific configuration
            config = ESP32Config(
                port=kwargs.get('port', '/dev/ttyUSB0'),
                baudrate=kwargs.get('baudrate', 115200),
                chip=platform,
                flash_mode=kwargs.get('flash_mode', 'dio'),
                flash_freq=kwargs.get('flash_freq', '40m'),
                flash_size=kwargs.get('flash_size', '4MB')
            )

            firmware = None
            if 'firmware_path' in kwargs:
                firmware = FirmwareInfo(
                    firmware_path=kwargs['firmware_path'],
                    bootloader_path=kwargs.get('bootloader_path'),
                    partitions_path=kwargs.get('partitions_path'),
                    version=kwargs.get('version', ''),
                    features=kwargs.get('features', [])
                )

            return env_class(config=config, firmware=firmware)

        # Add other platform configurations here
        return None

    def get_supported_platforms(self) -> list:
        """
        Get list of supported platforms.

        Returns:
            List of supported platform names
        """
        return list(self.environment_types.keys())

    def register_platform(self, platform: str, env_class: Type[TestEnvironment]):
        """
        Register a new platform type.

        Args:
            platform: Platform name
            env_class: Environment class for the platform
        """
        self.environment_types[platform.lower()] = env_class


# Global factory instance
embedded_factory = EmbeddedEnvironmentFactory()


def create_embedded_environment(platform: str, **kwargs) -> Optional[TestEnvironment]:
    """
    Convenience function to create embedded test environments.

    Args:
        platform: Platform type
        **kwargs: Platform configuration

    Returns:
        Configured test environment
    """
    return embedded_factory.create_environment(platform, **kwargs)