"""Generated Python dataclasses for sparetools.icd.obd"""

from dataclasses import dataclass, field
from typing import List, Any
from enum import Enum
import time

# Enums
class OBDService(Enum):
    CURRENT_DATA = 0x01
    FREEZE_FRAME = 0x02
    STORED_DIAGNOSTIC = 0x03
    CLEAR_DIAGNOSTIC = 0x04
    TEST_RESULTS_OXYGEN = 0x05
    TEST_RESULTS_SYSTEM = 0x06
    PENDING_DIAGNOSTIC = 0x07
    CONTROL_OPERATION = 0x08
    VEHICLE_INFO = 0x09
    PERMANENT_DIAGNOSTIC = 0x0A    // Permanent Diagnostic Trouble Codes


# Tables
@dataclass
class OBDQuery:
    service: OBDService
    pid: int
    timeout_ms: int
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class OBDResponse:
    service: OBDService
    pid: int
    success: bool
    data: List[int]
    decoded_value: float
    unit: str
    error_code: str
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class DTCode:
    code: str
    status: int
    description: str

@dataclass
class DTCQuery:
    service: OBDService
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class DTCResponse:
    service: OBDService
    dtcs: List[Any]
    success: bool
    error_message: str
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class DTCClear:
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class DTCClearResponse:
    success: bool
    cleared_count: int
    error_message: str
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class VehicleInfoQuery:
    info_type: Any
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class VehicleInfoResponse:
    info_type: Any
    info_data: str
    success: bool
    error_message: str
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class OBDEnvelope:
    message_type: Any
    message_id: int
    ecu_address: int

