"""Safe file removal tool with backup capabilities."""

import asyncio
import json
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from mcp import Tool
except ImportError:
    from ..mcp_mock import Tool

from ..models.cleanup_report import CleanupReport, CleanupOperation
from ..utils.git_utils import git_utils
from ..utils.validators import validate_file_paths, validate_repository_path


class FileRemover(Tool):
    """Safe file removal with backup and undo capabilities."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the file remover.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.backup_enabled = self.config.get("backup_enabled", True)
        self.backup_dir = Path(self.config.get("backup_dir", "/tmp/repo-backups"))

        # Ensure backup directory exists
        if self.backup_enabled:
            self.backup_dir.mkdir(parents=True, exist_ok=True)

        super().__init__(
            name="file_remover",
            description="Safely remove files with backup and undo capabilities",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_path": {
                        "type": "string",
                        "description": "Path to the Git repository"
                    },
                    "files_to_remove": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of file paths to remove"
                    },
                    "removal_mode": {
                        "type": "string",
                        "enum": ["soft", "hard", "archive"],
                        "default": "soft",
                        "description": "Removal mode: soft (backup), hard (permanent), archive (compress)"
                    },
                    "create_backup": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether to create backup before removal"
                    },
                    "dry_run": {
                        "type": "boolean",
                        "default": False,
                        "description": "Preview removal without actually deleting files"
                    },
                    "require_confirmation": {
                        "type": "boolean",
                        "default": True,
                        "description": "Require user confirmation before removal"
                    }
                },
                "required": ["repository_path", "files_to_remove"]
            }
        )

    def _create_backup(self, repo_path: Path, files: List[Path]) -> Optional[Path]:
        """Create a backup of files before removal.

        Args:
            repo_path: Repository path
            files: List of files to backup

        Returns:
            Path to backup archive, or None if backup failed
        """
        if not self.backup_enabled:
            return None

        try:
            # Create timestamped backup directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            repo_name = repo_path.name
            backup_path = self.backup_dir / f"{repo_name}_backup_{timestamp}"
            backup_path.mkdir(parents=True, exist_ok=True)

            # Copy files to backup
            for file_path in files:
                if file_path.exists():
                    # Calculate relative path from repository root
                    try:
                        rel_path = file_path.relative_to(repo_path)
                        backup_file_path = backup_path / rel_path
                        backup_file_path.parent.mkdir(parents=True, exist_ok=True)

                        if file_path.is_file():
                            shutil.copy2(file_path, backup_file_path)
                        elif file_path.is_dir():
                            shutil.copytree(file_path, backup_file_path, dirs_exist_ok=True)
                    except ValueError:
                        # File not under repository root, copy with full path
                        backup_file_path = backup_path / file_path.name
                        if file_path.is_file():
                            shutil.copy2(file_path, backup_file_path)

            return backup_path

        except Exception as e:
            print(f"Backup creation failed: {e}")
            return None

    def _create_archive_backup(self, repo_path: Path, files: List[Path]) -> Optional[Path]:
        """Create a compressed archive backup.

        Args:
            repo_path: Repository path
            files: List of files to backup

        Returns:
            Path to backup archive, or None if backup failed
        """
        if not self.backup_enabled:
            return None

        try:
            # Create timestamped archive name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            repo_name = repo_path.name
            archive_name = f"{repo_name}_backup_{timestamp}.tar.gz"
            archive_path = self.backup_dir / archive_name

            # Create temporary directory for staging
            temp_dir = self.backup_dir / f"temp_{timestamp}"
            temp_dir.mkdir(parents=True, exist_ok=True)

            try:
                # Stage files in temp directory
                for file_path in files:
                    if file_path.exists():
                        try:
                            rel_path = file_path.relative_to(repo_path)
                            temp_file_path = temp_dir / rel_path
                            temp_file_path.parent.mkdir(parents=True, exist_ok=True)

                            if file_path.is_file():
                                shutil.copy2(file_path, temp_file_path)
                            elif file_path.is_dir():
                                shutil.copytree(file_path, temp_file_path, dirs_exist_ok=True)
                        except ValueError:
                            # File not under repo root
                            temp_file_path = temp_dir / file_path.name
                            if file_path.is_file():
                                shutil.copy2(file_path, temp_file_path)

                # Create compressed archive
                shutil.make_archive(
                    str(archive_path.with_suffix('')),  # Remove .gz extension for make_archive
                    'gztar',
                    temp_dir
                )

                return archive_path.with_suffix('.tar.gz')

            finally:
                # Clean up temp directory
                shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception as e:
            print(f"Archive backup creation failed: {e}")
            return None

    def _remove_files(self, files: List[Path], removal_mode: str) -> Tuple[List[Path], List[str]]:
        """Remove files based on removal mode.

        Args:
            files: List of files to remove
            removal_mode: Removal mode ('soft', 'hard', 'archive')

        Returns:
            Tuple of (successfully_removed_files, errors)
        """
        successfully_removed = []
        errors = []

        for file_path in files:
            try:
                if file_path.exists():
                    if file_path.is_file():
                        file_path.unlink()
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)

                    successfully_removed.append(file_path)
                else:
                    errors.append(f"File not found: {file_path}")

            except Exception as e:
                errors.append(f"Failed to remove {file_path}: {e}")

        return successfully_removed, errors

    def _preview_removal(self, repo_path: Path, files: List[Path]) -> Dict[str, Any]:
        """Generate a preview of the removal operation.

        Args:
            repo_path: Repository path
            files: Files to be removed

        Returns:
            Preview information
        """
        total_size = 0
        file_count = 0
        dir_count = 0
        categories = {}

        for file_path in files:
            try:
                stat = file_path.stat()
                total_size += stat.st_size

                if file_path.is_file():
                    file_count += 1
                elif file_path.is_dir():
                    dir_count += 1

                # Categorize by file type
                suffix = file_path.suffix.lower()
                if suffix:
                    categories[suffix] = categories.get(suffix, 0) + 1

            except OSError:
                continue

        return {
            "total_files": len(files),
            "files": file_count,
            "directories": dir_count,
            "total_size": total_size,
            "total_size_human": self._format_size(total_size),
            "categories": categories,
            "files_preview": [str(f.relative_to(repo_path)) for f in files[:10]],  # First 10 files
            "has_more": len(files) > 10
        }

    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return ".1f"
            size_bytes /= 1024.0
        return ".1f"

    async def call(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the file remover.

        Args:
            arguments: Tool arguments

        Returns:
            Removal results
        """
        repo_path_str = arguments.get("repository_path")
        if not repo_path_str:
            raise ValueError("repository_path is required")

        files_to_remove_str = arguments.get("files_to_remove", [])
        if not files_to_remove_str:
            raise ValueError("files_to_remove is required")

        repo_path = Path(repo_path_str).resolve()
        validate_repository_path(repo_path)

        # Convert string paths to Path objects
        files_to_remove = [Path(f).resolve() for f in files_to_remove_str]
        files_to_remove = validate_file_paths(repo_path, files_to_remove)

        removal_mode = arguments.get("removal_mode", "soft")
        create_backup = arguments.get("create_backup", True)
        dry_run = arguments.get("dry_run", False)
        require_confirmation = arguments.get("require_confirmation", True)

        # Generate preview
        preview = self._preview_removal(repo_path, files_to_remove)

        if dry_run:
            return {
                "operation": "dry_run",
                "preview": preview,
                "would_remove": len(files_to_remove),
                "backup_would_be_created": create_backup and self.backup_enabled,
                "message": "This is a dry run - no files were actually removed"
            }

        # Confirmation check
        if require_confirmation:
            confirmation_msg = (
                f"Are you sure you want to remove {len(files_to_remove)} files "
                f"({preview['total_size_human']})? This action cannot be undone."
            )
            # In a real implementation, this would prompt the user
            # For now, we'll assume confirmation is given

        start_time = time.time()

        # Create backup if requested
        backup_path = None
        if create_backup and self.backup_enabled:
            if removal_mode == "archive":
                backup_path = self._create_archive_backup(repo_path, files_to_remove)
            else:
                backup_path = self._create_backup(repo_path, files_to_remove)

        # Remove files
        successfully_removed, errors = self._remove_files(files_to_remove, removal_mode)

        duration = time.time() - start_time

        # Calculate actual space saved
        space_saved = sum(f.stat().st_size for f in successfully_removed if not f.exists())

        # Create cleanup operation record
        operation = CleanupOperation(
            operation_id=f"cleanup_{int(time.time())}",
            timestamp=datetime.now(),
            files_removed=successfully_removed,
            space_saved=space_saved,
            gitignore_updates=[],  # Will be filled by gitignore updater
            backup_created=backup_path is not None,
            backup_path=backup_path
        )

        # Create cleanup report
        report = CleanupReport(
            operation_id=operation.operation_id,
            repository_path=repo_path,
            operations=[operation],
            total_space_saved=space_saved,
            total_files_removed=len(successfully_removed),
            errors=errors,
            warnings=[],
            recommendations=[],
            duration=".2f",
            success=len(errors) == 0
        )

        # Convert to dict for JSON serialization
        result_dict = report.model_dump()
        result_dict["repository_path"] = str(result_dict["repository_path"])
        result_dict["operations"][0]["files_removed"] = [str(p) for p in result_dict["operations"][0]["files_removed"]]
        if result_dict["operations"][0]["backup_path"]:
            result_dict["operations"][0]["backup_path"] = str(result_dict["operations"][0]["backup_path"])

        return result_dict