"""
SpareTools Base - Consolidated Foundation Utilities

A unified package providing filesystem, process, networking, git, conan,
logging, and security utilities for the SpareTools ecosystem.

Usage:
    from sparetools import fs, proc, net, git, scm, conan, logging, security, gui
    
    # Filesystem operations
    fs.symlink_with_check(source, dest)
    fs.create_zero_copy_environment(conanfile, "dependency", "./TOOLS")
    
    # Process management
    code, output = proc.execute_command(["ls", "-la"])
    
    # Source control (preferred)
    from sparetools.scm.git import GitHandler, clone_repository
    
    # Or backward compatible
    from sparetools.git import GitHandler
    
    # And more...
"""

# Import submodules
from .sparetools import fs, proc

# Import placeholder modules
from .sparetools import net, git, conan, logging, security, scm, gui

# Re-export commonly used functions for backward compatibility
from .sparetools.fs import (
    symlink_with_check,
    symlink_all_child_folders,
    create_zero_copy_environment,
    validate_zero_copy_setup,
    get_conan_cache_stats,
)

from .sparetools.proc import (
    execute_command,
    run_command_with_timeout,
    execute_command_silently,
)

# Import security gates from existing file (keeping backward compatibility)
try:
    from .security_gates import (
        run_trivy_scan,
        generate_sbom,
        validate_package,
        check_fips_compliance,
    )
except ImportError:
    # Fallback if security_gates.py doesn't exist
    def run_trivy_scan(*args, **kwargs):
        raise NotImplementedError("Security module not yet implemented")
    def generate_sbom(*args, **kwargs):
        raise NotImplementedError("Security module not yet implemented")
    def validate_package(*args, **kwargs):
        raise NotImplementedError("Security module not yet implemented")
    def check_fips_compliance(*args, **kwargs):
        raise NotImplementedError("Security module not yet implemented")

__version__ = "2.0.0"

__all__ = [
    # Submodules
    "fs",
    "proc",
    # Filesystem functions
    "symlink_with_check",
    "symlink_all_child_folders",
    "create_zero_copy_environment",
    "validate_zero_copy_setup",
    "get_conan_cache_stats",
    # Process functions
    "execute_command",
    "run_command_with_timeout",
    "execute_command_silently",
    # Security functions
    "run_trivy_scan",
    "generate_sbom",
    "validate_package",
    "check_fips_compliance",
]