#!/usr/bin/env python3
"""
OpenSSL Tools Command Execution Utilities
Based on openssl-tools patterns for command execution with proper error handling
"""

import logging
import subprocess
import sys
from pathlib import Path

log = logging.getLogger('__main__.' + __name__)


def execute_command(command, cwd=None, continuous_print=True, print_out=True, print_command=True, print_err_code=True):
    """
    Execute command with proper error handling and logging
    Based on openssl-tools patterns
    """
    if print_command:
        log.info(f"Executing command: {command}")
    
    try:
        if isinstance(command, str):
            result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, shell=True)
        else:
            result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
        
        if continuous_print and print_out:
            print(result.stdout)
        
        if result.stderr and print_err_code:
            print(result.stderr)
        
        return result.returncode, result.stdout.splitlines()
    except Exception as e:
        log.error(f"Command execution failed: {e}")
        return 1, [str(e)]


def execute_command_with_output(command, cwd=None):
    """
    Execute command and return output directly
    """
    try:
        if isinstance(command, str):
            result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, shell=True)
        else:
            result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
        
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        log.error(f"Command execution failed: {e}")
        return 1, "", str(e)