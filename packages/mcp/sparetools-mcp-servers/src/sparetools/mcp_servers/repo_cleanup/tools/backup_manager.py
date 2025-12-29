"""Backup management tool for safe repository operations."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from mcp import Tool
except ImportError:
    from ..mcp_mock import Tool

from ..utils.validators import validate_repository_path


class BackupManager(Tool):
    """Backup manager for creating and managing repository backups."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the backup manager.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.backup_dir = Path(self.config.get("backup_dir", "/tmp/repo-backups"))
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        super().__init__(
            name="backup_manager",
            description="Create and manage repository backups for safe cleanup operations",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_path": {
                        "type": "string",
                        "description": "Path to the Git repository"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["create", "list", "restore", "cleanup"],
                        "description": "Backup operation to perform"
                    },
                    "backup_type": {
                        "type": "string",
                        "enum": ["full", "selective", "archive"],
                        "default": "full",
                        "description": "Type of backup to create"
                    },
                    "files_to_backup": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific files to backup (for selective backup)"
                    },
                    "backup_name": {
                        "type": "string",
                        "description": "Custom name for the backup"
                    },
                    "compression": {
                        "type": "boolean",
                        "default": True,
                        "description": "Compress backup archive"
                    },
                    "max_backups": {
                        "type": "integer",
                        "default": 10,
                        "description": "Maximum number of backups to keep"
                    }
                },
                "required": ["repository_path", "operation"]
            }
        )

    def _create_backup_name(self, repo_path: Path, backup_name: Optional[str] = None) -> str:
        """Create a backup name.

        Args:
            repo_path: Repository path
            backup_name: Custom backup name

        Returns:
            Backup name
        """
        repo_name = repo_path.name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if backup_name:
            return f"{repo_name}_{backup_name}_{timestamp}"
        else:
            return f"{repo_name}_backup_{timestamp}"

    def _create_full_backup(self, repo_path: Path, backup_name: str,
                          compression: bool = True) -> Optional[Path]:
        """Create a full repository backup.

        Args:
            repo_path: Repository path
            backup_name: Name for the backup
            compression: Whether to compress the backup

        Returns:
            Path to created backup
        """
        try:
            if compression:
                # Create compressed archive
                archive_name = f"{backup_name}.tar.gz"
                archive_path = self.backup_dir / archive_name

                # Create archive
                shutil.make_archive(
                    str(archive_path.with_suffix('')),  # Remove .gz extension for make_archive
                    'gztar',
                    repo_path
                )

                return archive_path.with_suffix('.tar.gz')
            else:
                # Create directory backup
                backup_path = self.backup_dir / backup_name
                backup_path.mkdir(parents=True, exist_ok=True)

                # Copy entire repository
                for item in repo_path.iterdir():
                    if item.name != '.git':  # Skip .git directory
                        dest = backup_path / item.name
                        if item.is_file():
                            shutil.copy2(item, dest)
                        elif item.is_dir():
                            shutil.copytree(item, dest, dirs_exist_ok=True)

                return backup_path

        except Exception as e:
            print(f"Full backup failed: {e}")
            return None

    def _create_selective_backup(self, repo_path: Path, files: List[Path],
                               backup_name: str, compression: bool = True) -> Optional[Path]:
        """Create a selective backup of specific files.

        Args:
            repo_path: Repository path
            files: Files to backup
            backup_name: Name for the backup
            compression: Whether to compress the backup

        Returns:
            Path to created backup
        """
        try:
            # Create temporary staging directory
            temp_dir = self.backup_dir / f"temp_{backup_name}"
            temp_dir.mkdir(parents=True, exist_ok=True)

            try:
                # Copy selected files
                for file_path in files:
                    if file_path.exists():
                        try:
                            rel_path = file_path.relative_to(repo_path)
                            dest_path = temp_dir / rel_path
                            dest_path.parent.mkdir(parents=True, exist_ok=True)

                            if file_path.is_file():
                                shutil.copy2(file_path, dest_path)
                            elif file_path.is_dir():
                                shutil.copytree(file_path, dest_path, dirs_exist_ok=True)
                        except ValueError:
                            # File not under repository root
                            continue

                if compression:
                    # Create compressed archive
                    archive_name = f"{backup_name}.tar.gz"
                    archive_path = self.backup_dir / archive_name

                    shutil.make_archive(
                        str(archive_path.with_suffix('')),
                        'gztar',
                        temp_dir
                    )

                    final_path = archive_path.with_suffix('.tar.gz')
                else:
                    # Move temp directory to final location
                    final_path = self.backup_dir / backup_name
                    if final_path.exists():
                        shutil.rmtree(final_path)
                    temp_dir.rename(final_path)

                return final_path

            finally:
                # Clean up temp directory if it still exists
                if temp_dir.exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception as e:
            print(f"Selective backup failed: {e}")
            return None

    def _list_backups(self, repo_path: Path) -> List[Dict[str, Any]]:
        """List available backups for a repository.

        Args:
            repo_path: Repository path

        Returns:
            List of backup information
        """
        repo_name = repo_path.name
        backups = []

        try:
            for item in self.backup_dir.iterdir():
                if item.name.startswith(f"{repo_name}_") and (item.is_file() or item.is_dir()):
                    # Get backup info
                    stat = item.stat()
                    backup_info = {
                        "name": item.name,
                        "path": str(item),
                        "size": stat.st_size,
                        "size_human": self._format_size(stat.st_size),
                        "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "type": "archive" if item.suffix == '.gz' else "directory",
                        "compressed": item.suffix == '.gz'
                    }
                    backups.append(backup_info)

            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x["created"], reverse=True)

        except Exception as e:
            print(f"Error listing backups: {e}")

        return backups

    def _restore_backup(self, backup_path: str, repo_path: Path,
                       target_path: Optional[Path] = None) -> bool:
        """Restore a backup.

        Args:
            backup_path: Path to backup file/directory
            repo_path: Repository path
            target_path: Where to restore (defaults to repo_path)

        Returns:
            True if successful
        """
        if target_path is None:
            target_path = repo_path

        backup = Path(backup_path)

        if not backup.exists():
            return False

        try:
            if backup.is_file() and backup.suffix == '.gz':
                # Extract archive
                shutil.unpack_archive(backup, target_path, 'gztar')
            elif backup.is_dir():
                # Copy directory contents
                for item in backup.iterdir():
                    dest = target_path / item.name
                    if item.is_file():
                        shutil.copy2(item, dest)
                    elif item.is_dir():
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                return False

            return True

        except Exception as e:
            print(f"Restore failed: {e}")
            return False

    def _cleanup_old_backups(self, repo_path: Path, max_backups: int = 10) -> int:
        """Clean up old backups, keeping only the most recent ones.

        Args:
            repo_path: Repository path
            max_backups: Maximum number of backups to keep

        Returns:
            Number of backups removed
        """
        backups = self._list_backups(repo_path)
        removed_count = 0

        if len(backups) > max_backups:
            # Sort by creation time and remove oldest
            backups_to_remove = backups[max_backups:]

            for backup in backups_to_remove:
                try:
                    backup_path = Path(backup["path"])
                    if backup_path.is_file():
                        backup_path.unlink()
                    elif backup_path.is_dir():
                        shutil.rmtree(backup_path)
                    removed_count += 1
                except Exception as e:
                    print(f"Failed to remove backup {backup['name']}: {e}")

        return removed_count

    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return ".1f"
            size_bytes /= 1024.0
        return ".1f"

    async def call(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the backup manager.

        Args:
            arguments: Tool arguments

        Returns:
            Backup operation results
        """
        repo_path_str = arguments.get("repository_path")
        if not repo_path_str:
            raise ValueError("repository_path is required")

        repo_path = Path(repo_path_str).resolve()
        validate_repository_path(repo_path)

        operation = arguments.get("operation")
        if not operation:
            raise ValueError("operation is required")

        if operation == "create":
            backup_type = arguments.get("backup_type", "full")
            backup_name = arguments.get("backup_name")
            compression = arguments.get("compression", True)
            max_backups = arguments.get("max_backups", 10)

            custom_name = self._create_backup_name(repo_path, backup_name)

            if backup_type == "full":
                backup_path = self._create_full_backup(repo_path, custom_name, compression)
            elif backup_type == "selective":
                files_to_backup = arguments.get("files_to_backup", [])
                if not files_to_backup:
                    return {
                        "operation": "create",
                        "success": False,
                        "message": "No files specified for selective backup"
                    }

                files_paths = [Path(f).resolve() for f in files_to_backup]
                backup_path = self._create_selective_backup(repo_path, files_paths, custom_name, compression)
            else:
                return {
                    "operation": operation,
                    "success": False,
                    "message": f"Unsupported backup type: {backup_type}"
                }

            if backup_path:
                # Clean up old backups
                removed_count = self._cleanup_old_backups(repo_path, max_backups)

                return {
                    "operation": "create",
                    "success": True,
                    "backup_path": str(backup_path),
                    "backup_name": backup_path.name,
                    "backup_type": backup_type,
                    "compressed": compression,
                    "size": backup_path.stat().st_size if backup_path.exists() else 0,
                    "old_backups_cleaned": removed_count
                }
            else:
                return {
                    "operation": "create",
                    "success": False,
                    "message": "Failed to create backup"
                }

        elif operation == "list":
            backups = self._list_backups(repo_path)

            return {
                "operation": "list",
                "success": True,
                "backups": backups,
                "total_backups": len(backups)
            }

        elif operation == "restore":
            backup_path = arguments.get("backup_path")
            if not backup_path:
                return {
                    "operation": "restore",
                    "success": False,
                    "message": "backup_path is required for restore operation"
                }

            target_path = arguments.get("target_path")
            if target_path:
                target_path = Path(target_path)

            success = self._restore_backup(backup_path, repo_path, target_path)

            return {
                "operation": "restore",
                "success": success,
                "backup_path": backup_path,
                "target_path": str(target_path) if target_path else str(repo_path)
            }

        elif operation == "cleanup":
            max_backups = arguments.get("max_backups", 10)
            removed_count = self._cleanup_old_backups(repo_path, max_backups)

            return {
                "operation": "cleanup",
                "success": True,
                "backups_removed": removed_count,
                "max_backups_kept": max_backups
            }

        else:
            return {
                "operation": operation,
                "success": False,
                "message": f"Unknown operation: {operation}"
            }