"""
File Operations

Provides utilities for file and directory operations, including
symlinks, path resolution, and file management.
"""

import logging
import os
import shutil
import stat
from pathlib import Path
from typing import List, Optional, Union

from shared_dev_tools.exceptions import FileOperationError

log = logging.getLogger(__name__)


def del_rw(action, name, exc):
    """Error handler for read-only file removal."""
    try:
        os.chmod(name, stat.S_IWRITE)
        os.remove(name)
    except Exception:
        pass


def remove_directory_tree(directory: Union[str, Path]):
    """Remove a directory tree recursively."""
    directory = Path(directory)
    log.debug(f'Removing directory: {directory}')

    if directory.is_dir():
        shutil.rmtree(directory, onerror=del_rw)


def symlink_with_check(source: Union[str, Path], destination: Union[str, Path], folder: bool = False):
    """Create a symlink if it doesn't already exist."""
    source = Path(source)
    destination = Path(destination)

    if not destination.exists():
        try:
            os.symlink(source, destination, folder)
            log.debug(f'Created symlink: {destination} -> {source}')
        except OSError as e:
            raise FileOperationError(f"Failed to create symlink {destination} -> {source}: {e}")
    else:
        log.debug(f'Symlink already exists: {destination}')


def find_executable_in_path(file_name: str) -> Optional[Path]:
    """Find an executable in the system PATH."""
    import subprocess

    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(['where', file_name],
                                  capture_output=True, text=True, check=False)
            if result.returncode == 0 and result.stdout.strip():
                return Path(result.stdout.strip().split('\n')[0])
        else:  # Unix-like
            result = subprocess.run(['which', file_name],
                                  capture_output=True, text=True, check=False)
            if result.returncode == 0 and result.stdout.strip():
                return Path(result.stdout.strip())
    except Exception as e:
        log.debug(f"Error finding executable {file_name}: {e}")

    return None


def find_first_existing_file(file_list: List[Union[str, Path]], file_name: Optional[str] = None) -> Optional[Path]:
    """Find the first existing file from a list of paths."""
    for path in file_list:
        path_obj = Path(path)
        if path_obj.exists():
            log.debug(f'File found: {path_obj}')
            return path_obj

    if file_name:
        return find_executable_in_path(file_name)

    return None


def create_whole_dir_path(dir_path: Union[str, Path]) -> Path:
    """Create a directory path including all parent directories."""
    dir_path = Path(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def copy_file_with_metadata(source: Union[str, Path], destination: Union[str, Path]):
    """Copy a file while preserving metadata."""
    source = Path(source)
    destination = Path(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def get_file_metadata(file_path: Union[str, Path]) -> dict:
    """Get file metadata including size, modification time, etc."""
    file_path = Path(file_path)
    stat_info = file_path.stat()

    return {
        'size': stat_info.st_size,
        'modified': stat_info.st_mtime,
        'created': stat_info.st_ctime,
        'mode': stat_info.st_mode,
        'is_file': file_path.is_file(),
        'is_dir': file_path.is_dir(),
        'is_symlink': file_path.is_symlink()
    }


def find_files_by_pattern(directory: Union[str, Path], pattern: str) -> List[Path]:
    """Find files matching a pattern using glob."""
    import glob
    directory = Path(directory)
    pattern_path = directory / pattern

    matches = []
    for path in glob.glob(str(pattern_path)):
        matches.append(Path(path))

    return matches


def safe_remove_file(file_path: Union[str, Path]):
    """Safely remove a file, handling permissions and missing files."""
    file_path = Path(file_path)

    try:
        if file_path.exists():
            # Make sure file is writable
            if file_path.is_file():
                file_path.chmod(file_path.stat().st_mode | stat.S_IWRITE)
            file_path.unlink()
            log.debug(f'Removed file: {file_path}')
    except Exception as e:
        log.warning(f'Failed to remove file {file_path}: {e}')


def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory