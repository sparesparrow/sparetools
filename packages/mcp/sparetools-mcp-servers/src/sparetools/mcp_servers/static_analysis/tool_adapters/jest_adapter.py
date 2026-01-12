"""
Jest Tool Adapter

Adapter for Jest JavaScript testing framework.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

from .base_adapter import BaseToolAdapter, ToolCapabilities, ToolResult, ToolIssue, ToolCategory, Severity


class JestAdapter(BaseToolAdapter):
    """Adapter for Jest testing framework"""

    def __init__(self, executable: Optional[str] = None):
        super().__init__("jest", executable or "npx jest")

    @property
    def tool_category(self):
        return ToolCategory.TESTING

    def get_capabilities(self) -> ToolCapabilities:
        """Get Jest capabilities"""
        if self._capabilities:
            return self._capabilities

        # Check if jest is available
        available, version = self.is_available()

        capabilities = ToolCapabilities(
            name="jest",
            version=version,
            category=ToolCategory.TESTING,
            supported_platforms=["linux", "macos", "windows"],
            supported_languages=["javascript", "typescript"],
            supported_file_types=[".js", ".jsx", ".ts", ".tsx"],
            can_analyze_directories=True,
            can_analyze_files=True,
            requires_compilation=False,
            supports_custom_rules=False,
            supports_parallel_execution=True,
            has_timeout_support=True,
            output_formats=["json", "junit", "text"],
            metadata={
                "description": "JavaScript testing framework with built-in mocking and coverage",
                "website": "https://jestjs.io/",
                "features": [
                    "zero_config", "built_in_coverage", "mocking", "snapshot_testing",
                    "parallel_execution", "watch_mode", "typescript_support"
                ]
            }
        )

        self._capabilities = capabilities
        return capabilities

    def is_available(self) -> Tuple[bool, Optional[str]]:
        """Check if jest is available"""
        try:
            result = subprocess.run(
                ["npx", "jest", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Extract version
                version_match = re.search(r'(\d+\.\d+\.\d+)', result.stdout.strip())
                version = version_match.group(1) if version_match else None
                return True, version
            return False, None
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False, None

    def build_command(self, target: Union[str, Path], **kwargs) -> List[str]:
        """Build Jest command"""
        cmd = ["npx", "jest"]

        # Output format
        output_format = kwargs.get('output_format', 'json')
        if output_format == 'json':
            cmd.extend(['--json', '--outputFile', 'jest_results.json'])
        elif output_format == 'junit':
            cmd.extend(['--outputFile', 'jest_results.xml', '--testResultsProcessor', 'jest-junit'])

        # Coverage
        if kwargs.get('coverage', False):
            cmd.append('--coverage')
            coverage_dir = kwargs.get('coverage_dir')
            if coverage_dir:
                cmd.extend(['--coverageDirectory', str(coverage_dir)])

        # Test pattern
        test_pattern = kwargs.get('test_pattern')
        if test_pattern:
            cmd.extend(['--testNamePattern', test_pattern])

        # Test path pattern
        test_path_pattern = kwargs.get('test_path_pattern')
        if test_path_pattern:
            cmd.extend(['--testPathPattern', test_path_pattern])

        # Verbose output
        if kwargs.get('verbose', False):
            cmd.append('--verbose')

        # Silent mode
        if kwargs.get('silent', False):
            cmd.append('--silent')

        # Watch mode (usually not for CI/analysis)
        if kwargs.get('watch', False):
            cmd.append('--watch')

        # Max workers for parallel execution
        max_workers = kwargs.get('max_workers')
        if max_workers:
            cmd.extend(['--maxWorkers', str(max_workers)])

        # Bail on first failure
        if kwargs.get('bail', False):
            cmd.append('--bail')

        # Test timeout
        timeout = kwargs.get('timeout')
        if timeout:
            cmd.extend(['--testTimeout', str(timeout)])

        # Configuration file
        config_file = kwargs.get('config_file')
        if config_file:
            cmd.extend(['--config', str(config_file)])

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
        """Parse Jest output"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        # Combine stdout and stderr
        full_output = stdout + stderr
        result.raw_output = full_output

        try:
            # Try JSON format first
            json_file = Path('jest_results.json')
            if json_file.exists():
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
                return self._parse_json_output(json_data, exit_code)
            else:
                # Parse text output
                return self._parse_text_output(full_output, exit_code)

        except Exception as e:
            self.logger.error(f"Failed to parse Jest output: {e}")
            result.error_message = f"Failed to parse output: {str(e)}"
            return result

    def _parse_json_output(self, data: Dict[str, Any], exit_code: int) -> ToolResult:
        """Parse JSON output format"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        issues = []
        metrics = {}

        # Extract test results
        if 'testResults' in data:
            total_tests = 0
            passed_tests = 0
            failed_tests = 0

            for test_file in data['testResults']:
                for test_result in test_file.get('testResults', []):
                    total_tests += 1

                    if test_result.get('status') == 'passed':
                        passed_tests += 1
                    elif test_result.get('status') == 'failed':
                        failed_tests += 1

                        issue = ToolIssue(
                            file=test_file.get('name'),
                            severity=Severity.HIGH,
                            message=test_result.get('title', 'Test failed'),
                            category="test_failure",
                            metadata={
                                'test_name': test_result.get('fullName'),
                                'duration': test_result.get('duration'),
                                'failure_messages': test_result.get('failureMessages', [])
                            }
                        )
                        issues.append(issue)

            metrics.update({
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            })

        # Extract coverage if available
        if 'coverageMap' in data:
            metrics['coverage'] = True

        result.issues = issues
        result.metrics = metrics

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

        lines = output.strip().split('\n')

        # Extract summary information
        # Look for lines like "Tests: 5 passed, 2 failed, 1 skipped"
        test_summary_pattern = r'Tests?:\s*(\d+)\s*passed,\s*(\d+)\s*failed,\s*(\d+)\s*skipped'
        for line in lines:
            match = re.search(test_summary_pattern, line, re.IGNORECASE)
            if match:
                passed = int(match.group(1))
                failed = int(match.group(2))
                skipped = int(match.group(3))

                metrics.update({
                    'passed_tests': passed,
                    'failed_tests': failed,
                    'skipped_tests': skipped,
                    'total_tests': passed + failed + skipped
                })
                break

        # Extract failed test details
        in_failure = False
        current_test_file = None
        current_test_name = None

        for line in lines:
            if 'FAIL' in line and ('.js' in line or '.ts' in line):
                # Test file failure
                file_match = re.search(r'FAIL\s+(.+\.(?:js|ts|jsx|tsx))', line)
                if file_match:
                    current_test_file = file_match.group(1)
                    in_failure = True

            elif in_failure and line.strip().startswith('●'):
                # Individual test failure
                test_match = re.search(r'●\s+(.+)', line.strip())
                if test_match:
                    current_test_name = test_match.group(1)
                    # Look for error message in next lines
                    continue

            elif in_failure and current_test_name and ('Error:' in line or 'Expected:' in line):
                issue = ToolIssue(
                    file=current_test_file,
                    severity=Severity.HIGH,
                    message=f"{current_test_name}: {line.strip()}",
                    category="test_failure",
                    metadata={
                        'test_name': current_test_name,
                        'test_file': current_test_file
                    }
                )
                issues.append(issue)
                current_test_name = None

        result.issues = issues
        result.metrics = metrics

        return result