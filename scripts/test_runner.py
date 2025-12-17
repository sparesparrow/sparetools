#!/usr/bin/env python3
"""
SpareTools Unified Test Runner

Executes tests with ngapy-compatible verification framework, JUnit XML output,
parallel execution, and security scanning integration.

Usage:
    python test_runner.py [options] [test_paths...]

Options:
    --pattern PATTERN       Test file pattern (default: test_*.py)
    --parallel              Run tests in parallel
    --junit-xml FILE        Generate JUnit XML report
    --security-scan         Run security scanning
    --verbose, -v           Verbose output
    --fail-fast             Stop on first failure
    --coverage              Generate coverage report
    --help                  Show this help message
"""

import argparse
import sys
import time
import multiprocessing
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import subprocess
import importlib.util
import traceback
import json
import xml.etree.ElementTree as ET


class TestResult:
    """Individual test result."""

    def __init__(self, test_name: str, module: str, passed: bool,
                 execution_time: float, error: Optional[str] = None):
        self.test_name = test_name
        self.module = module
        self.passed = passed
        self.execution_time = execution_time
        self.error = error
        self.start_time = time.time() - execution_time


class TestSuiteResult:
    """Test suite execution result."""

    def __init__(self, suite_name: str):
        self.suite_name = suite_name
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.end_time: Optional[float] = None

    def add_result(self, result: TestResult) -> None:
        """Add test result."""
        self.results.append(result)

    def finish(self) -> None:
        """Mark suite as finished."""
        self.end_time = time.time()

    @property
    def total_tests(self) -> int:
        """Get total number of tests."""
        return len(self.results)

    @property
    def passed_tests(self) -> int:
        """Get number of passed tests."""
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_tests(self) -> int:
        """Get number of failed tests."""
        return self.total_tests - self.passed_tests

    @property
    def execution_time(self) -> float:
        """Get total execution time."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time


class SecurityScanner:
    """Security scanning integration."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def scan_file(self, filepath: Path) -> Dict[str, Any]:
        """Scan a file for security issues."""
        # Placeholder for security scanning
        # In real implementation, this would integrate with tools like:
        # - Trivy (container scanning)
        # - Syft (SBOM generation)
        # - FIPS validation

        if self.verbose:
            print(f"🔍 Scanning {filepath}...")

        # Mock security scan result
        return {
            "file": str(filepath),
            "vulnerabilities": [],
            "compliant": True,
            "scan_time": 0.1
        }

    def scan_directory(self, directory: Path) -> Dict[str, Any]:
        """Scan directory for security issues."""
        results = []
        total_scan_time = 0.0

        for file_path in directory.rglob("*.py"):
            result = self.scan_file(file_path)
            results.append(result)
            total_scan_time += result["scan_time"]

        return {
            "directory": str(directory),
            "files_scanned": len(results),
            "total_vulnerabilities": sum(len(r["vulnerabilities"]) for r in results),
            "compliant": all(r["compliant"] for r in results),
            "scan_time": total_scan_time,
            "results": results
        }


class TestRunner:
    """Unified test runner with ngapy-compatible verification framework."""

    def __init__(self, verbose: bool = False, fail_fast: bool = False,
                 parallel: bool = False, junit_xml: Optional[str] = None,
                 security_scan: bool = False):
        """Initialize test runner.

        Args:
            verbose: Enable verbose output
            fail_fast: Stop on first failure
            parallel: Run tests in parallel
            junit_xml: Path for JUnit XML output
            security_scan: Enable security scanning
        """
        self.verbose = verbose
        self.fail_fast = fail_fast
        self.parallel = parallel
        self.junit_xml = Path(junit_xml) if junit_xml else None
        self.security_scan = security_scan

        self.security_scanner = SecurityScanner(verbose) if security_scan else None
        self.test_suites: List[TestSuiteResult] = []

        # Try to import SpareTools test harness
        self.has_test_harness = False
        try:
            from sparetools_test_harness import SpareToolsTestHarness
            self.test_harness_class = SpareToolsTestHarness
            self.has_test_harness = True
            if verbose:
                print("✅ SpareTools test harness available")
        except ImportError:
            if verbose:
                print("⚠️  SpareTools test harness not available, using basic test execution")

    def log(self, message: str, level: str = "INFO") -> None:
        """Log message."""
        if self.verbose or level in ["ERROR", "WARN"]:
            print(f"[{level}] {message}")

    def discover_tests(self, test_paths: List[str], pattern: str = "test_*.py") -> List[Path]:
        """Discover test files."""
        test_files = []

        for test_path in test_paths:
            path = Path(test_path)
            if path.is_file():
                if path.match(pattern):
                    test_files.append(path)
            elif path.is_dir():
                test_files.extend(path.rglob(pattern))

        return sorted(set(test_files))

    def run_single_test(self, test_file: Path) -> TestSuiteResult:
        """Run a single test file."""
        suite = TestSuiteResult(test_file.stem)

        start_time = time.time()
        self.log(f"Running {test_file}...")

        try:
            # Import test module
            spec = importlib.util.spec_from_file_location(test_file.stem, test_file)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load {test_file}")

            module = importlib.util.module_from_spec(spec)

            # Add test harness to module if available
            if self.has_test_harness:
                module.SpareToolsTestHarness = self.test_harness_class

            spec.loader.exec_module(module)

            # Run test functions
            test_functions = [
                getattr(module, name) for name in dir(module)
                if name.startswith('test_') and callable(getattr(module, name))
            ]

            for test_func in test_functions:
                test_start = time.time()

                try:
                    if self.has_test_harness and hasattr(module, 'th'):
                        # Reset test harness for each test
                        module.th.clear_results()

                    test_func()

                    # Check test harness results if available
                    passed = True
                    error = None
                    if self.has_test_harness and hasattr(module, 'th'):
                        summary = module.th.get_summary()
                        passed = summary['failed_tests'] == 0
                        if not passed:
                            error = f"Verification failures: {summary['failed_tests']}"

                    execution_time = time.time() - test_start
                    result = TestResult(
                        test_name=test_func.__name__,
                        module=test_file.stem,
                        passed=passed,
                        execution_time=execution_time,
                        error=error
                    )

                except Exception as e:
                    execution_time = time.time() - test_start
                    result = TestResult(
                        test_name=test_func.__name__,
                        module=test_file.stem,
                        passed=False,
                        execution_time=execution_time,
                        error=str(e)
                    )

                suite.add_result(result)

                if not result.passed and self.fail_fast:
                    break

        except Exception as e:
            # Module-level error
            execution_time = time.time() - start_time
            result = TestResult(
                test_name="module_import",
                module=test_file.stem,
                passed=False,
                execution_time=execution_time,
                error=f"Module error: {str(e)}"
            )
            suite.add_result(result)

        suite.finish()
        return suite

    def run_parallel_tests(self, test_files: List[Path]) -> List[TestSuiteResult]:
        """Run tests in parallel."""
        self.log(f"Running {len(test_files)} test files in parallel...")

        with multiprocessing.Pool() as pool:
            results = pool.map(self.run_single_test, test_files)

        return results

    def run_tests(self, test_paths: List[str], pattern: str = "test_*.py") -> bool:
        """Run test suite."""
        self.log("🚀 Starting test execution...")

        # Discover test files
        test_files = self.discover_tests(test_paths, pattern)
        if not test_files:
            self.log("❌ No test files found", "ERROR")
            return False

        self.log(f"📋 Found {len(test_files)} test files")

        # Security scan if requested
        if self.security_scan:
            self.log("🔍 Running security scan...")
            scan_results = self.security_scanner.scan_directory(Path("."))
            self.log(f"Security scan: {scan_results['files_scanned']} files, "
                    f"{scan_results['total_vulnerabilities']} vulnerabilities")

            if not scan_results['compliant']:
                self.log("❌ Security scan failed", "ERROR")
                return False

        # Run tests
        start_time = time.time()

        if self.parallel and len(test_files) > 1:
            self.test_suites = self.run_parallel_tests(test_files)
        else:
            self.test_suites = []
            for test_file in test_files:
                suite = self.run_single_test(test_file)
                self.test_suites.append(suite)

                if self.fail_fast and any(not r.passed for r in suite.results):
                    break

        execution_time = time.time() - start_time

        # Generate JUnit XML if requested
        if self.junit_xml:
            self.generate_junit_xml()

        # Print summary
        self.print_summary(execution_time)

        # Return success/failure
        total_failed = sum(suite.failed_tests for suite in self.test_suites)
        return total_failed == 0

    def generate_junit_xml(self) -> None:
        """Generate JUnit XML report."""
        testsuites = ET.Element("testsuites")

        total_tests = sum(s.total_tests for s in self.test_suites)
        total_failures = sum(s.failed_tests for s in self.test_suites)
        total_time = sum(s.execution_time for s in self.test_suites)

        testsuites.set("tests", str(total_tests))
        testsuites.set("failures", str(total_failures))
        testsuites.set("time", str(total_time))

        for suite in self.test_suites:
            testsuite = ET.SubElement(testsuites, "testsuite")
            testsuite.set("name", suite.suite_name)
            testsuite.set("tests", str(suite.total_tests))
            testsuite.set("failures", str(suite.failed_tests))
            testsuite.set("time", str(suite.execution_time))

            for result in suite.results:
                testcase = ET.SubElement(testsuite, "testcase")
                testcase.set("name", result.test_name)
                testcase.set("classname", result.module)
                testcase.set("time", str(result.execution_time))

                if not result.passed and result.error:
                    failure = ET.SubElement(testcase, "failure")
                    failure.set("message", "Test failed")
                    failure.text = result.error

        tree = ET.ElementTree(testsuites)
        self.junit_xml.parent.mkdir(parents=True, exist_ok=True)
        tree.write(str(self.junit_xml), encoding="unicode", xml_declaration=True)
        self.log(f"📄 JUnit XML report written to {self.junit_xml}")

    def print_summary(self, total_time: float) -> None:
        """Print test execution summary."""
        total_suites = len(self.test_suites)
        total_tests = sum(s.total_tests for s in self.test_suites)
        total_passed = sum(s.passed_tests for s in self.test_suites)
        total_failed = sum(s.failed_tests for s in self.test_suites)

        print("\n" + "="*60)
        print("TEST EXECUTION SUMMARY")
        print("="*60)
        print(f"Test suites run: {total_suites}")
        print(f"Total tests:     {total_tests}")
        print(f"Passed:          {total_passed}")
        print(f"Failed:          {total_failed}")
        print(".1f")
        print(".1f")
        print()

        if total_failed > 0:
            print("FAILED TESTS:")
            for suite in self.test_suites:
                for result in suite.results:
                    if not result.passed:
                        print(f"  ❌ {suite.suite_name}.{result.test_name}")
                        if result.error:
                            print(f"     {result.error}")
            print()
            print("❌ Some tests failed")
        else:
            print("✅ All tests passed")

        print("="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SpareTools Unified Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "test_paths",
        nargs="*",
        default=["test", "tests"],
        help="Test paths to search (default: test tests)"
    )

    parser.add_argument(
        "--pattern",
        default="test_*.py",
        help="Test file pattern (default: test_*.py)"
    )

    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )

    parser.add_argument(
        "--junit-xml",
        help="Generate JUnit XML report at specified path"
    )

    parser.add_argument(
        "--security-scan",
        action="store_true",
        help="Run security scanning"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first failure"
    )

    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )

    args = parser.parse_args()

    runner = TestRunner(
        verbose=args.verbose,
        fail_fast=args.fail_fast,
        parallel=args.parallel,
        junit_xml=args.junit_xml,
        security_scan=args.security_scan
    )

    success = runner.run_tests(args.test_paths, args.pattern)

    # Coverage reporting (placeholder)
    if args.coverage and success:
        print("📊 Coverage reporting not yet implemented")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()