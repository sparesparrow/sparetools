"""
SpareTools Embedded Systems Components

Provides components for embedded systems testing including:
- Serial communication
- GPIO testing and control
- Sensor interfaces
- Network testing
"""

from .serial_component import SerialComponent, SerialConfig
from .gpio_component import GPIOComponent, GPIOConfig, GPIOTestResult

__all__ = [
    'SerialComponent',
    'SerialConfig',
    'GPIOComponent',
    'GPIOConfig',
    'GPIOTestResult'
]