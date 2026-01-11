"""
SpareTools Base - Consolidated Foundation Utilities

A unified package providing filesystem, process, networking, git, conan,
logging, and security utilities for the SpareTools ecosystem.
"""

from . import fs, proc, net, git, conan, logging, security, scm, gui

__version__ = "2.0.0"

__all__ = [
    "fs",
    "proc",
    "net",
    "git",  # Backward compatibility - use scm.git instead
    "conan",
    "logging",
    "security",
    "scm",
    "gui",
]