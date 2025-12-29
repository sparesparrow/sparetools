"""Simple FastMCP-based MCP server implementation for repository cleanup."""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Lazy imports for optional dependencies
try:
    from mcp.server import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from rich.console import Console
from rich.logging import RichHandler

# Configure logging (redirect to stderr for MCP stdio compatibility)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr  # Important: log to stderr, not stdout
)
logger = logging.getLogger(__name__)


class RepoCleanupServer:
    """Simple MCP server for basic repository cleanup operations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the MCP server.

        Args:
            config: Optional configuration dictionary
        """
        if not MCP_AVAILABLE:
            raise ImportError("MCP package not available. Install with: pip install mcp")

        self.config = config or {}

        # Initialize FastMCP server
        self.server = FastMCP("repo-cleanup")

        # Set up tools
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Set up MCP tools."""

        @self.server.tool()
        async def repo_cleanup_scan(repository_path: str, scan_mode: str = "quick") -> str:
            """Scan repository for cleanup opportunities

            Args:
                repository_path: Path to the Git repository to scan
                scan_mode: Scan mode - quick, thorough, or aggressive

            Returns:
                JSON string with scan results and cleanup recommendations
            """
            try:
                repo_path = Path(repository_path).expanduser()

                if not repo_path.exists():
                    return json.dumps({"error": f"Repository path does not exist: {repo_path}"})

                if not (repo_path / ".git").exists():
                    return json.dumps({"error": f"Not a Git repository: {repo_path}"})

                # Basic scan implementation
                scan_results = {
                    "repository_path": str(repo_path),
                    "scan_mode": scan_mode,
                    "total_files": 0,
                    "large_files": [],
                    "old_files": [],
                    "duplicate_files": [],
                    "untracked_files": [],
                    "recommendations": []
                }

                # Simple file counting
                total_files = 0
                large_files = []

                for root, dirs, files in os.walk(repo_path):
                    # Skip .git directory
                    if '.git' in dirs:
                        dirs.remove('.git')

                    for file in files:
                        file_path = Path(root) / file
                        total_files += 1

                        try:
                            size = file_path.stat().st_size
                            if size > 10 * 1024 * 1024:  # 10MB
                                large_files.append({
                                    "path": str(file_path.relative_to(repo_path)),
                                    "size_mb": size / (1024 * 1024)
                                })
                        except OSError:
                            pass

                scan_results["total_files"] = total_files
                scan_results["large_files"] = large_files[:10]  # Top 10

                # Generate recommendations
                recommendations = []
                if large_files:
                    recommendations.append(f"Found {len(large_files)} large files (>10MB). Consider using Git LFS.")
                if total_files > 1000:
                    recommendations.append("Repository has many files. Consider organizing into subdirectories.")

                scan_results["recommendations"] = recommendations

                return json.dumps(scan_results, indent=2)

            except Exception as e:
                return json.dumps({"error": str(e)})

        @self.server.tool()
        async def repo_cleanup_list_large_files(repository_path: str, min_size_mb: int = 10) -> str:
            """List large files in repository

            Args:
                repository_path: Path to the Git repository
                min_size_mb: Minimum file size in MB to include

            Returns:
                JSON string with list of large files
            """
            try:
                repo_path = Path(repository_path).expanduser()

                if not repo_path.exists():
                    return json.dumps({"error": f"Repository path does not exist: {repo_path}"})

                large_files = []
                min_size_bytes = min_size_mb * 1024 * 1024

                for root, dirs, files in os.walk(repo_path):
                    # Skip .git directory
                    if '.git' in dirs:
                        dirs.remove('.git')

                    for file in files:
                        file_path = Path(root) / file
                        try:
                            size = file_path.stat().st_size
                            if size >= min_size_bytes:
                                large_files.append({
                                    "path": str(file_path.relative_to(repo_path)),
                                    "size_mb": round(size / (1024 * 1024), 2),
                                    "size_bytes": size
                                })
                        except OSError:
                            pass

                # Sort by size descending
                large_files.sort(key=lambda x: x["size_bytes"], reverse=True)

                return json.dumps({
                    "repository_path": str(repo_path),
                    "min_size_mb": min_size_mb,
                    "large_files": large_files,
                    "count": len(large_files)
                }, indent=2)

            except Exception as e:
                return json.dumps({"error": str(e)})

        @self.server.tool()
        async def repo_cleanup_git_status(repository_path: str) -> str:
            """Get Git repository status

            Args:
                repository_path: Path to the Git repository

            Returns:
                JSON string with Git status information
            """
            try:
                import subprocess

                repo_path = Path(repository_path).expanduser()

                if not repo_path.exists():
                    return json.dumps({"error": f"Repository path does not exist: {repo_path}"})

                if not (repo_path / ".git").exists():
                    return json.dumps({"error": f"Not a Git repository: {repo_path}"})

                # Run git status
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []

                # Parse status
                staged = []
                unstaged = []
                untracked = []

                for line in status_lines:
                    if not line.strip():
                        continue

                    status_code = line[:2]
                    filename = line[3:]

                    if status_code[0] in 'MADRC':
                        staged.append(filename)
                    if status_code[1] in 'MADRC':
                        unstaged.append(filename)
                    if status_code == '??':
                        untracked.append(filename)

                return json.dumps({
                    "repository_path": str(repo_path),
                    "staged_files": staged,
                    "unstaged_files": unstaged,
                    "untracked_files": untracked,
                    "total_changes": len(staged) + len(unstaged) + len(untracked)
                }, indent=2)

            except subprocess.TimeoutExpired:
                return json.dumps({"error": "Git status command timed out"})
            except Exception as e:
                return json.dumps({"error": str(e)})

        @self.server.tool()
        async def repo_cleanup_disk_usage(repository_path: str) -> str:
            """Analyze repository disk usage

            Args:
                repository_path: Path to the Git repository

            Returns:
                JSON string with disk usage analysis
            """
            try:
                import subprocess

                repo_path = Path(repository_path).expanduser()

                if not repo_path.exists():
                    return json.dumps({"error": f"Repository path does not exist: {repo_path}"})

                # Get total size
                total_size = 0
                file_count = 0

                for root, dirs, files in os.walk(repo_path):
                    # Skip .git directory
                    if '.git' in dirs:
                        dirs.remove('.git')

                    for file in files:
                        file_path = Path(root) / file
                        try:
                            total_size += file_path.stat().st_size
                            file_count += 1
                        except OSError:
                            pass

                # Get .git size separately
                git_size = 0
                if (repo_path / ".git").exists():
                    for root, dirs, files in os.walk(repo_path / ".git"):
                        for file in files:
                            file_path = Path(root) / file
                            try:
                                git_size += file_path.stat().st_size
                            except OSError:
                                pass

                return json.dumps({
                    "repository_path": str(repo_path),
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "git_size_mb": round(git_size / (1024 * 1024), 2),
                    "working_size_mb": round((total_size - git_size) / (1024 * 1024), 2),
                    "file_count": file_count,
                    "average_file_size_kb": round((total_size / max(file_count, 1)) / 1024, 2)
                }, indent=2)

            except Exception as e:
                return json.dumps({"error": str(e)})


# Create global server instance for MCP CLI tools
try:
    server_instance = RepoCleanupServer()
    app = server_instance.server
except Exception as e:
    logging.error(f"Failed to create server instance: {e}")
    import traceback
    traceback.print_exc()
    app = None

# For MCP stdio transport, the app object should be available for import
# When run directly, start the stdio server
if __name__ == "__main__":
    import asyncio
    if app:
        try:
            # Run the server using stdio transport for MCP
            asyncio.run(app.run_stdio_async())
        except Exception as e:
            logging.error(f"Server failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        logging.error("Server app not available")