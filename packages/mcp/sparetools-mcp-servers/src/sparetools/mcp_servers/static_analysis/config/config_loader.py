"""
Configuration Loader

Loads and manages configuration files for the static analysis MCP server.
Supports YAML configuration files with environment variable overrides.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class ServerConfig:
    """Server configuration container"""
    name: str
    version: str
    timeouts: Dict[str, int]
    limits: Dict[str, int]
    mcp_prompts: Dict[str, Any]
    tool_registry: Dict[str, Any]
    workflows: Dict[str, Any]
    sessions: Dict[str, Any]
    logging: Dict[str, Any]
    security: Dict[str, Any]
    project_profiles: Dict[str, Any]
    output: Dict[str, Any]
    performance: Dict[str, Any]
    monitoring: Dict[str, Any]


class ConfigLoader:
    """
    Loads and manages configuration from YAML files with environment variable support
    """

    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """
        Initialize config loader

        Args:
            config_dir: Directory containing configuration files
        """
        if config_dir is None:
            # Default to the config directory relative to this file
            current_dir = Path(__file__).parent
            self.config_dir = current_dir
        else:
            self.config_dir = Path(config_dir)

        self._config_cache: Dict[str, Any] = {}
        self._server_config: Optional[ServerConfig] = None

    @lru_cache(maxsize=32)
    def load_yaml_config(self, filename: str) -> Dict[str, Any]:
        """
        Load a YAML configuration file with caching

        Args:
            filename: Name of the YAML file (without .yaml extension)

        Returns:
            Configuration dictionary
        """
        config_path = self.config_dir / f"{filename}.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Apply environment variable overrides
        config = self._apply_env_overrides(config, filename)

        self._config_cache[filename] = config
        return config

    def _apply_env_overrides(self, config: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """
        Apply environment variable overrides to configuration

        Environment variables should be prefixed with the config filename,
        e.g., STATIC_ANALYSIS_SERVER__NAME for server.name
        """
        prefix = filename.upper().replace('-', '_') + '__'

        def apply_overrides(data: Any, path: str = "") -> Any:
            if isinstance(data, dict):
                result = {}
                for key, value in data.items():
                    env_key = f"{prefix}{path}{key}".upper()
                    env_value = os.getenv(env_key)

                    if env_value is not None:
                        # Try to parse as YAML for complex values
                        try:
                            parsed_value = yaml.safe_load(env_value)
                            result[key] = parsed_value
                        except yaml.YAMLError:
                            # Treat as string
                            result[key] = env_value
                    else:
                        result[key] = apply_overrides(value, f"{path}{key}__")
                return result
            elif isinstance(data, list):
                return [apply_overrides(item, path) for item in data]
            else:
                return data

        return apply_overrides(config)

    def get_server_config(self) -> ServerConfig:
        """Get the complete server configuration"""
        if self._server_config is None:
            config = self.load_yaml_config("default_config")
            self._server_config = ServerConfig(**config)

        return self._server_config

    def get_project_profile(self, project_type: str) -> Dict[str, Any]:
        """Get configuration for a specific project type"""
        profiles = self.load_yaml_config("project_profiles")

        # Try exact match first
        if project_type in profiles:
            return profiles[project_type]

        # Try to find a matching profile
        for profile_name, profile_config in profiles.items():
            if profile_name != "default":
                languages = profile_config.get('languages', [])
                if project_type.lower() in [lang.lower() for lang in languages]:
                    return profile_config

        # Return default profile
        return profiles.get('default', {})

    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """Get configuration for a specific tool"""
        try:
            return self.load_yaml_config(f"tool_configs/{tool_name}")
        except FileNotFoundError:
            # Return minimal default config
            return {
                'tool': {
                    'name': tool_name,
                    'enabled': True
                },
                'default_args': [],
                'timeout': 300
            }

    def get_mcp_prompts_config(self) -> Dict[str, Any]:
        """Get MCP-Prompts integration configuration"""
        config = self.get_server_config()
        mcp_config = config.mcp_prompts.copy()

        # Override with environment variables
        mcp_config['server_url'] = os.getenv('MCP_PROMPTS_SERVER_URL', mcp_config['server_url'])
        mcp_config['api_key'] = os.getenv('MCP_PROMPTS_API_KEY', mcp_config.get('api_key'))

        return mcp_config

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        config = self.get_server_config()
        logging_config = config.logging.copy()

        # Expand user paths
        if 'file' in logging_config and 'path' in logging_config['file']:
            logging_config['file']['path'] = os.path.expanduser(logging_config['file']['path'])

        return logging_config

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        config = self.get_server_config()
        return config.security

    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        config = self.get_server_config()
        return config.performance

    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a tool is enabled in configuration"""
        tool_config = self.get_tool_config(tool_name)
        return tool_config.get('tool', {}).get('enabled', True)

    def get_tool_timeout(self, tool_name: str) -> int:
        """Get timeout configuration for a tool"""
        tool_config = self.get_tool_config(tool_name)
        return tool_config.get('timeout', 300)  # Default 5 minutes

    def get_project_quality_gates(self, project_type: str) -> Dict[str, Any]:
        """Get quality gates for a project type"""
        profile = self.get_project_profile(project_type)
        return profile.get('quality_gates', {})

    def validate_configuration(self) -> List[str]:
        """Validate the current configuration"""
        errors = []

        try:
            config = self.get_server_config()

            # Validate required fields
            required_fields = ['name', 'version', 'timeouts', 'limits']
            for field in required_fields:
                if not hasattr(config, field):
                    errors.append(f"Missing required configuration field: {field}")

            # Validate MCP-Prompts configuration
            if config.mcp_prompts.get('enabled', False):
                server_url = config.mcp_prompts.get('server_url')
                if not server_url:
                    errors.append("MCP-Prompts enabled but server_url not configured")

            # Validate tool configurations
            for tool_name in config.tool_registry.get('tools', {}):
                if not self.is_tool_enabled(tool_name):
                    continue

                try:
                    tool_config = self.get_tool_config(tool_name)
                    # Basic validation could be added here
                except Exception as e:
                    errors.append(f"Invalid tool configuration for {tool_name}: {e}")

        except Exception as e:
            errors.append(f"Configuration validation failed: {e}")

        return errors

    def reload_config(self):
        """Reload all cached configurations"""
        self._config_cache.clear()
        self._server_config = None
        self.load_yaml_config.cache_clear()  # Clear lru_cache


# Global config loader instance
_config_loader: Optional[ConfigLoader] = None


def get_config_loader() -> ConfigLoader:
    """Get the global configuration loader instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


def load_server_config() -> ServerConfig:
    """Load server configuration"""
    return get_config_loader().get_server_config()


def load_tool_config(tool_name: str) -> Dict[str, Any]:
    """Load configuration for a specific tool"""
    return get_config_loader().get_tool_config(tool_name)


def load_project_profile(project_type: str) -> Dict[str, Any]:
    """Load configuration for a project type"""
    return get_config_loader().get_project_profile(project_type)