"""
Process Management Core Module

Provides comprehensive process management utilities including:
- Command execution with proper error handling
- Output capture and logging
- Timeout support
- Cross-platform compatibility
- Silent execution options
"""

import logging
import os
import subprocess
from typing import Optional, Tuple, List, Union, Dict, Any

log = logging.getLogger(__name__)


# ============================================================================
# Command Execution Utilities
# ============================================================================

def remove_console_color_codes(string: str, strip_end: bool = False) -> str:
    """
    Remove ANSI color codes from console output.

    Args:
        string: Input string potentially containing ANSI codes
        strip_end: Whether to strip trailing whitespace

    Returns:
        String with ANSI codes removed
    """
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\\\-_]|\\[[0-?]*[ -/]*[@-~])')
    string = ansi_escape.sub('', string)
    if strip_end:
        return string.rstrip()
    else:
        return string


def execute_command(command: Union[str, List[str]],
                   custom_env: Optional[Dict[str, str]] = None,
                   print_command: bool = True,
                   print_env: bool = False,
                   print_out: bool = True,
                   print_error: bool = True,
                   print_err_code: bool = True,
                   combine_stdout_and_stderr: bool = True,
                   wait_till_finish: bool = True,
                   continuous_print: bool = False,
                   **kwargs) -> Tuple[int, List[str]]:
    """
    Execute a system command with comprehensive output handling.

    This is the core command execution utility providing:
    - Flexible command input (string or list)
    - Custom environment support
    - Comprehensive output control
    - Cross-platform compatibility
    - Proper error handling

    Args:
        command: Command to execute (string or list)
        custom_env: Custom environment variables to merge with current env
        print_command: Whether to print the command being executed
        print_env: Whether to print environment variables
        print_out: Whether to print stdout
        print_error: Whether to print stderr
        print_err_code: Whether to print exit code
        combine_stdout_and_stderr: Combine stdout and stderr into single stream
        wait_till_finish: Wait for command completion before returning
        continuous_print: Print output continuously during execution
        **kwargs: Additional subprocess arguments (cwd, timeout, etc.)

    Returns:
        Tuple of (return_code, output_lines)

    Example:
        >>> # Execute with full output
        >>> code, output = execute_command(["ls", "-la"])
        >>> print(f"Exit code: {code}")
        >>> for line in output:
        ...     print(line)

        >>> # Execute silently
        >>> code, _ = execute_command("mkdir test", print_command=False, print_out=False)
    """

    if print_command:
        log.info(f'Executing command: {command}')

    if print_env and custom_env:
        log.debug(f'Environment: {custom_env}')

    # Prepare environment
    env = custom_env or os.environ.copy()
    kwargs['env'] = env

    # Set up stdout/stderr handling
    if combine_stdout_and_stderr:
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.STDOUT
    else:
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE

    # Execute command
    try:
        if isinstance(command, str):
            # Use shell=True for string commands to support shell features
            kwargs['shell'] = True
            process = subprocess.Popen(command, **kwargs)
        else:
            # List commands
            process = subprocess.Popen(command, **kwargs)

        if wait_till_finish:
            output, error = process.communicate()

            # Handle output
            if combine_stdout_and_stderr:
                output_lines = output.decode('utf-8', errors='replace').splitlines() if output else []
                error_lines = []
            else:
                output_lines = output.decode('utf-8', errors='replace').splitlines() if output else []
                error_lines = error.decode('utf-8', errors='replace').splitlines() if error else []

            # Print output if requested
            if print_out and output_lines:
                for line in output_lines:
                    log.info(f'OUT: {line}')

            if print_error and error_lines:
                for line in error_lines:
                    log.error(f'ERR: {line}')

            if print_err_code:
                if process.returncode == 0:
                    log.debug(f'Command completed successfully (exit code: {process.returncode})')
                else:
                    log.warning(f'Command failed (exit code: {process.returncode})')

            return process.returncode, output_lines
        else:
            # Don't wait for completion - return immediately
            return 0, []

    except Exception as e:
        log.error(f'Failed to execute command {command}: {e}')
        return -1, [str(e)]


def run_command_with_timeout(command: Union[str, List[str]],
                           timeout: int = 30,
                           **kwargs) -> Tuple[int, List[str]]:
    """
    Execute a command with a timeout to prevent hanging processes.

    Args:
        command: Command to execute
        timeout: Timeout in seconds
        **kwargs: Additional arguments passed to execute_command

    Returns:
        Tuple of (return_code, output_lines)
        Return code -2 indicates timeout occurred

    Example:
        >>> code, output = run_command_with_timeout(["sleep", "10"], timeout=5)
        >>> if code == -2:
        ...     print("Command timed out")
    """
    import threading

    result = {'returncode': -1, 'output': []}

    def target():
        result['returncode'], result['output'] = execute_command(command, **kwargs)

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        log.warning(f'Command timed out after {timeout} seconds: {command}')
        # Note: Can't easily kill subprocess from thread, so just return timeout indication
        return -2, [f'Command timed out after {timeout} seconds']

    return result['returncode'], result['output']


def execute_command_silently(command: Union[str, List[str]], **kwargs) -> Tuple[int, List[str]]:
    """
    Execute a command with all output suppressed.

    Useful for background operations or when you only care about the exit code.

    Args:
        command: Command to execute
        **kwargs: Additional arguments passed to execute_command

    Returns:
        Tuple of (return_code, output_lines) - but output_lines will be empty due to silencing

    Example:
        >>> code, _ = execute_command_silently("mkdir -p /tmp/test")
        >>> if code == 0:
        ...     print("Directory created successfully")
    """
    kwargs.update({
        'print_command': False,
        'print_out': False,
        'print_error': False,
        'print_err_code': False
    })
    return execute_command(command, **kwargs)


# ============================================================================
# Process Management Utilities
# ============================================================================

def run_command_async(command: Union[str, List[str]],
                     custom_env: Optional[Dict[str, str]] = None,
                     **kwargs) -> subprocess.Popen:
    """
    Run a command asynchronously without waiting for completion.

    Args:
        command: Command to execute
        custom_env: Custom environment variables
        **kwargs: Additional subprocess arguments

    Returns:
        Popen object representing the running process

    Example:
        >>> process = run_command_async(["python", "long_running_script.py"])
        >>> # Do other work...
        >>> process.wait()  # Wait for completion when ready
    """
    env = custom_env or os.environ.copy()
    kwargs['env'] = env

    if isinstance(command, str):
        kwargs['shell'] = True
        process = subprocess.Popen(command, **kwargs)
    else:
        process = subprocess.Popen(command, **kwargs)

    return process


def is_process_running(pid: int) -> bool:
    """
    Check if a process with the given PID is currently running.

    Args:
        pid: Process ID to check

    Returns:
        True if process is running, False otherwise
    """
    try:
        os.kill(pid, 0)  # Signal 0 doesn't kill, just checks if process exists
        return True
    except OSError:
        return False


def wait_for_process(process: subprocess.Popen,
                    timeout: Optional[float] = None) -> Tuple[int, List[str]]:
    """
    Wait for an asynchronous process to complete.

    Args:
        process: Popen object from run_command_async
        timeout: Optional timeout in seconds

    Returns:
        Tuple of (return_code, output_lines)

    Example:
        >>> process = run_command_async(["python", "script.py"])
        >>> code, output = wait_for_process(process, timeout=60)
    """
    try:
        output, error = process.communicate(timeout=timeout)

        # Decode output
        output_lines = output.decode('utf-8', errors='replace').splitlines() if output else []
        error_lines = error.decode('utf-8', errors='replace').splitlines() if error else []

        return process.returncode, output_lines + error_lines

    except subprocess.TimeoutExpired:
        log.warning(f'Process timed out after {timeout} seconds')
        process.kill()
        return -2, [f'Process timed out after {timeout} seconds']


# ============================================================================
# Command Builder Utilities
# ============================================================================

def build_command_args(base_command: str, *args, **kwargs) -> List[str]:
    """
    Build command arguments from base command and parameters.

    Args:
        base_command: Base command (e.g., "conan")
        *args: Positional arguments
        **kwargs: Keyword arguments converted to --key=value format

    Returns:
        Complete command as list suitable for subprocess

    Example:
        >>> cmd = build_command_args("conan", "install", ".", "--build=missing", profile="release")
        >>> # Results in: ["conan", "install", ".", "--build=missing", "--profile=release"]
    """
    command = [base_command]

    # Add positional arguments
    for arg in args:
        if isinstance(arg, str):
            command.append(arg)
        elif isinstance(arg, (list, tuple)):
            command.extend(str(a) for a in arg)

    # Add keyword arguments
    for key, value in kwargs.items():
        if value is not None:
            if isinstance(value, bool):
                if value:
                    command.append(f"--{key}")
            else:
                command.append(f"--{key}={value}")

    return command