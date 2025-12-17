"""
Pytest Plugin for SpareTools Test Harness.

Provides pytest integration with the SpareTools test harness, allowing
ngapy-style verification methods to be used alongside pytest assertions.
"""

import pytest
from pathlib import Path
from typing import Optional

from .test_harness import SpareToolsTestHarness


class PytestTestHarness(SpareToolsTestHarness):
    """Test harness integrated with pytest."""

    def __init__(self, results_dir: Optional[Path] = None, request=None):
        """Initialize pytest-integrated test harness.

        Args:
            results_dir: Directory for test results
            request: pytest request fixture for test naming
        """
        super().__init__(results_dir)
        self.request = request
        self.pytest_failures = []

    def verify(self, actual, expected, msg="", test_num=0, on_fail=None):
        """Verify with pytest integration."""
        result = super().verify(actual, expected, msg, test_num, on_fail)
        if not result:
            test_name = self.request.node.name if self.request else f"test_{test_num}"
            failure_msg = f"Verification failed in {test_name}: {msg}"
            self.pytest_failures.append(failure_msg)
            pytest.fail(failure_msg)
        return result

    def verify_tol(self, actual, expected, tolerance, msg="", test_num=0, on_fail=None):
        """Verify with tolerance and pytest integration."""
        result = super().verify_tol(actual, expected, tolerance, msg, test_num, on_fail)
        if not result:
            test_name = self.request.node.name if self.request else f"test_{test_num}"
            failure_msg = f"Tolerance verification failed in {test_name}: {msg}"
            self.pytest_failures.append(failure_msg)
            pytest.fail(failure_msg)
        return result

    def verify_range(self, actual, min_value, max_value, msg="", test_num=0, on_fail=None):
        """Verify range with pytest integration."""
        result = super().verify_range(actual, min_value, max_value, msg, test_num, on_fail)
        if not result:
            test_name = self.request.node.name if self.request else f"test_{test_num}"
            failure_msg = f"Range verification failed in {test_name}: {msg}"
            self.pytest_failures.append(failure_msg)
            pytest.fail(failure_msg)
        return result


# Pytest fixtures
@pytest.fixture
def th(request):
    """Pytest fixture providing SpareTools test harness."""
    harness = PytestTestHarness(request=request)
    yield harness
    # Generate reports after test
    if harness.th_logger.test_results:
        test_class = request.cls.__name__ if request.cls else "tests"
        report_file = f"test-results/{test_class}-{request.node.name}.xml"
        harness.generate_junit_report(report_file)


@pytest.fixture(scope="session", autouse=True)
def setup_test_session():
    """Session-wide test setup."""
    # Ensure test-results directory exists
    Path("test-results").mkdir(exist_ok=True)


# Pytest plugin hooks
def pytest_configure(config):
    """Configure pytest with SpareTools test harness."""
    config.addinivalue_line(
        "markers",
        "sparetools: mark test as using SpareTools test harness"
    )
    config.addinivalue_line(
        "markers", "hardware: marks tests as hardware integration tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "simulation: marks tests as hardware simulation tests"
    )

    # Store results directory for fixtures
    results_base = Path(config.getoption("--basetemp", Path("test-results")))
    config._sparetools_results_dir = results_base / "sparetools"


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add SpareTools markers."""
    for item in items:
        # Check if test uses SpareTools test harness
        if "th" in item.fixturenames:
            item.add_marker(pytest.mark.sparetools)

        # Add simulation marker for hardware tests when simulation is enabled
        hardware_simulation = config.getoption("--hardware-simulation", True)
        if hardware_simulation and "hardware" in item.keywords:
            item.add_marker(pytest.mark.simulation)

        # Skip hardware tests if simulation is disabled and no real hardware available
        if not hardware_simulation and "hardware" in item.keywords:
            # Check if real hardware is available (would be implemented per project)
            hardware_available = False  # Placeholder
            if not hardware_available:
                item.add_marker(pytest.mark.skip(reason="Real hardware not available"))


# ESP32-specific fixtures
@pytest.fixture(scope="session")
def esp32_harness(request):
    """
    Session-scoped ESP32 test harness fixture.

    Provides an ESP32TestHarness instance for the entire test session.
    Results are stored in the session results directory.
    """
    # Get results directory from pytest config or use default
    results_dir = getattr(request.config, "_sparetools_results_dir", None)
    if results_dir is None:
        results_dir = Path("test-results") / "esp32-session"

    from .esp32_test_harness import ESP32TestHarness
    harness = ESP32TestHarness(results_dir=results_dir, hardware_simulation=True)
    yield harness

    # Generate session report at the end
    harness.export_hardware_state()


@pytest.fixture(scope="function")
def esp32_hardware_harness(request, tmp_path):
    """
    Function-scoped ESP32 hardware test harness fixture.

    Provides a fresh ESP32TestHarness instance for each test function.
    Hardware simulation is enabled by default.
    """
    results_dir = tmp_path / "esp32_hardware_test_results"
    from .esp32_test_harness import ESP32TestHarness
    harness = ESP32TestHarness(results_dir=results_dir, hardware_simulation=True)

    yield harness

    # Reset hardware simulation between tests
    harness.reset_hardware_state()


@pytest.fixture(scope="function")
def esp32_integration_harness(request, tmp_path):
    """
    Function-scoped ESP32 integration test harness fixture.

    Similar to esp32_hardware_harness but configured for integration testing.
    """
    results_dir = tmp_path / "esp32_integration_test_results"
    from .esp32_test_harness import ESP32TestHarness
    harness = ESP32TestHarness(results_dir=results_dir, hardware_simulation=True)

    yield harness

    # Generate integration-specific report
    harness.export_hardware_state()


@pytest.fixture(autouse=True)
def esp32_setup_test_environment(request):
    """
    Auto-used fixture to set up ESP32 test environment variables.

    Sets environment variables needed for ESP32 testing.
    """
    import os

    # Set test environment variables
    original_env = {}
    test_env_vars = {
        "ESP32_TEST_MODE": "1",
        "ESP32_HARDWARE_SIMULATION": "1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
    }

    for key, value in test_env_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value

    yield

    # Restore original environment
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


def pytest_addoption(parser):
    """Add command line options for ESP32 testing."""
    group = parser.getgroup("esp32", "ESP32 test harness options")

    group.addoption(
        "--hardware-simulation",
        action="store_true",
        default=True,
        help="Enable hardware simulation mode (default: enabled)"
    )

    group.addoption(
        "--disable-hardware-simulation",
        action="store_false",
        dest="hardware_simulation",
        help="Disable hardware simulation mode"
    )

    group.addoption(
        "--esp32-results-dir",
        type=Path,
        help="Directory to store ESP32 test results"
    )


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Add ESP32 test summary to pytest terminal output.
    """
    if hasattr(config, "_sparetools_results_dir"):
        results_dir = config._sparetools_results_dir
        if results_dir.exists():
            terminalreporter.write_sep("=", "ESP32 Test Results")
            terminalreporter.write_line(f"Results directory: {results_dir}")

            # Count result files
            json_files = list(results_dir.glob("**/*.json"))
            if json_files:
                terminalreporter.write_line(f"Generated {len(json_files)} result files")

            terminalreporter.write_line(f"Open reports: file://{results_dir}/esp32_session_report.json")


# Export fixtures for direct import
__all__ = [
    "th",
    "setup_test_session",
    "esp32_harness",
    "esp32_hardware_harness",
    "esp32_integration_harness",
    "esp32_setup_test_environment",
]