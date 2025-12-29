"""GitIgnore file management tool."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

try:
    from mcp import Tool
except ImportError:
    from ..mcp_mock import Tool

from ..utils.git_utils import git_utils
from ..utils.validators import validate_repository_path


class GitignoreUpdater(Tool):
    """Smart .gitignore file updater with pattern analysis and validation."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the gitignore updater.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

        super().__init__(
            name="gitignore_updater",
            description="Update .gitignore file with intelligent pattern suggestions",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_path": {
                        "type": "string",
                        "description": "Path to the Git repository"
                    },
                    "patterns_to_add": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of patterns to add to .gitignore"
                    },
                    "analyze_existing": {
                        "type": "boolean",
                        "default": True,
                        "description": "Analyze existing files and suggest missing patterns"
                    },
                    "comment": {
                        "type": "string",
                        "default": "# Added by repo-cleanup",
                        "description": "Comment to add before new patterns"
                    },
                    "validate_patterns": {
                        "type": "boolean",
                        "default": True,
                        "description": "Validate patterns before adding"
                    }
                },
                "required": ["repository_path"]
            }
        )

    def _analyze_missing_patterns(self, repo_path: Path) -> List[str]:
        """Analyze repository and suggest missing .gitignore patterns.

        Args:
            repo_path: Repository path

        Returns:
            List of suggested patterns
        """
        suggestions = []

        # Check for common patterns that should be ignored
        common_patterns = {
            "*.log": ["*.log"],
            "logs/": ["logs/"],
            "*.tmp": ["*.tmp", "*.temp"],
            "*.bak": ["*.bak", "*.backup"],
            "__pycache__/": ["__pycache__/", "*.pyc", "*.pyo", "*.pyd"],
            ".pytest_cache/": [".pytest_cache/", ".coverage"],
            "node_modules/": ["node_modules/"],
            ".DS_Store": [".DS_Store"],
            "Thumbs.db": ["Thumbs.db"],
            ".vscode/": [".vscode/"],
            ".idea/": [".idea/"],
            "*.swp": ["*.swp", "*.swo", "*~"],
            "build/": ["build/", "dist/", "*.egg-info/"],
            ".env": [".env", ".env.local", ".env.*.local"]
        }

        # Check current .gitignore
        current_gitignore = git_utils.get_gitignore_content(repo_path)
        existing_patterns = set()

        if current_gitignore:
            for line in current_gitignore.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    existing_patterns.add(line)

        # Check for files that match common patterns
        for pattern_group, files in common_patterns.items():
            for file_pattern in files:
                # Look for files matching this pattern
                matching_files = []
                try:
                    if file_pattern.endswith('/'):
                        # Directory pattern
                        for item in repo_path.rglob(file_pattern.rstrip('/')):
                            if item.is_dir():
                                matching_files.append(item)
                    else:
                        # File pattern
                        for item in repo_path.rglob(file_pattern):
                            if item.is_file():
                                matching_files.append(item)
                except:
                    continue

                if matching_files and file_pattern not in existing_patterns:
                    suggestions.append(file_pattern)
                    break  # Only suggest once per pattern group

        return list(set(suggestions))  # Remove duplicates

    def _validate_pattern(self, pattern: str) -> bool:
        """Validate a gitignore pattern.

        Args:
            pattern: Pattern to validate

        Returns:
            True if pattern is valid
        """
        if not pattern.strip():
            return False

        # Check for dangerous patterns
        dangerous_patterns = ['..', '**/**', '/*']
        for dangerous in dangerous_patterns:
            if dangerous in pattern:
                return False

        # Basic syntax check
        try:
            re.compile(pattern.replace('*', '.*').replace('?', '.'))
            return True
        except re.error:
            return False

    def _merge_patterns(self, existing_content: str, new_patterns: List[str],
                       comment: str) -> str:
        """Merge new patterns into existing .gitignore content.

        Args:
            existing_content: Current .gitignore content
            new_patterns: New patterns to add
            comment: Comment to add before new patterns

        Returns:
            Updated .gitignore content
        """
        if not existing_content:
            existing_content = ""

        # Parse existing content
        lines = existing_content.split('\n')
        existing_patterns = set()

        # Collect existing patterns (excluding comments and empty lines)
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                existing_patterns.add(line)

        # Filter out patterns that already exist
        patterns_to_add = [p for p in new_patterns if p not in existing_patterns]

        if not patterns_to_add:
            return existing_content

        # Add new patterns with comment
        if existing_content and not existing_content.endswith('\n'):
            result = existing_content + '\n'
        else:
            result = existing_content

        result += f"\n{comment}\n"
        for pattern in patterns_to_add:
            result += f"{pattern}\n"

        return result

    def _test_patterns(self, repo_path: Path, patterns: List[str]) -> Dict[str, List[Path]]:
        """Test patterns against actual files in repository.

        Args:
            repo_path: Repository path
            patterns: Patterns to test

        Returns:
            Dictionary mapping patterns to matching files
        """
        results = {}

        for pattern in patterns:
            try:
                # Simple glob matching for testing
                matching_files = []
                if pattern.endswith('/'):
                    # Directory pattern
                    for item in repo_path.rglob(pattern.rstrip('/')):
                        if item.is_dir():
                            matching_files.append(item)
                else:
                    # File pattern
                    for item in repo_path.rglob(pattern):
                        if item.is_file():
                            matching_files.append(item)

                if matching_files:
                    results[pattern] = matching_files[:10]  # Limit results

            except Exception:
                continue

        return results

    async def call(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the gitignore updater.

        Args:
            arguments: Tool arguments

        Returns:
            Update results
        """
        repo_path_str = arguments.get("repository_path")
        if not repo_path_str:
            raise ValueError("repository_path is required")

        repo_path = Path(repo_path_str).resolve()
        validate_repository_path(repo_path)

        patterns_to_add = arguments.get("patterns_to_add", [])
        analyze_existing = arguments.get("analyze_existing", True)
        comment = arguments.get("comment", "# Added by repo-cleanup")
        validate_patterns = arguments.get("validate_patterns", True)

        # Analyze repository for missing patterns
        suggested_patterns = []
        if analyze_existing:
            suggested_patterns = self._analyze_missing_patterns(repo_path)

        # Combine provided and suggested patterns
        all_patterns = list(set(patterns_to_add + suggested_patterns))

        # Validate patterns
        valid_patterns = []
        invalid_patterns = []

        for pattern in all_patterns:
            if validate_patterns:
                if self._validate_pattern(pattern):
                    valid_patterns.append(pattern)
                else:
                    invalid_patterns.append(pattern)
            else:
                valid_patterns.append(pattern)

        if not valid_patterns:
            return {
                "success": False,
                "message": "No valid patterns to add",
                "invalid_patterns": invalid_patterns,
                "suggested_patterns": suggested_patterns
            }

        # Test patterns against repository
        pattern_matches = self._test_patterns(repo_path, valid_patterns)

        # Read current .gitignore
        current_content = git_utils.get_gitignore_content(repo_path) or ""

        # Merge patterns
        updated_content = self._merge_patterns(current_content, valid_patterns, comment)

        # Check if content actually changed
        content_changed = updated_content != current_content

        if content_changed:
            # Write updated .gitignore
            gitignore_path = repo_path / ".gitignore"
            try:
                with open(gitignore_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

                return {
                    "success": True,
                    "message": f"Updated .gitignore with {len(valid_patterns)} patterns",
                    "patterns_added": valid_patterns,
                    "patterns_suggested": suggested_patterns,
                    "pattern_matches": {k: [str(p) for p in v] for k, v in pattern_matches.items()},
                    "invalid_patterns": invalid_patterns,
                    "content_changed": content_changed
                }

            except Exception as e:
                return {
                    "success": False,
                    "message": f"Failed to update .gitignore: {e}",
                    "patterns_added": [],
                    "invalid_patterns": invalid_patterns
                }
        else:
            return {
                "success": True,
                "message": "No changes needed - all patterns already exist",
                "patterns_added": [],
                "patterns_suggested": suggested_patterns,
                "pattern_matches": {k: [str(p) for p in v] for k, v in pattern_matches.items()},
                "invalid_patterns": invalid_patterns,
                "content_changed": content_changed
            }