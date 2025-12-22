"""Generated Python dataclasses for sparetools.icd"""

from dataclasses import dataclass, field
from typing import List, Any
from enum import Enum
import time

# Enums
class AudioAction(Enum):
    RECORD = 0
    PLAY = 1
    STREAM = 2
    ENUMERATE = 3


# Tables
@dataclass
class AudioCommand:
    action: AudioAction
    device_index: int
    duration_ms: int
    filename: str
    sample_rate: int

@dataclass
class AudioResponse:
    success: bool
    message: str
    data_size: int

