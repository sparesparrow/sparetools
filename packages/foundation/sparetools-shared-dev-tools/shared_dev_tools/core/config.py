"""
Configuration Management

Provides configuration loading and management utilities.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from shared_dev_tools.core.utilities import ConfigurationBase, load_yaml_config, save_yaml_config

log = logging.getLogger(__name__)


class ConfigLoader:
    """Configuration loader for various formats and sources."""

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.cwd() / 'config'
        self._configs = {}

    def load_yaml(self, name: str, subdir: Optional[str] = None) -> Dict[str, Any]:
        """Load a YAML configuration file."""
        config_path = self._get_config_path(name, 'yaml', subdir)
        config = load_yaml_config(config_path)
        self._configs[name] = config
        return config

    def save_yaml(self, name: str, config: Dict[str, Any], subdir: Optional[str] = None):
        """Save a YAML configuration file."""
        config_path = self._get_config_path(name, 'yaml', subdir)
        save_yaml_config(config_path, config)

    def get(self, name: str) -> Dict[str, Any]:
        """Get a loaded configuration."""
        return self._configs.get(name, {})

    def _get_config_path(self, name: str, ext: str, subdir: Optional[str] = None) -> Path:
        """Get the full path for a configuration file."""
        if subdir:
            config_dir = self.config_dir / subdir
        else:
            config_dir = self.config_dir

        return config_dir / f"{name}.{ext}"


# Global config loader instance
_config_loader = None


def get_config_loader() -> ConfigLoader:
    """Get the global configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


class ArtifactoryConfig(ConfigurationBase):
    """Configuration for Artifactory integration."""

    def __init__(self, config_file: Optional[Path] = None):
        super().__init__(config_file)

    def load_config(self):
        """Load Artifactory configuration."""
        if self.config_file and self.config_file.exists():
            self._config_data = load_yaml_config(self.config_file)
        else:
            # Default configuration
            self._config_data = {
                'url': 'https://artifactory.example.com',
                'repository': 'conan-local',
                'username': None,
                'password': None,
                'verify_ssl': True
            }

    def save_config(self):
        """Save Artifactory configuration."""
        if self.config_file:
            save_yaml_config(self.config_file, self._config_data)

    @property
    def url(self) -> str:
        return self.get('url')

    @property
    def repository(self) -> str:
        return self.get('repository')

    @property
    def username(self) -> Optional[str]:
        return self.get('username')

    @property
    def password(self) -> Optional[str]:
        return self.get('password')

    @property
    def verify_ssl(self) -> bool:
        return self.get('verify_ssl', True)