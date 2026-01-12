"""
Strace Tool Adapter

Adapter for strace system call tracer.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from collections import Counter

from .base_adapter import BaseToolAdapter, ToolCapabilities, ToolResult, ToolIssue, ToolCategory, Severity


class StraceAdapter(BaseToolAdapter):
    """Adapter for strace system call tracer"""

    def __init__(self, executable: Optional[str] = None):
        super().__init__("strace", executable)

    @property
    def tool_category(self):
        return ToolCategory.PROFILING

    def get_capabilities(self) -> ToolCapabilities:
        """Get strace capabilities"""
        if self._capabilities:
            return self._capabilities

        # Check if strace is available and get version
        available, version = self.is_available()

        capabilities = ToolCapabilities(
            name="strace",
            version=version,
            category=ToolCategory.PROFILING,
            supported_platforms=["linux"],  # Linux only
            supported_languages=[],  # Language agnostic
            supported_file_types=[],  # Any executable
            can_analyze_directories=False,
            can_analyze_files=True,
            requires_compilation=True,
            supports_custom_rules=False,
            supports_parallel_execution=False,
            has_timeout_support=True,
            output_formats=["text"],
            metadata={
                "description": "System call tracer for Linux",
                "website": "https://strace.io/",
                "features": [
                    "syscall_tracing", "signal_tracing", "network_tracing",
                    "file_access_tracing", "process_tracing"
                ]
            }
        )

        self._capabilities = capabilities
        return capabilities

    def is_available(self) -> Tuple[bool, Optional[str]]:
        """Check if strace is available"""
        try:
            result = subprocess.run(
                [self.executable, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Extract version from output like "strace -- version 5.16"
                version_match = re.search(r'version ([\d.]+)', result.stdout)
                version = version_match.group(1) if version_match else None
                return True, version
            return False, None
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False, None

    def build_command(self, target: Union[str, Path], **kwargs) -> List[str]:
        """Build strace command"""
        cmd = [self.executable]

        # Follow forks
        if kwargs.get('follow_forks', True):
            cmd.append('-f')

        # Trace specific syscalls
        trace = kwargs.get('trace')
        if trace:
            if isinstance(trace, list):
                trace = ','.join(trace)
            cmd.extend(['-e', f'trace={trace}'])

        # Trace signals
        if kwargs.get('trace_signals', False):
            cmd.append('-e')
            cmd.append('signal=all')

        # Trace network operations
        if kwargs.get('trace_network', False):
            cmd.extend(['-e', 'trace=network'])

        # Trace file operations
        if kwargs.get('trace_files', False):
            cmd.extend(['-e', 'trace=file'])

        # Output file
        output_file = kwargs.get('output_file', 'strace_output.txt')
        cmd.extend(['-o', output_file])

        # Time stamps
        if kwargs.get('timestamps', False):
            cmd.append('-t')

        # Relative time stamps
        if kwargs.get('relative_timestamps', False):
            cmd.append('-r')

        # Summary statistics
        if kwargs.get('summary', False):
            cmd.append('-c')

        # Verbose output
        if kwargs.get('verbose', False):
            cmd.append('-v')

        # Target command
        if isinstance(target, str):
            # If target is a command string, split it
            import shlex
            cmd.extend(shlex.split(target))
        else:
            cmd.append(str(target))

        return cmd

    def parse_output(self, stdout: str, stderr: str, exit_code: int) -> ToolResult:
        """Parse strace output"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        # Combine stdout and stderr
        full_output = stdout + stderr
        result.raw_output = full_output

        try:
            # Try to read from output file first
            output_file = self._extract_output_file_from_command(full_output)
            if output_file and Path(output_file).exists():
                with open(output_file, 'r') as f:
                    trace_content = f.read()
                return self._parse_trace_content(trace_content, exit_code)
            else:
                # Parse from stderr/stdout (less common)
                return self._parse_trace_content(full_output, exit_code)

        except Exception as e:
            self.logger.error(f"Failed to parse strace output: {e}")
            result.error_message = f"Failed to parse output: {str(e)}"
            return result

    def _extract_output_file_from_command(self, output: str) -> Optional[str]:
        """Extract output file path from command"""
        match = re.search(r'-o\s+([^\s]+)', output)
        return match.group(1) if match else None

    def _parse_trace_content(self, content: str, exit_code: int) -> ToolResult:
        """Parse strace trace content"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        issues = []
        metrics = {}

        # Check if this is a summary output (-c flag)
        if 'syscall' in content and 'calls' in content:
            return self._parse_summary_output(content, exit_code)

        # Parse individual syscall traces
        lines = content.strip().split('\n')
        syscalls = []
        errors = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Extract syscall name
            syscall_match = re.match(r'(\w+)\(', line)
            if syscall_match:
                syscall = syscall_match.group(1)
                syscalls.append(syscall)

                # Check for errors (= -1 ENOENT, etc.)
                if '= -1' in line:
                    error_match = re.search(r'= -1 (\w+)', line)
                    if error_match:
                        error_code = error_match.group(1)
                        error_msg = f"Syscall {syscall} failed with {error_code}"

                        issue = ToolIssue(
                            severity=Severity.MEDIUM,
                            message=error_msg,
                            category="syscall_error",
                            metadata={
                                'syscall': syscall,
                                'error_code': error_code,
                                'line': line
                            }
                        )
                        issues.append(issue)
                        errors.append(line)

        # Calculate syscall statistics
        syscall_counts = Counter(syscalls)
        total_syscalls = len(syscalls)
        unique_syscalls = len(syscall_counts)

        metrics.update({
            'total_syscalls': total_syscalls,
            'unique_syscalls': unique_syscalls,
            'syscall_counts': dict(syscall_counts.most_common(20)),  # Top 20
            'errors': len(errors)
        })

        # Add issues for common problematic patterns
        if any('mmap' in syscall for syscall in syscalls) and any('= -1' in line for line in lines):
            issue = ToolIssue(
                severity=Severity.MEDIUM,
                message="Memory mapping failures detected",
                category="memory_issue"
            )
            issues.append(issue)

        result.issues = issues
        result.metrics = metrics

        return result

    def _parse_summary_output(self, content: str, exit_code: int) -> ToolResult:
        """Parse strace summary output (-c flag)"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        metrics = {}

        # Parse summary table
        lines = content.strip().split('\n')
        in_table = False
        syscall_stats = {}

        for line in lines:
            if line.startswith('% time') or line.startswith('syscall'):
                in_table = True
                continue
            elif in_table and line.strip() and not line.startswith('-'):
                # Parse syscall statistics line
                parts = re.split(r'\s+', line.strip())
                if len(parts) >= 6:
                    syscall = parts[0]
                    calls = parts[1]
                    total_time = parts[2]
                    try:
                        syscall_stats[syscall] = {
                            'calls': int(calls),
                            'total_time': float(total_time)
                        }
                    except ValueError:
                        pass
            elif line.startswith('---'):
                break

        metrics['syscall_statistics'] = syscall_stats
        result.metrics = metrics

        return result