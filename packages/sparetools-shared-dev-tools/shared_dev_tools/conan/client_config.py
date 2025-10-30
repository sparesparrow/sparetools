"""
Conan Client Configuration

Utilities for managing Conan client configuration, profiles, and settings.
"""

import logging
import os
from pathlib import Path

from shared_dev_tools.conan.conan_functions import execute_conan_command
from shared_dev_tools.exceptions import SharedDevToolsError

log = logging.getLogger(__name__)


def get_conan_config(key=None):
    """Get Conan configuration value(s)."""
    if key:
        cmd = f'config get {key}'
    else:
        cmd = 'config list'

    rc, output = execute_conan_command(cmd)
    if rc != 0:
        log.error(f"Failed to get Conan config: {output}")
        return None

    if key:
        return output[0].strip() if output else None
    else:
        return output


def set_conan_config(key, value):
    """Set a Conan configuration value."""
    cmd = f'config set {key}={value}'
    rc, output = execute_conan_command(cmd)

    if rc != 0:
        log.error(f"Failed to set Conan config {key}={value}: {output}")
        return False

    log.info(f"Set Conan config {key}={value}")
    return True


def get_conan_profiles():
    """Get list of available Conan profiles."""
    cmd = 'profile list'
    rc, output = execute_conan_command(cmd)

    if rc != 0:
        log.error(f"Failed to list profiles: {output}")
        return []

    return [line.strip() for line in output if line.strip()]


def create_conan_profile(name, base_profile=None):
    """Create a new Conan profile."""
    cmd = f'profile new {name}'
    if base_profile:
        cmd += f' --detect --profile {base_profile}'
    else:
        cmd += ' --detect'

    rc, output = execute_conan_command(cmd)

    if rc != 0:
        log.error(f"Failed to create profile {name}: {output}")
        return False

    log.info(f"Created Conan profile {name}")
    return True


def update_profile_setting(profile_name, key, value):
    """Update a setting in a Conan profile."""
    cmd = f'profile update settings.{key}={value} {profile_name}'
    rc, output = execute_conan_command(cmd)

    if rc != 0:
        log.error(f"Failed to update profile {profile_name} setting {key}: {output}")
        return False

    return True


def update_profile_option(profile_name, package_ref, key, value):
    """Update an option in a Conan profile."""
    cmd = f'profile update options.{package_ref}.{key}={value} {profile_name}'
    rc, output = execute_conan_command(cmd)

    if rc != 0:
        log.error(f"Failed to update profile {profile_name} option {key}: {output}")
        return False

    return True


def get_profile_path(profile_name):
    """Get the path to a Conan profile file."""
    from shared_dev_tools.conan.conan_functions import get_conan_home
    conan_home = Path(get_conan_home())
    return conan_home / 'profiles' / profile_name


def load_profile(profile_name):
    """Load and return profile content."""
    profile_path = get_profile_path(profile_name)
    if not profile_path.exists():
        raise SharedDevToolsError(f"Profile {profile_name} not found")

    with open(profile_path, 'r') as f:
        return f.read()


def save_profile(profile_name, content):
    """Save profile content to file."""
    profile_path = get_profile_path(profile_name)
    profile_path.parent.mkdir(parents=True, exist_ok=True)

    with open(profile_path, 'w') as f:
        f.write(content)

    log.info(f"Saved profile {profile_name}")


def detect_compiler_settings():
    """Detect and return compiler settings for current system."""
    cmd = 'profile new default_temp --detect'
    rc, output = execute_conan_command(cmd)

    if rc != 0:
        log.error(f"Failed to detect compiler settings: {output}")
        return {}

    # Parse the detected settings (simplified)
    settings = {}
    for line in output:
        if '=' in line and not line.startswith('['):
            key, value = line.split('=', 1)
            settings[key.strip()] = value.strip()

    # Clean up temp profile
    execute_conan_command('profile remove default_temp')

    return settings