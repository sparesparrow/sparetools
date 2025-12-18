"""
Filesystem Utilities

Additional utility functions for path operations and project management.
"""

import os
from pathlib import Path
from typing import Optional


def get_project_root(start_path: Optional[Path] = None) -> Path:
    """Find the project root by looking for common markers."""
    if start_path is None:
        start_path = Path.cwd()

    current = start_path
    markers = ['.git', 'pyproject.toml', 'setup.py', 'requirements.txt']

    while current.parent != current:  # Stop at filesystem root
        for marker in markers:
            if (current / marker).exists():
                return current
        current = current.parent

    # Fallback to current directory
    return Path.cwd()