"""
Configuration Loader

Provides utilities for loading and merging configuration files.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from shared_dev_tools.core.utilities import load_yaml_config

log = logging.getLogger(__name__)


class ConanMergedConfiguration:
    """Configuration class that merges multiple configuration sources."""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self._config = {}
        self.conan_package_config = {}
        self.PACKAGE_ROOT_cache = {}

    def load_config(self):
        """Load and merge configuration from multiple sources."""
        # Load base configuration
        base_config = load_yaml_config(self.config_dir / 'base.yaml')
        self._config.update(base_config)

        # Load environment-specific configuration
        env = self._get_current_environment()
        env_config = load_yaml_config(self.config_dir / f'{env}.yaml')
        self._config.update(env_config)

        # Load Conan package configuration
        conan_config = load_yaml_config(self.config_dir / 'conan_packages.yaml')
        self.conan_package_config.update(conan_config)

        log.debug(f"Loaded configuration from {self.config_dir}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Get a configuration value with dict-like access."""
        return self._config[key]

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the configuration."""
        return key in self._config

    @property
    def munchified_config(self):
        """Return a munchified version of the config for backward compatibility."""
        try:
            from munch import Munch
            return Munch(self._config)
        except ImportError:
            # If munch is not available, return the config as-is
            return self._config

    def _get_current_environment(self) -> str:
        """Get the current environment (dev, staging, prod, etc.)."""
        import os
        return os.getenv('ENVIRONMENT', 'dev')


def get_conan_merged_configuration(config_path: Path) -> ConanMergedConfiguration:
    """Get a merged configuration loader for Conan."""
    config = ConanMergedConfiguration(config_path)
    config.load_config()
    return config


# Global config loader instance
_config_loader_instance = None


def get_config_loader():
    """Get the global configuration loader instance."""
    global _config_loader_instance
    if _config_loader_instance is None:
        # Try to find config directory
        config_dir = _find_config_directory()
        _config_loader_instance = ConanMergedConfiguration(config_dir)
        _config_loader_instance.load_config()
    return _config_loader_instance


def _find_config_directory() -> Path:
    """Find the configuration directory."""
    # Look in common locations
    candidates = [
        Path.cwd() / 'config',
        Path.cwd() / 'conf',
        Path.cwd() / 'Conf',
        Path.home() / '.config' / 'shared-dev-tools'
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate

    # Default to current directory config
    return Path.cwd() / 'config'