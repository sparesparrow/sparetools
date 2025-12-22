"""Generated Python dataclasses for sparetools.icd.hardware"""

from dataclasses import dataclass, field
from typing import List, Any
from enum import Enum
import time

# Enums
class GPIOMode(Enum):
    INPUT = 0
    OUTPUT = 1
    INPUT_PULLUP = 2
    INPUT_PULLDOWN = 3


# Tables
@dataclass
class GPIOCommand:
    pin: int
    state: bool
    mode: GPIOMode
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class GPIOResponse:
    pin: int
    state: bool
    success: bool
    error_message: str
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class SerialTelemetry:
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))
    sensor_id: str
    data_type: str
    value: float
    unit: str
    raw_data: List[int]

@dataclass
class SerialCommand:
    command: str
    parameters: List[str]
    timeout_ms: int
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class SerialResponse:
    command: str
    success: bool
    response_data: str
    error_message: str
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class HardwareEnvelope:
    message_type: Any
    message_id: int
    source: str

