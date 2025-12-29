"""
SpareTools Embedded Systems Provider

Provides test environments and components for embedded systems,
particularly ESP32-based devices and other microcontroller platforms.
"""

from .esp32_environment import ESP32Environment, ESP32Config, FirmwareInfo

__all__ = [
    'ESP32Environment',
    'ESP32Config',
    'FirmwareInfo'
]