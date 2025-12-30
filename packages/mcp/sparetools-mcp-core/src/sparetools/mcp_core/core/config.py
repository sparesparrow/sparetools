"""Configuration management for SpareTools MCP Core.

This module provides configuration management functionality through Pydantic models,
including settings validation and loading from various sources.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union
import json
import os

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Settings model for MCP Core utilities."""

    # Project paths
    workspace_dir: Path = Field(
        default_factory=Path.cwd,
        description="Root directory for the workspace",
    )
    templates_dir: Path = Field(
        default=Path("templates"),
        description="Directory containing project templates",
    )
    prompts_dir: Path = Field(
        default=Path("prompts"),
        description="Directory containing prompt templates",
    )
    resources_dir: Path = Field(
        default=Path("resources"),
        description="Directory containing project resources",
    )
    output_dir: Path = Field(
        default=Path("output"),
        description="Directory for generated output",
    )

    # Server settings
    host: str = Field(
        default="localhost",
        description="Host to bind the server to",
    )
    port: int = Field(
        default=8000,
        description="Port to bind the server to",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    # Component settings
    mermaid_path: Optional[str] = Field(
        default=None,
        description="Path to Mermaid CLI executable",
    )
    template_extensions: Dict[str, str] = Field(
        default={
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".md": "markdown",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".json": "json",
        },
        description="Mapping of file extensions to template types",
    )

    model_config = {"arbitrary_types_allowed": True}


class MCPConfig:
    """Configuration manager for MCP utilities."""

    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        env_prefix: str = "MCP_",
    ) -> None:
        """Initialize configuration manager.

        Args:
            config_path: Optional path to configuration file
            env_prefix: Prefix for environment variables
        """
        self.config_path = Path(config_path) if config_path else None
        self.env_prefix = env_prefix
        self.settings = Settings()
        self.name = "mcp-core"

    def load_config(self) -> None:
        """Load configuration from file and environment variables."""
        if self.config_path and self.config_path.exists():
            config_data = self._load_config_file(self.config_path)
            self.settings = Settings(**config_data)

        # Update with environment variables
        self._update_from_env()

        # Ensure directories exist
        self._create_directories()

    def _load_config_file(self, path: Path) -> Dict[str, Any]:
        """Load configuration from file.

        Args:
            path: Path to configuration file

        Returns:
            Configuration data dictionary
        """
        if path.suffix in [".yml", ".yaml"]:
            if yaml is None:
                raise ImportError("PyYAML is required for YAML config files")
            with open(path) as f:
                return yaml.safe_load(f)
        elif path.suffix == ".json":
            with open(path) as f:
                return json.load(f)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")

    def _update_from_env(self) -> None:
        """Update settings from environment variables."""
        for field_name in self.settings.model_fields:
            env_name = f"{self.env_prefix}{field_name.upper()}"
            env_value = os.environ.get(env_name)
            if env_value is not None:
                # Handle path fields
                if field_name.endswith("_dir") or field_name.endswith("_path"):
                    setattr(self.settings, field_name, Path(env_value))
                elif field_name in ("debug",):
                    setattr(
                        self.settings, field_name, env_value.lower() in ("true", "1", "yes")
                    )
                elif field_name == "port":
                    setattr(self.settings, field_name, int(env_value))
                else:
                    setattr(self.settings, field_name, env_value)

    def _create_directories(self) -> None:
        """Create required directories if they don't exist."""
        directories = [
            self.settings.templates_dir,
            self.settings.prompts_dir,
            self.settings.resources_dir,
            self.settings.output_dir,
        ]

        for directory in directories:
            if not directory.is_absolute():
                directory = self.settings.workspace_dir / directory
            directory.mkdir(parents=True, exist_ok=True)

    def get_workspace_path(self, *paths: str) -> Path:
        """Get a path relative to the workspace directory.

        Args:
            *paths: Path components to join

        Returns:
            Resolved workspace path
        """
        return self.settings.workspace_dir.joinpath(*paths)

    def get_template_path(self, *paths: str) -> Path:
        """Get a path relative to the templates directory.

        Args:
            *paths: Path components to join

        Returns:
            Resolved template path
        """
        base = self.settings.templates_dir
        if not base.is_absolute():
            base = self.settings.workspace_dir / base
        return base.joinpath(*paths)

    def get_prompt_path(self, *paths: str) -> Path:
        """Get a path relative to the prompts directory.

        Args:
            *paths: Path components to join

        Returns:
            Resolved prompt path
        """
        base = self.settings.prompts_dir
        if not base.is_absolute():
            base = self.settings.workspace_dir / base
        return base.joinpath(*paths)

    def get_resource_path(self, *paths: str) -> Path:
        """Get a path relative to the resources directory.

        Args:
            *paths: Path components to join

        Returns:
            Resolved resource path
        """
        base = self.settings.resources_dir
        if not base.is_absolute():
            base = self.settings.workspace_dir / base
        return base.joinpath(*paths)

    @property
    def prompt_templates_dir(self) -> Path:
        """Get the prompt templates directory."""
        return self.get_prompt_path()
