"""Device detection and serial communication for SpareTools MCP Core.

This module provides device detection capabilities for embedded systems
like ESP32, Arduino, and other USB serial devices.
"""

from sparetools.mcp_core.devices.detector import DeviceDetector, DeviceInfo
from sparetools.mcp_core.devices.identifiers import (
    DeviceIdentifier,
    ESP32_S3_CDC,
    ESP32_CP210X,
    ESP32_CH340,
    ARDUINO_FTDI,
    ARDUINO_CH340,
    get_default_identifiers,
)
from sparetools.mcp_core.devices.serial import SerialConnection

__all__ = [
    "DeviceDetector",
    "DeviceInfo",
    "DeviceIdentifier",
    "SerialConnection",
    # Pre-defined identifiers
    "ESP32_S3_CDC",
    "ESP32_CP210X",
    "ESP32_CH340",
    "ARDUINO_FTDI",
    "ARDUINO_CH340",
    "get_default_identifiers",
]
