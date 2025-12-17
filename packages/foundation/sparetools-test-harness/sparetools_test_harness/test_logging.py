"""
Test Logging Utilities for SpareTools Test Harness.

Provides structured logging with pass/fail tracking, JUnit XML output,
and integration with CI/CD systems.
"""

import time
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class TestResult:
    """Individual test result."""
    test_num: int
    description: str
    passed: bool
    actual: Any
    expected: Any
    tolerance: Optional[float] = None
    execution_time: float = 0.0
    timestamp: float = 0.0
    details: List[str] = None

    def __post_init__(self):
        if self.details is None:
            self.details = []
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class ThLogger:
    """Structured test logger with JUnit XML support."""

    def __init__(self, results_dir: Optional[Path] = None):
        """Initialize logger."""
        self.results_dir = results_dir or Path("test-results")
        self.results_dir.mkdir(exist_ok=True)
        self.test_results: List[TestResult] = []
        self.start_time = time.time()
        self.test_suite_name = "SpareTools Test Suite"

    def log_result(self, passed: bool, details: List[str],
                   test_num: int = 0, actual: Any = None,
                   expected: Any = None, tolerance: Optional[float] = None,
                   execution_time: float = 0.0) -> None:
        """Log a test result."""
        description = details[0] if details else f"Test {test_num}"

        result = TestResult(
            test_num=test_num,
            description=description,
            passed=passed,
            actual=actual,
            expected=expected,
            tolerance=tolerance,
            execution_time=execution_time,
            details=details[1:] if len(details) > 1 else []
        )

        self.test_results.append(result)

        # Print to console
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {description}")
        if not passed and details:
            for detail in details[1:]:
                print(f"       {detail}")

    def generate_junit_report(self, filepath: str) -> None:
        """Generate JUnit XML report."""
        testsuite = ET.Element("testsuite")
        testsuite.set("name", self.test_suite_name)
        testsuite.set("tests", str(len(self.test_results)))
        testsuite.set("failures", str(sum(1 for r in self.test_results if not r.passed)))
        testsuite.set("time", str(time.time() - self.start_time))

        for result in self.test_results:
            testcase = ET.SubElement(testsuite, "testcase")
            testcase.set("name", result.description)
            testcase.set("time", str(result.execution_time))

            if not result.passed:
                failure = ET.SubElement(testcase, "failure")
                failure.set("message", f"Test {result.test_num} failed")
                failure.text = "\n".join(result.details)

        tree = ET.ElementTree(testsuite)
        tree.write(filepath, encoding="unicode", xml_declaration=True)

    def generate_json_report(self, filepath: str) -> None:
        """Generate JSON report."""
        report = {
            "suite_name": self.test_suite_name,
            "start_time": self.start_time,
            "end_time": time.time(),
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results if r.passed),
            "failed_tests": sum(1 for r in self.test_results if not r.passed),
            "results": [asdict(r) for r in self.test_results]
        }

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)

    def get_summary(self) -> Dict[str, Any]:
        """Get test summary statistics."""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.passed)
        failed = total - passed

        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "pass_rate": passed / total if total > 0 else 0.0,
            "execution_time": time.time() - self.start_time
        }

    def clear_results(self) -> None:
        """Clear all logged results."""
        self.test_results.clear()
        self.start_time = time.time()