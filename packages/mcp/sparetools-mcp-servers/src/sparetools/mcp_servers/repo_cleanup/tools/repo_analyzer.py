"""Repository analysis tool for health metrics and insights."""

import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import git

try:
    from mcp import Tool
except ImportError:
    from ..mcp_mock import Tool

from ..utils.git_utils import git_utils
from ..utils.validators import validate_repository_path


class RepoAnalyzer(Tool):
    """Advanced repository analyzer providing health metrics and insights."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the repository analyzer.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

        super().__init__(
            name="repo_analyzer",
            description="Analyze repository health, size, and provide optimization insights",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_path": {
                        "type": "string",
                        "description": "Path to the Git repository"
                    },
                    "analysis_depth": {
                        "type": "string",
                        "enum": ["quick", "detailed", "comprehensive"],
                        "default": "detailed",
                        "description": "Depth of analysis to perform"
                    },
                    "include_history": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include Git history analysis"
                    },
                    "check_duplicates": {
                        "type": "boolean",
                        "default": False,
                        "description": "Check for duplicate files (slow)"
                    }
                },
                "required": ["repository_path"]
            }
        )

    def _calculate_repo_size(self, repo_path: Path) -> Dict[str, Any]:
        """Calculate repository size statistics.

        Args:
            repo_path: Repository path

        Returns:
            Size statistics
        """
        total_size = 0
        file_count = 0
        largest_files = []
        extension_stats = Counter()

        try:
            for root, dirs, files in os.walk(repo_path):
                # Skip .git directory
                if '.git' in dirs:
                    dirs.remove('.git')

                for file in files:
                    file_path = Path(root) / file
                    try:
                        stat = file_path.stat()
                        size = stat.st_size
                        total_size += size
                        file_count += 1

                        # Track largest files
                        largest_files.append((file_path, size))

                        # Track extensions
                        ext = file_path.suffix.lower()
                        if ext:
                            extension_stats[ext] += 1

                    except (OSError, IOError):
                        continue

            # Sort and limit largest files
            largest_files.sort(key=lambda x: x[1], reverse=True)
            largest_files = largest_files[:10]

            return {
                "total_size": total_size,
                "total_size_human": self._format_size(total_size),
                "file_count": file_count,
                "largest_files": [{"path": str(f[0]), "size": f[1], "size_human": self._format_size(f[1])} for f in largest_files],
                "extension_breakdown": dict(extension_stats.most_common(10))
            }

        except Exception as e:
            return {"error": str(e)}

    def _analyze_git_history(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze Git commit history.

        Args:
            repo_path: Repository path

        Returns:
            Git history statistics
        """
        try:
            repo = git.Repo(repo_path)

            # Get recent commits (last 100)
            commits = list(repo.iter_commits('HEAD', max_count=100))

            if not commits:
                return {"error": "No commits found"}

            # Analyze commit frequency
            commit_dates = [commit.authored_datetime.date() for commit in commits]
            commits_per_day = Counter(commit_dates)

            # Calculate average commits per day (last 30 days)
            thirty_days_ago = datetime.now().date() - timedelta(days=30)
            recent_commits = sum(1 for date in commit_dates if date >= thirty_days_ago)
            avg_commits_per_day = recent_commits / 30

            # Analyze contributors
            authors = Counter(commit.author.name for commit in commits)
            top_contributors = dict(authors.most_common(5))

            # Analyze commit messages
            message_lengths = [len(commit.message) for commit in commits]
            avg_message_length = sum(message_lengths) / len(message_lengths)

            return {
                "total_commits": len(commits),
                "avg_commits_per_day": round(avg_commits_per_day, 2),
                "top_contributors": top_contributors,
                "avg_message_length": round(avg_message_length, 1),
                "commits_last_30_days": recent_commits,
                "commit_frequency_trend": "increasing" if avg_commits_per_day > 0.5 else "stable" if avg_commits_per_day > 0.1 else "decreasing"
            }

        except Exception as e:
            return {"error": str(e)}

    def _check_gitignore_coverage(self, repo_path: Path) -> Dict[str, Any]:
        """Check how well .gitignore covers the repository.

        Args:
            repo_path: Repository path

        Returns:
            Gitignore coverage analysis
        """
        try:
            # Read .gitignore
            gitignore_path = repo_path / ".gitignore"
            gitignore_patterns = []

            if gitignore_path.exists():
                content = gitignore_path.read_text(encoding='utf-8')
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        gitignore_patterns.append(line)

            # Check for common files that should be ignored
            ignored_files_found = []
            potentially_ignored = []

            common_ignore_checks = [
                ("*.log", ["*.log"]),
                ("*.tmp", ["*.tmp", "*.temp"]),
                ("__pycache__/", ["__pycache__/", "*.pyc"]),
                (".DS_Store", [".DS_Store"]),
                ("node_modules/", ["node_modules/"]),
                ("build/", ["build/", "dist/"]),
                (".env", [".env", ".env.local"])
            ]

            for pattern_group, files in common_ignore_checks:
                for file_pattern in files:
                    matching = list(repo_path.rglob(file_pattern))
                    if matching:
                        # Check if any of these files are already ignored
                        is_ignored = any(self._matches_gitignore_patterns(f, gitignore_patterns)
                                       for f in matching[:5])  # Check first 5

                        if is_ignored:
                            ignored_files_found.extend([str(f) for f in matching[:3]])
                        else:
                            potentially_ignored.extend([str(f) for f in matching[:3]])

            coverage_score = 0
            if ignored_files_found or not potentially_ignored:
                coverage_score = 80  # Good coverage
            elif len(potentially_ignored) < 10:
                coverage_score = 60  # Moderate coverage
            else:
                coverage_score = 40  # Poor coverage

            return {
                "gitignore_exists": gitignore_path.exists(),
                "patterns_count": len(gitignore_patterns),
                "coverage_score": coverage_score,
                "ignored_files_sample": ignored_files_found[:5],
                "potentially_ignored_files": potentially_ignored[:5],
                "recommendations": self._gitignore_recommendations(potentially_ignored)
            }

        except Exception as e:
            return {"error": str(e)}

    def _matches_gitignore_patterns(self, file_path: Path, patterns: List[str]) -> bool:
        """Check if file path matches any gitignore pattern.

        Args:
            file_path: File path to check
            patterns: List of gitignore patterns

        Returns:
            True if file matches any pattern
        """
        from fnmatch import fnmatch

        for pattern in patterns:
            # Simple pattern matching (not full gitignore spec)
            if fnmatch(str(file_path), pattern):
                return True
            # Check relative to repo root
            try:
                rel_path = file_path.relative_to(file_path.parents[-1])  # Get relative path
                if fnmatch(str(rel_path), pattern):
                    return True
            except ValueError:
                continue

        return False

    def _gitignore_recommendations(self, potentially_ignored: List[str]) -> List[str]:
        """Generate .gitignore recommendations.

        Args:
            potentially_ignored: List of potentially ignored files

        Returns:
            List of recommendations
        """
        recommendations = []

        if any('.log' in f for f in potentially_ignored):
            recommendations.append("Add '*.log' to ignore log files")

        if any('__pycache__' in f or '.pyc' in f for f in potentially_ignored):
            recommendations.append("Add '__pycache__/' and '*.pyc' for Python")

        if any('node_modules' in f for f in potentially_ignored):
            recommendations.append("Add 'node_modules/' for Node.js")

        if any('.DS_Store' in f for f in potentially_ignored):
            recommendations.append("Add '.DS_Store' for macOS")

        return recommendations

    def _calculate_health_score(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall repository health score.

        Args:
            analysis_results: Results from various analyses

        Returns:
            Health score breakdown
        """
        scores = {}

        # Size health (smaller is better, but not too small)
        size_info = analysis_results.get("size_analysis", {})
        total_size_mb = size_info.get("total_size", 0) / (1024 * 1024)

        if total_size_mb < 10:
            scores["size_health"] = 100  # Very healthy
        elif total_size_mb < 100:
            scores["size_health"] = 80   # Good
        elif total_size_mb < 500:
            scores["size_health"] = 60   # Moderate
        else:
            scores["size_health"] = 40   # Large repository

        # Gitignore coverage
        gitignore_info = analysis_results.get("gitignore_analysis", {})
        scores["gitignore_coverage"] = gitignore_info.get("coverage_score", 50)

        # Commit hygiene
        history_info = analysis_results.get("git_history", {})
        commits_per_day = history_info.get("avg_commits_per_day", 0)

        if commits_per_day > 1:
            scores["commit_hygiene"] = 90
        elif commits_per_day > 0.5:
            scores["commit_hygiene"] = 70
        elif commits_per_day > 0.1:
            scores["commit_hygiene"] = 50
        else:
            scores["commit_hygiene"] = 30

        # Structure score (placeholder - would need more analysis)
        scores["structure"] = 85

        # Documentation score (placeholder)
        scores["documentation"] = 60

        # Overall health score (weighted average)
        weights = {
            "size_health": 0.2,
            "gitignore_coverage": 0.3,
            "commit_hygiene": 0.25,
            "structure": 0.15,
            "documentation": 0.1
        }

        overall_score = sum(scores[metric] * weights[metric] for metric in scores.keys())

        return {
            "overall_score": round(overall_score, 1),
            "breakdown": scores,
            "grade": self._score_to_grade(overall_score)
        }

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade.

        Args:
            score: Numeric score

        Returns:
            Letter grade
        """
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return ".1f"
            size_bytes /= 1024.0
        return ".1f"

    async def call(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the repository analyzer.

        Args:
            arguments: Tool arguments

        Returns:
            Analysis results
        """
        repo_path_str = arguments.get("repository_path")
        if not repo_path_str:
            raise ValueError("repository_path is required")

        repo_path = Path(repo_path_str).resolve()
        validate_repository_path(repo_path)

        analysis_depth = arguments.get("analysis_depth", "detailed")
        include_history = arguments.get("include_history", True)
        check_duplicates = arguments.get("check_duplicates", False)

        results = {
            "repository_path": str(repo_path),
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_depth": analysis_depth
        }

        # Size analysis
        results["size_analysis"] = self._calculate_repo_size(repo_path)

        # Git history analysis
        if include_history:
            results["git_history"] = self._analyze_git_history(repo_path)

        # Gitignore analysis
        results["gitignore_analysis"] = self._check_gitignore_coverage(repo_path)

        # Health score
        results["health_score"] = self._calculate_health_score(results)

        # Generate insights
        results["insights"] = self._generate_insights(results)

        return results

    def _generate_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate insights based on analysis results.

        Args:
            analysis_results: Complete analysis results

        Returns:
            List of insights and recommendations
        """
        insights = []

        # Size insights
        size_info = analysis_results.get("size_analysis", {})
        total_size_mb = size_info.get("total_size", 0) / (1024 * 1024)

        if total_size_mb > 1000:
            insights.append("Repository is very large. Consider using Git LFS for large assets.")
        elif total_size_mb > 500:
            insights.append("Repository is quite large. Review large files and consider cleanup.")

        # Gitignore insights
        gitignore_info = analysis_results.get("gitignore_analysis", {})
        if gitignore_info.get("coverage_score", 0) < 60:
            insights.append("Gitignore coverage could be improved. Many files should be ignored.")

        # Commit insights
        history_info = analysis_results.get("git_history", {})
        commits_per_day = history_info.get("avg_commits_per_day", 0)

        if commits_per_day < 0.1:
            insights.append("Low commit frequency. Consider more frequent, smaller commits.")
        elif commits_per_day > 2:
            insights.append("High commit frequency. Ensure commits are meaningful and well-described.")

        # Health insights
        health = analysis_results.get("health_score", {})
        overall = health.get("overall_score", 0)

        if overall < 60:
            insights.append("Repository health needs attention. Consider comprehensive cleanup.")
        elif overall > 90:
            insights.append("Repository is in excellent health!")

        return insights