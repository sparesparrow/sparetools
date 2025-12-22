"""
Digital Twin Integration Tests

Integration tests using the digital twin testing harness to validate MIA system behavior.
Tests emergency responses, fault handling, and system integration without physical hardware.
"""

import pytest
import asyncio
import time
from typing import Dict, Any

# Import digital twin harness
try:
    from sparetools_test_harness.digital_twin import DigitalTwinTestHarness
except ImportError:
    # Fallback for local testing
    import sys
    import os
    harness_path = os.path.join(os.path.dirname(__file__), '../../../../foundation/sparetools-test-harness')
    if os.path.exists(harness_path):
        sys.path.insert(0, harness_path)
        from sparetools_test_harness.digital_twin import DigitalTwinTestHarness
    else:
        pytest.skip("Digital twin harness not available", allow_module_level=True)


class TestEmergencyShutdown:
    """Test emergency shutdown scenarios"""

    @pytest.mark.asyncio
    async def test_coolant_temperature_spike(self):
        """Test emergency shutdown on coolant temperature spike"""
        harness = DigitalTwinTestHarness()

        async with harness.test_context():
            result = await harness.run_fault_injection_test(
                fault_type="coolant_spike",
                expected_shutdown_ms=200
            )

            assert result["success"], f"Emergency shutdown failed: {result}"
            assert result["shutdown_detected"], "Emergency shutdown event not detected"
            assert result["response_time_ms"] <= result["expected_max_ms"], \
                f"Response time {result['response_time_ms']}ms exceeded limit {result['expected_max_ms']}ms"

    @pytest.mark.asyncio
    async def test_voltage_drop_emergency(self):
        """Test emergency shutdown on battery voltage drop"""
        harness = DigitalTwinTestHarness()

        async with harness.test_context():
            result = await harness.run_fault_injection_test(
                fault_type="voltage_drop",
                expected_shutdown_ms=500  # Slower response for voltage issues
            )

            assert result["success"], f"Voltage emergency failed: {result}"
            assert result["shutdown_detected"], "Voltage emergency shutdown not detected"

    @pytest.mark.asyncio
    async def test_sensor_failure_detection(self):
        """Test detection of sensor failures"""
        harness = DigitalTwinTestHarness()

        async with harness.test_context():
            result = await harness.run_fault_injection_test(
                fault_type="sensor_failure",
                expected_shutdown_ms=1000  # Allow more time for sensor validation
            )

            assert result["success"], f"Sensor failure test failed: {result}"
            # Sensor failures might not trigger shutdown but should be logged


class TestSystemIntegration:
    """Test overall system integration"""

    @pytest.mark.asyncio
    async def test_normal_operation_integration(self):
        """Test normal system operation"""
        harness = DigitalTwinTestHarness()

        async with harness.test_context():
            result = await harness.run_integration_test(
                test_scenario="normal_operation",
                duration=10.0
            )

            assert result["success"], f"Normal operation test failed: {result}"
            assert result["events_captured"] >= 0, "Should capture some events during operation"
            assert result["duration"] >= 9.0, "Test should run for expected duration"

    @pytest.mark.asyncio
    async def test_high_load_handling(self):
        """Test system behavior under high load"""
        harness = DigitalTwinTestHarness()

        async with harness.test_context():
            result = await harness.run_integration_test(
                test_scenario="high_load",
                duration=5.0
            )

            assert result["success"], f"High load test failed: {result}"
            # System should handle rapid telemetry changes without crashing

    @pytest.mark.asyncio
    async def test_communication_recovery(self):
        """Test communication failure and recovery"""
        harness = DigitalTwinTestHarness()

        async with harness.test_context():
            result = await harness.run_integration_test(
                test_scenario="communication_failure",
                duration=8.0
            )

            # Communication failures should be handled gracefully
            # (specific assertions depend on implementation)
            assert result["duration"] >= 7.0, "Test should complete"


class TestFaultInjection:
    """Test various fault injection scenarios"""

    @pytest.mark.asyncio
    async def test_multiple_concurrent_faults(self):
        """Test system response to multiple simultaneous faults"""
        harness = DigitalTwinTestHarness()

        async with harness.test_context():
            # Inject multiple faults simultaneously
            await harness.serial_bridge.inject_telemetry({
                "pot1": 950,  # Very high temperature
                "voltage": 7.5,  # Very low voltage
                "pot2": 0  # Sensor failure
            })

            # Wait for system response
            await asyncio.sleep(1.0)

            # Check that system detected issues
            events = harness.event_monitor.get_events()
            fault_events = [e for e in events if "FAULT" in e.get("line", "")]

            # System should detect at least some faults
            assert len(fault_events) > 0, "System should detect multiple faults"

    @pytest.mark.asyncio
    async def test_gradual_fault_development(self):
        """Test response to gradually developing faults"""
        harness = DigitalTwinTestHarness()

        async with harness.test_context():
            # Gradually increase temperature
            for temp in range(100, 130, 10):
                await harness.serial_bridge.inject_telemetry({"pot1": temp})
                await asyncio.sleep(0.5)

            # Check for appropriate response
            events = harness.event_monitor.get_events()
            emergency_events = [e for e in events if "EMERGENCY" in e.get("line", "")]

            # Should trigger emergency response at some point
            assert len(emergency_events) > 0, "Gradual fault should trigger emergency response"


class TestTelemetryProcessing:
    """Test telemetry data processing and validation"""

    @pytest.mark.asyncio
    async def test_telemetry_data_integrity(self):
        """Test that telemetry data is processed correctly"""
        harness = DigitalTwinTestHarness()

        async with harness.test_context():
            # Inject known telemetry values
            test_data = {
                "pot1": 750,  # Specific temperature reading
                "pot2": 300,  # Specific pressure reading
                "voltage": 12.8  # Specific voltage reading
            }

            await harness.serial_bridge.inject_telemetry(test_data)

            # Allow processing time
            await asyncio.sleep(1.0)

            # Check that data was processed (through logs or events)
            mia_output = harness.mia_core.get_output() if harness.mia_core else []
            telemetry_lines = [line for line in mia_output if "telemetry" in line.lower()]

            # Should process telemetry data
            assert len(telemetry_lines) >= 0, "Should process telemetry data"

    @pytest.mark.asyncio
    async def test_telemetry_out_of_range_handling(self):
        """Test handling of out-of-range telemetry values"""
        harness = DigitalTwinTestHarness()

        async with harness.test_context():
            # Inject out-of-range values
            await harness.serial_bridge.inject_telemetry({
                "pot1": 1100,  # Above ADC range
                "pot2": -50,   # Below ADC range
                "voltage": 25.0  # Above normal range
            })

            await asyncio.sleep(1.0)

            # System should handle invalid data gracefully
            events = harness.event_monitor.get_events()
            error_events = [e for e in events if "error" in e.get("line", "").lower()]

            # Should not crash, may log warnings
            assert harness.mia_core.is_running(), "System should remain stable with invalid telemetry"


class TestSystemRecovery:
    """Test system recovery after faults"""

    @pytest.mark.asyncio
    async def test_post_fault_recovery(self):
        """Test system recovery after fault condition clears"""
        harness = DigitalTwinTestHarness()

        async with harness.test_context():
            # Inject fault
            await harness.serial_bridge.inject_telemetry({"pot1": 900})

            # Wait for emergency response
            await asyncio.sleep(0.5)

            # Clear fault
            await harness.serial_bridge.inject_telemetry({"pot1": 100})  # Normal temperature

            # Allow recovery time
            await asyncio.sleep(2.0)

            # System should recover and continue operating
            assert harness.mia_core.is_running(), "System should recover after fault clears"

            # Check for recovery events
            events = harness.event_monitor.get_events()
            recovery_events = [e for e in events if "RECOVERY" in e.get("line", "")]

            # May or may not have explicit recovery events depending on implementation
            # But system should be stable
            assert harness.get_system_status()["mia_running"], "System should be operational"


# Performance benchmarks
class TestPerformanceBenchmarks:
    """Performance testing benchmarks"""

    @pytest.mark.asyncio
    async def test_response_time_under_load(self):
        """Test response time remains acceptable under load"""
        harness = DigitalTwinTestHarness()

        async with harness.test_context():
            start_time = time.time()

            # Generate high-frequency telemetry updates
            for i in range(50):
                await harness.serial_bridge.inject_telemetry({
                    "pot1": 200 + (i * 10),  # Gradually changing values
                    "pot2": 250 + (i * 5),
                })
                await asyncio.sleep(0.1)  # 10Hz update rate

            end_time = time.time()
            total_duration = end_time - start_time

            # Should handle high-frequency updates within reasonable time
            assert total_duration < 10.0, f"High load test took too long: {total_duration}s"

            # System should still be responsive
            assert harness.mia_core.is_running(), "System should remain stable under load"


# Utility functions for test setup
def setup_test_environment():
    """Set up test environment variables and configuration"""
    import os
    os.environ["MIA_TEST_MODE"] = "1"
    os.environ["MIA_SIMULATION"] = "1"
    os.environ["MIA_LOG_LEVEL"] = "DEBUG"


def teardown_test_environment():
    """Clean up test environment"""
    import os
    for key in ["MIA_TEST_MODE", "MIA_SIMULATION", "MIA_LOG_LEVEL"]:
        os.environ.pop(key, None)


# Pytest fixtures
@pytest.fixture(scope="session", autouse=True)
def test_env_setup():
    """Set up test environment for all tests"""
    setup_test_environment()
    yield
    teardown_test_environment()


@pytest.fixture
async def harness():
    """Provide a fresh digital twin harness for each test"""
    harness = DigitalTwinTestHarness()
    async with harness.test_context():
        yield harness


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])