"""
Conan Versioning Utilities

Package version management and tracking.
"""

import logging
import os
import re
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

log = logging.getLogger(__name__)

# Use sparetools-base utilities
try:
    from sparetools.conan.core import (
        ConanJsonLoader,
        get_default_conan,
        get_conan_home,
    )
    from sparetools.util.execute_command import execute_command
except ImportError:
    # Fallback if sparetools-base not available
    log.warning("sparetools-base not available, limited functionality")
    ConanJsonLoader = None
    get_default_conan = None
    get_conan_home = None
    execute_command = None


def get_package_name_version(package) -> Tuple[str, str]:
    """
    Extract name and version from package.
    
    Args:
        package: Package object with display_name and provides attributes
        
    Returns:
        Tuple of (name, version)
    """
    if hasattr(package, 'display_name'):
        _, version = package.display_name.split('/', maxsplit=1)
        version = version.split(')', maxsplit=1)[0]
        if hasattr(package, 'provides') and package.provides:
            name = package.provides[0]
        else:
            # Fallback: try to extract from display_name
            name = package.display_name.split('/')[0] if '/' in package.display_name else "unknown"
        return name, version
    else:
        # Fallback for dict-like objects
        if isinstance(package, dict):
            ref = package.get('reference', 'unknown/unknown')
            parts = ref.split('/')
            if len(parts) >= 2:
                return parts[0], parts[1]
        return "unknown", "unknown"


def python_version_sort(s: str) -> int:
    """
    Sort versions numerically, handling +dev suffixes.
    
    Args:
        s: Version string (e.g., "3.10.6+dev1")
        
    Returns:
        Numeric rank for sorting
    """
    rank = 0
    numbers = s.replace('+dev', '.').split('.')
    numbers.reverse()
    position = 1
    for number in numbers:
        try:
            rank += int(number) * position
        except ValueError:
            # Handle non-numeric parts
            pass
        position *= 100
    return rank


class ConanVersionManager:
    """Manages Conan package versions and tracking."""

    def __init__(self, conan_home: Optional[str] = None):
        """
        Initialize version manager.
        
        Args:
            conan_home: Conan home directory (auto-detected if None)
        """
        import yaml
        from datetime import datetime

        self.conan_home = conan_home or (get_conan_home() if get_conan_home else None) or os.path.expanduser("~/.conan")
        self.expected_version = 1.0
        self._data = {
            'version': self.expected_version,
            'conan_usage': {},
        }
        self.load_config()

    @property
    def config_path(self) -> Path:
        """Get path to tracker configuration file."""
        return Path(self.conan_home) / 'conan_tracker.yaml'

    @property
    def packages(self) -> Dict[str, Any]:
        """Get package usage data."""
        return self._data['conan_usage']

    @packages.setter
    def packages(self, value: Dict[str, Any]) -> None:
        """Set package usage data."""
        self._data['conan_usage'] = value

    def load_config(self) -> None:
        """Load tracker configuration from file."""
        import yaml
        from datetime import datetime

        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as stream:
                    temp_data = yaml.safe_load(stream)
                    if temp_data and str(temp_data.get('version', 0)) == str(self.expected_version):
                        self._data = temp_data
                    else:
                        self.save_config()
            except (yaml.YAMLError, IOError) as e:
                log.warning(f"Failed to load conan tracker config: {e}")

    def save_config(self) -> None:
        """Save tracker configuration to file."""
        import yaml

        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as stream:
                yaml.safe_dump(self._data, stream)
        except IOError as e:
            log.error(f"Failed to save conan tracker config: {e}")

    def track_package(self, package_name: str, version: str) -> None:
        """
        Track a package usage.
        
        Args:
            package_name: Package name
            version: Package version
        """
        from datetime import datetime
        package_ref = f'{package_name}/{version}'
        self.packages[package_ref] = {'last_used': datetime.now().isoformat()}
        self.save_config()

    def get_tracked_packages(self) -> Dict[str, Any]:
        """
        Get all tracked packages.
        
        Returns:
            Dictionary of tracked packages
        """
        return self.packages.copy()
