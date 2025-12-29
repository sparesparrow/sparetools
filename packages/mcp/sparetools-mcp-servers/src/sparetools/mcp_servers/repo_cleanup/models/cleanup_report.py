"""Data models for cleanup reports."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class CleanupOperation:
    """Details of a cleanup operation."""

    operation_id: str
    timestamp: datetime
    files_removed: List[Path]
    space_saved: int  # Bytes
    gitignore_updates: List[str]
    commit_sha: Optional[str] = None
    backup_created: bool = False
    backup_path: Optional[Path] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "operation_id": self.operation_id,
            "timestamp": self.timestamp.isoformat(),
            "files_removed": [str(p) for p in self.files_removed],
            "space_saved": self.space_saved,
            "gitignore_updates": self.gitignore_updates,
            "commit_sha": self.commit_sha,
            "backup_created": self.backup_created,
            "backup_path": str(self.backup_path) if self.backup_path else None,
        }


@dataclass
class CleanupReport:
    """Complete cleanup report."""

    operation_id: str
    repository_path: Path
    operations: List[CleanupOperation]
    total_space_saved: int
    total_files_removed: int
    errors: List[str]
    warnings: List[str]
    recommendations: List[str]
    duration: str  # Human readable
    success: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "operation_id": self.operation_id,
            "repository_path": str(self.repository_path),
            "operations": [op.to_dict() for op in self.operations],
            "total_space_saved": self.total_space_saved,
            "total_files_removed": self.total_files_removed,
            "errors": self.errors,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "duration": self.duration,
            "success": self.success,
        }