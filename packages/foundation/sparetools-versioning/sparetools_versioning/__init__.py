"""
SpareTools Versioning Package

Provides git-based versioning utilities for Conan packages.
"""

from .versioning import git_to_conan_collector
from .git import git_handler
from .conan import conan_versioning

__version__ = "1.0.0"

__all__ = [
    "git_to_conan_collector",
    "git_handler",
    "conan_versioning",
]
