"""
Pytest Tool Adapter

Adapter for pytest Python testing framework.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

from .base_adapter import BaseToolAdapter, ToolCapabilities, ToolResult, ToolIssue, ToolCategory, Severity


class PytestAdapter(BaseToolAdapter):
    """Adapter for pytest testing framework"""

    def __init__(self, executable: Optional[str] = None):
        super().__init__("pytest", executable)

    @property
    def tool_category(self):
        return ToolCategory.TESTING

    def get_capabilities(self) -> ToolCapabilities:
        """Get pytest capabilities"""
        if self._capabilities:
            return self._capabilities

        # Check if pytest is available and get version
        available, version = self.is_available()

        capabilities = ToolCapabilities(
            name="pytest",
            version=version,
            category=ToolCategory.TESTING,
            supported_platforms=["linux", "macos", "windows"],
            supported_languages=["python"],
            supported_file_types=[".py"],
            can_analyze_directories=True,
            can_analyze_files=True,
            requires_compilation=False,
            supports_custom_rules=False,
            supports_parallel_execution=True,
            has_timeout_support=True,
            output_formats=["json", "junit", "text"],
            metadata={
                "description": "Python testing framework with fixtures and plugins",
                "website": "https://pytest.org/",
                "features": [
                    "fixtures", "parametrization", "plugins", "coverage",
                    "parallel_execution", "doctest", "unittest_compatibility"
                ]
            }
        )

        self._capabilities = capabilities
        return capabilities

    def is_available(self) -> Tuple[bool, Optional[str]]:
        """Check if pytest is available"""
        try:
            result = subprocess.run(
                [self.executable or "python", "-m", "pytest", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Extract version from output
                version_match = re.search(r'pytest (\d+\.\d+\.\d+)', result.stdout)
                version = version_match.group(1) if version_match else None
                return True, version
            return False, None
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False, None

    def build_command(self, target: Union[str, Path], **kwargs) -> List[str]:
        """Build pytest command"""
        cmd = [self.executable or "python", "-m", "pytest"]

        # Output format
        output_format = kwargs.get('output_format', 'json')
        if output_format == 'json':
            cmd.extend(['--json-report', '--json-report-file', 'pytest_results.json'])
        elif output_format == 'junit':
            junit_file = kwargs.get('junit_file', 'junit_results.xml')
            cmd.extend(['--junitxml', junit_file])

        # Verbose output
        if kwargs.get('verbose', False):
            cmd.append('-v')

        # Quiet mode
        if kwargs.get('quiet', False):
            cmd.append('-q')

        # Coverage
        if kwargs.get('coverage', False):
            cmd.extend(['--cov', str(target) if isinstance(target, Path) else target])
            coverage_file = kwargs.get('coverage_file')
            if coverage_file:
                cmd.extend(['--cov-report', f'html:{coverage_file}'])

        # Parallel execution
        parallel = kwargs.get('parallel')
        if parallel:
            cmd.extend(['-n', str(parallel)])

        # Test selection
        test_pattern = kwargs.get('test_pattern')
        if test_pattern:
            cmd.extend(['-k', test_pattern])

        # Markers
        markers = kwargs.get('markers')
        if markers:
            if isinstance(markers, list):
                markers = ' or '.join(markers)
            cmd.extend(['-m', markers])

        # Stop on first failure
        if kwargs.get('stop_on_first_failure', False):
            cmd.append('-x')

        # Fail fast
        if kwargs.get('fail_fast', False):
            cmd.append('--tb=short')

        # Timeout per test
        timeout = kwargs.get('timeout')
        if timeout:
            cmd.extend(['--timeout', str(timeout)])

        # Additional arguments
        extra_args = kwargs.get('extra_args')
        if extra_args:
            if isinstance(extra_args, list):
                cmd.extend(extra_args)
            else:
                cmd.append(extra_args)

        # Target
        if isinstance(target, (str, Path)):
            cmd.append(str(target))

        return cmd

    def parse_output(self, stdout: str, stderr: str, exit_code: int) -> ToolResult:
        """Parse pytest output"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code in [0, 1],  # 1 means tests failed but pytest ran
            exit_code=exit_code
        )

        # Combine stdout and stderr
        full_output = stdout + stderr
        result.raw_output = full_output

        try:
            # Try JSON format first
            json_file = Path('pytest_results.json')
            if json_file.exists():
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
                return self._parse_json_output(json_data, exit_code)
            else:
                # Parse text output
                return self._parse_text_output(full_output, exit_code)

        except Exception as e:
            self.logger.error(f"Failed to parse pytest output: {e}")
            result.error_message = f"Failed to parse output: {str(e)}"
            return result

    def _parse_json_output(self, data: Dict[str, Any], exit_code: int) -> ToolResult:
        """Parse JSON output format"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code in [0, 1],
            exit_code=exit_code
        )

        issues = []
        metrics = {}

        # Extract test summary
        summary = data.get('summary', {})
        metrics.update({
            'passed': summary.get('passed', 0),
            'failed': summary.get('failed', 0),
            'skipped': summary.get('skipped', 0),
            'errors': summary.get('errors', 0),
            'total': summary.get('num_tests', 0)
        })

        # Process individual test results
        for test_result in data.get('tests', []):
            outcome = test_result.get('outcome')

            if outcome == 'failed':
                issue = ToolIssue(
                    file=test_result.get('nodeid', '').split('::')[0],
                    line=test_result.get('lineno'),
                    severity=Severity.HIGH,
                    message=test_result.get('longrepr', {}).get('reprcrash', {}).get('message', 'Test failed'),
                    category="test_failure",
                    metadata={
                        'test_id': test_result.get('nodeid'),
                        'duration': test_result.get('duration'),
                        'markers': test_result.get('markers', [])
                    }
                )
                issues.append(issue)

            elif outcome == 'error':
                issue = ToolIssue(
                    severity=Severity.CRITICAL,
                    message=f"Test error: {test_result.get('longrepr', 'Unknown error')}",
                    category="test_error",
                    metadata={
                        'test_id': test_result.get('nodeid'),
                        'markers': test_result.get('markers', [])
                    }
                )
                issues.append(issue)

        result.issues = issues
        result.metrics = metrics

        return result

    def _parse_text_output(self, output: str, exit_code: int) -> ToolResult:
        """Parse text output format"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code in [0, 1],
            exit_code=exit_code
        )

        issues = []
        metrics = {}

        # Extract summary from text output
        lines = output.strip().split('\n')

        # Look for summary line like "====== 5 passed, 2 failed, 1 skipped in 1.23s ======="
        summary_pattern = r'=+\s+(\d+)\s+passed(?:,\s+(\d+)\s+failed)?(?:,\s+(\d+)\s+skipped)?(?:,\s+(\d+)\s+error)?'
        for line in reversed(lines):  # Check from end
            match = re.search(summary_pattern, line)
            if match:
                passed = int(match.group(1) or 0)
                failed = int(match.group(2) or 0) if match.group(2) else 0
                skipped = int(match.group(3) or 0) if match.group(3) else 0
                errors = int(match.group(4) or 0) if match.group(4) else 0

                metrics.update({
                    'passed': passed,
                    'failed': failed,
                    'skipped': skipped,
                    'errors': errors,
                    'total': passed + failed + skipped + errors
                })
                break

        # Extract failed tests
        in_failures = False
        current_test = None

        for line in lines:
            if line.startswith('___') and '::' in line:
                # Test header
                current_test = line.strip('_ ')
                in_failures = True
            elif in_failures and line.strip():
                # Failure details
                if current_test and ('FAILED' in line or 'ERROR' in line):
                    severity = Severity.CRITICAL if 'ERROR' in line else Severity.HIGH

                    issue = ToolIssue(
                        severity=severity,
                        message=f"Test {current_test} failed",
                        category="test_failure",
                        metadata={'test_id': current_test}
                    )
                    issues.append(issue)
            elif line.startswith('=') and in_failures:
                # End of failures section
                break

        result.issues = issues
        result.metrics = metrics

        return result