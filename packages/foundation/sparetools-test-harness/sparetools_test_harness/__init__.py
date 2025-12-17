"""
SpareTools Test Harness - ngapy-style verification framework for SpareTools ecosystem.

This package provides a unified test harness with verification methods compatible
with ngapy's API, enabling teams familiar with ngapy to use the same testing
patterns while benefiting from SpareTools' zero-copy architecture and bundled
CPython environment.
"""

from .test_harness import SpareToolsTestHarness
from .verification import VerificationMethods
from .test_logging import ThLogger

__version__ = "2.0.0"
__all__ = [
    "SpareToolsTestHarness",
    "VerificationMethods",
    "ThLogger"
]