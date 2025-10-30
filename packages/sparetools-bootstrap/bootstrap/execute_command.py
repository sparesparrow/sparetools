"""
Command Execution Utilities

Provides utilities for executing system commands with proper error handling,
output capture, and cross-platform support.
"""

import logging
import os
import subprocess
from typing import Optional, Tuple, List, Union

log = logging.getLogger(__name__)


def remove_console_color_codes(string: str, strip_end: bool = False) -> str:
    """Remove ANSI color codes from console output."""
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\\\-_]|\\[[0-?]*[ -/]*[@-~])')
    string = ansi_escape.sub('', string)
    if strip_end:
        return string.rstrip()
    else:
        return string


def execute_command(command: Union[str, List[str]],
                   custom_env: Optional[dict] = None,
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

    Args:
        command: Command to execute (string or list)
        custom_env: Custom environment variables
        print_command: Whether to print the command being executed
        print_env: Whether to print environment variables
        print_out: Whether to print stdout
        print_error: Whether to print stderr
        print_err_code: Whether to print exit code
        combine_stdout_and_stderr: Combine stdout and stderr
        wait_till_finish: Wait for command completion
        continuous_print: Print output continuously during execution
        **kwargs: Additional subprocess arguments

    Returns:
        Tuple of (return_code, output_lines)
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
            # Don't wait for completion
            return 0, []

    except Exception as e:
        log.error(f'Failed to execute command {command}: {e}')
        return -1, [str(e)]


def run_command_with_timeout(command: Union[str, List[str]],
                           timeout: int = 30,
                           **kwargs) -> Tuple[int, List[str]]:
    """Execute a command with a timeout."""
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
    """Execute a command with all output suppressed."""
    kwargs.update({
        'print_command': False,
        'print_out': False,
        'print_error': False,
        'print_err_code': False
    })
    return execute_command(command, **kwargs)