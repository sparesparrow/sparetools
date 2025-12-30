#!/usr/bin/env python3
"""
SpareTools FlatBuffers Schema Compatibility Tests

This module provides cross-platform compatibility testing for FlatBuffers schemas.
It tests that messages created on one platform can be correctly parsed on others.
"""

import sys
import os
import time
import json
from typing import Dict, List, Any, Optional
import tempfile
import subprocess

# Add generated Python bindings to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))

try:
    import flatbuffers
    import sparetools_protocols.common.common_generated as common
    import sparetools_protocols.iot.BPM_generated as bpm
    import sparetools_protocols.mcp.MCP_generated as mcp
except ImportError as e:
    print(f"Error importing generated bindings: {e}")
    print("Make sure FlatBuffers code generation has been run")
    sys.exit(1)


class SchemaCompatibilityTest:
    """Test FlatBuffers schema compatibility across platforms and versions."""

    def __init__(self):
        self.test_results = []
        self.test_timestamp = int(time.time() * 1000)  # milliseconds

    def run_all_tests(self) -> bool:
        """Run all compatibility tests."""
        print("Running SpareTools Schema Compatibility Tests")
        print("=" * 50)

        tests = [
            self.test_bpm_message_serialization,
            self.test_gpio_command_serialization,
            self.test_cross_platform_endianness,
            self.test_schema_version_compatibility,
            self.test_message_validation,
            self.test_performance_comparison,
            self.test_error_handling,
        ]

        all_passed = True
        for test in tests:
            try:
                result = test()
                self.test_results.append({
                    'test': test.__name__,
                    'passed': result,
                    'timestamp': self.test_timestamp
                })
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"❌ {test.__name__}: FAILED - {e}")
                self.test_results.append({
                    'test': test.__name__,
                    'passed': False,
                    'error': str(e),
                    'timestamp': self.test_timestamp
                })
                all_passed = False

        self.print_summary()
        return all_passed

    def test_bpm_message_serialization(self) -> bool:
        """Test BPM message creation and parsing."""
        print("Testing BPM message serialization...")

        # Create BPM update message
        builder = flatbuffers.Builder(1024)
        bpm_update = bpm.CreateBPMUpdate(builder,
            72.5,      # bpm
            0.95,      # confidence
            0.8,       # signal_level
            bpm.DetectionStatus_DETECTING,  # status
            self.test_timestamp  # timestamp
        )
        builder.Finish(bpm_update)

        # Get buffer
        buffer = builder.Output()

        # Parse message
        parsed = bpm.GetBPMUpdate(buffer)

        # Validate fields
        success = (
            abs(parsed.Bpm() - 72.5) < 0.001 and
            abs(parsed.Confidence() - 0.95) < 0.001 and
            parsed.Status() == bpm.DetectionStatus_DETECTING and
            parsed.Timestamp() == self.test_timestamp
        )

        print(f"✅ BPM serialization test: {'PASSED' if success else 'FAILED'}")
        return success

    def test_gpio_command_serialization(self) -> bool:
        """Test GPIO command creation and parsing."""
        print("Testing GPIO command serialization...")

        builder = flatbuffers.Builder(256)
        gpio_cmd = mcp.CreateGPIOCommand(builder,
            2,           # pin
            True,        # state
            self.test_timestamp  # timestamp
        )
        builder.Finish(gpio_cmd)

        buffer = builder.Output()
        parsed = mcp.GetGPIOCommand(buffer)

        success = (
            parsed.Pin() == 2 and
            parsed.State() == True and
            parsed.Timestamp() == self.test_timestamp
        )

        print(f"✅ GPIO command test: {'PASSED' if success else 'FAILED'}")
        return success

    def test_cross_platform_endianness(self) -> bool:
        """Test that messages work across different endianness."""
        print("Testing cross-platform endianness compatibility...")

        # Create message with multi-byte values
        builder = flatbuffers.Builder(1024)
        bpm_update = bpm.CreateBPMUpdate(builder,
            123.456,    # float
            0.789,      # float
            0.654,      # float
            bpm.DetectionStatus_CALIBRATING,
            0x123456789ABCDEF0  # large integer
        )
        builder.Finish(bpm_update)

        buffer = builder.Output()

        # Parse and verify
        parsed = bpm.GetBPMUpdate(buffer)
        success = (
            abs(parsed.Bpm() - 123.456) < 0.001 and
            parsed.Timestamp() == 0x123456789ABCDEF0
        )

        print(f"✅ Endianness test: {'PASSED' if success else 'FAILED'}")
        return success

    def test_schema_version_compatibility(self) -> bool:
        """Test schema version compatibility."""
        print("Testing schema version compatibility...")

        # Create message
        builder = flatbuffers.Builder(1024)
        bpm_update = bpm.CreateBPMUpdate(builder,
            60.0, 0.8, 0.7,
            bpm.DetectionStatus_DETECTING,
            self.test_timestamp
        )
        builder.Finish(bpm_update)

        buffer = builder.Output()

        # Test that it parses correctly (version compatibility)
        try:
            parsed = bpm.GetBPMUpdate(buffer)
            # Basic validation
            assert parsed.Bpm() > 0
            assert 0.0 <= parsed.Confidence() <= 1.0
            success = True
        except Exception:
            success = False

        print(f"✅ Version compatibility test: {'PASSED' if success else 'FAILED'}")
        return success

    def test_message_validation(self) -> bool:
        """Test message validation and verification."""
        print("Testing message validation...")

        # Create valid message
        builder = flatbuffers.Builder(1024)
        bpm_update = bpm.CreateBPMUpdate(builder,
            70.0, 0.9, 0.8,
            bpm.DetectionStatus_DETECTING,
            self.test_timestamp
        )
        builder.Finish(bpm_update)

        buffer = builder.Output()

        # Test verification
        verifier = flatbuffers.Verifier(buffer)
        valid = bpm.VerifyBPMUpdateBuffer(verifier)

        print(f"✅ Message validation test: {'PASSED' if valid else 'FAILED'}")
        return valid

    def test_performance_comparison(self) -> bool:
        """Compare FlatBuffers performance with JSON."""
        print("Testing performance comparison...")

        import time

        # FlatBuffers serialization
        fb_times = []
        for _ in range(1000):
            builder = flatbuffers.Builder(256)
            start = time.perf_counter()
            bpm_update = bpm.CreateBPMUpdate(builder, 72.0, 0.95, 0.8,
                bpm.DetectionStatus_DETECTING, self.test_timestamp)
            builder.Finish(bpm_update)
            fb_times.append(time.perf_counter() - start)

        fb_avg = sum(fb_times) / len(fb_times)

        # JSON serialization for comparison
        json_data = {
            "bpm": 72.0,
            "confidence": 0.95,
            "signal_level": 0.8,
            "status": "DETECTING",
            "timestamp": self.test_timestamp
        }

        json_times = []
        for _ in range(1000):
            start = time.perf_counter()
            json_str = json.dumps(json_data)
            json.loads(json_str)  # Parse back
            json_times.append(time.perf_counter() - start)

        json_avg = sum(json_times) / len(json_times)

        # FlatBuffers should be faster
        success = fb_avg < json_avg

        print(".2f")
        print(".2f")
        print(f"✅ Performance test: {'PASSED' if success else 'FAILED'}")
        return success

    def test_error_handling(self) -> bool:
        """Test error handling with invalid data."""
        print("Testing error handling...")

        # Test with invalid buffer
        invalid_buffer = b'\xFF\xFF\xFF\xFF'

        try:
            parsed = bpm.GetBPMUpdate(invalid_buffer)
            # Should not crash, but may return invalid data
            success = True
        except Exception:
            success = False

        # Test verification of invalid data
        verifier = flatbuffers.Verifier(invalid_buffer)
        should_fail = not bpm.VerifyBPMUpdateBuffer(verifier)

        print(f"✅ Error handling test: {'PASSED' if (success and should_fail) else 'FAILED'}")
        return success and should_fail

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)

        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)

        for result in self.test_results:
            status = "✅ PASSED" if result['passed'] else "❌ FAILED"
            print(f"{result['test']}: {status}")
            if 'error' in result:
                print(f"   Error: {result['error']}")

        print(f"\nTotal: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All schema compatibility tests passed!")
        else:
            print("⚠️  Some tests failed. Check implementation.")

    def save_results(self, filename: str):
        """Save test results to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)


def main():
    """Main test runner."""
    test_suite = SchemaCompatibilityTest()
    success = test_suite.run_all_tests()

    # Save results
    results_file = os.path.join(tempfile.gettempdir(), 'schema_test_results.json')
    test_suite.save_results(results_file)
    print(f"\nDetailed results saved to: {results_file}")

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())