"""Zero-copy symlink utilities for Conan packages (NGA pattern)"""
import os
from pathlib import Path


def symlink_with_check(source, destination, target_is_directory=True):
    """
    Creates symlink only if destination doesn't exist.
    
    Pattern from NGA aerospace project - enables zero-copy dependency management.
    
    Args:
        source: Path to existing directory/file in Conan cache
        destination: Path where symlink should be created
        target_is_directory: Whether source is a directory
    
    Raises:
        FileNotFoundError: If source doesn't exist
    
    Returns:
        True if symlink created, False if already existed
    """
    if not os.path.exists(source):
        raise FileNotFoundError(f"Source not found: {source}")
    
    if not os.path.exists(destination):
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


def symlink_all_child_folders(source_root, dest_root):
    """
    Symlink all subdirectories from source to destination.
    
    Pattern from NGA - used to link dependencies from Conan cache to workspace.
    
    Args:
        source_root: Source directory (e.g., Conan cache package folder)
        dest_root: Destination directory (e.g., workspace TOOLS/)
    
    Returns:
        dict with symlink statistics
    """
    stats = {
        "created": 0,
        "skipped": 0,
        "failed": 0,
        "paths": []
    }
    
    os.makedirs(dest_root, exist_ok=True)
    
    if not os.path.exists(source_root):
        raise FileNotFoundError(f"Source root not found: {source_root}")
    
    for item in os.listdir(source_root):
        source_path = os.path.join(source_root, item)
        dest_path = os.path.join(dest_root, item)
        
        if os.path.isdir(source_path):
            try:
                if symlink_with_check(source_path, dest_path, target_is_directory=True):
                    stats["created"] += 1
                else:
                    stats["skipped"] += 1
                stats["paths"].append(dest_path)
            except Exception as e:
                print(f"✗ Failed to symlink {item}: {e}")
                stats["failed"] += 1
    
    return stats


def create_zero_copy_environment(conanfile, dependency_name, dest_folder):
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
        cache_path = conanfile.dependencies[dependency_name].package_folder
    except KeyError:
        raise KeyError(
            f"Dependency '{dependency_name}' not found. "
            f"Available: {list(conanfile.dependencies.keys())}"
        )
    
    # Create parent directory
    os.makedirs(os.path.dirname(dest_folder), exist_ok=True)
    
    # Create symlink
    symlink_with_check(cache_path, dest_folder, target_is_directory=True)
    
    print(f"✓ Zero-copy environment created: {dest_folder}")
    return cache_path


def validate_zero_copy_setup(workspace_path, expected_symlinks=None):
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
    results = {
        "total_symlinks": 0,
        "total_copies": 0,
        "disk_savings_mb": 0,
        "issues": [],
        "expected_found": [],
        "expected_missing": []
    }
    
    # Scan for symlinks
    for root, dirs, files in os.walk(workspace_path):
        for d in dirs:
            path = os.path.join(root, d)
            if os.path.islink(path):
                results["total_symlinks"] += 1
                
                # Get link target and estimate size
                try:
                    target = os.readlink(path)
                    if os.path.exists(target):
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
            full_path = os.path.join(workspace_path, symlink_path)
            if os.path.islink(full_path):
                results["expected_found"].append(symlink_path)
            else:
                results["expected_missing"].append(symlink_path)
                if os.path.exists(full_path) and not os.path.islink(full_path):
                    results["issues"].append(
                        f"Should be symlink but is copy: {symlink_path}"
                    )
    
    return results


def get_conan_cache_stats():
    """
    Get statistics about Conan cache efficiency.
    
    Returns:
        dict with cache stats
    """
    conan_home = os.path.expanduser("~/.conan2")
    cache_path = os.path.join(conan_home, "p")
    
    stats = {
        "total_packages": 0,
        "total_size_mb": 0,
        "packages": []
    }
    
    if not os.path.exists(cache_path):
        return stats
    
    for item in os.listdir(cache_path):
        package_dir = os.path.join(cache_path, item)
        if os.path.isdir(package_dir):
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
