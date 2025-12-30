"""Prompt loader for SpareTools MCP Core.

This module provides functionality for loading prompt templates
from various sources (files, directories, remote repositories).
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set

from sparetools.mcp_core.core.base import BaseOrchestrator
from sparetools.mcp_core.core.config import MCPConfig
from sparetools.mcp_core.prompts.template import PromptTemplate

logger = logging.getLogger(__name__)


class PromptLoader(BaseOrchestrator):
    """Class for loading prompt templates from various sources."""

    def __init__(self, config: MCPConfig) -> None:
        """Initialize the prompt loader.

        Args:
            config: Configuration instance
        """
        super().__init__(config)
        self.templates: Dict[str, PromptTemplate] = {}
        self.categories: Set[str] = set()
        self.tags: Set[str] = set()

    async def initialize(self) -> None:
        """Initialize the prompt loader.

        Loads templates from the configured templates directory.
        """
        await super().initialize()
        try:
            await self.load_templates_from_directory(self.config.prompt_templates_dir)
        except FileNotFoundError:
            # Directory may not exist yet
            self.log_warning(f"Prompts directory not found: {self.config.prompt_templates_dir}")

    async def cleanup(self) -> None:
        """Clean up resources."""
        self.templates.clear()
        self.categories.clear()
        self.tags.clear()
        await super().cleanup()

    async def load_templates_from_directory(self, directory: Path) -> None:
        """Load all template files from a directory.

        Args:
            directory: Directory containing template files

        Raises:
            FileNotFoundError: If the directory doesn't exist
        """
        if not directory.exists():
            raise FileNotFoundError(f"Templates directory not found: {directory}")

        for file_path in directory.rglob("*.json"):
            try:
                template = PromptTemplate.from_file(file_path)
                if template.validate():
                    self.templates[template.name] = template

                    if template.category:
                        self.categories.add(str(template.category))
                    self.tags.update(template.tags)
                else:
                    self.log_warning(f"Invalid template: {file_path}")

            except (json.JSONDecodeError, ValueError) as e:
                self.log_error(f"Error loading template {file_path}", e)

    async def load_template_from_url(self, url: str) -> Optional[PromptTemplate]:
        """Load a template from a URL.

        Args:
            url: URL of the template JSON file

        Returns:
            Loaded template or None if loading failed
        """
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        self.log_error(
                            f"Failed to fetch template from {url}: Status {response.status}"
                        )
                        return None

                    data = await response.json()

                    # Support both formats
                    if "metadata" in data:
                        from sparetools.mcp_core.prompts.template import PromptMetadata

                        metadata = PromptMetadata.from_dict(data["metadata"])
                        template = PromptTemplate(
                            metadata=metadata,
                            content=data.get("content", ""),
                            examples=data.get("examples", []),
                        )
                    else:
                        # Create from flat format
                        template = PromptTemplate.from_file.__func__(
                            PromptTemplate, Path(url)
                        )

                    if template.validate():
                        return template
                    return None

        except ImportError:
            self.log_error("aiohttp is required for loading templates from URLs")
            return None
        except Exception as e:
            self.log_error(f"Error loading template from {url}", e)
            return None

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name.

        Args:
            name: Name of the template

        Returns:
            Template instance or None if not found
        """
        return self.templates.get(name)

    def get_templates_by_category(self, category: str) -> List[PromptTemplate]:
        """Get all templates in a category.

        Args:
            category: Category to filter by

        Returns:
            List of templates in the category
        """
        return [
            template
            for template in self.templates.values()
            if str(template.category) == category
        ]

    def get_templates_by_tag(self, tag: str) -> List[PromptTemplate]:
        """Get all templates with a specific tag.

        Args:
            tag: Tag to filter by

        Returns:
            List of templates with the tag
        """
        return [
            template for template in self.templates.values() if tag in template.tags
        ]

    def get_all_categories(self) -> List[str]:
        """Get all available categories.

        Returns:
            List of category names
        """
        return sorted(self.categories)

    def get_all_tags(self) -> List[str]:
        """Get all available tags.

        Returns:
            List of tag names
        """
        return sorted(self.tags)
