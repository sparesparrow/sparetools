"""Prompts resource for AI agent guidance."""

import json
from typing import Any, Dict

try:
    from mcp import Resource
except ImportError:
    from ..mcp_mock import Resource


class CleanupPrompts(Resource):
    """Resource providing prompts and guidance for cleanup operations."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the cleanup prompts resource.

        Args:
            config: Configuration dictionary
        """
        self.config = config

        super().__init__(
            uri="repo-cleanup://prompts",
            name="Repository Cleanup Prompts",
            description="Guidance prompts for AI agents performing repository cleanup",
            mime_type="application/json"
        )

    async def read(self) -> str:
        """Read the cleanup prompts.

        Returns:
            JSON string containing prompts and guidance
        """
        prompts = {
            "tool_usage": {
                "cleanup_scanner": {
                    "description": "Scan repository for files that should be cleaned up",
                    "when_to_use": "Before cleanup operations to identify removable files",
                    "parameters": {
                        "scan_mode": "Use 'thorough' for comprehensive scan, 'quick' for fast overview",
                        "include_patterns": "Additional patterns to check beyond defaults"
                    }
                },
                "file_remover": {
                    "description": "Safely remove identified files with backup options",
                    "when_to_use": "After scanning to perform the actual cleanup",
                    "safety_tips": "Always use dry_run=True first, enable backups for production repos"
                },
                "gitignore_updater": {
                    "description": "Update .gitignore with patterns for removed files",
                    "when_to_use": "After cleanup to prevent future commits of similar files"
                },
                "git_manager": {
                    "description": "Handle Git operations for staging, committing, and pushing",
                    "when_to_use": "After cleanup to commit changes",
                    "commit_message_guidance": "Include cleanup summary and space saved"
                }
            },
            "workflow_templates": {
                "basic_cleanup": [
                    "1. Run cleanup_scanner with scan_mode='thorough'",
                    "2. Review results and confirm files to remove",
                    "3. Run file_remover with dry_run=True first",
                    "4. Run file_remover with actual removal",
                    "5. Run gitignore_updater to add patterns",
                    "6. Run git_manager with full_cleanup operation"
                ],
                "aggressive_cleanup": [
                    "1. Run repo_analyzer to understand repository structure",
                    "2. Run cleanup_scanner with scan_mode='aggressive'",
                    "3. Use backup_manager to create full backup",
                    "4. Perform cleanup with file_remover",
                    "5. Update .gitignore and commit changes"
                ]
            },
            "best_practices": [
                "Always create backups before large cleanup operations",
                "Use dry-run mode first to preview changes",
                "Review scan results carefully before removal",
                "Update .gitignore to prevent future issues",
                "Write descriptive commit messages for cleanup operations",
                "Test repository functionality after cleanup"
            ],
            "error_handling": {
                "permission_denied": "Check file permissions and repository access rights",
                "git_conflicts": "Resolve any Git conflicts before proceeding",
                "large_files": "Consider using Git LFS for files over 100MB",
                "backup_failed": "Ensure backup directory has sufficient space and permissions"
            },
            "version": "1.0"
        }

        return json.dumps(prompts, indent=2)


def get_resources(config: Dict[str, Any]) -> Dict[str, Resource]:
    """Get all available resources.

    Args:
        config: Configuration dictionary

    Returns:
        Dictionary mapping resource URIs to resource instances
    """
    return {
        "repo-cleanup://prompts": CleanupPrompts(config)
    }