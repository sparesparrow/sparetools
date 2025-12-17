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


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add SpareTools markers."""
    for item in items:
        # Check if test uses SpareTools test harness
        if "th" in item.fixturenames:
            item.add_marker(pytest.mark.sparetools)