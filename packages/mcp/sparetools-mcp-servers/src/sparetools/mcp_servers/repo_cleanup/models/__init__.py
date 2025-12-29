"""Data models for the repository cleanup MCP server."""

from .scan_result import FileInfo, ScanResult, ScanSummary
from .cleanup_report import CleanupOperation, CleanupReport

__all__ = [
    "FileInfo",
    "ScanResult",
    "ScanSummary",
    "CleanupOperation",
    "CleanupReport",
]