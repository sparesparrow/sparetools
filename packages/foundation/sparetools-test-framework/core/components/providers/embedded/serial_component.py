#
# SpareTools Embedded Systems - Serial Communication Component
# ===========================================================
#
# Provides serial communication capabilities for embedded systems testing.
# Supports UART communication with various protocols and data formats.
#

import serial
import time
import threading
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass

from typing import Protocol


@dataclass
class SerialConfig:
    """Configuration for serial communication"""
    port: str
    baudrate: int = 115200
    bytesize: int = serial.EIGHTBITS
    parity: str = serial.PARITY_NONE
    stopbits: int = serial.STOPBITS_ONE
    timeout: float = 1.0
    xonxoff: bool = False
    rtscts: bool = False
    dsrdtr: bool = False


class SerialComponent:
    """
    Serial communication component for embedded systems.

    Provides reliable serial communication with features like:
    - Automatic reconnection
    - Data buffering and parsing
    - Protocol support (AT commands, custom protocols)
    - Background monitoring
    - Error handling and recovery
    """

    def __init__(self, config: SerialConfig):
        self.config = config
        self.serial_connection: Optional[serial.Serial] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.is_monitoring = False
        self.data_buffer: List[bytes] = []
        self.line_buffer: List[str] = []
        self.response_handlers: Dict[str, Callable] = {}
        self._setup_logging()

    def init(self):
        """Initialize the serial component"""
        return self.connect()

    def delete_file(self, module_path, backup_enabled=True):
        """Not applicable for serial component"""
        return False

    def delete_multiple_files(self, file_paths, backup_enabled=True):
        """Not applicable for serial component"""
        return False

    def download_file(self, module_path, local_path, echo=True):
        """Not applicable for serial component"""
        return False

    def download_multiple_files(self, paths_list, echo=True):
        """Not applicable for serial component"""
        return False

    def upload_file(self, local_path, module_path, backup_enabled=True):
        """Not applicable for serial component"""
        return False

    def upload_multiple_files(self, paths_list, backup_enabled=True):
        """Not applicable for serial component"""
        return False

    def get_files_list(self, path='*'):
        """Not applicable for serial component"""
        return []

    def load_image(self, image_path):
        """Not applicable for serial component"""
        return False

    def restart(self):
        """Restart serial connection"""
        self.disconnect()
        return self.connect()

    def start(self):
        """Start serial component"""
        return self.connect()

    def stop(self):
        """Stop serial component"""
        return self.disconnect()

    def _setup_logging(self):
        """Setup logging for serial component"""
        import logging
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def connect(self) -> bool:
        """
        Establish serial connection.

        Returns:
            True if connection successful
        """
        try:
            if self.serial_connection and self.serial_connection.is_open:
                return True

            self.serial_connection = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baudrate,
                bytesize=self.config.bytesize,
                parity=self.config.parity,
                stopbits=self.config.stopbits,
                timeout=self.config.timeout,
                xonxoff=self.config.xonxoff,
                rtscts=self.config.rtscts,
                dsrdtr=self.config.dsrdtr
            )

            self.logger.info(f"Connected to {self.config.port} at {self.config.baudrate} baud")
            return True

        except serial.SerialException as e:
            self.logger.error(f"Failed to connect to {self.config.port}: {e}")
            return False

    def disconnect(self) -> bool:
        """
        Close serial connection.

        Returns:
            True if disconnection successful
        """
        try:
            self.stop_monitoring()

            if self.serial_connection:
                self.serial_connection.close()
                self.serial_connection = None

            self.logger.info("Serial connection closed")
            return True

        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")
            return False

    def send_command(self, command: str, encoding: str = 'utf-8',
                    add_newline: bool = True) -> bool:
        """
        Send command via serial.

        Args:
            command: Command string to send
            encoding: Text encoding to use
            add_newline: Whether to add newline character

        Returns:
            True if command sent successfully
        """
        try:
            if not self.serial_connection or not self.serial_connection.is_open:
                if not self.connect():
                    return False

            data = command.encode(encoding)
            if add_newline:
                data += b'\r\n'

            self.serial_connection.write(data)
            self.serial_connection.flush()

            self.logger.debug(f"Sent: {command}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send command: {e}")
            return False

    def read_response(self, timeout: float = 1.0, encoding: str = 'utf-8') -> Optional[str]:
        """
        Read response from serial.

        Args:
            timeout: Read timeout in seconds
            encoding: Text encoding to use

        Returns:
            Response string or None if timeout
        """
        try:
            if not self.serial_connection or not self.serial_connection.is_open:
                return None

            start_time = time.time()
            response = ""

            while time.time() - start_time < timeout:
                if self.serial_connection.in_waiting:
                    char = self.serial_connection.read().decode(encoding, errors='ignore')
                    response += char

                    # Check for common response terminators
                    if response.endswith('\n') or response.endswith('\r'):
                        break

                time.sleep(0.01)

            response = response.strip()
            if response:
                self.logger.debug(f"Received: {response}")
                return response

            return None

        except Exception as e:
            self.logger.error(f"Failed to read response: {e}")
            return None

    def send_and_receive(self, command: str, timeout: float = 2.0) -> Optional[str]:
        """
        Send command and wait for response.

        Args:
            command: Command to send
            timeout: Total timeout for send+receive

        Returns:
            Response string or None
        """
        if self.send_command(command):
            return self.read_response(timeout=timeout)
        return None

    def start_monitoring(self, callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        Start background monitoring of serial data.

        Args:
            callback: Optional callback function for received lines

        Returns:
            True if monitoring started successfully
        """
        if self.is_monitoring:
            return True

        try:
            if not self.connect():
                return False

            self.is_monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_serial,
                args=(callback,),
                name="Serial-Monitor",
                daemon=True
            )
            self.monitor_thread.start()

            self.logger.info("Serial monitoring started")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            return False

    def stop_monitoring(self) -> List[str]:
        """
        Stop monitoring and return buffered data.

        Returns:
            List of buffered lines
        """
        if not self.is_monitoring:
            return self.line_buffer.copy()

        self.is_monitoring = False

        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

        buffered_lines = self.line_buffer.copy()
        self.line_buffer.clear()

        self.logger.info(f"Monitoring stopped, returned {len(buffered_lines)} lines")
        return buffered_lines

    def register_response_handler(self, pattern: str, handler: Callable[[str], Any]):
        """
        Register a handler for specific response patterns.

        Args:
            pattern: Response pattern to match
            handler: Handler function to call
        """
        self.response_handlers[pattern] = handler

    def wait_for_pattern(self, pattern: str, timeout: float = 10.0) -> Optional[str]:
        """
        Wait for a specific pattern in the serial output.

        Args:
            pattern: Pattern to wait for
            timeout: Timeout in seconds

        Returns:
            Matching line or None if timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.line_buffer:
                for line in self.line_buffer:
                    if pattern in line:
                        return line

            # Also check current serial input
            if self.serial_connection and self.serial_connection.in_waiting:
                line = self.read_response(timeout=0.1)
                if line and pattern in line:
                    return line

            time.sleep(0.1)

        return None

    def _monitor_serial(self, callback: Optional[Callable[[str], None]] = None):
        """Background monitoring thread"""
        while self.is_monitoring and self.serial_connection:
            try:
                if self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()

                    if line:
                        self.line_buffer.append(line)

                        # Check for registered response handlers
                        for pattern, handler in self.response_handlers.items():
                            if pattern in line:
                                try:
                                    handler(line)
                                except Exception as e:
                                    self.logger.error(f"Response handler error: {e}")

                        # Call callback if provided
                        if callback:
                            try:
                                callback(line)
                            except Exception as e:
                                self.logger.error(f"Callback error: {e}")

                time.sleep(0.05)

            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                break

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get information about the current serial connection.

        Returns:
            Dictionary with connection details
        """
        info = {
            "port": self.config.port,
            "connected": False,
            "baudrate": self.config.baudrate,
            "bytesize": self.config.bytesize,
            "parity": self.config.parity,
            "stopbits": self.config.stopbits,
            "monitoring": self.is_monitoring,
            "buffered_lines": len(self.line_buffer)
        }

        if self.serial_connection:
            info["connected"] = self.serial_connection.is_open
            if self.serial_connection.is_open:
                info.update({
                    "in_waiting": self.serial_connection.in_waiting,
                    "out_waiting": getattr(self.serial_connection, 'out_waiting', 0),
                    "dsr": self.serial_connection.dsr,
                    "cts": self.serial_connection.cts,
                    "cd": self.serial_connection.cd,
                    "ri": self.serial_connection.ri
                })

        return info


"""
MIGRATION RECORD
================

Original Source: New implementation for embedded systems
Migration Date: 2024-12-XX
Target Location: sparetools/core/components/providers/embedded/serial_component.py

Changes Made:
- Created new SerialComponent class for embedded serial communication
- Implemented connection management, command/response handling
- Added background monitoring and pattern matching
- Follows Component interface patterns from aerospace migration

Logic Preservation: N/A (new implementation)
Test Status: ✅ Integration testing with ESP32 projects required
Performance Impact: N/A (new functionality)
"""