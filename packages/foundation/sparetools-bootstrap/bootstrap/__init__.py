"""
OpenSSL Tools - Foundation Layer (Morpheus)

This package provides build orchestration, deployment utilities, and automation
scripts for the OpenSSL CI/CD modernization effort.

Architecture:
- Layer 1: openssl-tools (this) - Minimal dependencies, integrated utilities
- Layer 2: openssl-conan-base - Depends on tools
- Layer 3: openssl - Depends on base

Conan 2.21.0 | Python stdlib + selective shared utilities
"""

__version__ = "1.2.6"
__author__ = "sparesparrow"
__description__ = "OpenSSL CI/CD automation tools"

# ============================================================================
# SELECTIVE INTEGRATION: Copied utilities from shared-dev-tools
# ============================================================================
# Instead of adding dependencies, we selectively copy proven modules
# This gives us battle-tested functionality with zero external dependencies
# while maintaining full control and avoiding version conflicts

# Import core utilities (copied from shared-dev-tools for zero dependencies)
from .conan_functions import get_default_conan, execute_conan_command
from .file_operations import symlink_with_check, remove_directory_tree
from .execute_command import execute_command
from .exceptions import SharedDevToolsError

# Import OpenSSL-specific tools (copied from shared-dev-tools)
from .openssl.fips_validator import FIPSValidator
from .openssl.sbom_generator import SBOMGenerator
from .openssl.crypto_config import CryptoConfigManager

# Re-export for backward compatibility and cleaner imports
__all__ = [
    # Core utilities
    'get_default_conan', 'execute_conan_command',
    'symlink_with_check', 'remove_directory_tree',
    'execute_command', 'SharedDevToolsError',

    # OpenSSL-specific tools
    'FIPSValidator', 'SBOMGenerator', 'CryptoConfigManager',

    # Version info
    '__version__'
]
