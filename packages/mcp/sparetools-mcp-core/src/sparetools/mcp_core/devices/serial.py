"""Serial communication utilities for embedded devices.

This module provides serial communication functionality for
interacting with embedded development boards.
"""

import logging
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

from sparetools.mcp_core.core.exceptions import DeviceError, ErrorCode

logger = logging.getLogger(__name__)


@dataclass
class SerialConfig:
    """Configuration for serial connection."""

    port: str
    baud_rate: int = 115200
    timeout: float = 1.0
    write_timeout: float = 1.0
    byte_size: int = 8
    parity: str = "N"
    stop_bits: float = 1.0
    xonxoff: bool = False
    rtscts: bool = False
    dsrdtr: bool = False


class SerialConnection:
    """Serial connection manager for embedded devices."""

    def __init__(
        self,
        port: str,
        baud_rate: int = 115200,
        timeout: float = 1.0,
    ) -> None:
        """Initialize serial connection.

        Args:
            port: Serial port path (e.g., /dev/ttyUSB0, COM3)
            baud_rate: Baud rate for communication
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self._serial: Any = None
        self._read_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._callbacks: list[Callable[[bytes], None]] = []

    def open(self) -> None:
        """Open the serial connection.

        Raises:
            DeviceError: If connection fails
        """
        try:
            import serial

            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout,
                write_timeout=self.timeout,
            )
            logger.info(f"Opened serial connection to {self.port} at {self.baud_rate} baud")

        except ImportError:
            raise DeviceError(
                "pyserial is required for serial communication",
                code=ErrorCode.DEVICE_CONNECTION_FAILED,
            )
        except Exception as e:
            raise DeviceError(
                f"Failed to open serial port {self.port}: {e}",
                device_port=self.port,
                code=ErrorCode.DEVICE_CONNECTION_FAILED,
                cause=e,
            )

    def close(self) -> None:
        """Close the serial connection."""
        self.stop_reading()
        if self._serial and self._serial.is_open:
            self._serial.close()
            logger.info(f"Closed serial connection to {self.port}")
        self._serial = None

    @property
    def is_open(self) -> bool:
        """Check if connection is open.

        Returns:
            True if open, False otherwise
        """
        return self._serial is not None and self._serial.is_open

    def write(self, data: bytes) -> int:
        """Write data to serial port.

        Args:
            data: Data to write

        Returns:
            Number of bytes written

        Raises:
            DeviceError: If write fails
        """
        if not self.is_open:
            raise DeviceError(
                "Serial port not open",
                device_port=self.port,
                code=ErrorCode.DEVICE_CONNECTION_FAILED,
            )

        try:
            return self._serial.write(data)
        except Exception as e:
            raise DeviceError(
                f"Failed to write to serial port: {e}",
                device_port=self.port,
                code=ErrorCode.DEVICE_COMMUNICATION_ERROR,
                cause=e,
            )

    def write_line(self, line: str, encoding: str = "utf-8") -> int:
        """Write a line to serial port with newline.

        Args:
            line: Line to write
            encoding: Character encoding

        Returns:
            Number of bytes written
        """
        data = (line + "\n").encode(encoding)
        return self.write(data)

    def read(self, size: int = 1) -> bytes:
        """Read data from serial port.

        Args:
            size: Number of bytes to read

        Returns:
            Data read from port

        Raises:
            DeviceError: If read fails
        """
        if not self.is_open:
            raise DeviceError(
                "Serial port not open",
                device_port=self.port,
                code=ErrorCode.DEVICE_CONNECTION_FAILED,
            )

        try:
            return self._serial.read(size)
        except Exception as e:
            raise DeviceError(
                f"Failed to read from serial port: {e}",
                device_port=self.port,
                code=ErrorCode.DEVICE_COMMUNICATION_ERROR,
                cause=e,
            )

    def read_line(self, encoding: str = "utf-8") -> str:
        """Read a line from serial port.

        Args:
            encoding: Character encoding

        Returns:
            Line read from port
        """
        if not self.is_open:
            raise DeviceError(
                "Serial port not open",
                device_port=self.port,
                code=ErrorCode.DEVICE_CONNECTION_FAILED,
            )

        try:
            line = self._serial.readline()
            return line.decode(encoding).strip()
        except Exception as e:
            raise DeviceError(
                f"Failed to read line from serial port: {e}",
                device_port=self.port,
                code=ErrorCode.DEVICE_COMMUNICATION_ERROR,
                cause=e,
            )

    def read_all(self) -> bytes:
        """Read all available data from serial port.

        Returns:
            All available data
        """
        if not self.is_open:
            return b""

        try:
            return self._serial.read_all()
        except Exception:
            return b""

    def flush(self) -> None:
        """Flush serial port buffers."""
        if self.is_open:
            self._serial.flush()

    def reset_input_buffer(self) -> None:
        """Clear input buffer."""
        if self.is_open:
            self._serial.reset_input_buffer()

    def reset_output_buffer(self) -> None:
        """Clear output buffer."""
        if self.is_open:
            self._serial.reset_output_buffer()

    def add_read_callback(self, callback: Callable[[bytes], None]) -> None:
        """Add a callback for async reading.

        Args:
            callback: Function to call with received data
        """
        self._callbacks.append(callback)

    def remove_read_callback(self, callback: Callable[[bytes], None]) -> None:
        """Remove a read callback.

        Args:
            callback: Callback to remove
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def start_reading(self, buffer_size: int = 1024) -> None:
        """Start async reading in background thread.

        Args:
            buffer_size: Size of read buffer
        """
        if self._read_thread is not None:
            return

        self._stop_event.clear()
        self._read_thread = threading.Thread(
            target=self._read_loop,
            args=(buffer_size,),
            daemon=True,
        )
        self._read_thread.start()
        logger.info(f"Started async reading from {self.port}")

    def stop_reading(self) -> None:
        """Stop async reading."""
        if self._read_thread is None:
            return

        self._stop_event.set()
        self._read_thread.join(timeout=2.0)
        self._read_thread = None
        logger.info(f"Stopped async reading from {self.port}")

    def _read_loop(self, buffer_size: int) -> None:
        """Internal read loop for async reading.

        Args:
            buffer_size: Size of read buffer
        """
        while not self._stop_event.is_set():
            try:
                if self.is_open and self._serial.in_waiting > 0:
                    data = self._serial.read(min(buffer_size, self._serial.in_waiting))
                    if data:
                        for callback in self._callbacks:
                            try:
                                callback(data)
                            except Exception as e:
                                logger.error(f"Error in read callback: {e}")
                else:
                    time.sleep(0.01)  # Avoid busy waiting
            except Exception as e:
                if not self._stop_event.is_set():
                    logger.error(f"Error in read loop: {e}")
                break

    def send_command(
        self,
        command: str,
        wait_response: bool = True,
        timeout: float = 1.0,
        encoding: str = "utf-8",
    ) -> Optional[str]:
        """Send a command and optionally wait for response.

        Args:
            command: Command to send
            wait_response: Whether to wait for response
            timeout: Response timeout
            encoding: Character encoding

        Returns:
            Response if wait_response is True, None otherwise
        """
        self.write_line(command, encoding)

        if not wait_response:
            return None

        # Wait for response
        start_time = time.time()
        response_lines = []

        while time.time() - start_time < timeout:
            if self._serial.in_waiting > 0:
                line = self.read_line(encoding)
                if line:
                    response_lines.append(line)
                    # Check for common response terminators
                    if line.endswith("OK") or line.endswith("ERROR"):
                        break
            else:
                time.sleep(0.01)

        return "\n".join(response_lines) if response_lines else None

    def __enter__(self) -> "SerialConnection":
        """Context manager entry."""
        self.open()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
