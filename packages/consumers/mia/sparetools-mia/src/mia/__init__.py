"""MIA (Modular IoT Architecture) - Core IoT connectivity and device management.

This module provides the foundation for IoT device connectivity, cloud integration,
and device lifecycle management in the SpareTools ecosystem.
"""

__version__ = "2.0.0"

from .core import MiaCore
from .device_manager import DeviceManager
from .connectivity import ConnectivityManager
from .cloud_integration import CloudIntegration

__all__ = [
    "MiaCore",
    "DeviceManager",
    "ConnectivityManager",
    "CloudIntegration",
]