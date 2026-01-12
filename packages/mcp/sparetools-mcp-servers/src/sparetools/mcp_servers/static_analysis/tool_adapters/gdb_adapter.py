"""
GDB Tool Adapter

Adapter for GNU Debugger (GDB) debugging tool.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

from .base_adapter import BaseToolAdapter, ToolCapabilities, ToolResult, ToolIssue, ToolCategory, Severity


class GdbAdapter(BaseToolAdapter):
    """Adapter for GDB debugging tool"""

    def __init__(self, executable: Optional[str] = None):
        super().__init__("gdb", executable)

    @property
    def tool_category(self):
        return ToolCategory.DEBUGGING

    def get_capabilities(self) -> ToolCapabilities:
        """Get GDB capabilities"""
        if self._capabilities:
            return self._capabilities

        # Check if gdb is available and get version
        available, version = self.is_available()

        capabilities = ToolCapabilities(
            name="gdb",
            version=version,
            category=ToolCategory.DEBUGGING,
            supported_platforms=["linux", "macos", "windows"],
            supported_languages=["c", "c++", "fortran", "ada"],
            supported_file_types=[".exe", ".out", ""],  # Executables
            can_analyze_directories=False,
            can_analyze_files=True,
            requires_compilation=True,
            supports_custom_rules=False,
            supports_parallel_execution=False,
            has_timeout_support=True,
            output_formats=["text"],
            metadata={
                "description": "GNU Debugger for debugging programs",
                "website": "https://www.gnu.org/software/gdb/",
                "features": [
                    "breakpoint_setting", "watchpoints", "backtrace",
                    "memory_inspection", "register_inspection", "core_dump_analysis"
                ]
            }
        )

        self._capabilities = capabilities
        return capabilities

    def is_available(self) -> Tuple[bool, Optional[str]]:
        """Check if gdb is available"""
        try:
            result = subprocess.run(
                [self.executable, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Extract version from first line
                first_line = result.stdout.strip().split('\n')[0]
                version_match = re.search(r'(\d+\.\d+)', first_line)
                version = version_match.group(1) if version_match else None
                return True, version
            return False, None
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False, None

    def build_command(self, target: Union[str, Path], **kwargs) -> List[str]:
        """Build gdb command"""
        cmd = [self.executable]

        # Batch mode
        cmd.append('--batch')

        # Commands to execute
        commands = kwargs.get('commands', ['run', 'bt', 'info registers', 'quit'])

        # Create temporary command file
        command_file = kwargs.get('command_file')
        if command_file:
            cmd.extend(['-x', str(command_file)])
        elif commands:
            # Write commands to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.gdb', delete=False) as f:
                for command in commands:
                    f.write(command + '\n')
                temp_file = f.name
            cmd.extend(['-x', temp_file])
            # Note: cleanup should be handled by caller

        # Core file for post-mortem debugging
        core_file = kwargs.get('core_file')
        if core_file:
            cmd.extend(['-c', str(core_file)])

        # PID for attaching to running process
        pid = kwargs.get('pid')
        if pid:
            cmd.extend(['-p', str(pid)])

        # Target executable
        cmd.append(str(target))

        return cmd

    def parse_output(self, stdout: str, stderr: str, exit_code: int) -> ToolResult:
        """Parse gdb output"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        # Combine stdout and stderr
        full_output = stdout + stderr
        result.raw_output = full_output

        try:
            return self._parse_gdb_output(full_output, exit_code)
        except Exception as e:
            self.logger.error(f"Failed to parse gdb output: {e}")
            result.error_message = f"Failed to parse output: {str(e)}"
            return result

    def _parse_gdb_output(self, output: str, exit_code: int) -> ToolResult:
        """Parse GDB output"""
        result = ToolResult(
            tool_name=self.name,
            success=exit_code == 0,
            exit_code=exit_code
        )

        issues = []
        metrics = {}

        # Extract signal information (program crashes)
        signal_match = re.search(r'Program received signal (\w+)', output)
        if signal_match:
            signal = signal_match.group(1)
            metrics['signal'] = signal

            issue = ToolIssue(
                severity=Severity.CRITICAL,
                message=f"Program received signal: {signal}",
                category="crash",
                metadata={'signal': signal}
            )
            issues.append(issue)

        # Extract backtrace
        bt_start = output.find('#0')
        if bt_start != -1:
            bt_end = output.find('\n\n', bt_start)
            if bt_end == -1:
                bt_end = len(output)
            backtrace = output[bt_start:bt_end].strip()
            metrics['backtrace'] = backtrace

            # Count stack frames
            frame_count = len(re.findall(r'#\d+', backtrace))
            metrics['stack_frames'] = frame_count

        # Extract register information
        reg_match = re.search(r'rax\s+(.+?)\n', output, re.MULTILINE)
        if reg_match:
            metrics['registers'] = True  # Indicate registers were captured

        # Look for specific error patterns
        if 'Segmentation fault' in output:
            issue = ToolIssue(
                severity=Severity.CRITICAL,
                message="Segmentation fault detected",
                category="memory_error"
            )
            issues.append(issue)

        result.issues = issues
        result.metrics = metrics

        return result