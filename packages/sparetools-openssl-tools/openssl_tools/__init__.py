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

# Import core utilities (minimal, stable interfaces)
from .conan_functions import get_default_conan, execute_conan_command
from .file_operations import symlink_with_check, remove_directory_tree
from .execute_command import execute_command
from .exceptions import SharedDevToolsError

# Import OpenSSL-specific tools (exactly what we need)
from .openssl.fips_validator import FIPSValidator
from .openssl.sbom_generator import SBOMGenerator
from .openssl.crypto_config import CryptoConfigManager

# Re-export for backward compatibility
__all__ = [
    # Core utilities
    "get_default_conan",
    "execute_conan_command",
    "execute_command",
    "symlink_with_check",
    "remove_directory_tree",
    "SharedDevToolsError",

    # OpenSSL tools
    "FIPSValidator",
    "SBOMGenerator",
    "CryptoConfigManager",

    # Version info
    "__version__",
    "__author__",
    "__description__"
]
