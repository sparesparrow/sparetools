"""Validation utilities."""

import os
from pathlib import Path
from typing import List, Optional

from .git_utils import git_utils


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_repository_path(repo_path: Path) -> None:
    """Validate that path is a valid Git repository.

    Args:
        repo_path: Path to validate

    Raises:
        ValidationError: If path is not a valid repository
    """
    if not repo_path.exists():
        raise ValidationError(f"Repository path does not exist: {repo_path}")

    if not repo_path.is_dir():
        raise ValidationError(f"Repository path is not a directory: {repo_path}")

    if not git_utils.is_git_repository(repo_path):
        raise ValidationError(f"Path is not a Git repository: {repo_path}")


def validate_file_paths(repo_path: Path, file_paths: List[Path]) -> List[Path]:
    """Validate that file paths exist and are within repository.

    Args:
        repo_path: Repository root path
        file_paths: List of file paths to validate

    Returns:
        List of validated file paths

    Raises:
        ValidationError: If any path is invalid
    """
    validated = []

    for file_path in file_paths:
        # Resolve to absolute path
        abs_path = file_path.resolve()

        # Check if file exists
        if not abs_path.exists():
            raise ValidationError(f"File does not exist: {file_path}")

        # Check if file is within repository
        try:
            abs_path.relative_to(repo_path.resolve())
        except ValueError:
            raise ValidationError(f"File is outside repository: {file_path}")

        validated.append(abs_path)

    return validated


def validate_patterns(patterns: List[str]) -> List[str]:
    """Validate glob patterns.

    Args:
        patterns: List of patterns to validate

    Returns:
        List of validated patterns

    Raises:
        ValidationError: If any pattern is invalid
    """
    # Basic validation - patterns should not be empty and not contain dangerous characters
    dangerous_chars = ['..', '<', '>', '|', '&', ';']

    for pattern in patterns:
        if not pattern.strip():
            raise ValidationError("Empty pattern found")

        for char in dangerous_chars:
            if char in pattern:
                raise ValidationError(f"Dangerous character '{char}' in pattern: {pattern}")

    return patterns


def validate_config(config: dict) -> dict:
    """Validate server configuration.

    Args:
        config: Configuration dictionary

    Returns:
        Validated configuration

    Raises:
        ValidationError: If configuration is invalid
    """
    # Validate repository path if provided
    if "repository_path" in config:
        repo_path = Path(config["repository_path"])
        validate_repository_path(repo_path)

    # Validate backup settings
    if "backup_enabled" in config:
        if not isinstance(config["backup_enabled"], bool):
            raise ValidationError("backup_enabled must be a boolean")

    if "backup_dir" in config:
        backup_dir = Path(config["backup_dir"])
        if not backup_dir.exists():
            try:
                backup_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValidationError(f"Cannot create backup directory: {e}")

    # Validate scan settings
    if "max_file_size" in config:
        max_size_str = str(config["max_file_size"]).upper()
        if max_size_str.endswith('MB'):
            try:
                int(max_size_str[:-2])
            except ValueError:
                raise ValidationError("Invalid max_file_size format")
        elif max_size_str.endswith('GB'):
            try:
                int(max_size_str[:-2])
            except ValueError:
                raise ValidationError("Invalid max_file_size format")

    return config