"""
ESP32 Test Runner

Provides comprehensive test execution capabilities for ESP32 projects:
- Unit tests (C++ with GoogleTest)
- Integration tests (Python with hardware simulation)
- Linting and formatting checks
- Security scanning
- Coverage reporting
- Parallel test execution
"""

import os
import sys
import time
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict


@dataclass
class TestSuiteResult:
    """Result of a test suite execution."""
    suite_name: str
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    return_code: int
    output: str
    junit_file: Optional[str] = None


class ESP32TestRunner:
    """
    Unified test runner for ESP32 projects following SpareTools patterns.

    Provides comprehensive test execution capabilities:
    - Unit tests (C++ with GoogleTest)
    - Integration tests (Python with hardware simulation)
    - Linting and formatting checks
    - Security scanning
    - Coverage reporting
    - Parallel test execution
    """

    def __init__(self, project_root: Optional[Path] = None, verbose: bool = False):
        """
        Initialize test runner.

        Args:
            project_root: Root directory of the project
            verbose: Enable verbose output
        """
        self.project_root = project_root or Path.cwd()
        self.verbose = verbose
        self.results_dir = self.project_root / "test-results"
        self.coverage_dir = self.project_root / "coverage"
        self.junit_dir = self.results_dir / "junit"

        # Create output directories
        self.results_dir.mkdir(exist_ok=True)
        self.coverage_dir.mkdir(exist_ok=True)
        self.junit_dir.mkdir(exist_ok=True)

        # Test suite results
        self.test_results: List[TestSuiteResult] = []

    def run_command(self, cmd: List[str], cwd: Optional[Path] = None,
                   capture_output: bool = True, check: bool = False) -> Tuple[int, str, str]:
        """
        Run a command and return results.

        Args:
            cmd: Command to run
            cwd: Working directory
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise exception on non-zero exit

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        if self.verbose:
            print(f"[EXEC] {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.project_root,
                capture_output=capture_output,
                text=True,
                check=check
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr

    def run_unit_tests(self, parallel: bool = True, coverage: bool = True) -> TestSuiteResult:
        """
        Run C++ unit tests using GoogleTest.

        Args:
            parallel: Run tests in parallel
            coverage: Generate coverage reports

        Returns:
            TestSuiteResult for unit tests
        """
        print("🧪 Running unit tests (C++)...")

        start_time = time.time()

        # Build tests first
        print("   Building test executables...")
        build_cmd = ["cmake", "--build", "build-release", "--config", "Debug"]
        if parallel:
            build_cmd.extend(["--parallel", str(os.cpu_count() or 4)])

        return_code, stdout, stderr = self.run_command(build_cmd)

        if return_code != 0:
            print(f"   ❌ Build failed with code {return_code}")
            return TestSuiteResult(
                suite_name="unit_tests",
                passed=0, failed=0, skipped=0, errors=1,
                duration=time.time() - start_time,
                return_code=return_code,
                output=stdout + stderr
            )

        # Run unit tests
        print("   Running C++ unit tests...")
        test_cmd = ["ctest", "--output-on-failure", "--output-junit", str(self.junit_dir / "unit_tests.xml")]

        if coverage:
            # Set up coverage environment
            os.environ['LLVM_PROFILE_FILE'] = str(self.coverage_dir / "unit_tests.profraw")

        return_code, stdout, stderr = self.run_command(test_cmd)

        duration = time.time() - start_time
        output = stdout + stderr

        # Parse test results from output
        passed, failed, skipped = self._parse_ctest_output(output)

        result = TestSuiteResult(
            suite_name="unit_tests",
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=0,
            duration=duration,
            return_code=return_code,
            output=output,
            junit_file=str(self.junit_dir / "unit_tests.xml")
        )

        print(f"   ✅ Unit tests completed: {passed} passed, {failed} failed, {skipped} skipped")

        if coverage:
            self._generate_coverage_report("unit_tests")

        return result

    def run_integration_tests(self, hardware_simulation: bool = True) -> TestSuiteResult:
        """
        Run Python integration tests with hardware simulation.

        Args:
            hardware_simulation: Enable hardware simulation

        Returns:
            TestSuiteResult for integration tests
        """
        print("🔗 Running integration tests (Python)...")

        start_time = time.time()

        # Set environment variables for hardware simulation
        env = os.environ.copy()
        if hardware_simulation:
            env['ESP32_HARDWARE_SIMULATION'] = '1'
            env['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'

        # Run pytest with ESP32 test harness
        cmd = [
            sys.executable, "-m", "pytest",
            "test/integration/",
            "-v",
            "--tb=short",
            "--junitxml", str(self.junit_dir / "integration_tests.xml"),
            "--esp32-hardware-simulation" if hardware_simulation else ""
        ]

        return_code, stdout, stderr = self.run_command(cmd, env=env)

        duration = time.time() - start_time
        output = stdout + stderr

        # Parse pytest output for results
        passed, failed, skipped = self._parse_pytest_output(output)

        result = TestSuiteResult(
            suite_name="integration_tests",
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=0,
            duration=duration,
            return_code=return_code,
            output=output,
            junit_file=str(self.junit_dir / "integration_tests.xml")
        )

        print(f"   ✅ Integration tests completed: {passed} passed, {failed} failed, {skipped} skipped")

        return result

    def run_hardware_tests(self) -> TestSuiteResult:
        """
        Run hardware-specific tests (requires actual hardware).

        Returns:
            TestSuiteResult for hardware tests
        """
        print("🔌 Running hardware tests...")

        start_time = time.time()

        # Check if hardware is available
        if not self._check_hardware_available():
            print("   ⚠️  Hardware not available, skipping hardware tests")
            return TestSuiteResult(
                suite_name="hardware_tests",
                passed=0, failed=0, skipped=1, errors=0,
                duration=time.time() - start_time,
                return_code=0,
                output="Hardware not available"
            )

        # Run hardware tests
        cmd = [
            sys.executable, "-m", "pytest",
            "test/hardware/",
            "-v",
            "--tb=short",
            "--junitxml", str(self.junit_dir / "hardware_tests.xml"),
            "-m", "hardware"
        ]

        return_code, stdout, stderr = self.run_command(cmd)

        duration = time.time() - start_time
        output = stdout + stderr

        # Parse pytest output for results
        passed, failed, skipped = self._parse_pytest_output(output)

        result = TestSuiteResult(
            suite_name="hardware_tests",
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=0,
            duration=duration,
            return_code=return_code,
            output=output,
            junit_file=str(self.junit_dir / "hardware_tests.xml")
        )

        print(f"   ✅ Hardware tests completed: {passed} passed, {failed} failed, {skipped} skipped")

        return result

    def run_quality_checks(self) -> TestSuiteResult:
        """
        Run code quality checks (linting, formatting, etc.).

        Returns:
            TestSuiteResult for quality checks
        """
        print("🔍 Running quality checks...")

        start_time = time.time()

        # Run pre-commit hooks
        cmd = ["pre-commit", "run", "--all-files", "--show-diff-on-failure"]
        return_code, stdout, stderr = self.run_command(cmd)

        duration = time.time() - start_time
        output = stdout + stderr

        # Quality checks are considered passed if they return 0
        passed = 1 if return_code == 0 else 0
        failed = 1 if return_code != 0 else 0

        result = TestSuiteResult(
            suite_name="quality_checks",
            passed=passed,
            failed=failed,
            skipped=0,
            errors=0,
            duration=duration,
            return_code=return_code,
            output=output
        )

        status = "✅" if passed else "❌"
        print(f"   {status} Quality checks completed")

        return result

    def run_security_scan(self) -> TestSuiteResult:
        """
        Run security scanning.

        Returns:
            TestSuiteResult for security scan
        """
        print("🔒 Running security scan...")

        start_time = time.time()

        # Run Trivy security scan
        cmd = ["trivy", "fs", "--format", "json", "--output", str(self.results_dir / "security_scan.json"), "."]
        return_code, stdout, stderr = self.run_command(cmd)

        duration = time.time() - start_time
        output = stdout + stderr

        # Security scan is considered passed if no critical vulnerabilities found
        # In a real implementation, you'd parse the JSON output
        passed = 1 if return_code == 0 else 0
        failed = 1 if return_code != 0 else 0

        result = TestSuiteResult(
            suite_name="security_scan",
            passed=passed,
            failed=failed,
            skipped=0,
            errors=0,
            duration=duration,
            return_code=return_code,
            output=output
        )

        status = "✅" if passed else "❌"
        print(f"   {status} Security scan completed")

        return result

    def run_tests(self, unit_only: bool = False, integration_only: bool = False,
                  hardware_only: bool = False, coverage: bool = False,
                  parallel: bool = True, report_dir: Optional[Path] = None,
                  formats: List[str] = None) -> int:
        """
        Run all enabled test suites.

        Args:
            unit_only: Run only unit tests
            integration_only: Run only integration tests
            hardware_only: Run only hardware tests
            coverage: Generate coverage reports
            parallel: Run tests in parallel
            report_dir: Directory for reports
            formats: Output formats

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        if report_dir:
            self.results_dir = report_dir
            self.junit_dir = self.results_dir / "junit"

        formats = formats or ['console']

        print("🚀 ESP32 Test Runner")
        print("=" * 50)

        # Determine which tests to run
        run_all = not (unit_only or integration_only or hardware_only)
        run_unit = run_all or unit_only
        run_integration = run_all or integration_only
        run_hardware = run_all or hardware_only

        # Run test suites
        if run_unit:
            result = self.run_unit_tests(parallel=parallel, coverage=coverage)
            self.test_results.append(result)

        if run_integration:
            result = self.run_integration_tests()
            self.test_results.append(result)

        if run_hardware:
            result = self.run_hardware_tests()
            self.test_results.append(result)

        # Run quality checks and security scan
        quality_result = self.run_quality_checks()
        self.test_results.append(quality_result)

        security_result = self.run_security_scan()
        self.test_results.append(security_result)

        # Generate reports
        self._generate_reports(formats)

        # Calculate overall result
        total_passed = sum(r.passed for r in self.test_results)
        total_failed = sum(r.failed for r in self.test_results)
        total_errors = sum(r.errors for r in self.test_results)

        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)
        print(f"Total Passed: {total_passed}")
        print(f"Total Failed: {total_failed}")
        print(f"Total Errors: {total_errors}")

        for result in self.test_results:
            status = "✅" if result.failed == 0 and result.errors == 0 else "❌"
            print(f"{status} {result.suite_name}: {result.passed} passed, {result.failed} failed, {result.errors} errors ({result.duration:.2f}s)")

        # Return appropriate exit code
        if total_failed > 0 or total_errors > 0:
            print("\n❌ Some tests failed")
            return 1
        else:
            print("\n✅ All tests passed")
            return 0

    def _parse_ctest_output(self, output: str) -> Tuple[int, int, int]:
        """Parse CTest output to extract test counts."""
        # Simple parsing - in a real implementation, you'd use more robust parsing
        passed = output.count("PASSED")
        failed = output.count("FAILED")
        skipped = 0  # CTest doesn't typically report skipped tests the same way

        return passed, failed, skipped

    def _parse_pytest_output(self, output: str) -> Tuple[int, int, int]:
        """Parse pytest output to extract test counts."""
        # Simple parsing - in a real implementation, you'd parse the JUnit XML
        passed = output.count("PASSED") + output.count("passed")
        failed = output.count("FAILED") + output.count("failed")
        skipped = output.count("SKIPPED") + output.count("skipped")

        return passed, failed, skipped

    def _check_hardware_available(self) -> bool:
        """Check if ESP32 hardware is available."""
        # In a real implementation, this would check for connected hardware
        # For now, assume hardware is not available in CI/simulation environments
        return os.environ.get('ESP32_HARDWARE_AVAILABLE', 'false').lower() == 'true'

    def _generate_coverage_report(self, test_suite: str):
        """Generate coverage report for a test suite."""
        print(f"   Generating coverage report for {test_suite}...")

        # Use llvm-cov for clang coverage
        profraw_file = self.coverage_dir / f"{test_suite}.profraw"
        profdata_file = self.coverage_dir / f"{test_suite}.profdata"

        if profraw_file.exists():
            # Convert profraw to profdata
            cmd = ["llvm-profdata", "merge", str(profraw_file), "-o", str(profdata_file)]
            self.run_command(cmd)

            # Generate coverage report
            cmd = [
                "llvm-cov", "show",
                "--format=html",
                "--output-dir", str(self.coverage_dir / test_suite),
                "--instr-profile", str(profdata_file),
                "build-release/unit_tests"  # This would need to be configurable
            ]
            self.run_command(cmd)

    def _generate_reports(self, formats: List[str]):
        """Generate test reports in requested formats."""
        print("\n📄 Generating reports...")

        # Generate JSON report
        if 'json' in formats:
            json_report = {
                'timestamp': time.time(),
                'project': 'esp32-project',  # This should be configurable
                'test_results': [asdict(r) for r in self.test_results]
            }

            with open(self.results_dir / 'test_report.json', 'w') as f:
                json.dump(json_report, f, indent=2, default=str)

            print(f"   📄 JSON report: {self.results_dir / 'test_report.json'}")

        # Generate HTML report
        if 'html' in formats:
            self._generate_html_report()

        # Generate JUnit reports (already generated by individual test suites)
        if 'junit' in formats:
            print(f"   📄 JUnit reports: {self.junit_dir}")

    def _generate_html_report(self):
        """Generate HTML test report."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ESP32 Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f0f0f0; padding: 10px; border-radius: 5px; }}
                .test-suite {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
                .passed {{ background: #d4edda; }}
                .failed {{ background: #f8d7da; }}
            </style>
        </head>
        <body>
            <h1>ESP32 Test Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Test Suites: {len(self.test_results)}</p>
                <p>Total Passed: {sum(r.passed for r in self.test_results)}</p>
                <p>Total Failed: {sum(r.failed for r in self.test_results)}</p>
            </div>

            <h2>Test Results</h2>
        """

        for result in self.test_results:
            css_class = "passed" if result.failed == 0 and result.errors == 0 else "failed"
            html_content += f"""
            <div class="test-suite {css_class}">
                <h3>{result.suite_name}</h3>
                <p>Duration: {result.duration:.2f}s</p>
                <p>Passed: {result.passed}, Failed: {result.failed}, Skipped: {result.skipped}, Errors: {result.errors}</p>
            </div>
            """

        html_content += """
        </body>
        </html>
        """

        with open(self.results_dir / 'test_report.html', 'w') as f:
            f.write(html_content)

        print(f"   📄 HTML report: {self.results_dir / 'test_report.html'}")