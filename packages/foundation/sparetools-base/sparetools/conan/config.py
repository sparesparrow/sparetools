"""
Conan Configuration Management

Handles configuration for different repository types and Conan settings.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

import yaml

from .repositories import RepositoryConfig, RepositoryType

log = logging.getLogger(__name__)


class ConanRepositoryConfig:
    """Configuration for Conan repositories."""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize repository configuration.

        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or self._get_default_config_path()
        self.config = self._load_config()

    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        config_dir = Path.home() / ".sparetools"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "conan_repositories.yaml")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not Path(self.config_file).exists():
            return self._create_default_config()

        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f) or self._create_default_config()
        except (yaml.YAMLError, IOError) as e:
            log.warning(f"Failed to load config file {self.config_file}: {e}")
            return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        return {
            'version': '1.0',
            'repositories': {},
            'defaults': {
                'remote_name': 'sparetools',
                'parallel_download': 4
            }
        }

    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                yaml.safe_dump(self.config, f, default_flow_style=False)
        except IOError as e:
            log.error(f"Failed to save config file {self.config_file}: {e}")

    def add_repository(self, name: str, config: RepositoryConfig) -> None:
        """
        Add a repository configuration.

        Args:
            name: Repository name
            config: Repository configuration
        """
        if 'repositories' not in self.config:
            self.config['repositories'] = {}

        self.config['repositories'][name] = {
            'name': config.name,
            'url': config.url,
            'type': config.repo_type.value,
            'credentials': config.credentials,
            'config': config.extra_config
        }
        self.save_config()

    def get_repository(self, name: str) -> Optional[RepositoryConfig]:
        """
        Get repository configuration by name.

        Args:
            name: Repository name

        Returns:
            RepositoryConfig or None
        """
        repo_data = self.config.get('repositories', {}).get(name)
        if not repo_data:
            return None

        return RepositoryConfig(
            name=repo_data['name'],
            url=repo_data['url'],
            repo_type=RepositoryType(repo_data.get('type', 'generic')),
            credentials=repo_data.get('credentials', {}),
            **repo_data.get('config', {})
        )

    def list_repositories(self) -> List[str]:
        """
        List all configured repository names.

        Returns:
            List of repository names
        """
        return list(self.config.get('repositories', {}).keys())

    def remove_repository(self, name: str) -> bool:
        """
        Remove a repository configuration.

        Args:
            name: Repository name

        Returns:
            True if removed, False if not found
        """
        if name in self.config.get('repositories', {}):
            del self.config['repositories'][name]
            self.save_config()
            return True
        return False

    def get_default_remote_name(self) -> str:
        """Get default remote name."""
        return self.config.get('defaults', {}).get('remote_name', 'sparetools')

    def set_default_remote_name(self, name: str) -> None:
        """Set default remote name."""
        if 'defaults' not in self.config:
            self.config['defaults'] = {}
        self.config['defaults']['remote_name'] = name
        self.save_config()


# Predefined repository templates

CLOUDSMITH_TEMPLATE = """
# Cloudsmith Repository Configuration Template
# Replace with your actual values

repositories:
  my-cloudsmith-repo:
    name: my-cloudsmith
    url: https://conan.cloudsmith.io/my-organization
    type: cloudsmith
    credentials:
      token: YOUR_API_TOKEN_HERE
    config:
      clean_existing: false

defaults:
  remote_name: my-cloudsmith
  parallel_download: 4
"""

GITHUB_PACKAGES_TEMPLATE = """
# GitHub Packages Repository Configuration Template
# Replace with your actual values

repositories:
  my-github-repo:
    name: my-github
    url: https://maven.pkg.github.com/my-owner/my-repo
    type: github
    credentials:
      token: YOUR_GITHUB_TOKEN_HERE
    config:
      clean_existing: false

defaults:
  remote_name: my-github
  parallel_download: 4
"""

GENERIC_CONAN_TEMPLATE = """
# Generic Conan Repository Configuration Template
# Replace with your actual values

repositories:
  my-conan-repo:
    name: my-conan
    url: https://my-conan-server.com
    type: conan
    credentials:
      username: YOUR_USERNAME
      password: YOUR_PASSWORD
    config:
      clean_existing: false

defaults:
  remote_name: my-conan
  parallel_download: 4
"""


def create_config_template(repo_type: str) -> str:
    """
    Get configuration template for repository type.

    Args:
        repo_type: Repository type ('cloudsmith', 'github', 'generic')

    Returns:
        YAML configuration template
    """
    templates = {
        'cloudsmith': CLOUDSMITH_TEMPLATE,
        'github': GITHUB_PACKAGES_TEMPLATE,
        'generic': GENERIC_CONAN_TEMPLATE
    }

    return templates.get(repo_type.lower(), GENERIC_CONAN_TEMPLATE)


def load_repositories_from_config(config_file: str) -> Dict[str, RepositoryConfig]:
    """
    Load repository configurations from a YAML file.

    Args:
        config_file: Path to configuration file

    Returns:
        Dictionary of repository configurations
    """
    config_manager = ConanRepositoryConfig(config_file)
    repositories = {}

    for name in config_manager.list_repositories():
        repo_config = config_manager.get_repository(name)
        if repo_config:
            repositories[name] = repo_config

    return repositories