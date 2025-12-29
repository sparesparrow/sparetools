"""Intelligent cleanup scanner tool."""

import asyncio
import hashlib
import json
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    from mcp import Tool
except ImportError:
    from ..mcp_mock import Tool

from ..models.scan_result import FileInfo, ScanResult, ScanSummary
from ..utils.file_matcher import file_matcher
from ..utils.git_utils import git_utils
from ..utils.validators import validate_repository_path


class CleanupScanner(Tool):
    """Advanced cleanup scanner with intelligence and pattern recognition."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the cleanup scanner.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

        # Load cleanup rules
        self.cleanup_rules = self._load_cleanup_rules()
        self.language_patterns = self._load_language_patterns()

        super().__init__(
            name="cleanup_scanner",
            description="Intelligent repository scanner that identifies files for cleanup",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_path": {
                        "type": "string",
                        "description": "Path to the Git repository to scan"
                    },
                    "scan_mode": {
                        "type": "string",
                        "enum": ["quick", "thorough", "aggressive", "custom"],
                        "default": "quick",
                        "description": "Scan mode affecting depth and aggressiveness"
                    },
                    "include_patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Additional patterns to include in scan"
                    },
                    "exclude_patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Patterns to exclude from scan"
                    },
                    "max_file_size": {
                        "type": "string",
                        "description": "Maximum file size to scan (e.g., '100MB')"
                    },
                    "scan_timeout": {
                        "type": "integer",
                        "description": "Scan timeout in seconds",
                        "default": 300
                    }
                },
                "required": ["repository_path"]
            }
        )

    def _load_cleanup_rules(self) -> Dict[str, Any]:
        """Load cleanup rules from configuration."""
        # Default cleanup rules
        rules_path = Path(__file__).parent.parent / ".." / "config" / "default_cleanup_rules.json"
        if rules_path.exists():
            with open(rules_path, 'r') as f:
                return json.load(f)

        # Fallback default rules
        return {
            "temporary_scripts": {
                "patterns": ["commit-and-push.*", "run_tests.*", "capture_*.py", "temp_*"],
                "description": "Temporary scripts and utilities"
            },
            "build_artifacts": {
                "patterns": ["*.o", "*.so", "*.dylib", "*.dll", "*.exe", "*.out", "build/", "dist/", "*.egg-info/"],
                "description": "Compiled build artifacts"
            },
            "test_results": {
                "patterns": ["test_results.*", "*_test_output.txt", "EXECUTION_RESULTS_*", "htmlcov/", ".coverage"],
                "description": "Test execution results and coverage reports"
            },
            "excessive_documentation": {
                "patterns": ["*_REPORT.md", "*_SUMMARY.md", "*_GUIDE.md", "*_ANALYSIS.md", "*_DEMO.md"],
                "description": "Excessive documentation that should be in commit messages"
            },
            "local_config": {
                "patterns": ["*.local", "*.backup", "*_local.*", ".env.local"],
                "description": "Local configuration files specific to machine/user/workspace"
            },
            "binary_files": {
                "patterns": ["*.bin", "*.hex", "*.pyc", "*.pyo", "*.pyd"],
                "description": "Binary files not needed in repository"
            },
            "log_files": {
                "patterns": ["*.log", "logs/", "*.log.*"],
                "description": "Log files that should not be committed"
            },
            "cache_directories": {
                "patterns": ["__pycache__/", ".pytest_cache/", ".cache/", "*.cache"],
                "description": "Cache directories that should be regenerated"
            },
            "ide_files": {
                "patterns": [".vscode/", ".idea/", "*.swp", "*.swo", "*~"],
                "description": "IDE-specific files and settings"
            },
            "os_files": {
                "patterns": [".DS_Store", "Thumbs.db", "desktop.ini"],
                "description": "Operating system specific files"
            }
        }

    def _load_language_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Load language-specific patterns."""
        patterns_path = Path(__file__).parent.parent / ".." / "config" / "language_patterns.json"
        if patterns_path.exists():
            with open(patterns_path, 'r') as f:
                return json.load(f)

        # Fallback patterns
        return {
            "python": {
                "build": ["*.pyc", "__pycache__/", "*.egg-info/", "dist/", "build/"],
                "test": ["htmlcov/", ".coverage", ".pytest_cache/"],
                "ide": [".venv/", "venv/", ".python-version"]
            },
            "javascript": {
                "build": ["node_modules/", "dist/", ".next/", ".nuxt/"],
                "test": ["coverage/", ".nyc_output/"],
                "cache": [".eslintcache", ".cache/"]
            }
        }

    def _parse_size_limit(self, size_str: str) -> int:
        """Parse human-readable size limit to bytes."""
        if not size_str:
            return 100 * 1024 * 1024  # 100MB default

        size_str = size_str.upper()
        if size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        elif size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        else:
            return int(size_str)

    def _detect_project_languages(self, repo_path: Path) -> List[str]:
        """Detect programming languages used in the project."""
        languages = []

        # Check for language-specific files
        indicators = {
            "python": ["requirements.txt", "setup.py", "pyproject.toml", "*.py"],
            "javascript": ["package.json", "*.js", "*.ts"],
            "java": ["pom.xml", "build.gradle", "*.java"],
            "cpp": ["CMakeLists.txt", "Makefile", "*.cpp", "*.h"],
            "rust": ["Cargo.toml", "*.rs"],
            "go": ["go.mod", "*.go"]
        }

        for lang, patterns in indicators.items():
            for pattern in patterns:
                if pattern.startswith("*."):
                    # File extension pattern
                    ext = pattern[1:]
                    if any(f.suffix == ext for f in repo_path.rglob(f"*{ext}") if f.is_file()):
                        languages.append(lang)
                        break
                else:
                    # Specific file pattern
                    if (repo_path / pattern).exists():
                        languages.append(lang)
                        break

        return list(set(languages))

    def _calculate_file_hash(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Calculate SHA256 hash of file."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except (OSError, IOError):
            return ""

    def _find_duplicates(self, files: List[Path], max_files: int = 1000) -> Dict[str, List[Path]]:
        """Find duplicate files based on content hash."""
        hash_map = defaultdict(list)

        for file_path in files[:max_files]:  # Limit for performance
            if file_path.is_file() and file_path.stat().st_size > 0:
                file_hash = self._calculate_file_hash(file_path)
                if file_hash:
                    hash_map[file_hash].append(file_path)

        # Return only actual duplicates
        return {h: paths for h, paths in hash_map.items() if len(paths) > 1}

    def _analyze_file_age(self, file_path: Path) -> Tuple[bool, str]:
        """Analyze if file is old and potentially stale."""
        try:
            stat = file_path.stat()
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            age_days = (datetime.now() - modified_time).days

            if age_days > 30:
                return True, f"File is {age_days} days old"
            elif age_days > 7:
                return False, f"File is {age_days} days old (recently modified)"
            else:
                return False, f"File is {age_days} days old (very recent)"
        except OSError:
            return False, "Could not determine file age"

    async def _scan_files(self, repo_path: Path, scan_mode: str,
                         include_patterns: Optional[List[str]] = None,
                         exclude_patterns: Optional[List[str]] = None,
                         max_file_size: int = 100 * 1024 * 1024,
                         timeout: int = 300) -> Tuple[List[FileInfo], Dict[str, int]]:
        """Perform the actual file scanning."""

        start_time = time.time()
        files_found = []
        categories_count = defaultdict(int)

        # Detect project languages for smarter scanning
        languages = self._detect_project_languages(repo_path)

        # Build comprehensive pattern list
        all_patterns = []
        pattern_categories = {}

        # Add default cleanup patterns
        for category, rule in self.cleanup_rules.items():
            patterns = rule["patterns"]
            for pattern in patterns:
                all_patterns.append(pattern)
                pattern_categories[pattern] = category

        # Add language-specific patterns
        for lang in languages:
            if lang in self.language_patterns:
                for category, patterns in self.language_patterns[lang].items():
                    category_name = f"{lang}_{category}"
                    for pattern in patterns:
                        all_patterns.append(pattern)
                        pattern_categories[pattern] = category_name

        # Add custom include patterns
        if include_patterns:
            for pattern in include_patterns:
                all_patterns.append(pattern)
                pattern_categories[pattern] = "custom"

        # Find all files matching patterns
        for pattern in all_patterns:
            try:
                matching_files = file_matcher.find_files_by_patterns(
                    repo_path, [pattern], max_depth=10 if scan_mode == "quick" else None
                )

                for file_path in matching_files:
                    # Skip if excluded
                    if exclude_patterns and file_matcher.match_multiple(file_path, exclude_patterns):
                        continue

                    # Skip if too large
                    try:
                        file_size = file_path.stat().st_size
                        if file_size > max_file_size:
                            continue
                    except OSError:
                        continue

                    # Get category
                    category = pattern_categories.get(pattern, "unknown")

                    # Calculate confidence and reason
                    confidence = 0.8  # Default confidence
                    reason = self.cleanup_rules.get(category, {}).get("description", f"Matches pattern: {pattern}")

                    # Check file age for additional context
                    is_old, age_info = self._analyze_file_age(file_path)
                    if is_old and scan_mode in ["thorough", "aggressive"]:
                        confidence += 0.1
                        reason += f" ({age_info})"

                    # Create FileInfo
                    file_info = FileInfo(
                        path=file_path,
                        size=file_size,
                        category=category,
                        confidence=min(confidence, 1.0),
                        reason=reason,
                        last_modified=datetime.fromtimestamp(file_path.stat().st_mtime),
                        is_binary=self._is_binary_file(file_path)
                    )

                    files_found.append(file_info)
                    categories_count[category] += 1

                    # Check timeout
                    if time.time() - start_time > timeout:
                        break

                if time.time() - start_time > timeout:
                    break

            except Exception as e:
                # Log error but continue scanning
                print(f"Error scanning pattern {pattern}: {e}")
                continue

        # Find duplicates if thorough scan
        if scan_mode in ["thorough", "aggressive"]:
            all_file_paths = [f.path for f in files_found]
            duplicates = self._find_duplicates(all_file_paths)

            for hash_val, dup_paths in duplicates.items():
                # Keep one, mark others as duplicates
                for i, dup_path in enumerate(dup_paths[1:], 1):
                    dup_info = FileInfo(
                        path=dup_path,
                        size=dup_path.stat().st_size,
                        category="duplicates",
                        confidence=0.9,
                        reason=f"Duplicate of {dup_paths[0].name} (hash: {hash_val[:8]}...)",
                        last_modified=datetime.fromtimestamp(dup_path.stat().st_mtime),
                        hash_value=hash_val
                    )
                    files_found.append(dup_info)
                    categories_count["duplicates"] += 1

        return files_found, dict(categories_count)

    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if file is binary."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                # Check for null bytes (common in binary files)
                return b'\x00' in chunk
        except (OSError, IOError):
            return True  # Assume binary if can't read

    def _generate_recommendations(self, scan_data: Dict) -> List[str]:
        """Generate recommendations based on scan results."""
        recommendations = []

        # Check for missing .gitignore patterns
        categories_found = set(scan_data["categories"].keys())
        if "build_artifacts" in categories_found and "python_build" not in categories_found:
            recommendations.append("Consider adding Python build patterns to .gitignore (*.pyc, __pycache__/)")

        if "ide_files" in categories_found:
            recommendations.append("Consider adding IDE files to .gitignore (.vscode/, .idea/)")

        if "duplicates" in categories_found:
            recommendations.append("Duplicate files found - consider removing redundant copies")

        # Size recommendations
        total_size = sum(f.size for f in scan_data["files_found"])
        if total_size > 500 * 1024 * 1024:  # 500MB
            recommendations.append("Large amount of removable files detected - consider Git LFS for large assets")

        return recommendations

    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return ".1f"
            size_bytes /= 1024.0
        return ".1f"

    async def call(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the cleanup scanner.

        Args:
            arguments: Tool arguments

        Returns:
            Scan results
        """
        repo_path_str = arguments.get("repository_path")
        if not repo_path_str:
            raise ValueError("repository_path is required")

        repo_path = Path(repo_path_str).resolve()
        validate_repository_path(repo_path)

        scan_mode = arguments.get("scan_mode", "quick")
        include_patterns = arguments.get("include_patterns", [])
        exclude_patterns = arguments.get("exclude_patterns", [])
        max_file_size_str = arguments.get("max_file_size", "100MB")
        timeout = arguments.get("scan_timeout", 300)

        max_file_size = self._parse_size_limit(max_file_size_str)

        # Perform scan
        start_time = time.time()
        files_found, categories_count = await self._scan_files(
            repo_path, scan_mode, include_patterns, exclude_patterns,
            max_file_size, timeout
        )
        scan_duration = time.time() - start_time

        # Calculate summary
        total_size = sum(f.size for f in files_found)
        summary = ScanSummary(
            total_files_scanned=len(files_found),  # This is approximate
            files_to_remove=len(files_found),
            potential_space_saved=self._format_size(total_size),
            scan_duration=".2f",
            categories_count=categories_count
        )

        # Group files by category
        categories = defaultdict(list)
        for file_info in files_found:
            categories[file_info.category].append(file_info)

        # Generate recommendations
        recommendations = self._generate_recommendations({
            "files_found": files_found,
            "categories": dict(categories),
            "summary": summary
        })

        # Create scan result
        scan_result = ScanResult(
            scan_id=f"scan_{int(time.time())}",
            timestamp=datetime.now(),
            repository_path=repo_path,
            files_found=files_found,
            categories=dict(categories),
            summary=summary,
            recommendations=recommendations
        )

        # Convert to dict for JSON serialization
        result_dict = scan_result.to_dict()

        return result_dict