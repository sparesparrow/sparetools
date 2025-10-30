"""
Configuration Management Utilities

This module provides configuration management utilities for OpenSSL development tools.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Configuration manager for OpenSSL tools."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file or Path.home() / ".openssl-tools" / "config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def save_config(self) -> bool:
        """Save configuration to file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except IOError:
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
    
    def get_github_token(self) -> Optional[str]:
        """Get GitHub token from config or environment."""
        return self.get('github_token') or os.getenv('GITHUB_TOKEN')
    
    def get_github_username(self) -> Optional[str]:
        """Get GitHub username from config or environment."""
        return self.get('github_username') or os.getenv('GITHUB_USERNAME')
    
    def get_conan_home(self) -> Path:
        """Get Conan home directory."""
        conan_home = self.get('conan_home')
        if conan_home:
            return Path(conan_home)
        return Path.home() / ".conan2"
