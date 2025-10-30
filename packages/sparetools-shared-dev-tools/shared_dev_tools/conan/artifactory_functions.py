"""
Artifactory Integration Functions

Provides utilities for interacting with Artifactory repositories,
uploading, downloading, and managing Conan packages.
"""

import logging
from pathlib import Path

from shared_dev_tools.conan.conan_functions import execute_conan_command
from shared_dev_tools.exceptions import SharedDevToolsError

log = logging.getLogger(__name__)


def upload_package(package_ref, remote_name="artifactory"):
    """Upload a package to Artifactory."""
    cmd = f'upload {package_ref} --remote {remote_name}'
    rc, output = execute_conan_command(cmd)

    if rc != 0:
        log.error(f"Failed to upload package {package_ref}: {output}")
        return False

    log.info(f"Successfully uploaded package {package_ref}")
    return True


def download_package(package_ref, remote_name="artifactory"):
    """Download a package from Artifactory."""
    cmd = f'download {package_ref} --remote {remote_name}'
    rc, output = execute_conan_command(cmd)

    if rc != 0:
        log.error(f"Failed to download package {package_ref}: {output}")
        return False

    log.info(f"Successfully downloaded package {package_ref}")
    return True


def search_packages(pattern="*", remote_name="artifactory"):
    """Search for packages in Artifactory."""
    cmd = f'search {pattern} --remote {remote_name}'
    rc, output = execute_conan_command(cmd)

    if rc != 0:
        log.error(f"Failed to search packages: {output}")
        return []

    return [line.strip() for line in output if line.strip()]


def add_remote(name, url, verify_ssl=True):
    """Add a Conan remote."""
    verify_flag = "--verify-ssl" if verify_ssl else "--no-verify-ssl"
    cmd = f'remote add {name} {url} {verify_flag}'
    rc, output = execute_conan_command(cmd)

    if rc != 0:
        log.error(f"Failed to add remote {name}: {output}")
        return False

    log.info(f"Successfully added remote {name}")
    return True


def remove_remote(name):
    """Remove a Conan remote."""
    cmd = f'remote remove {name}'
    rc, output = execute_conan_command(cmd)

    if rc != 0:
        log.error(f"Failed to remove remote {name}: {output}")
        return False

    log.info(f"Successfully removed remote {name}")
    return True


def list_remotes():
    """List all Conan remotes."""
    cmd = 'remote list'
    rc, output = execute_conan_command(cmd)

    if rc != 0:
        log.error(f"Failed to list remotes: {output}")
        return []

    return [line.strip() for line in output if line.strip()]


def enable_remote(name):
    """Enable a Conan remote."""
    cmd = f'remote enable {name}'
    rc, output = execute_conan_command(cmd)

    if rc != 0:
        log.error(f"Failed to enable remote {name}: {output}")
        return False

    return True


def disable_remote(name):
    """Disable a Conan remote."""
    cmd = f'remote disable {name}'
    rc, output = execute_conan_command(cmd)

    if rc != 0:
        log.error(f"Failed to disable remote {name}: {output}")
        return False

    return True


def authenticate_remote(name, username=None, password=None):
    """Authenticate with a remote repository."""
    cmd = f'remote auth {name}'

    if username and password:
        # Use environment variables for security
        import os
        os.environ['CONAN_LOGIN_USERNAME'] = username
        os.environ['CONAN_PASSWORD'] = password

    rc, output = execute_conan_command(cmd)

    if rc != 0:
        log.error(f"Failed to authenticate with remote {name}: {output}")
        return False

    log.info(f"Successfully authenticated with remote {name}")
    return True