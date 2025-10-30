#!/usr/bin/env python3
"""
OpenSSL Tools Copy Utilities
Based on openssl-tools patterns for file operations
"""

import hashlib
import logging
import os
import shutil
from pathlib import Path

log = logging.getLogger('__main__.' + __name__)


def ensure_target_exists(target):
    """Ensure target directory exists"""
    os.makedirs(os.path.dirname(target), exist_ok=True)


def get_file_metadata(filepath):
    """Get file metadata including MD5 hash"""
    with open(filepath, 'rb') as f:
        content = f.read()
        md5_hash = hashlib.md5(content).hexdigest()
    
    stat = os.stat(filepath)
    return {
        'MD5': md5_hash,
        'size': stat.st_size,
        'mtime': stat.st_mtime
    }


def copy_file(source, destination):
    """Copy file with proper error handling"""
    try:
        ensure_target_exists(destination)
        shutil.copy2(source, destination)
        log.debug(f"Copied file: {source} -> {destination}")
    except Exception as e:
        log.error(f"Failed to copy file {source} to {destination}: {e}")
        raise


def copy_folder(source, destination):
    """Copy folder with proper error handling"""
    try:
        if os.path.exists(destination):
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
        log.debug(f"Copied folder: {source} -> {destination}")
    except Exception as e:
        log.error(f"Failed to copy folder {source} to {destination}: {e}")
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