"""Data models for scan results."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class FileInfo:
    """Information about a file identified for cleanup."""

    path: Path
    size: int
    category: str
    confidence: float
    reason: str
    last_modified: Optional[datetime] = None
    is_binary: bool = False
    hash_value: Optional[str] = None  # For duplicate detection

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": str(self.path),
            "size": self.size,
            "category": self.category,
            "confidence": self.confidence,
            "reason": self.reason,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "is_binary": self.is_binary,
            "hash_value": self.hash_value,
        }


@dataclass
class ScanSummary:
    """Summary of scan results."""

    total_files_scanned: int
    files_to_remove: int
    potential_space_saved: str  # Human readable, e.g., "125.3 MB"
    scan_duration: str  # Human readable, e.g., "2.3s"
    categories_count: Dict[str, int]

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_files_scanned": self.total_files_scanned,
            "files_to_remove": self.files_to_remove,
            "potential_space_saved": self.potential_space_saved,
            "scan_duration": self.scan_duration,
            "categories_count": self.categories_count,
        }


@dataclass
class ScanResult:
    """Complete scan result."""

    scan_id: str
    timestamp: datetime
    repository_path: Path
    files_found: List[FileInfo]
    categories: Dict[str, List[FileInfo]]
    summary: ScanSummary
    recommendations: List[str]
    scan_mode: str = "quick"  # quick, thorough, aggressive, custom

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "scan_id": self.scan_id,
            "timestamp": self.timestamp.isoformat(),
            "repository_path": str(self.repository_path),
            "files_found": [f.to_dict() for f in self.files_found],
            "categories": {k: [f.to_dict() for f in v] for k, v in self.categories.items()},
            "summary": self.summary.to_dict(),
            "recommendations": self.recommendations,
            "scan_mode": self.scan_mode,
        }