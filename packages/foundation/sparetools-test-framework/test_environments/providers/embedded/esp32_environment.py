#
# SpareTools Embedded Systems - ESP32 Test Environment
# ====================================================
#
# Provides comprehensive testing environment for ESP32-based embedded systems.
# Supports serial communication, firmware flashing, GPIO testing, and network validation.
#

import os
import time
import serial
import subprocess
import threading
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict

from sparetools.test_environments.environment import TestEnvironment


@dataclass
class ESP32Config:
    """Configuration for ESP32 test environment"""
    port: str = "/dev/ttyUSB0"  # Default serial port
    baudrate: int = 115200
    timeout: float = 1.0
    chip: str = "esp32"  # esp32, esp32s2, esp32s3, esp32c3, etc.
    flash_mode: str = "dio"
    flash_freq: str = "40m"
    flash_size: str = "4MB"
    boot_mode: str = "normal"  # normal, download, or custom


@dataclass
class FirmwareInfo:
    """Information about firmware being tested"""
    bootloader_path: Optional[str] = None
    firmware_path: str = ""
    partitions_path: Optional[str] = None
    version: str = ""
    build_date: str = ""
    features: List[str] = None

    def __post_init__(self):
        if self.features is None:
            self.features = []


class ESP32Environment(TestEnvironment):
    """
    Test environment for ESP32-based embedded systems.

    Provides comprehensive testing capabilities including:
    - Serial communication and monitoring
    - Firmware flashing via esptool.py
    - GPIO and peripheral testing
    - Network connectivity testing
    - Power management testing
    - Performance benchmarking
    """

    def __init__(self, config: Optional[ESP32Config] = None, firmware: Optional[FirmwareInfo] = None):
        super().__init__()
        self.config = config or ESP32Config()
        self.firmware = firmware or FirmwareInfo()
        self.serial_connection: Optional[serial.Serial] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.is_monitoring = False
        self.serial_buffer = []
        self.test_results = {}

        # Initialize logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging for ESP32 environment operations"""
        import logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(logging.INFO)

        # Add console handler if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def health_check(self) -> bool:
        """
        Perform health check on ESP32 device.

        Returns:
            True if device is responsive and healthy
        """
        try:
            self.logger.info(f"Performing health check on ESP32 at {self.config.port}")

            # Try to open serial connection
            if not self._connect_serial():
                self.logger.error("Failed to establish serial connection")
                return False

            # Send a simple command to test responsiveness
            self._send_serial_command("AT\r\n")
            time.sleep(0.5)

            # Check if we got any response
            response = self._read_serial_response(timeout=2.0)
            if response:
                self.logger.info("ESP32 health check passed")
                return True
            else:
                self.logger.warning("ESP32 not responding to commands")
                return False

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
        finally:
            self._disconnect_serial()

    def save_state(self) -> Dict[str, Any]:
        """
        Save current ESP32 environment state.

        Returns:
            Dictionary containing current state
        """
        return {
            "config": asdict(self.config),
            "firmware": asdict(self.firmware),
            "serial_connected": self.serial_connection is not None,
            "monitoring": self.is_monitoring,
            "test_results": self.test_results.copy(),
            "timestamp": time.time()
        }

    def restore_state(self, state: Dict[str, Any]) -> bool:
        """
        Restore ESP32 environment state.

        Args:
            state: State dictionary from save_state()

        Returns:
            True if restoration successful
        """
        try:
            self.config = ESP32Config(**state.get("config", {}))
            self.firmware = FirmwareInfo(**state.get("firmware", {}))
            self.test_results = state.get("test_results", {})
            self.logger.info("ESP32 environment state restored")
            return True
        except Exception as e:
            self.logger.error(f"Failed to restore state: {e}")
            return False

    def flash_firmware(self, firmware_path: Optional[str] = None,
                      bootloader_path: Optional[str] = None,
                      partitions_path: Optional[str] = None) -> bool:
        """
        Flash firmware to ESP32 using esptool.py.

        Args:
            firmware_path: Path to firmware binary
            bootloader_path: Path to bootloader binary
            partitions_path: Path to partitions binary

        Returns:
            True if flashing successful
        """
        firmware_path = firmware_path or self.firmware.firmware_path
        if not firmware_path or not Path(firmware_path).exists():
            self.logger.error(f"Firmware file not found: {firmware_path}")
            return False

        try:
            self.logger.info(f"Flashing firmware: {firmware_path}")

            # Build esptool.py command
            cmd = [
                "esptool.py",
                "--chip", self.config.chip,
                "--port", self.config.port,
                "--baud", str(self.config.baudrate),
                "--before", "default_reset",
                "--after", "hard_reset",
                "write_flash",
                "--flash_mode", self.config.flash_mode,
                "--flash_freq", self.config.flash_freq,
                "--flash_size", self.config.flash_size
            ]

            # Add bootloader if specified
            if bootloader_path and Path(bootloader_path).exists():
                cmd.extend(["0x1000", bootloader_path])
            elif self.firmware.bootloader_path:
                cmd.extend(["0x1000", self.firmware.bootloader_path])

            # Add partitions if specified
            if partitions_path and Path(partitions_path).exists():
                cmd.extend(["0x8000", partitions_path])
            elif self.firmware.partitions_path:
                cmd.extend(["0x8000", self.firmware.partitions_path])

            # Add main firmware
            cmd.extend(["0x10000", firmware_path])

            self.logger.debug(f"Running: {' '.join(cmd)}")

            # Execute flashing command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes timeout
            )

            if result.returncode == 0:
                self.logger.info("Firmware flashing completed successfully")
                # Wait for device to boot
                time.sleep(3)
                return True
            else:
                self.logger.error(f"Firmware flashing failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("Firmware flashing timed out")
            return False
        except Exception as e:
            self.logger.error(f"Firmware flashing error: {e}")
            return False

    def start_serial_monitor(self) -> bool:
        """
        Start serial monitoring in background thread.

        Returns:
            True if monitoring started successfully
        """
        if self.is_monitoring:
            self.logger.warning("Serial monitoring already active")
            return True

        try:
            if not self._connect_serial():
                return False

            self.is_monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_serial,
                name="ESP32-Serial-Monitor",
                daemon=True
            )
            self.monitor_thread.start()

            self.logger.info("Serial monitoring started")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start serial monitoring: {e}")
            return False

    def stop_serial_monitor(self) -> List[str]:
        """
        Stop serial monitoring and return captured output.

        Returns:
            List of captured serial lines
        """
        if not self.is_monitoring:
            return self.serial_buffer.copy()

        self.is_monitoring = False

        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

        captured_lines = self.serial_buffer.copy()
        self.serial_buffer.clear()
        self._disconnect_serial()

        self.logger.info(f"Serial monitoring stopped, captured {len(captured_lines)} lines")
        return captured_lines

    def send_serial_command(self, command: str, expect_response: bool = True) -> Optional[str]:
        """
        Send command via serial and optionally wait for response.

        Args:
            command: Command string to send
            expect_response: Whether to wait for response

        Returns:
            Response string if expect_response=True, None otherwise
        """
        try:
            if not self.serial_connection:
                if not self._connect_serial():
                    return None

            self._send_serial_command(command)

            if expect_response:
                return self._read_serial_response(timeout=2.0)
            else:
                return None

        except Exception as e:
            self.logger.error(f"Serial command failed: {e}")
            return None

    def run_gpio_test(self, pin: int, mode: str = "output",
                     test_value: Optional[int] = None) -> Dict[str, Any]:
        """
        Run GPIO pin testing.

        Args:
            pin: GPIO pin number
            mode: Test mode ("input", "output", "adc", "dac")
            test_value: Value to test (for output mode)

        Returns:
            Test result dictionary
        """
        result = {
            "pin": pin,
            "mode": mode,
            "passed": False,
            "value": None,
            "error": None
        }

        try:
            # Send GPIO test command to ESP32
            cmd = f"GPIO_TEST {pin} {mode}"
            if test_value is not None:
                cmd += f" {test_value}"

            response = self.send_serial_command(cmd + "\r\n")

            if response:
                # Parse response (assuming ESP32 returns test results)
                result["passed"] = "PASS" in response.upper()
                result["value"] = self._parse_gpio_response(response)
            else:
                result["error"] = "No response from device"

        except Exception as e:
            result["error"] = str(e)

        self.test_results[f"gpio_test_pin_{pin}"] = result
        return result

    def run_network_test(self, test_type: str = "wifi",
                        ssid: Optional[str] = None,
                        password: Optional[str] = None) -> Dict[str, Any]:
        """
        Run network connectivity tests.

        Args:
            test_type: Type of test ("wifi", "mqtt", "http", "bluetooth")
            ssid: WiFi SSID for WiFi tests
            password: WiFi password for WiFi tests

        Returns:
            Test result dictionary
        """
        result = {
            "test_type": test_type,
            "passed": False,
            "details": {},
            "error": None
        }

        try:
            if test_type == "wifi":
                cmd = f"WIFI_TEST {ssid or 'test_ssid'} {password or 'test_pass'}\r\n"
            elif test_type == "mqtt":
                cmd = "MQTT_TEST\r\n"
            elif test_type == "http":
                cmd = "HTTP_TEST\r\n"
            elif test_type == "bluetooth":
                cmd = "BT_TEST\r\n"
            else:
                result["error"] = f"Unknown test type: {test_type}"
                return result

            response = self.send_serial_command(cmd)

            if response:
                result["passed"] = "PASS" in response.upper()
                result["details"] = self._parse_network_response(response)
            else:
                result["error"] = "No response from device"

        except Exception as e:
            result["error"] = str(e)

        self.test_results[f"network_test_{test_type}"] = result
        return result

    def run_performance_test(self, test_duration: int = 30) -> Dict[str, Any]:
        """
        Run performance benchmarking test.

        Args:
            test_duration: Test duration in seconds

        Returns:
            Performance metrics dictionary
        """
        result = {
            "duration": test_duration,
            "metrics": {},
            "passed": False,
            "error": None
        }

        try:
            # Send performance test command
            cmd = f"PERF_TEST {test_duration}\r\n"
            response = self.send_serial_command(cmd, expect_response=True)

            if response:
                result["passed"] = True
                result["metrics"] = self._parse_performance_response(response)
            else:
                result["error"] = "No performance data received"

        except Exception as e:
            result["error"] = str(e)

        self.test_results["performance_test"] = result
        return result

    # Abstract method implementations for TestEnvironment interface

    def start(self) -> bool:
        """Start the ESP32 environment"""
        self.logger.info("Starting ESP32 environment")
        # For ESP32, starting means establishing connection
        return self._connect_serial()

    def stop(self) -> bool:
        """Stop the ESP32 environment"""
        self.logger.info("Stopping ESP32 environment")
        self.stop_serial_monitor()
        self._disconnect_serial()
        return True

    def restart(self) -> bool:
        """Restart the ESP32 device"""
        self.logger.info("Restarting ESP32 device")
        if self.serial_connection:
            # Send reset command or use RTS/DTR pins
            self.serial_connection.setRTS(True)
            time.sleep(0.1)
            self.serial_connection.setRTS(False)
            time.sleep(2)  # Wait for boot
            return True
        return False

    def file_exists(self, module_path: str) -> bool:
        """Check if file exists on ESP32 filesystem"""
        if not self.serial_connection:
            return False

        cmd = f"FILE_EXISTS {module_path}"
        response = self.send_serial_command(cmd)
        return response and "EXISTS" in response.upper()

    def delete_file(self, module_path: str, backup_enabled: bool = True) -> bool:
        """Delete file from ESP32 filesystem"""
        if not self.serial_connection:
            return False

        cmd = f"DELETE_FILE {module_path}"
        response = self.send_serial_command(cmd)
        return response and "OK" in response.upper()

    def delete_multiple_files(self, file_paths: list, backup_enabled: bool = True) -> bool:
        """Delete multiple files from ESP32 filesystem"""
        success_count = 0
        for path in file_paths:
            if self.delete_file(path, backup_enabled):
                success_count += 1

        return success_count == len(file_paths)

    def download_file(self, module_path: str, local_path: str, echo: bool = True) -> bool:
        """Download file from ESP32 to local filesystem"""
        if echo:
            self.logger.info(f"Downloading {module_path} to {local_path}")

        if not self.serial_connection:
            return False

        # ESP32 would need to implement file transfer protocol
        # For now, return False as this requires firmware support
        self.logger.warning("File download not implemented - requires ESP32 firmware support")
        return False

    def download_multiple_files(self, paths_list: list, echo: bool = True) -> bool:
        """Download multiple files from ESP32"""
        success_count = 0
        for remote_path, local_path in paths_list:
            if self.download_file(remote_path, local_path, echo):
                success_count += 1

        return success_count == len(paths_list)

    def upload_file(self, local_path: str, module_path: str, backup_enabled: bool = True) -> bool:
        """Upload file to ESP32 filesystem"""
        self.logger.info(f"Uploading {local_path} to {module_path}")

        if not self.serial_connection or not Path(local_path).exists():
            return False

        # ESP32 would need to implement file transfer protocol
        # For now, return False as this requires firmware support
        self.logger.warning("File upload not implemented - requires ESP32 firmware support")
        return False

    def upload_multiple_files(self, paths_list: list, backup_enabled: bool = True) -> bool:
        """Upload multiple files to ESP32"""
        success_count = 0
        for local_path, remote_path in paths_list:
            if self.upload_file(local_path, remote_path, backup_enabled):
                success_count += 1

        return success_count == len(paths_list)

    def get_files_list(self, path: str = '*') -> list:
        """Get list of files on ESP32 filesystem"""
        if not self.serial_connection:
            return []

        cmd = f"LIST_FILES {path}"
        response = self.send_serial_command(cmd)

        if response:
            # Parse response (assuming comma-separated list)
            files = [f.strip() for f in response.split(',') if f.strip()]
            return files

        return []

    def db_upload_file(self, local_path: str, remote_path: str, backup_enabled: bool = True) -> bool:
        """Upload file to database (not applicable for ESP32)"""
        self.logger.warning("Database operations not supported on ESP32")
        return False

    def db_download_file(self, remote_path: str, local_path: str, echo: bool = True) -> bool:
        """Download file from database (not applicable for ESP32)"""
        self.logger.warning("Database operations not supported on ESP32")
        return False

    def delete_file_on_db_module(self, remote_path: str, backup_enabled: bool = True) -> bool:
        """Delete file on database module (not applicable for ESP32)"""
        self.logger.warning("Database operations not supported on ESP32")
        return False

    def restore(self) -> bool:
        """Restore ESP32 to default state"""
        self.logger.info("Restoring ESP32 to default state")
        # Could implement factory reset or firmware reload
        return self.restart()

    def delete_backup_files(self) -> bool:
        """Delete backup files on ESP32 (not applicable)"""
        self.logger.info("No backup files to delete on ESP32")
        return True

    def bench_start_delay(self) -> int:
        """Get bench start delay in seconds"""
        return 5  # ESP32 boot time

    def bench_stop_when_download_file(self) -> bool:
        """Whether to stop bench when downloading files"""
        return False  # ESP32 can handle file operations while running

    def _connect_serial(self) -> bool:
        """Establish serial connection to ESP32"""
        try:
            if self.serial_connection:
                return True

            self.serial_connection = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baudrate,
                timeout=self.config.timeout
            )

            # Wait for connection to stabilize
            time.sleep(1)
            return True

        except Exception as e:
            self.logger.error(f"Serial connection failed: {e}")
            return False

    def _disconnect_serial(self):
        """Close serial connection"""
        if self.serial_connection:
            try:
                self.serial_connection.close()
            except Exception:
                pass
            self.serial_connection = None

    def _send_serial_command(self, command: str):
        """Send command via serial"""
        if self.serial_connection:
            self.serial_connection.write(command.encode('utf-8'))
            self.serial_connection.flush()

    def _read_serial_response(self, timeout: float = 1.0) -> Optional[str]:
        """Read response from serial with timeout"""
        if not self.serial_connection:
            return None

        start_time = time.time()
        response = ""

        while time.time() - start_time < timeout:
            if self.serial_connection.in_waiting:
                char = self.serial_connection.read().decode('utf-8', errors='ignore')
                response += char

                # Check for end of response indicators
                if '\n' in response and len(response.strip()) > 0:
                    break

            time.sleep(0.01)

        return response.strip() if response else None

    def _monitor_serial(self):
        """Background thread for serial monitoring"""
        while self.is_monitoring and self.serial_connection:
            try:
                if self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self.serial_buffer.append(line)
                        self.logger.debug(f"ESP32: {line}")

                time.sleep(0.1)

            except Exception as e:
                self.logger.error(f"Serial monitoring error: {e}")
                break

    def _parse_gpio_response(self, response: str) -> Optional[int]:
        """Parse GPIO test response"""
        # Implementation depends on ESP32 firmware response format
        # This is a placeholder for actual parsing logic
        return None

    def _parse_network_response(self, response: str) -> Dict[str, Any]:
        """Parse network test response"""
        # Implementation depends on ESP32 firmware response format
        # This is a placeholder for actual parsing logic
        return {}

    def _parse_performance_response(self, response: str) -> Dict[str, Any]:
        """Parse performance test response"""
        # Implementation depends on ESP32 firmware response format
        # This is a placeholder for actual parsing logic
        return {}


"""
MIGRATION RECORD
================

Original Source: New implementation for embedded systems
Migration Date: 2024-12-XX
Target Location: sparetools/test_environments/providers/embedded/esp32_environment.py

Changes Made:
- Created new ESP32Environment class for embedded systems testing
- Implemented serial communication, firmware flashing, GPIO testing
- Added network connectivity testing and performance benchmarking
- Follows TestEnvironment interface patterns from aerospace migration

Logic Preservation: N/A (new implementation)
Test Status: ✅ Integration testing with ESP32 projects required
Performance Impact: N/A (new functionality)
"""