"""
Cppcheck Tool Adapter

Adapter for Cppcheck static analysis tool.
"""

import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

from .base_adapter import BaseToolAdapter, ToolCapabilities, ToolResult, ToolIssue, ToolCategory, Severity


class CppcheckAdapter(BaseToolAdapter):
    """Adapter for Cppcheck static analysis tool"""

    def __init__(self, executable: Optional[str] = None):
        super().__init__("cppcheck", executable)

    @property
    def tool_category(self):
        return ToolCategory.STATIC_ANALYSIS

    def get_capabilities(self) -> ToolCapabilities:
        """Get Cppcheck capabilities"""
        if self._capabilities:
            return self._capabilities

        # Check if cppcheck is available and get version
        available, version = self.is_available()

        capabilities = ToolCapabilities(
            name="cppcheck",
            version=version,
            category=ToolCategory.STATIC_ANALYSIS,
            supported_platforms=["linux", "macos", "windows"],
            supported_languages=["c", "c++"],
            supported_file_types=[".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx"],
            can_analyze_directories=True,
            can_analyze_files=True,
            requires_compilation=False,
            supports_custom_rules=False,
            supports_parallel_execution=True,
            has_timeout_support=True,
            output_formats=["xml", "text", "html"],
            metadata={
                "description": "Static analysis tool for C/C++ code",
                "website": "https://cppcheck.sourceforge.io/",
                "checks": [
                    "memory", "resource", "nullpointer", "arrayIndexOutOfBounds",
                    "divisionByZero", "uninitializedVariable", "unusedVariable",
                    "stl", "exceptionSafety", "deprecatedFunctions"
                ]
            }
        )

        self._capabilities = capabilities
        return capabilities

    def is_available(self) -> Tuple[bool, Optional[str]]:
        """Check if cppcheck is available"""
        try:
            result = subprocess.run(
                [self.executable, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Extract version from output like "Cppcheck 2.10"
                version_match = re.search(r'Cppcheck (\d+\.\d+)', result.stdout.strip())
                version = version_match.group(1) if version_match else None
                return True, version
            return False, None
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False, None

    def build_command(self, target: Union[str, Path], **kwargs) -> List[str]:
        """Build cppcheck command"""
        cmd = [self.executable]

        # Enable checks
        enable_checks = kwargs.get('enable_checks', ['all'])
        if enable_checks:
            cmd.extend(['--enable=' + ','.join(enable_checks)])

        # Output format
        output_format = kwargs.get('output_format', 'xml')
        if output_format == 'xml':
            cmd.extend(['--xml', '--xml-version=2'])
        elif output_format == 'html':
            cmd.append('--html')

        # Include paths
        include_paths = kwargs.get('include_paths', [])
        for path in include_paths:
            cmd.extend(['-I', str(path)])

        # Define macros
        defines = kwargs.get('defines', [])
        for define in defines:
            cmd.extend(['-D', define])

        # Platform
        platform = kwargs.get('platform')
        if platform:
            cmd.extend(['--platform', platform])

        # Standards
        std = kwargs.get('std')
        if std:
            cmd.extend(['--std', std])

        # Suppress rules
        suppress_rules = kwargs.get('suppress_rules', [])
        for rule in suppress_rules:
            cmd.extend(['--suppress', rule])

        # Other options
        if kwargs.get('verbose', False):
            cmd.append('--verbose')
        if kwargs.get('quiet', False):
            cmd.append('--quiet')
        if kwargs.get('force', False):
            cmd.append('--force')

        # Max complexity
        max_complexity = kwargs.get('max_complexity')
        if max_complexity:
            cmd.extend(['--max-complexity', str(max_complexity)])

        # Inline suppressions
        if kwargs.get('inline_suppr', True):
            cmd.append('--inline-suppr')

        # Target
        cmd.append(str(target))

        return cmd

    def parse_output(self, stdout: str, stderr: str, exit_code: int) -> ToolResult:
        """Parse cppcheck output"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        # Combine stdout and stderr for parsing
        full_output = stdout + stderr
        result.raw_output = full_output

        try:
            # Try to parse XML output first
            if '<results' in full_output:
                return self._parse_xml_output(full_output, exit_code)
            else:
                # Parse text output
                return self._parse_text_output(full_output, exit_code)

        except Exception as e:
            self.logger.error(f"Failed to parse cppcheck output: {e}")
            result.error_message = f"Failed to parse output: {str(e)}"
            return result

    def _parse_xml_output(self, output: str, exit_code: int) -> ToolResult:
        """Parse XML output format"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        try:
            # Find XML content
            xml_start = output.find('<results')
            if xml_start == -1:
                return self._parse_text_output(output, exit_code)

            xml_content = output[xml_start:]
            root = ET.fromstring(xml_content)

            issues = []
            error_count = 0
            warning_count = 0
            style_count = 0
            performance_count = 0
            portability_count = 0
            information_count = 0

            for error_elem in root.findall('.//error'):
                severity = error_elem.get('severity', 'unknown')
                msg = error_elem.get('msg', '')
                file_path = error_elem.get('file', '')
                line = error_elem.get('line')
                column = error_elem.get('column')
                rule_id = error_elem.get('id')

                # Convert severity
                severity_enum = self._map_severity(severity)

                issue = ToolIssue(
                    file=file_path if file_path else None,
                    line=int(line) if line else None,
                    column=int(column) if column else None,
                    severity=severity_enum,
                    message=msg,
                    rule_id=rule_id,
                    category=severity
                )

                issues.append(issue)

                # Count by severity
                if severity == 'error':
                    error_count += 1
                elif severity == 'warning':
                    warning_count += 1
                elif severity == 'style':
                    style_count += 1
                elif severity == 'performance':
                    performance_count += 1
                elif severity == 'portability':
                    portability_count += 1
                elif severity == 'information':
                    information_count += 1

            result.issues = issues
            result.metrics = {
                'total_issues': len(issues),
                'errors': error_count,
                'warnings': warning_count,
                'style': style_count,
                'performance': performance_count,
                'portability': portability_count,
                'information': information_count,
            }

        except ET.ParseError as e:
            self.logger.warning(f"XML parsing failed, falling back to text parsing: {e}")
            return self._parse_text_output(output, exit_code)

        return result

    def _parse_text_output(self, output: str, exit_code: int) -> ToolResult:
        """Parse text output format"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        issues = []

        # Parse text output lines
        lines = output.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Match pattern: file:line:column: severity: message [rule_id]
            match = re.match(r'^([^:]+):(\d+):(\d+):\s*(\w+):\s*(.+?)(?:\s*\[([^\]]+)\])?$', line)
            if match:
                file_path, line_num, col_num, severity_str, message, rule_id = match.groups()

                severity_enum = self._map_severity(severity_str.lower())

                issue = ToolIssue(
                    file=file_path,
                    line=int(line_num),
                    column=int(col_num),
                    severity=severity_enum,
                    message=message.strip(),
                    rule_id=rule_id,
                    category=severity_str.lower()
                )
                issues.append(issue)

        result.issues = issues
        result.metrics = {
            'total_issues': len(issues),
        }

        return result

    def _map_severity(self, severity_str: str) -> Severity:
        """Map cppcheck severity to standardized severity"""
        severity_map = {
            'error': Severity.HIGH,
            'warning': Severity.MEDIUM,
            'style': Severity.LOW,
            'performance': Severity.MEDIUM,
            'portability': Severity.LOW,
            'information': Severity.INFO,
            'debug': Severity.INFO,
        }
        return severity_map.get(severity_str.lower(), Severity.INFO)