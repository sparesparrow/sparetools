"""File pattern matching utilities."""

import fnmatch
import re
from pathlib import Path
from typing import List, Optional, Set, Union


class FileMatcher:
    """Advanced file pattern matching with glob and regex support."""

    def __init__(self):
        self._compiled_patterns: dict = {}

    def match_glob(self, path: Union[str, Path], pattern: str) -> bool:
        """Match path against glob pattern.

        Args:
            path: File path to match
            pattern: Glob pattern

        Returns:
            True if path matches pattern
        """
        path_str = str(path)
        return fnmatch.fnmatch(path_str, pattern)

    def match_regex(self, path: Union[str, Path], pattern: str) -> bool:
        """Match path against regex pattern.

        Args:
            path: File path to match
            pattern: Regex pattern

        Returns:
            True if path matches pattern
        """
        if pattern not in self._compiled_patterns:
            self._compiled_patterns[pattern] = re.compile(pattern)

        path_str = str(path)
        return bool(self._compiled_patterns[pattern].search(path_str))

    def match_multiple(self, path: Union[str, Path], patterns: List[str],
                      pattern_type: str = "glob") -> bool:
        """Match path against multiple patterns.

        Args:
            path: File path to match
            patterns: List of patterns
            pattern_type: Type of patterns ('glob' or 'regex')

        Returns:
            True if path matches any pattern
        """
        for pattern in patterns:
            if pattern_type == "regex":
                if self.match_regex(path, pattern):
                    return True
            else:
                if self.match_glob(path, pattern):
                    return True
        return False

    def filter_paths(self, paths: List[Path], include_patterns: Optional[List[str]] = None,
                    exclude_patterns: Optional[List[str]] = None,
                    pattern_type: str = "glob") -> List[Path]:
        """Filter paths based on include/exclude patterns.

        Args:
            paths: List of paths to filter
            include_patterns: Patterns that must match (if None, all paths included)
            exclude_patterns: Patterns that must not match
            pattern_type: Type of patterns ('glob' or 'regex')

        Returns:
            Filtered list of paths
        """
        filtered = []

        for path in paths:
            # Check exclusions first
            if exclude_patterns and self.match_multiple(path, exclude_patterns, pattern_type):
                continue

            # Check inclusions
            if include_patterns and not self.match_multiple(path, include_patterns, pattern_type):
                continue

            filtered.append(path)

        return filtered

    def find_files_by_patterns(self, root_path: Path, patterns: List[str],
                             pattern_type: str = "glob", max_depth: Optional[int] = None) -> List[Path]:
        """Find files matching given patterns.

        Args:
            root_path: Root directory to search
            patterns: List of patterns to match
            pattern_type: Type of patterns ('glob' or 'regex')
            max_depth: Maximum directory depth to search

        Returns:
            List of matching file paths
        """
        matches = []

        def _walk_and_match(current_path: Path, current_depth: int = 0):
            if max_depth is not None and current_depth > max_depth:
                return

            try:
                for item in current_path.iterdir():
                    if item.is_file() and self.match_multiple(item, patterns, pattern_type):
                        matches.append(item)
                    elif item.is_dir():
                        _walk_and_match(item, current_depth + 1)
            except PermissionError:
                # Skip directories we can't access
                pass

        _walk_and_match(root_path)
        return matches


# Global matcher instance
file_matcher = FileMatcher()