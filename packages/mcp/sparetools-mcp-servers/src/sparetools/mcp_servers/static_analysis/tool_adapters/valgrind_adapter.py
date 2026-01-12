"""
Valgrind Tool Adapter

Adapter for Valgrind memory analysis and profiling tool.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

from .base_adapter import BaseToolAdapter, ToolCapabilities, ToolResult, ToolIssue, ToolCategory, Severity


class ValgrindAdapter(BaseToolAdapter):
    """Adapter for Valgrind memory analysis tool"""

    def __init__(self, executable: Optional[str] = None):
        super().__init__("valgrind", executable)

    @property
    def tool_category(self):
        return ToolCategory.DYNAMIC_ANALYSIS

    def get_capabilities(self) -> ToolCapabilities:
        """Get Valgrind capabilities"""
        if self._capabilities:
            return self._capabilities

        # Check if valgrind is available and get version
        available, version = self.is_available()

        capabilities = ToolCapabilities(
            name="valgrind",
            version=version,
            category=ToolCategory.DYNAMIC_ANALYSIS,
            supported_platforms=["linux", "macos", "windows"],  # Limited Windows support
            supported_languages=["c", "c++"],
            supported_file_types=[".exe", ".out", ""],  # Executables
            can_analyze_directories=False,
            can_analyze_files=True,
            requires_compilation=True,
            supports_custom_rules=False,
            supports_parallel_execution=False,  # Typically run one at a time
            has_timeout_support=True,
            output_formats=["text", "xml"],
            metadata={
                "description": "Memory debugging and profiling tool",
                "website": "https://valgrind.org/",
                "tools": [
                    "memcheck", "cachegrind", "callgrind", "helgrind",
                    "drd", "massif", "dhat", "lackey", "none"
                ]
            }
        )

        self._capabilities = capabilities
        return capabilities

    def is_available(self) -> Tuple[bool, Optional[str]]:
        """Check if valgrind is available"""
        try:
            result = subprocess.run(
                [self.executable, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Extract version from output like "valgrind-3.19.0"
                version_match = re.search(r'valgrind-(\d+\.\d+\.\d+)', result.stdout.strip())
                version = version_match.group(1) if version_match else None
                return True, version
            return False, None
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False, None

    def build_command(self, target: Union[str, Path], **kwargs) -> List[str]:
        """Build valgrind command"""
        cmd = [self.executable]

        # Tool selection
        tool = kwargs.get('tool', 'memcheck')
        cmd.append(f'--tool={tool}')

        # Memory checking options (memcheck)
        if tool == 'memcheck':
            if kwargs.get('leak_check', True):
                cmd.append('--leak-check=full')
                cmd.append('--show-leak-kinds=all')
                cmd.append('--track-origins=yes')

            if kwargs.get('expensive_definedness_checks'):
                cmd.append('--expensive-definedness-checks=yes')

            if kwargs.get('track_fds', True):
                cmd.append('--track-fds=yes')

        # Cache profiling options (cachegrind)
        elif tool == 'cachegrind':
            cachegrind_out_file = kwargs.get('cachegrind_out_file')
            if cachegrind_out_file:
                cmd.append(f'--cachegrind-out-file={cachegrind_out_file}')

        # Call graph options (callgrind)
        elif tool == 'callgrind':
            callgrind_out_file = kwargs.get('callgrind_out_file')
            if callgrind_out_file:
                cmd.append(f'--callgrind-out-file={callgrind_out_file}')

            if kwargs.get('collect_bus_events'):
                cmd.append('--collect-bus=yes')

        # Output format
        output_format = kwargs.get('output_format', 'text')
        if output_format == 'xml':
            cmd.append('--xml=yes')
            xml_output = kwargs.get('xml_output', 'valgrind-output.xml')
            cmd.append(f'--xml-file={xml_output}')

        # Log file
        log_file = kwargs.get('log_file')
        if log_file:
            cmd.append(f'--log-file={log_file}')
        else:
            # Default log to file to avoid mixing with program output
            cmd.append('--log-file=valgrind.log')

        # Verbosity
        verbosity = kwargs.get('verbosity', 1)
        cmd.append(f'-v')  # Default verbosity

        # Other options
        if kwargs.get('trace_children', True):
            cmd.append('--trace-children=yes')

        # Target executable
        cmd.append(str(target))

        # Program arguments
        program_args = kwargs.get('args', [])
        if program_args:
            cmd.extend(program_args)

        return cmd

    def parse_output(self, stdout: str, stderr: str, exit_code: int) -> ToolResult:
        """Parse valgrind output"""
        result = ToolResult(
            tool_name=self.name,
            success=True,  # Valgrind usually succeeds even when finding issues
            exit_code=exit_code
        )

        # Valgrind outputs to log file, so combine stdout and stderr
        full_output = stdout + stderr
        result.raw_output = full_output

        try:
            # Try to read from log file if it exists
            log_file = self._extract_log_file_from_command(full_output)
            if log_file and Path(log_file).exists():
                with open(log_file, 'r') as f:
                    log_content = f.read()
                return self._parse_log_content(log_content, exit_code)
            else:
                # Parse from combined output
                return self._parse_log_content(full_output, exit_code)

        except Exception as e:
            self.logger.error(f"Failed to parse valgrind output: {e}")
            result.error_message = f"Failed to parse output: {str(e)}"
            return result

    def _extract_log_file_from_command(self, output: str) -> Optional[str]:
        """Extract log file path from command output"""
        # Look for log file in the output
        match = re.search(r'--log-file=([^\s]+)', output)
        return match.group(1) if match else None

    def _parse_log_content(self, content: str, exit_code: int) -> ToolResult:
        """Parse valgrind log content"""
        result = ToolResult(
            tool_name=self.name,
            success=True,
            exit_code=exit_code
        )

        issues = []
        metrics = {}

        # Extract tool used
        tool_match = re.search(r'==\d+== (Memcheck|Cachegrind|Callgrind|Helgrind|DRD),', content)
        tool_used = tool_match.group(1).lower() if tool_match else 'memcheck'

        # Parse based on tool
        if tool_used == 'memcheck':
            issues, metrics = self._parse_memcheck_output(content)
        elif tool_used == 'cachegrind':
            issues, metrics = self._parse_cachegrind_output(content)
        elif tool_used == 'callgrind':
            issues, metrics = self._parse_callgrind_output(content)
        else:
            # Generic parsing for other tools
            issues, metrics = self._parse_generic_output(content)

        result.issues = issues
        result.metrics = metrics

        return result

    def _parse_memcheck_output(self, content: str) -> Tuple[List[ToolIssue], Dict[str, Any]]:
        """Parse memcheck output"""
        issues = []
        metrics = {}

        # Extract memory leak summary
        leak_summary_match = re.search(
            r'==\d+==\s+HEAP SUMMARY:\s+==\d+==\s+in use at exit: ([^\n]+)\s+==\d+==\s+total heap usage: ([^\n]+)',
            content,
            re.MULTILINE | re.DOTALL
        )

        if leak_summary_match:
            in_use = leak_summary_match.group(1)
            total_usage = leak_summary_match.group(2)
            metrics['heap_in_use_at_exit'] = in_use
            metrics['total_heap_usage'] = total_usage

        # Extract definitely lost bytes
        definitely_lost_match = re.search(r'==\d+==\s+definitely lost: ([^\n]+)', content)
        if definitely_lost_match:
            metrics['definitely_lost'] = definitely_lost_match.group(1)

        # Extract indirectly lost bytes
        indirectly_lost_match = re.search(r'==\d+==\s+indirectly lost: ([^\n]+)', content)
        if indirectly_lost_match:
            metrics['indirectly_lost'] = indirectly_lost_match.group(1)

        # Extract possibly lost bytes
        possibly_lost_match = re.search(r'==\d+==\s+possibly lost: ([^\n]+)', content)
        if possibly_lost_match:
            metrics['possibly_lost'] = possibly_lost_match.group(1)

        # Extract still reachable bytes
        still_reachable_match = re.search(r'==\d+==\s+still reachable: ([^\n]+)', content)
        if still_reachable_match:
            metrics['still_reachable'] = still_reachable_match.group(1)

        # Extract error summary
        error_summary_match = re.search(r'==\d+==\s+ERROR SUMMARY: (\d+) errors', content)
        if error_summary_match:
            error_count = int(error_summary_match.group(1))
            metrics['total_errors'] = error_count

            if error_count > 0:
                # Create issue for each error
                # This is a simplified parsing - real implementation would need more sophisticated parsing
                issue = ToolIssue(
                    severity=Severity.HIGH,
                    message=f"Valgrind detected {error_count} memory errors",
                    category="memory_error",
                    metadata={'error_count': error_count}
                )
                issues.append(issue)

        return issues, metrics

    def _parse_cachegrind_output(self, content: str) -> Tuple[List[ToolIssue], Dict[str, Any]]:
        """Parse cachegrind output"""
        issues = []
        metrics = {}

        # Extract cache statistics
        # This is a simplified implementation
        metrics['tool'] = 'cachegrind'
        metrics['note'] = 'Cache profiling completed'

        return issues, metrics

    def _parse_callgrind_output(self, content: str) -> Tuple[List[ToolIssue], Dict[str, Any]]:
        """Parse callgrind output"""
        issues = []
        metrics = {}

        # Extract call graph statistics
        # This is a simplified implementation
        metrics['tool'] = 'callgrind'
        metrics['note'] = 'Call graph profiling completed'

        return issues, metrics

    def _parse_generic_output(self, content: str) -> Tuple[List[ToolIssue], Dict[str, Any]]:
        """Parse generic valgrind output"""
        issues = []
        metrics = {'tool': 'unknown'}

        # Look for any ERROR or WARNING patterns
        error_pattern = r'==\d+==\s+(ERROR|WARNING): (.+)'
        for match in re.finditer(error_pattern, content):
            level, message = match.groups()
            severity = Severity.HIGH if level == 'ERROR' else Severity.MEDIUM

            issue = ToolIssue(
                severity=severity,
                message=message.strip(),
                category=level.lower()
            )
            issues.append(issue)

        return issues, metrics