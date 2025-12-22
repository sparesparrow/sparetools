"""Generated Python dataclasses for sparetools.icd.rf"""

from dataclasses import dataclass, field
from typing import List, Any
from enum import Enum
import time

# Enums
class RFModulation(Enum):
    ASK = 0
    FSK = 1
    OOK = 2
    GFSK = 3
    MSK = 4
    RAW = 5       // Raw signal


# Tables
@dataclass
class RFCaptureConfig:
    frequency: int
    modulation: RFModulation
    sample_rate: int
    gain: Any
    bandwidth: int
    squelch: Any

@dataclass
class RFCaptureStart:
    config: Any
    duration_ms: int
    max_frames: int
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class RFCaptureStop:
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class RFFrame:
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))
    frequency: int
    modulation: RFModulation
    data: List[int]
    rssi: Any
    snr: float
    frame_id: int

@dataclass
class RFCaptureStatus:
    active: bool
    frames_captured: int
    duration_ms: int
    config: Any
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class RFCaptureResponse:
    success: bool
    error_message: str
    status: Any
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class RFReplayConfig:
    frequency: int
    modulation: RFModulation
    tx_power: Any
    repeat_count: Any
    repeat_delay_ms: int

@dataclass
class RFReplay:
    frame: Any
    config: Any
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class RFReplayResponse:
    success: bool
    frames_sent: int
    error_message: str
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class RFSpectrumQuery:
    start_freq: int
    end_freq: int
    step_hz: int
    dwell_ms: int
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class RFSpectrumData:
    frequency: int
    power: float
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class RFSpectrumResponse:
    success: bool
    data: List[Any]
    error_message: str
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class RFDeviceStatus:
    firmware_version: str
    temperature: float
    battery_voltage: float
    rx_active: bool
    tx_active: bool
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class RFEnvelope:
    message_type: Any
    message_id: int
    device_id: str

