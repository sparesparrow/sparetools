"""
Symlink Helpers - Backward Compatibility Shim

This module is maintained for backward compatibility.
New code should import from sparetools.fs instead.

Deprecated: Use sparetools.fs instead
"""

import warnings

warnings.warn(
    "symlink-helpers.py is deprecated. Use sparetools.fs instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from new location
from .sparetools.fs import (
    symlink_with_check,
    symlink_all_child_folders,
    create_zero_copy_environment,
    validate_zero_copy_setup,
    get_conan_cache_stats,
)

__all__ = [
    "symlink_with_check",
    "symlink_all_child_folders",
    "create_zero_copy_environment",
    "validate_zero_copy_setup",
    "get_conan_cache_stats",
]