"""
GTest Tool Adapter

Adapter for Google Test (GTest) C++ testing framework.
"""

import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

from .base_adapter import BaseToolAdapter, ToolCapabilities, ToolResult, ToolIssue, ToolCategory, Severity


class GtestAdapter(BaseToolAdapter):
    """Adapter for Google Test framework"""

    def __init__(self, executable: Optional[str] = None):
        super().__init__("gtest", executable)

    @property
    def tool_category(self):
        return ToolCategory.TESTING

    def get_capabilities(self) -> ToolCapabilities:
        """Get GTest capabilities"""
        if self._capabilities:
            return self._capabilities

        # For GTest, we check if the executable exists and is a test binary
        available, version = self.is_available()

        capabilities = ToolCapabilities(
            name="gtest",
            version=version,
            category=ToolCategory.TESTING,
            supported_platforms=["linux", "macos", "windows"],
            supported_languages=["c++"],
            supported_file_types=[".exe", ".out", ""],  # Test executables
            can_analyze_directories=False,
            can_analyze_files=True,
            requires_compilation=True,
            supports_custom_rules=False,
            supports_parallel_execution=False,  # GTest doesn't support parallel execution directly
            has_timeout_support=True,
            output_formats=["xml", "text"],
            metadata={
                "description": "Google Test C++ testing framework",
                "website": "https://google.github.io/googletest/",
                "features": [
                    "fixtures", "parametrization", "mocking", "death_tests",
                    "type-driven_tests", "xml_output"
                ]
            }
        )

        self._capabilities = capabilities
        return capabilities

    def is_available(self) -> Tuple[bool, Optional[str]]:
        """Check if the test executable is available and contains GTest"""
        if not self.executable:
            return False, None

        try:
            result = subprocess.run(
                [self.executable, "--gtest_version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Extract version if available
                version_match = re.search(r'(\d+\.\d+\.\d+)', result.stdout)
                version = version_match.group(1) if version_match else "unknown"
                return True, version

            # Try --help to see if it's a GTest executable
            result = subprocess.run(
                [self.executable, "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if "--gtest_" in result.stdout:
                return True, "unknown"

            return False, None
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False, None

    def build_command(self, target: Union[str, Path], **kwargs) -> List[str]:
        """Build GTest command"""
        cmd = [str(target)]  # Target is the test executable

        # Output format
        output_format = kwargs.get('output_format', 'xml')
        if output_format == 'xml':
            output_file = kwargs.get('output_file', 'gtest_results.xml')
            cmd.extend([f'--gtest_output=xml:{output_file}'])

        # Test filters
        test_filter = kwargs.get('test_filter')
        if test_filter:
            cmd.extend(['--gtest_filter', test_filter])

        # Repeat tests
        repeat = kwargs.get('repeat')
        if repeat:
            cmd.extend(['--gtest_repeat', str(repeat)])

        # Randomize test order
        if kwargs.get('shuffle', False):
            cmd.append('--gtest_shuffle')

        # Break on failure
        if kwargs.get('break_on_failure', False):
            cmd.append('--gtest_break_on_failure')

        # Color output
        if kwargs.get('color', True):
            cmd.append('--gtest_color=yes')
        else:
            cmd.append('--gtest_color=no')

        # Verbose output
        if kwargs.get('verbose', False):
            cmd.append('--gtest_print_time=1')

        # Additional arguments
        extra_args = kwargs.get('extra_args')
        if extra_args:
            if isinstance(extra_args, list):
                cmd.extend(extra_args)
            else:
                cmd.append(extra_args)

        return cmd

    def parse_output(self, stdout: str, stderr: str, exit_code: int) -> ToolResult:
        """Parse GTest output"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        # Combine stdout and stderr
        full_output = stdout + stderr
        result.raw_output = full_output

        try:
            # Try XML format first
            xml_file = Path('gtest_results.xml')
            if xml_file.exists():
                return self._parse_xml_output(str(xml_file), exit_code)
            else:
                # Parse text output
                return self._parse_text_output(full_output, exit_code)

        except Exception as e:
            self.logger.error(f"Failed to parse GTest output: {e}")
            result.error_message = f"Failed to parse output: {str(e)}"
            return result

    def _parse_xml_output(self, xml_file: str, exit_code: int) -> ToolResult:
        """Parse XML output format"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            issues = []
            metrics = {
                'tests': 0,
                'failures': 0,
                'errors': 0,
                'skipped': 0
            }

            # Process test suites
            for testsuite in root.findall('.//testsuite'):
                for testcase in testsuite.findall('testcase'):
                    metrics['tests'] += 1

                    # Check for failures
                    failure = testcase.find('failure')
                    if failure is not None:
                        issue = ToolIssue(
                            file=testcase.get('file'),
                            line=testcase.get('line'),
                            severity=Severity.HIGH,
                            message=failure.get('message', 'Test failed'),
                            category="test_failure",
                            metadata={
                                'test_name': testcase.get('name'),
                                'classname': testcase.get('classname'),
                                'time': testcase.get('time')
                            }
                        )
                        issues.append(issue)
                        metrics['failures'] += 1

                    # Check for errors
                    error = testcase.find('error')
                    if error is not None:
                        issue = ToolIssue(
                            severity=Severity.CRITICAL,
                            message=error.get('message', 'Test error'),
                            category="test_error",
                            metadata={
                                'test_name': testcase.get('name'),
                                'classname': testcase.get('classname')
                            }
                        )
                        issues.append(issue)
                        metrics['errors'] += 1

                    # Check for skipped
                    skipped = testcase.find('skipped')
                    if skipped is not None:
                        metrics['skipped'] += 1

            result.issues = issues
            result.metrics = metrics

        except ET.ParseError as e:
            self.logger.warning(f"XML parsing failed: {e}")
            return self._parse_text_output("", exit_code)

        return result

    def _parse_text_output(self, output: str, exit_code: int) -> ToolResult:
        """Parse text output format"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        issues = []
        metrics = {}

        # Extract summary information
        lines = output.strip().split('\n')

        # Look for summary line like "[==========] Running 5 tests from 2 test cases."
        running_match = re.search(r'Running (\d+) tests? from (\d+) test cases?', output)
        if running_match:
            metrics['tests'] = int(running_match.group(1))
            metrics['test_cases'] = int(running_match.group(2))

        # Look for results like "[  PASSED  ] 3 tests." or "[  FAILED  ] 2 tests."
        passed_match = re.search(r'\[  PASSED  \]\s+(\d+) tests?', output)
        if passed_match:
            metrics['passed'] = int(passed_match.group(1))

        failed_match = re.search(r'\[  FAILED  \]\s+(\d+) tests?', output)
        if failed_match:
            metrics['failed'] = int(failed_match.group(1))

        # Extract individual test failures
        in_failure_details = False
        current_test = None

        for line in lines:
            if '[  FAILED  ]' in line and 'tests?' not in line:
                # Individual test failure
                test_match = re.search(r'\[  FAILED  \]\s+(.+)', line)
                if test_match:
                    current_test = test_match.group(1).strip()
                    in_failure_details = True

            elif in_failure_details and line.strip():
                if line.startswith('Failure:') or 'error:' in line.lower():
                    issue = ToolIssue(
                        severity=Severity.HIGH,
                        message=f"Test {current_test} failed: {line.strip()}",
                        category="test_failure",
                        metadata={'test_name': current_test}
                    )
                    issues.append(issue)
                    in_failure_details = False

        result.issues = issues
        result.metrics = metrics

        return result