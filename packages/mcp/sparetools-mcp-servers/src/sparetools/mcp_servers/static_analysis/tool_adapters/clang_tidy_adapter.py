"""
Clang-Tidy Tool Adapter

Adapter for Clang-Tidy static analysis tool.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

from .base_adapter import BaseToolAdapter, ToolCapabilities, ToolResult, ToolIssue, ToolCategory, Severity


class ClangTidyAdapter(BaseToolAdapter):
    """Adapter for Clang-Tidy static analysis tool"""

    def __init__(self, executable: Optional[str] = None):
        super().__init__("clang-tidy", executable)

    @property
    def tool_category(self):
        return ToolCategory.STATIC_ANALYSIS

    def get_capabilities(self) -> ToolCapabilities:
        """Get Clang-Tidy capabilities"""
        if self._capabilities:
            return self._capabilities

        # Check if clang-tidy is available and get version
        available, version = self.is_available()

        capabilities = ToolCapabilities(
            name="clang-tidy",
            version=version,
            category=ToolCategory.STATIC_ANALYSIS,
            supported_platforms=["linux", "macos", "windows"],
            supported_languages=["c", "c++"],
            supported_file_types=[".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hxx"],
            can_analyze_directories=True,
            can_analyze_files=True,
            requires_compilation=True,  # Needs compile_commands.json
            supports_custom_rules=True,
            supports_parallel_execution=True,
            has_timeout_support=True,
            output_formats=["json", "text", "yaml"],
            metadata={
                "description": "Clang-based C++ static analysis tool",
                "website": "https://clang.llvm.org/extra/clang-tidy/",
                "requires_compile_commands": True,
                "categories": [
                    "performance", "modernize", "readability", "bugprone",
                    "cert", "cppcoreguidelines", "clang-analyzer", "misc"
                ]
            }
        )

        self._capabilities = capabilities
        return capabilities

    def is_available(self) -> Tuple[bool, Optional[str]]:
        """Check if clang-tidy is available"""
        try:
            result = subprocess.run(
                [self.executable, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Extract version from output
                version_match = re.search(r'version (\d+\.\d+\.\d+)', result.stdout)
                version = version_match.group(1) if version_match else None
                return True, version
            return False, None
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False, None

    def build_command(self, target: Union[str, Path], **kwargs) -> List[str]:
        """Build clang-tidy command"""
        cmd = [self.executable]

        # Compile commands database
        compile_commands = kwargs.get('compile_commands')
        if compile_commands:
            cmd.extend(['-p', str(compile_commands)])

        # Checks to run
        checks = kwargs.get('checks')
        if checks:
            if isinstance(checks, list):
                checks = ','.join(checks)
            cmd.extend(['-checks', checks])

        # Configuration file
        config_file = kwargs.get('config_file')
        if config_file:
            cmd.extend(['-config-file', str(config_file)])

        # Header filter
        header_filter = kwargs.get('header_filter')
        if header_filter:
            cmd.extend(['-header-filter', header_filter])

        # Fix issues
        if kwargs.get('fix', False):
            cmd.append('-fix')

        # Fix errors
        if kwargs.get('fix_errors', False):
            cmd.append('-fix-errors')

        # Export fixes
        export_fixes = kwargs.get('export_fixes')
        if export_fixes:
            cmd.extend(['-export-fixes', str(export_fixes)])

        # Output format
        output_format = kwargs.get('output_format', 'text')
        if output_format == 'json':
            cmd.append('-export-fixes=-')  # Output to stdout as JSON

        # Quiet mode
        if kwargs.get('quiet', False):
            cmd.append('-quiet')

        # Extra arguments
        extra_args = kwargs.get('extra_args')
        if extra_args:
            cmd.extend(['--'] + extra_args)

        # Target files
        if isinstance(target, (str, Path)):
            target = [target]

        for t in target:
            cmd.append(str(t))

        return cmd

    def parse_output(self, stdout: str, stderr: str, exit_code: int) -> ToolResult:
        """Parse clang-tidy output"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code in [0, 1],  # 1 means issues found, but successful execution
            exit_code=exit_code
        )

        # Combine stdout and stderr
        full_output = stdout + stderr
        result.raw_output = full_output

        try:
            # Try JSON format first (from -export-fixes)
            if full_output.strip().startswith('{'):
                return self._parse_json_output(full_output, exit_code)
            else:
                # Parse text output
                return self._parse_text_output(full_output, exit_code)

        except Exception as e:
            self.logger.error(f"Failed to parse clang-tidy output: {e}")
            result.error_message = f"Failed to parse output: {str(e)}"
            return result

    def _parse_json_output(self, output: str, exit_code: int) -> ToolResult:
        """Parse JSON output format"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code in [0, 1],
            exit_code=exit_code
        )

        try:
            data = json.loads(output)
            diagnostics = data.get('Diagnostics', [])

            issues = []
            for diag in diagnostics:
                issue = ToolIssue(
                    file=diag.get('FilePath'),
                    line=diag.get('FileOffset', {}).get('Line'),
                    column=diag.get('FileOffset', {}).get('Col'),
                    severity=self._map_severity(diag.get('Level', 'Remark')),
                    message=diag.get('Message', ''),
                    rule_id=diag.get('DiagnosticName'),
                    category=diag.get('Category', 'clang-tidy'),
                    context=diag.get('BuildDirectory'),
                    metadata={
                        'replacements': diag.get('Replacements', []),
                        'notes': diag.get('Notes', [])
                    }
                )
                issues.append(issue)

            result.issues = issues
            result.metrics = {
                'total_issues': len(issues),
                'fixes_applied': data.get('FixesApplied', 0),
                'notes': data.get('Notes', [])
            }

        except json.JSONDecodeError:
            self.logger.warning("Invalid JSON output, falling back to text parsing")
            return self._parse_text_output(output, exit_code)

        return result

    def _parse_text_output(self, output: str, exit_code: int) -> ToolResult:
        """Parse text output format"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code in [0, 1],
            exit_code=exit_code
        )

        issues = []

        # Parse text output lines
        lines = output.strip().split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # Match clang-tidy diagnostic pattern
            # file:line:column: severity: message [rule-id]
            match = re.match(r'^([^:]+):(\d+):(\d+):\s*(\w+):\s*(.+?)(?:\s*\[([^\]]+)\])?$', line)
            if match:
                file_path, line_num, col_num, severity_str, message, rule_id = match.groups()

                # Read additional lines for multi-line messages
                full_message = message
                j = i + 1
                while j < len(lines) and not re.match(r'^[^:]+:\d+:\d+:', lines[j]):
                    if lines[j].strip():
                        full_message += ' ' + lines[j].strip()
                    j += 1

                severity_enum = self._map_severity(severity_str)

                issue = ToolIssue(
                    file=file_path,
                    line=int(line_num),
                    column=int(col_num),
                    severity=severity_enum,
                    message=full_message.strip(),
                    rule_id=rule_id,
                    category=severity_str.lower()
                )
                issues.append(issue)

                i = j
            else:
                i += 1

        result.issues = issues
        result.metrics = {
            'total_issues': len(issues),
        }

        return result

    def _map_severity(self, severity_str: str) -> Severity:
        """Map clang-tidy severity to standardized severity"""
        severity_map = {
            'error': Severity.HIGH,
            'warning': Severity.MEDIUM,
            'remark': Severity.LOW,
            'note': Severity.INFO,
            'fatal': Severity.CRITICAL,
        }
        return severity_map.get(severity_str.lower(), Severity.INFO)