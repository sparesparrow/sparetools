"""Device detector for embedded systems.

This module provides device detection functionality for identifying
connected embedded development boards.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from sparetools.mcp_core.core.exceptions import DeviceError, ErrorCode
from sparetools.mcp_core.devices.identifiers import DeviceIdentifier, get_default_identifiers

logger = logging.getLogger(__name__)


@dataclass
class DeviceInfo:
    """Information about a detected device."""

    port: str
    name: str
    device_type: str
    variant: str
    vid: int
    pid: int
    serial_number: Optional[str] = None
    description: str = ""
    baud_rates: List[int] = field(default_factory=lambda: [115200])
    has_jtag: bool = False
    capabilities: List[str] = field(default_factory=list)
    manufacturer: Optional[str] = None
    product: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format.

        Returns:
            Dictionary representation
        """
        return {
            "port": self.port,
            "name": self.name,
            "device_type": self.device_type,
            "variant": self.variant,
            "vid": f"0x{self.vid:04X}",
            "pid": f"0x{self.pid:04X}",
            "serial_number": self.serial_number,
            "description": self.description,
            "baud_rates": self.baud_rates,
            "has_jtag": self.has_jtag,
            "capabilities": self.capabilities,
            "manufacturer": self.manufacturer,
            "product": self.product,
        }

    def to_json(self) -> str:
        """Convert to JSON string.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=2)


class DeviceDetector:
    """Detector for embedded development devices."""

    def __init__(self) -> None:
        """Initialize the device detector."""
        self.identifiers: List[DeviceIdentifier] = []
        self._use_defaults = True

    def add_identifier(self, identifier: DeviceIdentifier) -> None:
        """Add a device identifier.

        Args:
            identifier: Device identifier to add
        """
        self.identifiers.append(identifier)

    def add_identifiers(self, identifiers: List[DeviceIdentifier]) -> None:
        """Add multiple device identifiers.

        Args:
            identifiers: List of device identifiers to add
        """
        self.identifiers.extend(identifiers)

    def clear_identifiers(self) -> None:
        """Clear all device identifiers."""
        self.identifiers.clear()
        self._use_defaults = False

    def _get_all_identifiers(self) -> List[DeviceIdentifier]:
        """Get all identifiers including defaults if enabled.

        Returns:
            List of all device identifiers
        """
        if self._use_defaults:
            return get_default_identifiers() + self.identifiers
        return self.identifiers

    def detect_all(self) -> List[DeviceInfo]:
        """Detect all connected devices.

        Returns:
            List of detected device information
        """
        devices = []

        try:
            import serial.tools.list_ports

            ports = serial.tools.list_ports.comports()

            for port in ports:
                device_info = self._identify_device(port)
                if device_info:
                    devices.append(device_info)

        except ImportError:
            logger.warning("pyserial not installed, device detection unavailable")

        return devices

    def detect(
        self,
        platforms: Optional[List[str]] = None,
        output_format: str = "json",
    ) -> str:
        """Detect devices with optional filtering.

        Args:
            platforms: Optional list of platforms to filter (e.g., ["esp32", "arduino"])
            output_format: Output format ("json" or "text")

        Returns:
            Detection results in specified format
        """
        devices = self.detect_all()

        # Filter by platform if specified
        if platforms:
            devices = [d for d in devices if d.device_type in platforms]

        if output_format == "json":
            return json.dumps([d.to_dict() for d in devices], indent=2)
        else:
            # Text format
            lines = [f"Found {len(devices)} device(s):"]
            for device in devices:
                lines.append(
                    f"  - {device.name} at {device.port} "
                    f"(VID:0x{device.vid:04X} PID:0x{device.pid:04X})"
                )
            return "\n".join(lines)

    def detect_by_type(self, device_type: str) -> List[DeviceInfo]:
        """Detect devices of a specific type.

        Args:
            device_type: Device type to filter (e.g., "esp32", "arduino")

        Returns:
            List of matching device information
        """
        all_devices = self.detect_all()
        return [d for d in all_devices if d.device_type == device_type]

    def detect_first(self, device_type: Optional[str] = None) -> Optional[DeviceInfo]:
        """Detect the first matching device.

        Args:
            device_type: Optional device type to filter

        Returns:
            First matching device or None
        """
        if device_type:
            devices = self.detect_by_type(device_type)
        else:
            devices = self.detect_all()

        return devices[0] if devices else None

    def _identify_device(self, port: Any) -> Optional[DeviceInfo]:
        """Identify a device from port information.

        Args:
            port: Serial port information

        Returns:
            Device information if identified, None otherwise
        """
        vid = port.vid
        pid = port.pid

        if vid is None or pid is None:
            return None

        # Check against all identifiers
        for identifier in self._get_all_identifiers():
            if identifier.matches(vid, pid):
                return DeviceInfo(
                    port=port.device,
                    name=identifier.name,
                    device_type=identifier.device_type,
                    variant=identifier.variant,
                    vid=vid,
                    pid=pid,
                    serial_number=port.serial_number,
                    description=identifier.description,
                    baud_rates=identifier.baud_rates.copy(),
                    has_jtag=identifier.has_jtag,
                    capabilities=identifier.capabilities.copy(),
                    manufacturer=port.manufacturer,
                    product=port.product,
                )

        # Return generic device info for unknown devices
        return DeviceInfo(
            port=port.device,
            name=port.description or "Unknown Device",
            device_type="unknown",
            variant="",
            vid=vid,
            pid=pid,
            serial_number=port.serial_number,
            description=port.description or "",
            manufacturer=port.manufacturer,
            product=port.product,
        )

    def get_port_by_serial(self, serial_number: str) -> Optional[str]:
        """Get device port by serial number.

        Args:
            serial_number: Device serial number

        Returns:
            Device port if found, None otherwise
        """
        devices = self.detect_all()
        for device in devices:
            if device.serial_number == serial_number:
                return device.port
        return None

    def wait_for_device(
        self,
        device_type: Optional[str] = None,
        timeout: float = 30.0,
        poll_interval: float = 0.5,
    ) -> Optional[DeviceInfo]:
        """Wait for a device to be connected.

        Args:
            device_type: Optional device type to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: Time between polls in seconds

        Returns:
            Device information when found, None if timeout

        Raises:
            DeviceError: If timeout occurs
        """
        import time

        start_time = time.time()

        while time.time() - start_time < timeout:
            device = self.detect_first(device_type)
            if device:
                return device
            time.sleep(poll_interval)

        raise DeviceError(
            f"Timeout waiting for device of type {device_type or 'any'}",
            code=ErrorCode.DEVICE_NOT_FOUND,
        )
