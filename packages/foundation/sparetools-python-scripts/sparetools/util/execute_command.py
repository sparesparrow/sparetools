"""
Command Execution Utilities

Based on ngapy-dev/ngapy/util/execute_command.py
Extended with additional command execution utilities.
"""

import logging
import os
import subprocess

log = logging.getLogger(__name__)


# Copied from ngapy/util/execute_command.py
def remove_console_color_codes(string: str, strip_end: bool = False) -> str:
    """
    Remove ANSI color codes from console output.
    
    Based on ngapy/util/execute_command.py remove_console_color_codes function.
    """
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    string = ansi_escape.sub('', string)
    if strip_end:
        return string.rstrip()
    else:
        return string


# Copied from ngapy/util/execute_command.py
def execute_command(command,
                    custom_env=os.environ,
                    print_command=True,
                    print_env=False,
                    print_out=True,
                    print_error=True,
                    print_err_code=True,
                    combine_stdout_and_stderr=True,
                    wait_till_finish=True,
                    continuous_print=False,
                    **kwargs):
    """
    Execute a system command with comprehensive output handling.
    
    Based on ngapy/util/execute_command.py execute_command function.

    Args:
        command: Command to execute (string or list)
        custom_env: Custom environment variables (defaults to os.environ)
        print_command: Whether to print the command being executed
        print_env: Whether to print environment variables
        print_out: Whether to print stdout
        print_error: Whether to print stderr
        print_err_code: Whether to print exit code
        combine_stdout_and_stderr: Combine stdout and stderr into single stream
        wait_till_finish: Wait for command completion before returning
        continuous_print: Print output continuously during execution
        **kwargs: Additional subprocess arguments (e.g., cwd for working directory)

    Returns:
        Tuple of (return_code, output_lines) or (return_code, output_lines, process_handle) if wait_till_finish=False
    """
    if print_command:
        log.info(f'Executing command: {command}')
    if print_env:
        log.debug(f'Variables: {custom_env}')
    kwargs['env'] = custom_env
    if combine_stdout_and_stderr:
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.STDOUT
    else:
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE
    if continuous_print:
        with subprocess.Popen(command, bufsize=1, universal_newlines=True, **kwargs) as p:
            lines = []
            log.debug(f'Output:\n')
            for line in p.stdout:
                log.debug(line)
                lines.append(remove_console_color_codes(line))
        return p.returncode, lines
    if wait_till_finish:
        output = subprocess.run(command, **kwargs)
        output_string = output.stdout.decode('ascii', errors="ignore").rstrip()
        if not combine_stdout_and_stderr:
            output_err_string = output.stderr.decode('ascii', errors="ignore")
        if print_out and output_string:
            log.debug(f'Output:\n{output_string}')
        if print_error and not combine_stdout_and_stderr and output_err_string:
            log.error(f'Error:\n{output_err_string}')
        if print_err_code:
            log.info(f'Executing result code: {output.returncode}')
        output_string = remove_console_color_codes(output_string, True)
        return output.returncode, output_string.splitlines()
    else:
        process_handle = subprocess.Popen(command, **kwargs)
        return 0, [], process_handle


# Extended functions beyond ngapy
def run_command_with_timeout(command,
                           timeout: int = 30,
                           **kwargs):
    """
    Execute a command with a timeout.
    
    Extended function beyond ngapy.

    Args:
        command: Command to execute
        timeout: Timeout in seconds
        **kwargs: Additional arguments passed to execute_command

    Returns:
        Tuple of (return_code, output_lines)
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
        return -2, [f'Command timed out after {timeout} seconds']

    return result['returncode'], result['output']


def execute_command_silently(command, **kwargs):
    """
    Execute a command with all output suppressed.
    
    Extended function beyond ngapy.

    Args:
        command: Command to execute
        **kwargs: Additional arguments

    Returns:
        Tuple of (return_code, output_lines)
    """
    kwargs.update({
        'print_command': False,
        'print_out': False,
        'print_error': False,
        'print_err_code': False
    })
    return execute_command(command, **kwargs)


def run_command_async(command,
                     custom_env=os.environ,
                     **kwargs):
    """
    Run a command asynchronously without waiting for completion.
    
    Extended function beyond ngapy.

    Args:
        command: Command to execute
        custom_env: Custom environment variables
        **kwargs: Additional subprocess arguments

    Returns:
        subprocess.Popen process handle
    """
    return execute_command(command, custom_env=custom_env, wait_till_finish=False, **kwargs)[2]


def wait_for_process(process: subprocess.Popen,
                    timeout=None):
    """
    Wait for an asynchronous process to complete.
    
    Extended function beyond ngapy.

    Args:
        process: subprocess.Popen process handle
        timeout: Optional timeout in seconds

    Returns:
        Tuple of (return_code, output_lines)
    """
    try:
        output, error = process.communicate(timeout=timeout)

        output_lines = output.decode('utf-8', errors='replace').splitlines() if output else []
        error_lines = error.decode('utf-8', errors='replace').splitlines() if error else []

        return process.returncode, output_lines + error_lines

    except subprocess.TimeoutExpired:
        log.warning(f'Process timed out after {timeout} seconds')
        process.kill()
        return -2, [f'Process timed out after {timeout} seconds']


def build_command_args(base_command: str, *args, **kwargs):
    """
    Build command arguments from base command and parameters.
    
    Extended function beyond ngapy.

    Args:
        base_command: Base command (e.g., "conan")
        *args: Positional arguments
        **kwargs: Keyword arguments converted to --key=value format

    Returns:
        Complete command as list suitable for subprocess
    """
    command = [base_command]

    for arg in args:
        if isinstance(arg, str):
            command.append(arg)
        elif isinstance(arg, (list, tuple)):
            command.extend(str(a) for a in arg)

    for key, value in kwargs.items():
        if value is not None:
            if isinstance(value, bool):
                if value:
                    command.append(f"--{key}")
            else:
                command.append(f"--{key}={value}")

    return command
