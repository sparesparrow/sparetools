"""
SpareTools Test Harness - ngapy-style verification framework.

Core test harness implementation with ngapy-compatible API for the SpareTools ecosystem.
"""

import time
from typing import Optional, Callable, Any
from pathlib import Path

from .test_logging import ThLogger
from .verification import VerificationMethods


class SpareToolsTestHarness:
    """Test harness with ngapy-compatible API.

    Provides structured testing with verification methods that mirror ngapy's API,
    enabling teams familiar with ngapy to use the same testing patterns in SpareTools.
    """

    def __init__(self, results_dir: Optional[Path] = None):
        """Initialize test harness.

        Args:
            results_dir: Directory to store test results and reports.
                        Defaults to 'test-results'.
        """
        self.__output_format__ = "dec"
        self.__callback_function__ = None
        self.th_logger = ThLogger(results_dir)
        self.verification = VerificationMethods(self.th_logger)
        self.results_dir = results_dir or Path("test-results")
        self._start_time = time.time()

    # Output format control
    def set_output_format(self, format: str) -> None:
        """Set output format for numeric values.

        Args:
            format: "dec" (decimal), "hex" (hexadecimal), or "bin" (binary)
        """
        if format not in ["dec", "hex", "bin"]:
            raise ValueError("Format must be 'dec', 'hex', or 'bin'")
        self.__output_format__ = format

    def set_callback_function(self, func: Callable) -> None:
        """Set callback function for custom result handling.

        Args:
            func: Function to call for each test result
        """
        self.__callback_function__ = func

    # Core verification methods (ngapy-compatible)
    def verify(self, actual: Any, expected: Any, msg: str = "",
               test_num: int = 0, on_fail: Optional[Callable] = None) -> bool:
        """Verify equality (ngapy-compatible)."""
        return self.verification.verify(actual, expected, msg, test_num, on_fail)

    def verify_tol(self, actual, expected, tolerance, msg="", test_num=0, on_fail=None) -> bool:
        """Verify with tolerance (ngapy-compatible)."""
        return self.verification.verify_tol(actual, expected, tolerance, msg, test_num, on_fail)

    def verify_range(self, actual, min_value, max_value, msg="", test_num=0, on_fail=None) -> bool:
        """Verify value in range (ngapy-compatible)."""
        return self.verification.verify_range(actual, min_value, max_value, msg, test_num, on_fail)

    def verify_ne(self, actual, expected, msg="", test_num=0, on_fail=None) -> bool:
        """Verify values are not equal."""
        return self.verification.verify_ne(actual, expected, msg, test_num, on_fail)

    def verify_lt(self, actual, expected, msg="", test_num=0, on_fail=None) -> bool:
        """Verify actual < expected."""
        return self.verification.verify_lt(actual, expected, msg, test_num, on_fail)

    def verify_gt(self, actual, expected, msg="", test_num=0, on_fail=None) -> bool:
        """Verify actual > expected."""
        return self.verification.verify_gt(actual, expected, msg, test_num, on_fail)

    def verify_le(self, actual, expected, msg="", test_num=0, on_fail=None) -> bool:
        """Verify actual <= expected."""
        return self.verification.verify_le(actual, expected, msg, test_num, on_fail)

    def verify_ge(self, actual, expected, msg="", test_num=0, on_fail=None) -> bool:
        """Verify actual >= expected."""
        return self.verification.verify_ge(actual, expected, msg, test_num, on_fail)

    def verify_string(self, actual, expected, msg="", test_num=0, on_fail=None) -> bool:
        """Verify string equality (case-sensitive)."""
        return self.verification.verify_string(actual, expected, msg, test_num, on_fail)

    def verify_percent(self, actual, expected, tolerance_percent, msg="", test_num=0, on_fail=None) -> bool:
        """Verify values are within percentage tolerance."""
        return self.verification.verify_percent(actual, expected, tolerance_percent, msg, test_num, on_fail)

    # Reporting methods
    def generate_junit_report(self, filepath: str) -> None:
        """Generate JUnit XML report for CI/CD integration.

        Args:
            filepath: Path to write the JUnit XML report
        """
        self.th_logger.generate_junit_report(filepath)

    def generate_json_report(self, filepath: str) -> None:
        """Generate JSON report with detailed results.

        Args:
            filepath: Path to write the JSON report
        """
        self.th_logger.generate_json_report(filepath)

    def get_summary(self) -> dict:
        """Get test summary statistics.

        Returns:
            Dictionary with test statistics
        """
        return self.th_logger.get_summary()

    def clear_results(self) -> None:
        """Clear all logged test results."""
        self.th_logger.clear_results()
        self._start_time = time.time()

    # Utility methods
    def log_info(self, message: str) -> None:
        """Log informational message."""
        print(f"[INFO] {message}")

    def log_warning(self, message: str) -> None:
        """Log warning message."""
        print(f"[WARN] {message}")

    def log_error(self, message: str) -> None:
        """Log error message."""
        print(f"[ERROR] {message}")

    # Context management
    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic reporting."""
        if exc_type is None:
            # Generate summary report on successful exit
            summary = self.get_summary()
            print(f"\nTest Summary: {summary['passed_tests']}/{summary['total_tests']} passed")
            if summary['failed_tests'] > 0:
                print(f"Failed tests: {summary['failed_tests']}")
        return False  # Don't suppress exceptions