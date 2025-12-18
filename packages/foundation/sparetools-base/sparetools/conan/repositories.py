"""
Conan Repository Management

Generic utilities for managing different types of package repositories:
- Cloudsmith
- GitHub Packages
- Pip
- DockerHub
- Generic Conan remotes
"""

import logging
import os
from enum import Enum
from typing import Optional, Dict, Any

from .core import get_default_conan

log = logging.getLogger(__name__)


class RepositoryType(Enum):
    """Supported repository types."""
    CONAN = "conan"
    CLOUDSMITH = "cloudsmith"
    GITHUB = "github"
    PIP = "pip"
    DOCKER = "docker"
    GENERIC = "generic"


class RepositoryConfig:
    """Configuration for a package repository."""

    def __init__(self,
                 name: str,
                 url: str,
                 repo_type: RepositoryType,
                 credentials: Optional[Dict[str, str]] = None,
                 **kwargs):
        """
        Initialize repository configuration.

        Args:
            name: Repository name
            url: Repository URL
            repo_type: Type of repository
            credentials: Authentication credentials
            **kwargs: Additional configuration
        """
        self.name = name
        self.url = url
        self.repo_type = repo_type
        self.credentials = credentials or {}
        self.extra_config = kwargs

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'RepositoryConfig':
        """Create config from dictionary."""
        return cls(
            name=config_dict['name'],
            url=config_dict['url'],
            repo_type=RepositoryType(config_dict.get('type', 'generic')),
            credentials=config_dict.get('credentials', {}),
            **config_dict.get('config', {})
        )


class RepositoryManager:
    """Manages Conan repository configurations."""

    def __init__(self):
        """Initialize repository manager."""
        self.conan_path = get_default_conan()

    def setup_repository(self, config: RepositoryConfig) -> bool:
        """
        Set up a repository remote.

        Args:
            config: Repository configuration

        Returns:
            True if successful, False otherwise
        """
        if not self.conan_path:
            log.error("Conan executable not found")
            return False

        try:
            # Clean existing remotes if needed
            if config.extra_config.get('clean_existing', False):
                self._clean_remotes()

            # Add the remote
            success = self._add_remote(config)
            if not success:
                return False

            # Authenticate if credentials provided
            if config.credentials:
                success = self._authenticate_remote(config)

            return success

        except Exception as e:
            log.error(f"Failed to setup repository {config.name}: {e}")
            return False

    def _add_remote(self, config: RepositoryConfig) -> bool:
        """Add a Conan remote."""
        import subprocess

        try:
            result = subprocess.run(
                [self.conan_path, "remote", "add", config.name, config.url],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            log.error(f"Failed to add remote {config.name}: {e}")
            return False

    def _authenticate_remote(self, config: RepositoryConfig) -> bool:
        """Authenticate with a remote repository."""
        import subprocess

        username = config.credentials.get('username')
        password = config.credentials.get('password')
        token = config.credentials.get('token')

        if not username or (not password and not token):
            log.warning(f"No authentication credentials provided for {config.name}")
            return True  # Not an error, just no auth

        try:
            if token:
                # Use token for authentication
                result = subprocess.run(
                    [self.conan_path, "user", "-p", token, "-r", config.name, username],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                # Use username/password
                result = subprocess.run(
                    [self.conan_path, "user", "-p", password, "-r", config.name, username],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

            return result.returncode == 0

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            log.error(f"Failed to authenticate with {config.name}: {e}")
            return False

    def _clean_remotes(self) -> bool:
        """Clean all existing remotes."""
        import subprocess

        try:
            result = subprocess.run(
                [self.conan_path, "remote", "clean"],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            log.error(f"Failed to clean remotes: {e}")
            return False

    def enable_remote(self, name: str) -> bool:
        """
        Enable a Conan remote.

        Args:
            name: Remote name

        Returns:
            True if successful, False otherwise
        """
        import subprocess

        if not self.conan_path:
            return False

        try:
            result = subprocess.run(
                [self.conan_path, "remote", "enable", name],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            log.error(f"Failed to enable remote {name}: {e}")
            return False

    def disable_remote(self, name: str) -> bool:
        """
        Disable a Conan remote.

        Args:
            name: Remote name

        Returns:
            True if successful, False otherwise
        """
        import subprocess

        if not self.conan_path:
            return False

        try:
            result = subprocess.run(
                [self.conan_path, "remote", "disable", name],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            log.error(f"Failed to disable remote {name}: {e}")
            return False

    def remove_remote(self, name: str) -> bool:
        """
        Remove a Conan remote.

        Args:
            name: Remote name

        Returns:
            True if successful, False otherwise
        """
        import subprocess

        if not self.conan_path:
            return False

        try:
            result = subprocess.run(
                [self.conan_path, "remote", "remove", name],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            log.error(f"Failed to remove remote {name}: {e}")
            return False


# Convenience functions for backward compatibility and common use cases

def setup_cloudsmith_repository(name: str, organization: str, credentials: Dict[str, str]) -> bool:
    """
    Set up a Cloudsmith Conan repository.

    Args:
        name: Remote name
        organization: Cloudsmith organization
        credentials: Dict with 'token' key

    Returns:
        True if successful, False otherwise
    """
    url = f"https://conan.cloudsmith.io/{organization}"
    config = RepositoryConfig(
        name=name,
        url=url,
        repo_type=RepositoryType.CLOUDSMITH,
        credentials=credentials
    )

    manager = RepositoryManager()
    return manager.setup_repository(config)


def setup_github_repository(name: str, owner: str, repo: str, credentials: Dict[str, str]) -> bool:
    """
    Set up a GitHub Packages Conan repository.

    Args:
        name: Remote name
        owner: GitHub owner/organization
        repo: Repository name
        credentials: Dict with 'token' key

    Returns:
        True if successful, False otherwise
    """
    url = f"https://maven.pkg.github.com/{owner}/{repo}"
    config = RepositoryConfig(
        name=name,
        url=url,
        repo_type=RepositoryType.GITHUB,
        credentials=credentials
    )

    manager = RepositoryManager()
    return manager.setup_repository(config)


def setup_generic_conan_remote(name: str, url: str, credentials: Optional[Dict[str, str]] = None) -> bool:
    """
    Set up a generic Conan remote.

    Args:
        name: Remote name
        url: Remote URL
        credentials: Authentication credentials

    Returns:
        True if successful, False otherwise
    """
    config = RepositoryConfig(
        name=name,
        url=url,
        repo_type=RepositoryType.GENERIC,
        credentials=credentials
    )

    manager = RepositoryManager()
    return manager.setup_repository(config)


def enable_conan_remote(name: str) -> bool:
    """
    Enable a Conan remote.

    Args:
        name: Remote name

    Returns:
        True if successful, False otherwise
    """
    manager = RepositoryManager()
    return manager.enable_remote(name)


def disable_conan_remote(name: str) -> bool:
    """
    Disable a Conan remote.

    Args:
        name: Remote name

    Returns:
        True if successful, False otherwise
    """
    manager = RepositoryManager()
    return manager.disable_remote(name)


def remove_conan_remote(name: str) -> bool:
    """
    Remove a Conan remote.

    Args:
        name: Remote name

    Returns:
        True if successful, False otherwise
    """
    manager = RepositoryManager()
    return manager.remove_remote(name)