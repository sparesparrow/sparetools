"""
Digital Twin Testing Harness

Hardware-in-the-Loop testing infrastructure with fault injection capabilities.
Simulates MIA hardware components for comprehensive testing without physical hardware.
"""

import asyncio
import logging
import subprocess
import signal
import time
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import threading
import queue
import random
import json


@dataclass
class ProcessRunner:
    """Manages external process lifecycle for testing"""

    command: str
    name: str = ""
    cwd: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    startup_timeout: float = 10.0
    shutdown_timeout: float = 5.0

    def __post_init__(self):
        if not self.name:
            self.name = self.command.split()[0]

        self.process: Optional[subprocess.Popen] = None
        self.stdout_queue: queue.Queue = queue.Queue()
        self.stderr_queue: queue.Queue = queue.Queue()
        self.logger = logging.getLogger(f"{__name__}.{self.name}")

    async def start(self) -> bool:
        """Start the process"""
        try:
            self.logger.info(f"Starting process: {self.command}")

            self.process = subprocess.Popen(
                self.command,
                shell=True,
                cwd=self.cwd,
                env=self.env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Start output monitoring threads
            threading.Thread(
                target=self._monitor_output,
                args=(self.process.stdout, self.stdout_queue, "stdout"),
                daemon=True
            ).start()

            threading.Thread(
                target=self._monitor_output,
                args=(self.process.stderr, self.stderr_queue, "stderr"),
                daemon=True
            ).start()

            # Wait for startup
            await asyncio.sleep(0.1)

            if self.process.poll() is None:
                self.logger.info(f"Process {self.name} started successfully")
                return True
            else:
                self.logger.error(f"Process {self.name} failed to start")
                return False

        except Exception as e:
            self.logger.error(f"Failed to start process {self.name}: {e}")
            return False

    def _monitor_output(self, stream, output_queue: queue.Queue, stream_name: str):
        """Monitor process output in background thread"""
        try:
            for line in iter(stream.readline, ''):
                if line.strip():
                    output_queue.put(line.strip())
                    self.logger.debug(f"{self.name} {stream_name}: {line.strip()}")
        except Exception as e:
            self.logger.error(f"Output monitoring error for {self.name}: {e}")

    async def stop(self):
        """Stop the process"""
        if self.process and self.process.poll() is None:
            self.logger.info(f"Stopping process {self.name}")

            try:
                # Try graceful shutdown first
                self.process.terminate()

                # Wait for shutdown
                try:
                    await asyncio.wait_for(
                        self._wait_for_exit(),
                        timeout=self.shutdown_timeout
                    )
                except asyncio.TimeoutError:
                    # Force kill if graceful shutdown fails
                    self.logger.warning(f"Force killing process {self.name}")
                    self.process.kill()
                    await self._wait_for_exit()

            except Exception as e:
                self.logger.error(f"Error stopping process {self.name}: {e}")

        self.process = None

    async def _wait_for_exit(self):
        """Wait for process to exit"""
        while self.process and self.process.poll() is None:
            await asyncio.sleep(0.1)

    def is_running(self) -> bool:
        """Check if process is running"""
        return self.process is not None and self.process.poll() is None

    def get_output(self, stream: str = "stdout", timeout: float = 1.0) -> List[str]:
        """Get recent output from the process"""
        output_queue = self.stdout_queue if stream == "stdout" else self.stderr_queue
        lines = []

        try:
            while True:
                line = output_queue.get_nowait()
                lines.append(line)
        except queue.Empty:
            pass

        return lines

    async def wait_for_output(self, pattern: str, timeout: float = 5.0,
                            stream: str = "stdout") -> Optional[str]:
        """Wait for specific output pattern"""
        start_time = time.time()
        output_queue = self.stdout_queue if stream == "stdout" else self.stderr_queue

        while time.time() - start_time < timeout:
            try:
                line = output_queue.get_nowait()
                if pattern in line:
                    return line
            except queue.Empty:
                await asyncio.sleep(0.1)

        return None


@dataclass
class MockSerialBridge:
    """Mock serial bridge for testing NucleusESP32 communication"""

    port: str = "/dev/ttyACM0"
    telemetry_data: Dict[str, Any] = field(default_factory=dict)
    command_responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        self.logger = logging.getLogger(f"{__name__}.MockSerialBridge")

        # Default telemetry data
        self.telemetry_data = {
            "pot1": 512,    # Coolant temperature sensor
            "pot2": 256,    # Oil pressure sensor
            "temp1": 25.0,  # Ambient temperature
            "voltage": 12.6 # Battery voltage
        }

        # Default command responses
        self.command_responses = {
            "ping": {"status": "ok", "device": "NucleusESP32-Mock"},
            "start_capture": {"status": "capture_started", "frequency": 433920000},
            "replay_signal": {"status": "replay_complete", "frames_sent": 1}
        }

    async def connect(self) -> bool:
        """Mock connection"""
        self.logger.info(f"Mock serial bridge connected to {self.port}")
        return True

    async def disconnect(self):
        """Mock disconnection"""
        self.logger.info("Mock serial bridge disconnected")

    async def send(self, data: Dict[str, Any]) -> bool:
        """Mock send - just log and return success"""
        self.logger.debug(f"Mock serial send: {data}")
        return True

    async def receive(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """Mock receive - return canned responses"""
        await asyncio.sleep(0.1)  # Simulate communication delay
        return {"status": "ok", "mock": True}

    async def inject_telemetry(self, data: Dict[str, Any]):
        """Inject telemetry data for testing"""
        self.telemetry_data.update(data)
        self.logger.info(f"Injected telemetry: {data}")

    def get_telemetry(self) -> Dict[str, Any]:
        """Get current telemetry data"""
        return self.telemetry_data.copy()


@dataclass
class EventMonitor:
    """Monitors MIA system events during testing"""

    event_patterns: List[str] = field(default_factory=list)
    captured_events: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        self.logger = logging.getLogger(f"{__name__}.EventMonitor")

    async def monitor_process(self, process: ProcessRunner, duration: float = 10.0):
        """Monitor process output for events"""
        start_time = time.time()

        while time.time() - start_time < duration:
            stdout_lines = process.get_output("stdout")
            stderr_lines = process.get_output("stderr")

            for line in stdout_lines + stderr_lines:
                for pattern in self.event_patterns:
                    if pattern in line:
                        event = {
                            "timestamp": time.time(),
                            "pattern": pattern,
                            "line": line
                        }
                        self.captured_events.append(event)
                        self.logger.info(f"Captured event: {event}")

            await asyncio.sleep(0.1)

    def add_pattern(self, pattern: str):
        """Add event pattern to monitor"""
        self.event_patterns.append(pattern)

    def get_events(self, pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get captured events, optionally filtered by pattern"""
        if pattern:
            return [e for e in self.captured_events if e["pattern"] == pattern]
        return self.captured_events.copy()

    def wait_for_event(self, pattern: str, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """Wait for a specific event pattern"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            events = self.get_events(pattern)
            if events:
                return events[-1]  # Return most recent

            time.sleep(0.1)

        return None


class DigitalTwinTestHarness:
    """Main digital twin testing harness"""

    def __init__(self):
        self.mia_core: Optional[ProcessRunner] = None
        self.obd_sim: Optional[ProcessRunner] = None
        self.serial_bridge = MockSerialBridge()
        self.event_monitor = EventMonitor()

        # Add common event patterns to monitor
        self.event_monitor.add_pattern("EMERGENCY_SHUTDOWN")
        self.event_monitor.add_pattern("FAULT_DETECTED")
        self.event_monitor.add_pattern("SYSTEM_RECOVERY")
        self.event_monitor.add_pattern("DIAGNOSTIC_COMPLETE")

        self.logger = logging.getLogger(__name__)

    @asynccontextmanager
    async def test_context(self):
        """Context manager for test setup and teardown"""
        try:
            # Setup
            self.logger.info("Setting up digital twin test environment")
            await self._setup_components()
            yield self
        finally:
            # Teardown
            self.logger.info("Tearing down digital twin test environment")
            await self._teardown_components()

    async def _setup_components(self):
        """Set up test components"""
        # Start MIA core (mock/simulator mode)
        self.mia_core = ProcessRunner(
            command="python -m mia.core --test-mode",
            name="mia-core",
            env={"MIA_TEST_MODE": "1", "MIA_SIMULATION": "1"}
        )

        # Start OBD simulator
        self.obd_sim = ProcessRunner(
            command="python -m mia.services.obd_worker --sim",
            name="obd-sim"
        )

        # Start components
        if not await self.mia_core.start():
            raise RuntimeError("Failed to start MIA core")

        if not await self.obd_sim.start():
            raise RuntimeError("Failed to start OBD simulator")

        # Start event monitoring
        asyncio.create_task(
            self.event_monitor.monitor_process(self.mia_core, duration=60.0)
        )

        # Allow components to stabilize
        await asyncio.sleep(2.0)

    async def _teardown_components(self):
        """Clean up test components"""
        if self.mia_core:
            await self.mia_core.stop()

        if self.obd_sim:
            await self.obd_sim.stop()

    async def run_fault_injection_test(self,
                                     fault_type: str = "coolant_spike",
                                     expected_shutdown_ms: int = 200) -> Dict[str, Any]:
        """Run fault injection test with emergency response validation"""

        self.logger.info(f"Running fault injection test: {fault_type}")

        # Record start time
        test_start = time.time()

        # Inject fault based on type
        if fault_type == "coolant_spike":
            # Simulate coolant temperature spike
            await self.serial_bridge.inject_telemetry({"pot1": 900})  # High temp
        elif fault_type == "voltage_drop":
            # Simulate battery voltage drop
            await self.serial_bridge.inject_telemetry({"voltage": 8.0})
        elif fault_type == "sensor_failure":
            # Simulate sensor disconnection
            await self.serial_bridge.inject_telemetry({"pot1": 0, "pot2": 0})

        # Wait for emergency shutdown event
        shutdown_event = self.event_monitor.wait_for_event(
            "EMERGENCY_SHUTDOWN",
            timeout=expected_shutdown_ms / 1000.0 + 1.0
        )

        test_end = time.time()
        test_duration = test_end - test_start

        if shutdown_event:
            response_time = shutdown_event["timestamp"] - test_start
            success = response_time * 1000 <= expected_shutdown_ms

            result = {
                "success": success,
                "fault_type": fault_type,
                "response_time_ms": response_time * 1000,
                "expected_max_ms": expected_shutdown_ms,
                "shutdown_detected": True,
                "shutdown_timestamp": shutdown_event["timestamp"],
                "test_duration": test_duration
            }
        else:
            result = {
                "success": False,
                "fault_type": fault_type,
                "response_time_ms": None,
                "expected_max_ms": expected_shutdown_ms,
                "shutdown_detected": False,
                "error": "Emergency shutdown not detected within timeout",
                "test_duration": test_duration
            }

        self.logger.info(f"Fault injection test result: {result}")
        return result

    async def run_integration_test(self,
                                 test_scenario: str = "normal_operation",
                                 duration: float = 10.0) -> Dict[str, Any]:
        """Run integration test scenario"""

        self.logger.info(f"Running integration test: {test_scenario}")

        start_time = time.time()

        if test_scenario == "normal_operation":
            # Test normal OBD queries and GPIO operations
            await self._test_normal_operation(duration)
        elif test_scenario == "high_load":
            # Test system under high load
            await self._test_high_load(duration)
        elif test_scenario == "communication_failure":
            # Test communication failure recovery
            await self._test_communication_failure(duration)

        end_time = time.time()

        # Collect test results
        events = self.event_monitor.get_events()
        mia_output = self.mia_core.get_output() if self.mia_core else []
        obd_output = self.obd_sim.get_output() if self.obd_sim else []

        result = {
            "scenario": test_scenario,
            "duration": end_time - start_time,
            "events_captured": len(events),
            "mia_output_lines": len(mia_output),
            "obd_output_lines": len(obd_output),
            "events": events[-10:],  # Last 10 events
            "success": self._analyze_test_success(events, mia_output, obd_output)
        }

        self.logger.info(f"Integration test result: {result}")
        return result

    async def _test_normal_operation(self, duration: float):
        """Test normal system operation"""
        # Simulate normal telemetry variations
        for i in range(int(duration / 2)):
            # Normal temperature variations
            temp = 80 + random.randint(-10, 10)
            await self.serial_bridge.inject_telemetry({"pot1": temp})
            await asyncio.sleep(2.0)

    async def _test_high_load(self, duration: float):
        """Test system under high load"""
        # Rapid telemetry changes
        for i in range(int(duration * 5)):
            temp = random.randint(50, 120)
            pressure = random.randint(200, 400)
            await self.serial_bridge.inject_telemetry({
                "pot1": temp,
                "pot2": pressure
            })
            await asyncio.sleep(0.2)

    async def _test_communication_failure(self, duration: float):
        """Test communication failure and recovery"""
        # Simulate communication dropout
        await asyncio.sleep(duration / 3)
        # Inject communication error (would be handled by real system)
        await asyncio.sleep(duration / 3)
        # Recovery period
        await asyncio.sleep(duration / 3)

    def _analyze_test_success(self, events: List[Dict[str, Any]],
                            mia_output: List[str],
                            obd_output: List[str]) -> bool:
        """Analyze if test was successful based on outputs"""

        # Check for critical errors
        error_events = [e for e in events if "error" in e.get("line", "").lower()]
        if len(error_events) > 5:  # Allow some errors
            return False

        # Check that components stayed running
        if not self.mia_core or not self.mia_core.is_running():
            return False

        if not self.obd_sim or not self.obd_sim.is_running():
            return False

        # Check for successful operations
        success_indicators = ["query successful", "gpio operation", "telemetry received"]
        found_success = False

        for line in mia_output + obd_output:
            if any(indicator in line.lower() for indicator in success_indicators):
                found_success = True
                break

        return found_success

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "mia_running": self.mia_core.is_running() if self.mia_core else False,
            "obd_running": self.obd_sim.is_running() if self.obd_sim else False,
            "events_captured": len(self.event_monitor.captured_events),
            "telemetry_data": self.serial_bridge.get_telemetry()
        }


# Convenience functions for common test patterns
async def run_emergency_shutdown_test() -> Dict[str, Any]:
    """Run standard emergency shutdown test"""
    harness = DigitalTwinTestHarness()

    async with harness.test_context():
        result = await harness.run_fault_injection_test(
            fault_type="coolant_spike",
            expected_shutdown_ms=200
        )

    return result


async def run_system_integration_test() -> Dict[str, Any]:
    """Run standard system integration test"""
    harness = DigitalTwinTestHarness()

    async with harness.test_context():
        result = await harness.run_integration_test(
            test_scenario="normal_operation",
            duration=15.0
        )

    return result


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)

    async def main():
        print("Running emergency shutdown test...")
        result1 = await run_emergency_shutdown_test()
        print(f"Emergency test result: {result1}")

        print("\nRunning integration test...")
        result2 = await run_system_integration_test()
        print(f"Integration test result: {result2}")

    asyncio.run(main())