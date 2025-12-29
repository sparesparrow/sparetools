"""
SpareTools Python Utilities

A collection of Python utilities for embedded development with SpareTools.
"""

__version__ = "1.0.0"
__author__ = "SpareSparrow"
__email__ = "dev@sparesparrow.com"

from .bpm_decoder import BPMDecoder, BPMMode, AudioConfig, BPMParams, BPMResult
from .test_harness import ProtocolTestHarness, TestResult, TestCase, TestRun, create_protocol_test, run_command_test
from .conan_helpers import ConanHelper, ConanPackage, ConanProfile, create_conanfile_txt, setup_cloudsmith_remote

__all__ = [
    # BPM Decoder
    "BPMDecoder", "BPMMode", "AudioConfig", "BPMParams", "BPMResult",

    # Test Harness
    "ProtocolTestHarness", "TestResult", "TestCase", "TestRun",
    "create_protocol_test", "run_command_test",

    # Conan Helpers
    "ConanHelper", "ConanPackage", "ConanProfile",
    "create_conanfile_txt", "setup_cloudsmith_remote",
]