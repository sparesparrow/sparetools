"""Device identifiers for embedded systems.

This module provides pre-defined device identifiers for common
embedded development boards like ESP32, Arduino, etc.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DeviceIdentifier:
    """Identifier for a device type based on USB VID/PID."""

    name: str
    vid: int  # Vendor ID
    pid: int  # Product ID
    device_type: str  # e.g., "esp32", "arduino"
    variant: str = ""  # e.g., "s3", "uno"
    description: str = ""
    baud_rates: List[int] = field(default_factory=lambda: [115200])
    has_jtag: bool = False
    capabilities: List[str] = field(default_factory=list)

    def matches(self, vid: int, pid: int) -> bool:
        """Check if this identifier matches the given VID/PID.

        Args:
            vid: Vendor ID to check
            pid: Product ID to check

        Returns:
            True if matches, False otherwise
        """
        return self.vid == vid and self.pid == pid


# ESP32 Device Identifiers
ESP32_S3_CDC = DeviceIdentifier(
    name="ESP32-S3 USB-CDC",
    vid=0x303A,
    pid=0x1001,
    device_type="esp32",
    variant="s3",
    description="ESP32-S3 native USB CDC",
    baud_rates=[115200, 921600],
    has_jtag=True,
    capabilities=["wifi", "bluetooth", "usb-otg", "psram"],
)

ESP32_S3_JTAG = DeviceIdentifier(
    name="ESP32-S3 JTAG",
    vid=0x303A,
    pid=0x1001,
    device_type="esp32",
    variant="s3-jtag",
    description="ESP32-S3 USB JTAG interface",
    has_jtag=True,
    capabilities=["jtag", "debug"],
)

ESP32_CP210X = DeviceIdentifier(
    name="ESP32 CP210x",
    vid=0x10C4,
    pid=0xEA60,
    device_type="esp32",
    variant="cp210x",
    description="ESP32 with Silicon Labs CP210x USB-UART",
    baud_rates=[115200, 230400, 460800, 921600],
    capabilities=["wifi", "bluetooth"],
)

ESP32_CH340 = DeviceIdentifier(
    name="ESP32 CH340",
    vid=0x1A86,
    pid=0x7523,
    device_type="esp32",
    variant="ch340",
    description="ESP32 with CH340 USB-UART",
    baud_rates=[115200, 230400, 460800, 921600],
    capabilities=["wifi", "bluetooth"],
)

ESP32_FTDI = DeviceIdentifier(
    name="ESP32 FTDI",
    vid=0x0403,
    pid=0x6001,
    device_type="esp32",
    variant="ftdi",
    description="ESP32 with FTDI USB-UART",
    baud_rates=[115200, 230400, 460800, 921600],
    capabilities=["wifi", "bluetooth"],
)

ESP32_C3_CDC = DeviceIdentifier(
    name="ESP32-C3 USB-CDC",
    vid=0x303A,
    pid=0x1001,
    device_type="esp32",
    variant="c3",
    description="ESP32-C3 native USB CDC",
    baud_rates=[115200, 921600],
    has_jtag=True,
    capabilities=["wifi", "bluetooth-le", "risc-v"],
)

# Arduino Device Identifiers
ARDUINO_FTDI = DeviceIdentifier(
    name="Arduino FTDI",
    vid=0x0403,
    pid=0x6001,
    device_type="arduino",
    variant="ftdi",
    description="Arduino with FTDI USB-UART (Duemilanove, older boards)",
    baud_rates=[9600, 57600, 115200],
    capabilities=["avr", "8-bit"],
)

ARDUINO_CH340 = DeviceIdentifier(
    name="Arduino CH340",
    vid=0x1A86,
    pid=0x7523,
    device_type="arduino",
    variant="ch340",
    description="Arduino Nano/Uno clones with CH340",
    baud_rates=[9600, 57600, 115200],
    capabilities=["avr", "8-bit"],
)

ARDUINO_UNO_R3 = DeviceIdentifier(
    name="Arduino Uno R3",
    vid=0x2341,
    pid=0x0043,
    device_type="arduino",
    variant="uno-r3",
    description="Official Arduino Uno R3",
    baud_rates=[9600, 57600, 115200],
    capabilities=["avr", "atmega328p"],
)

ARDUINO_MEGA = DeviceIdentifier(
    name="Arduino Mega 2560",
    vid=0x2341,
    pid=0x0042,
    device_type="arduino",
    variant="mega",
    description="Official Arduino Mega 2560",
    baud_rates=[9600, 57600, 115200],
    capabilities=["avr", "atmega2560"],
)

ARDUINO_LEONARDO = DeviceIdentifier(
    name="Arduino Leonardo",
    vid=0x2341,
    pid=0x8036,
    device_type="arduino",
    variant="leonardo",
    description="Arduino Leonardo with native USB",
    baud_rates=[9600, 57600, 115200],
    capabilities=["avr", "atmega32u4", "native-usb"],
)

# STM32 Device Identifiers
STM32_STLINK_V2 = DeviceIdentifier(
    name="STM32 ST-Link V2",
    vid=0x0483,
    pid=0x3748,
    device_type="stm32",
    variant="stlink-v2",
    description="ST-Link V2 debugger",
    has_jtag=True,
    capabilities=["swd", "debug", "stlink"],
)

STM32_STLINK_V3 = DeviceIdentifier(
    name="STM32 ST-Link V3",
    vid=0x0483,
    pid=0x374B,
    device_type="stm32",
    variant="stlink-v3",
    description="ST-Link V3 debugger",
    has_jtag=True,
    capabilities=["swd", "debug", "stlink", "virtual-com"],
)

# Raspberry Pi Pico
PICO_CDC = DeviceIdentifier(
    name="Raspberry Pi Pico",
    vid=0x2E8A,
    pid=0x000A,
    device_type="rp2040",
    variant="pico",
    description="Raspberry Pi Pico (RP2040)",
    baud_rates=[115200],
    capabilities=["dual-core", "pio", "usb-host"],
)


def get_default_identifiers() -> List[DeviceIdentifier]:
    """Get the list of default device identifiers.

    Returns:
        List of pre-defined device identifiers
    """
    return [
        # ESP32 family
        ESP32_S3_CDC,
        ESP32_S3_JTAG,
        ESP32_CP210X,
        ESP32_CH340,
        ESP32_FTDI,
        ESP32_C3_CDC,
        # Arduino family
        ARDUINO_FTDI,
        ARDUINO_CH340,
        ARDUINO_UNO_R3,
        ARDUINO_MEGA,
        ARDUINO_LEONARDO,
        # STM32
        STM32_STLINK_V2,
        STM32_STLINK_V3,
        # RP2040
        PICO_CDC,
    ]
