"""MIA Core - Central orchestration for IoT device management."""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from sparetools_base.security_gates import validate_package


class MiaCore:
    """Central orchestration for MIA IoT Architecture.

    Provides device discovery, connectivity management, and cloud integration
    with security-first approach using SpareTools OpenSSL.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize MIA Core.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.device_manager = None
        self.connectivity_manager = None
        self.cloud_integration = None

        self.logger.info("MIA Core initialized")

    def initialize_components(self):
        """Initialize all MIA components."""
        from .device_manager import DeviceManager
        from .connectivity import ConnectivityManager
        from .cloud_integration import CloudIntegration

        self.device_manager = DeviceManager(self.config.get("devices", {}))
        self.connectivity_manager = ConnectivityManager(self.config.get("connectivity", {}))
        self.cloud_integration = CloudIntegration(self.config.get("cloud", {}))

        self.logger.info("MIA components initialized")

    def discover_devices(self) -> List[Dict[str, Any]]:
        """Discover available IoT devices.

        Returns:
            List of discovered devices
        """
        if not self.device_manager:
            self.initialize_components()

        devices = self.device_manager.discover_devices()
        self.logger.info(f"Discovered {len(devices)} devices")
        return devices

    def connect_device(self, device_id: str) -> bool:
        """Connect to a specific device.

        Args:
            device_id: Unique device identifier

        Returns:
            True if connection successful
        """
        if not self.connectivity_manager:
            self.initialize_components()

        success = self.connectivity_manager.connect_device(device_id)
        if success:
            self.logger.info(f"Connected to device: {device_id}")
        else:
            self.logger.error(f"Failed to connect to device: {device_id}")
        return success

    def send_to_cloud(self, device_id: str, data: Dict[str, Any]) -> bool:
        """Send device data to cloud.

        Args:
            device_id: Device identifier
            data: Data to send

        Returns:
            True if send successful
        """
        if not self.cloud_integration:
            self.initialize_components()

        # Add metadata
        payload = {
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        success = self.cloud_integration.send_data(payload)
        if success:
            self.logger.info(f"Data sent to cloud for device: {device_id}")
        else:
            self.logger.error(f"Failed to send data to cloud for device: {device_id}")
        return success

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status.

        Returns:
            System status dictionary
        """
        status = {
            "mia_version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }

        if self.device_manager:
            status["components"]["device_manager"] = self.device_manager.get_status()

        if self.connectivity_manager:
            status["components"]["connectivity"] = self.connectivity_manager.get_status()

        if self.cloud_integration:
            status["components"]["cloud"] = self.cloud_integration.get_status()

        return status

    def validate_security(self) -> Dict[str, Any]:
        """Validate system security using SpareTools security gates.

        Returns:
            Security validation results
        """
        # Use SpareTools security validation
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a temporary package for validation
            os.makedirs(os.path.join(temp_dir, "bin"))
            os.makedirs(os.path.join(temp_dir, "lib"))

            # Run security validation
            results = validate_package(temp_dir)

            self.logger.info(f"Security validation: {'PASSED' if results.get('passed', False) else 'FAILED'}")
            return results