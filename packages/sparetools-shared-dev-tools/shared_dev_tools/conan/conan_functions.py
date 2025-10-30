"""
Conan Functions

Core Conan package management utilities and functions.
"""

import logging
import os
import sys
import tempfile
from functools import cache
from pathlib import Path

from shared_dev_tools.util.execute_command import execute_command
from shared_dev_tools.util.file_operations import find_executable_in_path, find_first_existing_file
from shared_dev_tools.exceptions import SharedDevToolsError

log = logging.getLogger(__name__)

# Set Conan color output
os.environ['CONAN_COLOR_DISPLAY'] = '1'
os.environ['CLICOLOR_FORCE'] = '1'
os.environ['CLICOLOR'] = '1'


@cache
def get_default_conan() -> Path:
    """Get the default Conan executable path."""
    conan_exe = Path()

    # Check if application is frozen (PyInstaller)
    if getattr(sys, 'frozen', False):
        application_path = Path(sys.executable).parent
        conan_exe = application_path / 'conan.exe'
    elif __file__:
        # Try to find conan in PATH
        conan_exe = find_executable_in_path('conan.exe')
        if conan_exe is None:
            # Fallback: try common installation paths
            conan_paths = [
                '/usr/local/bin/conan',
                '/usr/bin/conan',
                '/opt/conan/bin/conan',
                'C:\\Program Files\\Conan\\conan\\conan.exe',
                str(Path.home() / '.conan' / 'conan.exe')
            ]
            conan_exe = find_first_existing_file(conan_paths, 'conan.exe')

    if conan_exe and conan_exe.exists():
        log.debug(f'Default conan found: {conan_exe}')
        return conan_exe
    else:
        raise SharedDevToolsError(
            'Default Conan executable not found. Please install Conan from: '
            'https://conan.io/downloads.html'
        )


@cache
def get_conan_home():
    """Get the Conan home directory."""
    rc, return_string = execute_command(f'{get_default_conan()} config home')
    if rc == 0 and return_string:
        conan_home = return_string[-1].strip()
        return conan_home
    else:
        # Default fallback
        return str(Path.home() / '.conan')


def get_all_packages_in_cache() -> list:
    """Get all packages currently in the Conan cache."""
    rc, return_string = execute_command(f'{get_default_conan()} search --raw')
    if rc == 0:
        # Filter out warning lines
        return [line for line in return_string if not line.startswith('WARN')]
    else:
        return []


def remove_conan_package_from_cache(package_name):
    """Remove a package from the Conan cache."""
    return execute_command(f'{get_default_conan()} remove {package_name} --force')


def execute_conan_command(command, **kwargs):
    """Execute a Conan command with proper error handling."""
    full_command = f'{get_default_conan()} {command}'
    return execute_command(full_command, **kwargs)


def get_conan_version():
    """Get the Conan version."""
    rc, output = execute_command(f'{get_default_conan()} --version')
    if rc == 0 and output:
        return output[0].strip()
    return None


class ConanPackageInfo:
    """Container for Conan package information."""

    def __init__(self, package_ref, info_dict=None):
        self.package_ref = package_ref
        self.info = info_dict or {}

    @property
    def name(self):
        return self.info.get('name', '')

    @property
    def version(self):
        return self.info.get('version', '')

    @property
    def user(self):
        return self.info.get('user', '')

    @property
    def channel(self):
        return self.info.get('channel', '')


def search_conan_packages(pattern="*", remote=None):
    """Search for packages in Conan cache or remote."""
    cmd = f'search {pattern}'
    if remote:
        cmd += f' --remote {remote}'

    rc, output = execute_conan_command(cmd)
    if rc == 0:
        return [line.strip() for line in output if line.strip()]
    return []


def install_conan_package(package_ref, build=None, options=None):
    """Install a Conan package."""
    cmd = f'install {package_ref}'

    if build:
        cmd += f' --build={build}'
    if options:
        for key, value in options.items():
            cmd += f' -o {key}={value}'

    return execute_conan_command(cmd)


def create_conan_package(conanfile_path, **kwargs):
    """Create a Conan package."""
    cmd = f'create {conanfile_path}'

    # Add common options
    if 'build' in kwargs:
        cmd += f' --build={kwargs["build"]}'

    return execute_conan_command(cmd)