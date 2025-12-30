"""Template manager for SpareTools MCP Core.

This module provides the TemplateManager class that handles template
loading, storage, and retrieval.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from sparetools.mcp_core.core.config import MCPConfig
from sparetools.mcp_core.core.exceptions import TemplateError
from sparetools.mcp_core.templates.base import BaseTemplate
from sparetools.mcp_core.templates.types import (
    TemplateCategory,
    TemplateFile,
    TemplateMetadata,
    TemplateType,
)


class SimpleTemplate(BaseTemplate):
    """Simple template implementation for the manager."""

    def validate(self) -> bool:
        """Validate template configuration."""
        return bool(self.metadata.name and self.metadata.description)

    def apply(self, target_path: Union[str, Path]) -> None:
        """Apply template to target directory."""
        if not self.validate():
            raise ValueError("Template validation failed")

        target_path = Path(target_path)
        target_path.mkdir(parents=True, exist_ok=True)

        for file in self.files:
            file_path = target_path / file.path
            file_path.parent.mkdir(parents=True, exist_ok=True)

            content = self.substitute_variables(file.content)
            with open(file_path, "w") as f:
                f.write(content)


class TemplateManager:
    """Manager for handling template storage and retrieval."""

    def __init__(self, config: Optional[MCPConfig] = None) -> None:
        """Initialize the template manager.

        Args:
            config: Optional configuration instance
        """
        self.config = config or MCPConfig()
        self.templates: Dict[str, BaseTemplate] = {}
        self._categories: set[TemplateCategory] = set()
        self._tags: set[str] = set()

    def load_templates(self, directory: Optional[Union[str, Path]] = None) -> None:
        """Load templates from a directory.

        Args:
            directory: Directory to load templates from (defaults to config templates_dir)
        """
        if directory is None:
            directory = self.config.get_template_path()
        else:
            directory = Path(directory)

        if not directory.exists():
            return

        for template_dir in directory.iterdir():
            if not template_dir.is_dir():
                continue

            metadata_path = template_dir / "template.json"
            if not metadata_path.exists():
                continue

            try:
                with open(metadata_path) as f:
                    metadata_dict = json.load(f)

                metadata = TemplateMetadata.from_dict(metadata_dict)
                template = SimpleTemplate(metadata)

                # Load files
                files_dir = template_dir / "files"
                if files_dir.exists():
                    for file_path in files_dir.rglob("*"):
                        if file_path.is_file():
                            relative_path = file_path.relative_to(files_dir)
                            with open(file_path) as f:
                                content = f.read()
                            template.add_file(
                                TemplateFile(path=str(relative_path), content=content)
                            )

                self.register_template(template)

            except Exception:
                # Skip invalid templates
                continue

    def register_template(self, template: BaseTemplate) -> None:
        """Register a template with the manager.

        Args:
            template: Template to register
        """
        self.templates[template.metadata.name] = template

        if template.metadata.category:
            self._categories.add(template.metadata.category)
        self._tags.update(template.metadata.tags)

    def get_template(self, name: str) -> Optional[BaseTemplate]:
        """Get a template by name.

        Args:
            name: Template name

        Returns:
            Template if found, None otherwise
        """
        return self.templates.get(name)

    def get_templates_by_type(self, template_type: TemplateType) -> List[BaseTemplate]:
        """Get all templates of a specific type.

        Args:
            template_type: Type to filter by

        Returns:
            List of matching templates
        """
        return [t for t in self.templates.values() if t.metadata.type == template_type]

    def get_templates_by_category(
        self, category: TemplateCategory
    ) -> List[BaseTemplate]:
        """Get all templates in a category.

        Args:
            category: Category to filter by

        Returns:
            List of matching templates
        """
        return [t for t in self.templates.values() if t.metadata.category == category]

    def get_templates_by_tag(self, tag: str) -> List[BaseTemplate]:
        """Get all templates with a specific tag.

        Args:
            tag: Tag to filter by

        Returns:
            List of matching templates
        """
        return [t for t in self.templates.values() if tag in t.metadata.tags]

    def list_templates(self) -> List[str]:
        """List all template names.

        Returns:
            List of template names
        """
        return list(self.templates.keys())

    def list_categories(self) -> List[TemplateCategory]:
        """List all categories.

        Returns:
            List of categories
        """
        return list(self._categories)

    def list_tags(self) -> List[str]:
        """List all tags.

        Returns:
            List of tags
        """
        return list(self._tags)

    def create_template(
        self,
        name: str,
        description: str,
        template_type: TemplateType,
        category: Optional[TemplateCategory] = None,
        tags: Optional[List[str]] = None,
        variables: Optional[Dict[str, str]] = None,
        files: Optional[List[TemplateFile]] = None,
    ) -> BaseTemplate:
        """Create a new template.

        Args:
            name: Template name
            description: Template description
            template_type: Type of template
            category: Optional category
            tags: Optional list of tags
            variables: Optional variables dictionary
            files: Optional list of files

        Returns:
            Created template
        """
        metadata = TemplateMetadata(
            name=name,
            description=description,
            type=template_type,
            category=category,
            tags=tags or [],
            variables=variables or {},
        )

        template = SimpleTemplate(metadata)

        if files:
            template.add_files(files)

        self.register_template(template)
        return template

    def save_template(
        self, name: str, directory: Optional[Union[str, Path]] = None
    ) -> None:
        """Save a template to disk.

        Args:
            name: Template name to save
            directory: Directory to save to (defaults to config templates_dir)

        Raises:
            TemplateError: If template not found
        """
        template = self.get_template(name)
        if template is None:
            raise TemplateError(f"Template not found: {name}")

        if directory is None:
            directory = self.config.get_template_path()
        else:
            directory = Path(directory)

        template_dir = directory / name
        template.save(template_dir)

    def delete_template(self, name: str) -> bool:
        """Delete a template from the manager.

        Args:
            name: Template name to delete

        Returns:
            True if deleted, False if not found
        """
        if name not in self.templates:
            return False

        del self.templates[name]
        return True

    def apply_template(
        self,
        name: str,
        target_path: Union[str, Path],
        variables: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Apply a template to a target path.

        Args:
            name: Template name to apply
            target_path: Target directory path
            variables: Optional variables to override

        Raises:
            TemplateError: If template not found
        """
        template = self.get_template(name)
        if template is None:
            raise TemplateError(f"Template not found: {name}")

        # Set variables if provided
        if variables:
            for var_name, var_value in variables.items():
                template.set_variable(var_name, str(var_value))

        template.apply(target_path)
