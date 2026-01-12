"""
Filesystem Operations Module

Provides utilities for file and directory operations, symlinks, path resolution,
and file management.
"""

from .core import (
    symlink_with_check,
    symlink_all_child_folders,
    create_zero_copy_environment,
    validate_zero_copy_setup,
    remove_directory_tree,
    ensure_directory_exists,
    create_whole_dir_path,
    copy_file_with_metadata,
    safe_remove_file,
    get_file_metadata,
    find_executable_in_path,
    find_first_existing_file,
    find_files_by_pattern,
    resolve_profile_path,
    get_conan_cache_stats,
    archive_files,
    decompress_with_progress,
    find_file_in_parents,
)

__all__ = [
    "symlink_with_check",
    "symlink_all_child_folders",
    "create_zero_copy_environment",
    "validate_zero_copy_setup",
    "remove_directory_tree",
    "ensure_directory_exists",
    "create_whole_dir_path",
    "copy_file_with_metadata",
    "safe_remove_file",
    "get_file_metadata",
    "find_executable_in_path",
    "find_first_existing_file",
    "find_files_by_pattern",
    "resolve_profile_path",
    "get_conan_cache_stats",
    "archive_files",
    "decompress_with_progress",
    "find_file_in_parents",
]