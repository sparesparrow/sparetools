"""Prompt template class for SpareTools MCP Core.

This module defines the PromptTemplate class that represents a single
prompt template with its metadata and rendering capabilities.
"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class PromptCategory(Enum):
    """Categories for organizing prompts."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    DOCUMENTATION = "documentation"
    CODE_GENERATION = "code_generation"
    REVIEW = "review"
    TESTING = "testing"
    DEBUGGING = "debugging"
    EMBEDDED = "embedded"
    DEPLOYMENT = "deployment"
    MCP = "mcp"

    def __str__(self) -> str:
        return self.value


@dataclass
class PromptMetadata:
    """Metadata for a prompt template."""

    name: str
    description: str
    category: PromptCategory
    version: str = "1.0.0"
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Union[str, List[str], Dict[str, str], None]]:
        """Convert metadata to dictionary format.

        Returns:
            Dictionary representation of the metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "category": str(self.category),
            "version": self.version,
            "author": self.author,
            "tags": self.tags,
            "variables": self.variables,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptMetadata":
        """Create metadata from dictionary.

        Args:
            data: Dictionary containing metadata fields

        Returns:
            PromptMetadata instance
        """
        data = data.copy()
        # Convert string values to enums
        if "category" in data and isinstance(data["category"], str):
            data["category"] = PromptCategory(data["category"])

        return cls(**data)


@dataclass
class PromptTemplate:
    """Class representing a prompt template."""

    metadata: PromptMetadata
    content: str
    examples: List[Dict[str, str]] = field(default_factory=list)

    # Aliases for convenience
    @property
    def name(self) -> str:
        """Get the template name."""
        return self.metadata.name

    @property
    def category(self) -> PromptCategory:
        """Get the template category."""
        return self.metadata.category

    @property
    def tags(self) -> List[str]:
        """Get the template tags."""
        return self.metadata.tags

    @classmethod
    def from_file(cls, path: Path) -> "PromptTemplate":
        """Load a prompt template from a JSON file.

        Args:
            path: Path to the JSON template file

        Returns:
            Loaded PromptTemplate instance

        Raises:
            FileNotFoundError: If the template file doesn't exist
            ValueError: If the template is invalid
        """
        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {path}")

        with open(path) as f:
            data = json.load(f)

        # Support both flat and nested formats
        if "metadata" in data:
            metadata = PromptMetadata.from_dict(data["metadata"])
            content = data.get("content", "")
            examples = data.get("examples", [])
        else:
            # Flat format (like mcp-prompts uses)
            metadata = PromptMetadata(
                name=data.get("id", data.get("name", path.stem)),
                description=data.get("description", ""),
                category=PromptCategory(data.get("category", "system")),
                version=str(data.get("version", "1.0.0")),
                author=data.get("author"),
                tags=data.get("tags", []),
                variables={v: "" for v in data.get("variables", [])},
            )
            content = data.get("content", "")
            examples = data.get("examples", [])

        return cls(metadata=metadata, content=content, examples=examples)

    def render(self, variables: Dict[str, Any]) -> str:
        """Render the template with the provided variables.

        Args:
            variables: Dictionary of variables to substitute in the template

        Returns:
            Rendered prompt string

        Raises:
            KeyError: If a required variable is missing
        """
        result = self.content

        # Extract all variables from content using regex
        # Match both {{ var }} and {{var}} patterns
        pattern = r"\{\{\s*(\w+)\s*\}\}"
        content_vars = set(re.findall(pattern, result))

        # Check if required metadata variables are provided
        for var_name, var_desc in self.metadata.variables.items():
            if var_name not in variables:
                raise KeyError(f"Missing required variable '{var_name}': {var_desc}")

        # Check if all content variables are provided (if no metadata variables defined)
        if not self.metadata.variables:
            for var_name in content_vars:
                if var_name not in variables:
                    raise KeyError(f"Missing required variable '{var_name}'")

        # Substitute all provided variables
        for var_name, var_value in variables.items():
            # Support both {{ var }} and {{var}} formats
            placeholder_with_spaces = f"{{{{ {var_name} }}}}"
            placeholder_without_spaces = f"{{{{{var_name}}}}}"
            result = result.replace(placeholder_with_spaces, str(var_value))
            result = result.replace(placeholder_without_spaces, str(var_value))

        return result

    def to_dict(self) -> Dict[str, Any]:
        """Convert the template to a dictionary.

        Returns:
            Dictionary representation of the template
        """
        return {
            "metadata": self.metadata.to_dict(),
            "content": self.content,
            "examples": self.examples,
        }

    def save(self, path: Path) -> None:
        """Save the template to a JSON file.

        Args:
            path: Path where to save the template
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def validate(self) -> bool:
        """Validate the template.

        Returns:
            True if valid, False otherwise
        """
        if not self.metadata.name:
            return False

        if not self.content:
            return False

        if not self.metadata.description:
            return False

        return True
