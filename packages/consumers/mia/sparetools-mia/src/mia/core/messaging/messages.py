"""
MIA Messaging System

ICD-generated message types for inter-component communication.
Generated from FlatBuffers schemas using the Active ICD strategy.
"""

# Import ICD-generated types
try:
    # Try importing from sparetools.icd package (when available via Conan)
    from sparetools.icd.hardware import (
        GPIOCommand, GPIOResponse, SerialTelemetry, SerialCommand, SerialResponse,
        HardwareEnvelope, GPIOMode
    )
    from sparetools.icd.obd import (
        OBDQuery, OBDResponse, OBDService
    )
    from sparetools.icd.rf import (
        RFCaptureStart, RFReplay, RFModulation
    )
    ICD_AVAILABLE = True
except ImportError:
    # Fallback to local generated files during development
    import sys
    import os
    icd_path = os.path.join(os.path.dirname(__file__), '../../../foundation/sparetools-icd')
    if os.path.exists(icd_path):
        sys.path.insert(0, icd_path)
        try:
            from hardware_generated import (
                GPIOCommand, GPIOResponse, SerialTelemetry, SerialCommand, SerialResponse,
                HardwareEnvelope, GPIOMode
            )
            from obd_generated import OBDQuery, OBDResponse
            from rf_generated import RFCaptureStart, RFReplay
            # Create OBDService and RFModulation enums manually
            from enum import Enum
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
                PERMANENT_DIAGNOSTIC = 0x0A

            class RFModulation(Enum):
                ASK = 0
                FSK = 1
                OOK = 2
                GFSK = 3
                MSK = 4
                RAW = 5

            ICD_AVAILABLE = True
        except ImportError:
            ICD_AVAILABLE = False
    else:
        ICD_AVAILABLE = False

if not ICD_AVAILABLE:
    # Ultimate fallback - manual definitions (should not be used in production)
    from dataclasses import dataclass, field
    from typing import List
    from datetime import datetime
    from enum import Enum

    class GPIOMode(Enum):
        INPUT = 0
        OUTPUT = 1
        INPUT_PULLUP = 2
        INPUT_PULLDOWN = 3

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
        PERMANENT_DIAGNOSTIC = 0x0A

    class RFModulation(Enum):
        ASK = 0
        FSK = 1
        OOK = 2
        GFSK = 3
        MSK = 4
        RAW = 5

    @dataclass
    class GPIOCommand:
        pin: int
        state: bool
        mode: GPIOMode
        timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1_000_000))

    @dataclass
    class GPIOResponse:
        pin: int
        state: bool
        success: bool
        error_message: str
        timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1_000_000))

    @dataclass
    class OBDQuery:
        service: OBDService
        pid: int
        timeout_ms: int = 1000
        timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1_000_000))

    @dataclass
    class OBDResponse:
        service: OBDService
        pid: int
        success: bool = True
        data: List[int] = field(default_factory=list)
        decoded_value: float = 0.0
        unit: str = ""
        error_code: str = ""
        timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1_000_000))

    @dataclass
    class RFCaptureStart:
        frequency: int = 433920000
        modulation: RFModulation = RFModulation.FSK
        sample_rate: int = 1000000
        gain: int = 0
        bandwidth: int = 100000
        squelch: int = 0
        duration_ms: int = 0
        max_frames: int = 0
        timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1_000_000))

    @dataclass
    class RFReplay:
        frame_data: List[int] = field(default_factory=list)
        frequency: int = 433920000
        modulation: RFModulation = RFModulation.FSK
        repeat_count: int = 1
        tx_power: int = -10
        timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1_000_000))


# Message type registry for serialization
MESSAGE_TYPES = {
    "GPIOCommand": GPIOCommand,
    "GPIOResponse": GPIOResponse,
    "OBDQuery": OBDQuery,
    "OBDResponse": OBDResponse,
    "SerialTelemetry": SerialTelemetry,
    "SerialCommand": SerialCommand,
    "SerialResponse": SerialResponse,
    "RFCaptureStart": RFCaptureStart,
    "RFReplay": RFReplay,
}