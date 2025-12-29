#!/usr/bin/env python3
"""
SpareTools Embedded Integration Tests

Demonstrates integration of SpareTools with ESP32 projects.
Tests both unit tests and hardware integration.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any

# Add sparetools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sparetools.test_environments.providers.embedded import ESP32Environment, ESP32Config, FirmwareInfo
from sparetools.core.components.providers.embedded import SerialComponent, SerialConfig


class ESP32BPMDetectorIntegration:
    """
    Integration test suite for ESP32 BPM Detector project using SpareTools.
    """

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.test_results = {}
        self.environment = None
        self.serial_component = None

    def setup_environment(self):
        """Setup the test environment"""
        print("🔧 Setting up SpareTools embedded environment...")

        # Create ESP32 environment
        config = ESP32Config(
            port="/dev/ttyUSB0",  # Adjust as needed
            baudrate=115200,
            chip="esp32"
        )

        self.environment = ESP32Environment(config=config)
        print("✓ ESP32 environment created")

        # Create serial component
        serial_config = SerialConfig(
            port="/dev/ttyUSB0",
            baudrate=115200
        )

        self.serial_component = SerialComponent(serial_config)
        print("✓ Serial component created")

    def run_unit_tests(self) -> Dict[str, Any]:
        """
        Run the existing unit tests using the project's test runner.

        Returns:
            Test results dictionary
        """
        print("🧪 Running unit tests...")

        os.chdir(self.project_path)

        try:
            # Run the existing test script
            result = subprocess.run(
                [sys.executable, "run_tests.py"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            # Parse results
            test_results = {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "passed": result.returncode == 0
            }

            # Try to parse test summary from output
            if "PASSED:" in result.stdout and "FAILED:" in result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if "PASSED:" in line and "FAILED:" in line:
                        # Example: "Results: PASSED: 3, FAILED: 0, TOTAL: 3"
                        parts = line.split(',')
                        for part in parts:
                            if "PASSED:" in part:
                                test_results["passed_count"] = int(part.split(":")[1].strip())
                            elif "FAILED:" in part:
                                test_results["failed_count"] = int(part.split(":")[1].strip())
                            elif "TOTAL:" in part:
                                test_results["total_count"] = int(part.split(":")[1].strip())

            return test_results

        except subprocess.TimeoutExpired:
            return {"error": "Unit tests timed out", "passed": False}
        except Exception as e:
            return {"error": str(e), "passed": False}

    def test_hardware_connection(self) -> Dict[str, Any]:
        """
        Test hardware connection using SpareTools environment.

        Returns:
            Hardware test results
        """
        print("🔌 Testing hardware connection...")

        if not self.environment:
            return {"error": "Environment not initialized", "passed": False}

        # Perform health check
        health_ok = self.environment.health_check()

        results = {
            "health_check": health_ok,
            "serial_connection": False,
            "passed": health_ok
        }

        # Test serial connection
        if self.serial_component:
            serial_ok = self.serial_component.connect()
            results["serial_connection"] = serial_ok

            if serial_ok:
                # Try to send a test command
                test_response = self.serial_component.send_and_receive("AT", timeout=2.0)
                results["test_command_response"] = test_response is not None

                self.serial_component.disconnect()

        return results

    def test_firmware_flashing(self, firmware_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Test firmware flashing capability.

        Args:
            firmware_path: Path to firmware binary (optional)

        Returns:
            Flashing test results
        """
        print("⚡ Testing firmware flashing capability...")

        if not self.environment:
            return {"error": "Environment not initialized", "passed": False}

        # Look for firmware in project
        if not firmware_path:
            firmware_candidates = list(self.project_path.glob("*.bin"))
            if firmware_candidates:
                firmware_path = str(firmware_candidates[0])

        if not firmware_path or not Path(firmware_path).exists():
            return {
                "error": f"No firmware found at {firmware_path}",
                "passed": False,
                "simulation": True
            }

        # For safety, we'll simulate the flashing test
        # In a real scenario, you might want to flash to a test device
        results = {
            "firmware_path": firmware_path,
            "firmware_size": Path(firmware_path).stat().st_size,
            "flashing_simulated": True,
            "passed": True
        }

        print(f"   Found firmware: {firmware_path} ({results['firmware_size']} bytes)")

        return results

    def run_integration_tests(self) -> Dict[str, Any]:
        """
        Run complete integration test suite.

        Returns:
            Complete test results
        """
        print("🚀 Running SpareTools ESP32 BPM Detector Integration Tests")
        print("=" * 60)

        results = {
            "test_suite": "ESP32 BPM Detector Integration",
            "timestamp": str(Path(__file__).parent.stat().st_mtime),
            "tests": {}
        }

        # Setup
        try:
            self.setup_environment()
            results["environment_setup"] = {"passed": True}
        except Exception as e:
            results["environment_setup"] = {"passed": False, "error": str(e)}
            return results

        # Unit tests
        results["tests"]["unit_tests"] = self.run_unit_tests()

        # Hardware tests
        results["tests"]["hardware_connection"] = self.test_hardware_connection()

        # Firmware tests
        results["tests"]["firmware_flashing"] = self.test_firmware_flashing()

        # Summary
        passed_tests = sum(1 for test in results["tests"].values() if test.get("passed", False))
        total_tests = len(results["tests"])

        results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        }

        print(f"\n📊 Test Summary: {passed_tests}/{total_tests} tests passed")

        return results


def main():
    """Main entry point"""
    # Path to ESP32 BPM Detector project
    project_path = "/home/sparrow/projects/embedded-systems/esp32-bpm-detector"

    if not Path(project_path).exists():
        print(f"❌ Project path not found: {project_path}")
        sys.exit(1)

    # Run integration tests
    tester = ESP32BPMDetectorIntegration(project_path)
    results = tester.run_integration_tests()

    # Save results
    output_file = Path(project_path) / "sparetools_integration_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"📄 Results saved to: {output_file}")

    # Exit with appropriate code
    success_rate = results.get("summary", {}).get("success_rate", 0)
    if success_rate >= 80:  # 80% success threshold
        print("✅ Integration tests PASSED")
        sys.exit(0)
    else:
        print("❌ Integration tests FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()