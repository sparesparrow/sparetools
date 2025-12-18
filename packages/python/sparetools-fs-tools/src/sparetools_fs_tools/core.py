"""
Filesystem Operations Core Module

Provides comprehensive filesystem utilities including:
- Symlink management (zero-copy pattern)
- File and directory operations
- Path resolution and validation
- File metadata and search
"""

import logging
import os
import shutil
import stat
from pathlib import Path
from typing import Dict, List, Optional, Union, Set

log = logging.getLogger(__name__)


# ============================================================================
# Symlink Operations (Zero-Copy Pattern)
# ============================================================================

def symlink_with_check(source: Union[str, Path], destination: Union[str, Path],
                      target_is_directory: bool = True) -> bool:
    """
    Creates symlink only if destination doesn't exist.

    Pattern from NGA aerospace project - enables zero-copy dependency management.

    Args:
        source: Path to existing directory/file in Conan cache
        destination: Path where symlink should be created
        target_is_directory: Whether source is a directory

    Raises:
        FileNotFoundError: If source doesn't exist
        OSError: If symlink creation fails

    Returns:
        True if symlink created, False if already existed
    """
    source = Path(source)
    destination = Path(destination)

    if not source.exists():
        raise FileNotFoundError(f"Source not found: {source}")

    if not destination.exists():
        try:
            os.symlink(source, destination, target_is_directory)
            print(f"✓ Symlink created: {destination} -> {source}")
            return True
        except OSError as e:
            print(f"⚠ Failed to create symlink: {e}")
            raise
    else:
        print(f"⚠ Skipped (exists): {destination}")
        return False


def symlink_all_child_folders(source_root: Union[str, Path],
                             dest_root: Union[str, Path]) -> Dict[str, Union[int, List[str]]]:
    """
    Symlink all subdirectories from source to destination.

    Pattern from NGA - used to link dependencies from Conan cache to workspace.

    Args:
        source_root: Source directory (e.g., Conan cache package folder)
        dest_root: Destination directory (e.g., workspace TOOLS/)

    Returns:
        dict with symlink statistics
    """
    source_root = Path(source_root)
    dest_root = Path(dest_root)

    stats = {
        "created": 0,
        "skipped": 0,
        "failed": 0,
        "paths": []
    }

    dest_root.mkdir(exist_ok=True)

    if not source_root.exists():
        raise FileNotFoundError(f"Source root not found: {source_root}")

    for item in os.listdir(source_root):
        source_path = source_root / item
        dest_path = dest_root / item

        if source_path.is_dir():
            try:
                if symlink_with_check(source_path, dest_path, target_is_directory=True):
                    stats["created"] += 1
                else:
                    stats["skipped"] += 1
                stats["paths"].append(str(dest_path))
            except Exception as e:
                print(f"✗ Failed to symlink {item}: {e}")
                stats["failed"] += 1

    return stats


def create_zero_copy_environment(conanfile, dependency_name: str,
                                dest_folder: Union[str, Path]) -> Path:
    """
    Zero-copy pattern: symlink entire dependency from Conan cache.

    This is the core pattern enabling fast, efficient dependency management:
    - Artifacts downloaded ONCE to Conan cache
    - Build workspaces use OS symlinks pointing to cache
    - NO intermediate copies during consumption

    Args:
        conanfile: The consuming ConanFile instance
        dependency_name: Name of dependency (e.g., "sparetools-cpython", "openssl")
        dest_folder: Where to create symlink (e.g., "./TOOLS/python")

    Returns:
        Path to Conan cache package folder

    Raises:
        KeyError: If dependency not found
        OSError: If symlink creation fails

    Example:
        >>> class MyProjectConan(ConanFile):
        ...     requires = "sparetools-cpython/3.12.7"
        ...
        ...     def build(self):
        ...         cache_path = create_zero_copy_environment(
        ...             self, "sparetools-cpython", "./TOOLS/python"
        ...         )
        ...         # Now ./TOOLS/python links to cache, zero-copy!
    """
    try:
        cache_path = Path(conanfile.dependencies[dependency_name].package_folder)
    except KeyError:
        raise KeyError(
            f"Dependency '{dependency_name}' not found. "
            f"Available: {list(conanfile.dependencies.keys())}"
        )

    # Create parent directory
    dest_folder = Path(dest_folder)
    dest_folder.parent.mkdir(parents=True, exist_ok=True)

    # Create symlink
    symlink_with_check(cache_path, dest_folder, target_is_directory=True)

    print(f"✓ Zero-copy environment created: {dest_folder}")
    return cache_path


def validate_zero_copy_setup(workspace_path: Union[str, Path],
                           expected_symlinks: Optional[List[str]] = None) -> Dict[str, Union[int, float, List[str]]]:
    """
    Validate that workspace uses symlinks, not copies.

    Helps detect accidentally-copied files instead of using symlinks,
    which defeats the purpose of zero-copy strategy.

    Args:
        workspace_path: Root of workspace to check
        expected_symlinks: List of paths that should be symlinks

    Returns:
        dict with validation results
    """
    workspace_path = Path(workspace_path)

    results = {
        "total_symlinks": 0,
        "total_copies": 0,
        "disk_savings_mb": 0.0,
        "issues": [],
        "expected_found": [],
        "expected_missing": []
    }

    # Scan for symlinks
    for root, dirs, files in os.walk(workspace_path):
        for d in dirs:
            path = Path(root) / d
            if path.is_symlink():
                results["total_symlinks"] += 1

                # Get link target and estimate size
                try:
                    target = path.readlink()
                    if target.exists():
                        size = sum(
                            os.path.getsize(os.path.join(root, f))
                            for root, dirs, files in os.walk(target)
                            for f in files
                        ) / (1024 * 1024)
                        results["disk_savings_mb"] += size
                except Exception as e:
                    results["issues"].append(f"Broken link: {path} ({e})")

    # Check expected symlinks
    if expected_symlinks:
        for symlink_path in expected_symlinks:
            full_path = workspace_path / symlink_path
            if full_path.is_symlink():
                results["expected_found"].append(symlink_path)
            else:
                results["expected_missing"].append(symlink_path)
                if full_path.exists() and not full_path.is_symlink():
                    results["issues"].append(
                        f"Should be symlink but is copy: {symlink_path}"
                    )

    return results


# ============================================================================
# Directory Operations
# ============================================================================

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


def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def create_whole_dir_path(dir_path: Union[str, Path]) -> Path:
    """Create a directory path including all parent directories."""
    return ensure_directory_exists(dir_path)


# ============================================================================
# File Operations
# ============================================================================

def copy_file_with_metadata(source: Union[str, Path], destination: Union[str, Path]):
    """Copy a file while preserving metadata."""
    source = Path(source)
    destination = Path(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


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


def get_file_metadata(file_path: Union[str, Path]) -> Dict[str, Union[int, float, bool]]:
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


# ============================================================================
# Path Resolution and Search
# ============================================================================

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


def find_files_by_pattern(directory: Union[str, Path], pattern: str) -> List[Path]:
    """Find files matching a pattern using glob."""
    import glob
    directory = Path(directory)
    pattern_path = directory / pattern

    matches = []
    for path in glob.glob(str(pattern_path)):
        matches.append(Path(path))

    return matches


def resolve_profile_path(profile_relative_path: str, base_path: Optional[Union[str, Path]] = None) -> str:
    """
    Resolve a relative profile path to an absolute path.

    Args:
        profile_relative_path: Relative path like 'packages/sparetools-bootstrap/profiles/base/linux-gcc11'
        base_path: Optional base path (defaults to project root)

    Returns:
        Absolute path to the profile

    Raises:
        FileNotFoundError: If profile not found
    """
    from .utilities import get_project_root

    if base_path is None:
        # Try to use GITHUB_WORKSPACE first (GitHub Actions)
        github_workspace = os.environ.get('GITHUB_WORKSPACE', '')
        if github_workspace and Path(github_workspace).exists():
            base_path = Path(github_workspace)
        else:
            # Fall back to finding project root
            base_path = get_project_root()
    else:
        base_path = Path(base_path)

    profile_path = base_path / profile_relative_path

    if not profile_path.exists():
        raise FileNotFoundError(
            f"Profile not found: {profile_path}\n"
            f"Base path: {base_path}\n"
            f"Relative path: {profile_relative_path}"
        )

    return str(profile_path.absolute())


# ============================================================================
# Conan Cache Utilities
# ============================================================================

def get_conan_cache_stats() -> Dict[str, Union[int, float, List[Dict[str, Union[str, float]]]]]:
    """
    Get statistics about Conan cache efficiency.

    Returns:
        dict with cache stats
    """
    conan_home = Path("~/.conan2").expanduser()
    cache_path = conan_home / "p"

    stats = {
        "total_packages": 0,
        "total_size_mb": 0.0,
        "packages": []
    }

    if not cache_path.exists():
        return stats

    for item in os.listdir(cache_path):
        package_dir = cache_path / item
        if package_dir.is_dir():
            stats["total_packages"] += 1

            # Calculate size
            size = sum(
                os.path.getsize(os.path.join(root, f))
                for root, dirs, files in os.walk(package_dir)
                for f in files
            )
            size_mb = size / (1024 * 1024)
            stats["total_size_mb"] += size_mb
            stats["packages"].append({
                "name": item,
                "size_mb": size_mb
            })

    return stats