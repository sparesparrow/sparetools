"""Generated Python dataclasses for sparetools.bpm"""

from dataclasses import dataclass, field
from typing import List, Any
from enum import Enum
import time

# Enums
class BPMStatus(Enum):
    DETECTING = 0
    LOW_SIGNAL = 1
    LOW_CONFIDENCE = 2
    ERROR = 3
    INITIALIZING = 4
    BUFFERING = 5


# Tables
@dataclass
class BPMData:
    bpm: float
    confidence: float
    signal_level: float
    status: str
    timestamp: int = field(default_factory=lambda: int(time.time() * 1_000_000))

@dataclass
class BPMSettings:
    min_bpm: int
    max_bpm: int
    sample_rate: int
    fft_size: int
    version: str

@dataclass
class BPMHealth:
    status: str
    uptime: int
    heap_free: int

@dataclass
class BPMEnvelope:
    message_type: Any
    message_id: int
    source: str

