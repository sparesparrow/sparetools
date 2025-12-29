"""Git operations management tool."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from mcp import Tool
except ImportError:
    from ..mcp_mock import Tool

from ..utils.git_utils import git_utils
from ..utils.validators import validate_repository_path


class GitManager(Tool):
    """Git operations tool for staging, committing, and pushing changes."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the git manager.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

        super().__init__(
            name="git_manager",
            description="Manage Git operations for repository cleanup",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_path": {
                        "type": "string",
                        "description": "Path to the Git repository"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["status", "stage", "commit", "push", "full_cleanup"],
                        "description": "Git operation to perform"
                    },
                    "files_to_stage": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Files to stage (for stage operation)"
                    },
                    "commit_message": {
                        "type": "string",
                        "description": "Commit message (for commit operation)"
                    },
                    "remote": {
                        "type": "string",
                        "default": "origin",
                        "description": "Remote name (for push operation)"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch name (for push operation, defaults to current)"
                    },
                    "auto_commit": {
                        "type": "boolean",
                        "default": False,
                        "description": "Automatically commit staged changes"
                    }
                },
                "required": ["repository_path", "operation"]
            }
        )

    def _generate_commit_message(self, files_removed: List[str],
                               space_saved: int, gitignore_updates: List[str]) -> str:
        """Generate a descriptive commit message based on cleanup actions.

        Args:
            files_removed: List of removed file descriptions
            space_saved: Space saved in bytes
            gitignore_updates: Gitignore patterns added

        Returns:
            Commit message
        """
        # Categorize removed files
        categories = {}
        for file_desc in files_removed:
            # Extract category from file description
            if 'temporary' in file_desc.lower():
                categories['temporary_scripts'] = categories.get('temporary_scripts', 0) + 1
            elif 'build' in file_desc.lower() or 'artifact' in file_desc.lower():
                categories['build_artifacts'] = categories.get('build_artifacts', 0) + 1
            elif 'test' in file_desc.lower():
                categories['test_results'] = categories.get('test_results', 0) + 1
            elif 'log' in file_desc.lower():
                categories['log_files'] = categories.get('log_files', 0) + 1
            elif 'cache' in file_desc.lower():
                categories['cache_files'] = categories.get('cache_files', 0) + 1
            else:
                categories['other'] = categories.get('other', 0) + 1

        # Format space saved
        space_mb = space_saved / (1024 * 1024)
        space_str = ".1f" if space_mb < 1000 else ".0f"

        # Build message
        message_lines = ["Clean up repository"]
        message_lines.append("")

        if files_removed:
            message_lines.append("Removed files:")
            for category, count in categories.items():
                category_name = category.replace('_', ' ')
                message_lines.append(f"  - {count} {category_name}")
        else:
            # Check if this is just a .gitignore update
            if gitignore_updates:
                message_lines.append("Updated .gitignore patterns")
            else:
                message_lines.append("General repository cleanup")

        if space_mb > 0:
            message_lines.append(f"Total space saved: {space_str} MB")

        if gitignore_updates:
            message_lines.append("")
            message_lines.append("Updated .gitignore:")
            for update in gitignore_updates[:5]:  # Limit to 5
                message_lines.append(f"  - Added {update}")
            if len(gitignore_updates) > 5:
                message_lines.append(f"  - ... and {len(gitignore_updates) - 5} more patterns")

        return "\n".join(message_lines)

    def _format_file_list(self, files: List[str]) -> List[str]:
        """Format file list for commit message."""
        formatted = []
        for file in files:
            # Extract just the filename or a short description
            if isinstance(file, str):
                # If it's a path, get just the filename
                filename = Path(file).name
                if len(filename) > 50:
                    filename = filename[:47] + "..."
                formatted.append(filename)
            else:
                formatted.append(str(file))

        return formatted

    async def call(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the git manager.

        Args:
            arguments: Tool arguments

        Returns:
            Git operation results
        """
        repo_path_str = arguments.get("repository_path")
        if not repo_path_str:
            raise ValueError("repository_path is required")

        repo_path = Path(repo_path_str).resolve()
        validate_repository_path(repo_path)

        operation = arguments.get("operation")
        if not operation:
            raise ValueError("operation is required")

        if operation == "status":
            # Get repository status
            status = git_utils.get_repo_status(repo_path)
            return {
                "operation": "status",
                "status": status,
                "success": True
            }

        elif operation == "stage":
            # Stage files
            files_to_stage = arguments.get("files_to_stage", [])
            if not files_to_stage:
                return {
                    "operation": "stage",
                    "success": False,
                    "message": "No files specified for staging"
                }

            success = git_utils.add_files_to_index(repo_path, files_to_stage)

            if success:
                # Get updated status
                status = git_utils.get_repo_status(repo_path)
                return {
                    "operation": "stage",
                    "success": True,
                    "files_staged": files_to_stage,
                    "status": status
                }
            else:
                return {
                    "operation": "stage",
                    "success": False,
                    "message": "Failed to stage files"
                }

        elif operation == "commit":
            # Commit changes
            commit_message = arguments.get("commit_message")
            if not commit_message:
                # Try to generate a commit message
                files_removed = arguments.get("files_removed", [])
                space_saved = arguments.get("space_saved", 0)
                gitignore_updates = arguments.get("gitignore_updates", [])

                formatted_files = self._format_file_list(files_removed)
                commit_message = self._generate_commit_message(
                    formatted_files, space_saved, gitignore_updates
                )

            commit_sha = git_utils.commit_changes(repo_path, commit_message)

            if commit_sha:
                return {
                    "operation": "commit",
                    "success": True,
                    "commit_sha": commit_sha,
                    "commit_message": commit_message
                }
            else:
                return {
                    "operation": "commit",
                    "success": False,
                    "message": "Failed to create commit"
                }

        elif operation == "push":
            # Push changes
            remote = arguments.get("remote", "origin")
            branch = arguments.get("branch")

            success = git_utils.push_changes(repo_path, remote, branch)

            if success:
                return {
                    "operation": "push",
                    "success": True,
                    "remote": remote,
                    "branch": branch or "current branch"
                }
            else:
                return {
                    "operation": "push",
                    "success": False,
                    "message": f"Failed to push to {remote}"
                }

        elif operation == "full_cleanup":
            # Perform complete cleanup workflow
            results = {}

            # 1. Check status
            status = git_utils.get_repo_status(repo_path)
            results["status_check"] = status

            if not status.get("has_uncommitted_changes", False):
                return {
                    "operation": "full_cleanup",
                    "success": False,
                    "message": "No uncommitted changes to clean up",
                    "results": results
                }

            # 2. Stage all changes (assuming cleanup files are already staged)
            # This would typically be done by the file_remover

            # 3. Commit changes
            files_removed = arguments.get("files_removed", [])
            space_saved = arguments.get("space_saved", 0)
            gitignore_updates = arguments.get("gitignore_updates", [])

            formatted_files = self._format_file_list(files_removed)
            commit_message = self._generate_commit_message(
                formatted_files, space_saved, gitignore_updates
            )

            commit_sha = git_utils.commit_changes(repo_path, commit_message)
            results["commit"] = {
                "success": commit_sha is not None,
                "commit_sha": commit_sha,
                "message": commit_message
            }

            # 4. Push changes (optional)
            auto_commit = arguments.get("auto_commit", False)
            if auto_commit and commit_sha:
                remote = arguments.get("remote", "origin")
                push_success = git_utils.push_changes(repo_path, remote)
                results["push"] = {
                    "success": push_success,
                    "remote": remote
                }

            overall_success = results["commit"]["success"]

            return {
                "operation": "full_cleanup",
                "success": overall_success,
                "results": results,
                "message": "Cleanup workflow completed" if overall_success else "Cleanup workflow failed"
            }

        else:
            return {
                "operation": operation,
                "success": False,
                "message": f"Unknown operation: {operation}"
            }