"""
Test Harness for SpareTools Protocols

This module provides testing utilities for validating protocol implementations
across different platforms and environments.
"""

import subprocess
import sys
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import json
import os

class TestResult(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"

@dataclass
class TestCase:
    name: str
    description: str
    test_func: Callable[[], TestResult]
    platforms: List[str]  # ["esp32", "linux", "android", "all"]
    timeout: int = 30

@dataclass
class TestRun:
    test_case: TestCase
    result: TestResult
    duration: float
    output: str
    error: Optional[str] = None

class ProtocolTestHarness:
    """Test harness for protocol validation"""

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or os.getcwd()
        self.test_cases: List[TestCase] = []
        self.test_runs: List[TestRun] = []

    def add_test_case(self, test_case: TestCase):
        """Add a test case to the harness"""
        self.test_cases.append(test_case)

    def run_tests(self, platform_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Run all test cases

        Args:
            platform_filter: Filter tests by platform ("esp32", "linux", etc.)

        Returns:
            Test results summary
        """
        results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "runs": []
        }

        for test_case in self.test_cases:
            if platform_filter and platform_filter not in test_case.platforms and "all" not in test_case.platforms:
                continue

            start_time = time.time()
            try:
                result = test_case.test_func()
                duration = time.time() - start_time

                test_run = TestRun(
                    test_case=test_case,
                    result=result,
                    duration=duration,
                    output="Test completed successfully"
                )

            except Exception as e:
                duration = time.time() - start_time
                test_run = TestRun(
                    test_case=test_case,
                    result=TestResult.ERROR,
                    duration=duration,
                    output="",
                    error=str(e)
                )

            self.test_runs.append(test_run)
            results["runs"].append({
                "name": test_run.test_case.name,
                "result": test_run.result.value,
                "duration": test_run.duration,
                "error": test_run.error
            })

            results["total"] += 1
            if test_run.result == TestResult.PASS:
                results["passed"] += 1
            elif test_run.result == TestResult.FAIL:
                results["failed"] += 1
            elif test_run.result == TestResult.SKIP:
                results["skipped"] += 1
            elif test_run.result == TestResult.ERROR:
                results["errors"] += 1

        return results

    def generate_report(self, output_file: Optional[str] = None) -> str:
        """Generate a test report"""
        report = "# SpareTools Protocol Test Report\n\n"
        report += f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        if not self.test_runs:
            report += "No tests were run.\n"
            return report

        # Summary
        total = len(self.test_runs)
        passed = sum(1 for r in self.test_runs if r.result == TestResult.PASS)
        failed = sum(1 for r in self.test_runs if r.result == TestResult.FAIL)
        errors = sum(1 for r in self.test_runs if r.result == TestResult.ERROR)
        skipped = sum(1 for r in self.test_runs if r.result == TestResult.SKIP)

        report += "## Summary\n\n"
        report += f"- Total tests: {total}\n"
        report += f"- Passed: {passed}\n"
        report += f"- Failed: {failed}\n"
        report += f"- Errors: {errors}\n"
        report += f"- Skipped: {skipped}\n\n"

        # Detailed results
        report += "## Test Results\n\n"
        for run in self.test_runs:
            status_icon = {
                TestResult.PASS: "✅",
                TestResult.FAIL: "❌",
                TestResult.ERROR: "💥",
                TestResult.SKIP: "⏭️"
            }[run.result]

            report += f"### {status_icon} {run.test_case.name}\n\n"
            report += f"**Description:** {run.test_case.description}\n\n"
            report += f"**Result:** {run.result.value}\n"
            report += ".2f"
            if run.error:
                report += f"**Error:** {run.error}\n"
            report += "\n"

        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)

        return report

# Convenience functions for creating test cases
def create_protocol_test(name: str, description: str, test_func: Callable[[], TestResult],
                        platforms: List[str] = ["all"], timeout: int = 30) -> TestCase:
    """Create a protocol test case"""
    return TestCase(name, description, test_func, platforms, timeout)

def run_command_test(command: List[str], expected_exit_code: int = 0) -> TestResult:
    """Run a command and return test result based on exit code"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.returncode == expected_exit_code:
            return TestResult.PASS
        else:
            print(f"Command failed with exit code {result.returncode}")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return TestResult.FAIL
    except subprocess.TimeoutExpired:
        print("Command timed out")
        return TestResult.ERROR
    except Exception as e:
        print(f"Command execution failed: {e}")
        return TestResult.ERROR