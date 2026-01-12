"""
Filesystem Operations Core

Consolidated filesystem utilities from SpareTools and ngapy-dev patterns.
"""

import logging
import os
import shutil
import stat
import zipfile
import fnmatch
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
        source: Path to existing directory/file
        destination: Path where symlink should be created
        target_is_directory: Whether source is a directory

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

    Args:
        source_root: Source directory
        dest_root: Destination directory

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

    Args:
        conanfile: The consuming ConanFile instance
        dependency_name: Name of dependency
        dest_folder: Where to create symlink

    Returns:
        Path to Conan cache package folder
    """
    try:
        cache_path = Path(conanfile.dependencies[dependency_name].package_folder)
    except KeyError:
        raise KeyError(
            f"Dependency '{dependency_name}' not found. "
            f"Available: {list(conanfile.dependencies.keys())}"
        )

    dest_folder = Path(dest_folder)
    dest_folder.parent.mkdir(parents=True, exist_ok=True)

    symlink_with_check(cache_path, dest_folder, target_is_directory=True)

    print(f"✓ Zero-copy environment created: {dest_folder}")
    return cache_path


def validate_zero_copy_setup(workspace_path: Union[str, Path],
                           expected_symlinks: Optional[List[str]] = None) -> Dict[str, Union[int, float, List[str]]]:
    """
    Validate that workspace uses symlinks, not copies.

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

    for root, dirs, files in os.walk(workspace_path):
        for d in dirs:
            path = Path(root) / d
            if path.is_symlink():
                results["total_symlinks"] += 1

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

# Copied from ngapy/util/file_operations.py
def del_rw(action, name, exc):
    """
    Error handler for read-only file removal.
    
    Based on ngapy/util/file_operations.py del_rw function.
    """
    try:
        os.chmod(name, stat.S_IWRITE)
        os.remove(name)
    except:
        pass


# Copied from ngapy/util/file_operations.py
def remove_directory_tree(directory):
    """
    Remove a directory tree recursively.
    
    Based on ngapy/util/file_operations.py remove_directory_tree function.
    """
    log.debug(f'Removing directory: {directory}')
    if Path(directory).is_dir():
        shutil.rmtree(directory, onerror=del_rw)


def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


# Copied from ngapy/util/file_operations.py
def create_whole_dir_path(dir_path):
    """
    Create a directory path including all parent directories.
    
    Based on ngapy/util/file_operations.py create_whole_dir_path function.
    """
    return Path(dir_path).mkdir(parents=True, exist_ok=True)


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

# Copied from ngapy/util/file_operations.py
def find_executable_in_path(file_name):
    """
    Find an executable in the system PATH.
    
    Based on ngapy/util/file_operations.py find_executable_in_path function.
    """
    from ..util.execute_command import execute_command
    log.debug(f'Searching using where in PATH: {os.environ["PATH"]}')
    rc, result = execute_command(f'where {file_name}')
    if rc == 0 and len(result):
        return result[0]
    return None


# Copied from ngapy/util/file_operations.py
def find_first_existing_file(file_list, file_name=None):
    """
    Find the first existing file from a list of paths.
    
    Based on ngapy/util/file_operations.py find_first_existing_file function.
    """
    for path in file_list:
        if Path(path).exists():
            log.debug(f'File found here: {path}')
            return Path(path)
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
    """
    if base_path is None:
        github_workspace = os.environ.get('GITHUB_WORKSPACE', '')
        if github_workspace and Path(github_workspace).exists():
            base_path = Path(github_workspace)
        else:
            # Find project root by looking for common markers
            current = Path.cwd()
            markers = ['.git', 'pyproject.toml', 'setup.py', 'requirements.txt']
            while current.parent != current:
                for marker in markers:
                    if (current / marker).exists():
                        base_path = current
                        break
                if base_path:
                    break
                current = current.parent
            if not base_path:
                base_path = Path.cwd()
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
# Archive Operations
# ============================================================================

# Copied from ngapy/util/file_operations.py
def archive_files(zip_name: Path, files_to_add):
    """
    Archive files into a zip file.
    
    Based on ngapy/util/file_operations.py archive_files function.
    """
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zip_obj:
        for zip_element in files_to_add:
            if type(zip_element) == str or isinstance(zip_element, Path):
                zip_obj.write(zip_element, arcname=Path(zip_element).name)
            elif type(zip_element) == tuple:
                # Handle tuple format: (file_location, archive_location) or object with attributes
                if hasattr(zip_element, 'file_location'):
                    zip_obj.write(zip_element.file_location, arcname=zip_element.archive_location)
                elif len(zip_element) == 2:
                    zip_obj.write(zip_element[0], arcname=zip_element[1])
                else:
                    raise RuntimeError(f'Cannot get information needed for compression.')
            else:
                raise RuntimeError(f'Cannot get information needed for compression.')


# Copied from ngapy/util/file_operations.py
def decompress_with_progress(source_archive, target_path, decompression_filter=None):
    """
    Decompress archive with progress indication.
    
    Based on ngapy/util/file_operations.py decompress_with_progress function.
    """
    from tqdm import tqdm
    
    def make_list_from_variable(var):
        """Convert variable to list if not already."""
        if isinstance(var, (list, tuple)):
            return var
        return [var]
    
    def match_any_of_patterns(value, patterns):
        """Check if value matches any pattern."""
        for pattern in make_list_from_variable(patterns):
            if fnmatch.fnmatch(value, pattern):
                return True
        return False
    
    with zipfile.ZipFile(source_archive, 'r') as zip_ref:
        if decompression_filter:
            files = list(filter(lambda info: match_any_of_patterns(info.filename, decompression_filter),
                                zip_ref.infolist()))
        else:
            files = zip_ref.infolist()
        for member in tqdm(files, desc='Extracting'):
            zip_ref.extract(member, target_path)


# ============================================================================
# File Finding Utilities
# ============================================================================

# Copied from ngapy/util/file_operations.py
def find_file_in_parents(file_name, file_to_find='conanfile.py'):
    """
    Find a file in parent directories.
    
    Based on ngapy/util/file_operations.py find_file_in_parents function.

    Args:
        file_name: Starting path
        file_to_find: File name to search for

    Returns:
        Tuple of (directory_path, file_path)
    """
    path_to_resolve = Path(file_name)
    if not path_to_resolve.exists():
        raise RuntimeError(f'Path {file_name} does not exists!')
    if path_to_resolve.is_file():
        path_to_resolve = path_to_resolve.parent
    while 1:
        test_path = Path(path_to_resolve / file_to_find)
        if not test_path:
            raise RuntimeError(f'File {file_to_find} not found in any of the parent folders!')
        if test_path.exists():
            return path_to_resolve, test_path
        else:
            path_to_resolve = path_to_resolve.parent


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