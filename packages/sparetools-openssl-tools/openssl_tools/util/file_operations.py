#!/usr/bin/env python3
"""
OpenSSL Tools File Operations Utilities
Based on openssl-tools patterns for file operations
"""

import logging
import os
import shutil
from pathlib import Path

log = logging.getLogger('__main__.' + __name__)


def find_first_existing_file(paths, filename):
    """Find first existing file in list of paths"""
    for path in paths:
        full_path = os.path.join(path, filename)
        if os.path.exists(full_path):
            return full_path
    return None


def find_executable_in_path(executable_name):
    """Find executable in PATH"""
    for path in os.environ.get('PATH', '').split(os.pathsep):
        full_path = os.path.join(path, executable_name)
        if os.path.exists(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return None


def symlink_with_check(source, target, is_directory=False):
    """Create symlink with proper error handling"""
    try:
        if os.path.exists(target):
            if os.path.islink(target):
                os.unlink(target)
            elif os.path.isdir(target):
                shutil.rmtree(target)
            else:
                os.remove(target)
        
        if is_directory:
            os.symlink(source, target, target_is_directory=True)
        else:
            os.symlink(source, target)
        log.debug(f"Created symlink: {source} -> {target}")
    except Exception as e:
        log.error(f"Failed to create symlink {source} -> {target}: {e}")
        raise


def remove_directory_tree(path):
    """Remove directory tree with proper error handling"""
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
            log.debug(f"Removed directory tree: {path}")
    except Exception as e:
        log.error(f"Failed to remove directory tree {path}: {e}")
        raise