"""
Core Utilities

Provides base classes and utilities for configuration and common operations.
"""

import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigurationBase(ABC):
    """Base class for configuration management."""

    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file
        self._config_data = {}
        self.load_config()

    @abstractmethod
    def load_config(self):
        """Load configuration from file or default values."""
        pass

    @abstractmethod
    def save_config(self):
        """Save configuration to file."""
        pass

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config_data.get(key, default)

    def set(self, key: str, value: Any):
        """Set a configuration value."""
        self._config_data[key] = value

    def update(self, config_dict: Dict[str, Any]):
        """Update multiple configuration values."""
        self._config_data.update(config_dict)


def setup_logging(level: str = "INFO", log_file: Optional[Path] = None):
    """Set up logging configuration."""
    # Convert string level to logging level
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    log_level = level_map.get(level.upper(), logging.INFO)

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[]
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        import yaml
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    except ImportError:
        # YAML not available, return empty config
        return {}
    except Exception:
        return {}


def save_yaml_config(config_path: Path, config_data: Dict[str, Any]):
    """Save configuration to YAML file."""
    try:
        import yaml
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
    except ImportError:
        # YAML not available, skip saving
        pass
    except Exception as e:
        logging.error(f"Failed to save config to {config_path}: {e}")


def get_environment_variable(name: str, default: Optional[str] = None) -> Optional[str]:
    """Get environment variable with optional default."""
    return os.getenv(name, default)


def set_environment_variable(name: str, value: str):
    """Set environment variable."""
    os.environ[name] = value


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


def ensure_path_exists(path: Path) -> Path:
    """Ensure a path exists, creating directories if necessary."""
    if path.suffix:  # It's a file
        path.parent.mkdir(parents=True, exist_ok=True)
    else:  # It's a directory
        path.mkdir(parents=True, exist_ok=True)
    return path