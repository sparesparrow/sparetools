"""FastMCP-based MCP server implementation for repository cleanup."""

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

from .utils.validators import validate_config

# Configure rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)
console = Console()


class RepoCleanupServer:
    """MCP server for intelligent repository cleanup."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the MCP server.

        Args:
            config: Optional configuration dictionary
        """
        if not MCP_AVAILABLE:
            raise ImportError("MCP package not available. Install with: pip install mcp")

        self.config = validate_config(config or {})

        # Initialize FastMCP server
        self.server = FastMCP("repo-cleanup")

        # Set up tools
        self._setup_tools()

        logger.info("Repository Cleanup MCP Server initialized")

    def _setup_tools(self) -> None:
        """Set up MCP tools."""

        # Import the tools dynamically to avoid import errors
        try:
            from .tools.cleanup_scanner import CleanupScanner
            cleanup_scanner = CleanupScanner(self.config)

            @self.server.tool()
            async def cleanup_scanner_tool(repository_path: str, scan_mode: str = "quick",
                                         include_patterns: str = "", exclude_patterns: str = "",
                                         max_file_size: int = 100) -> str:
                """Intelligent repository scanner that identifies files for cleanup

                Args:
                    repository_path: Path to the Git repository to scan
                    scan_mode: Scan mode - quick, thorough, aggressive, or custom
                    include_patterns: Comma-separated patterns to include (optional)
                    exclude_patterns: Comma-separated patterns to exclude (optional)
                    max_file_size: Maximum file size in MB to scan

                Returns:
                    JSON string with scan results and cleanup recommendations
                """
                try:
                    result = await cleanup_scanner.call({
                        "repository_path": repository_path,
                        "scan_mode": scan_mode,
                        "include_patterns": include_patterns,
                        "exclude_patterns": exclude_patterns,
                        "max_file_size": max_file_size
                    })
                    return json.dumps(result, indent=2)
                except Exception as e:
                    return json.dumps({"error": str(e)}, indent=2)

        except ImportError as e:
            logger.warning(f"Could not load cleanup_scanner: {e}")

        try:
            from .tools.file_remover import FileRemover
            file_remover = FileRemover(self.config)

            @self.server.tool()
            async def file_remover_tool(repository_path: str, files_to_remove: str,
                                      dry_run: bool = True, backup: bool = True) -> str:
                """Safely remove files from repository with backup support

                Args:
                    repository_path: Path to the Git repository
                    files_to_remove: JSON string array of file paths to remove
                    dry_run: If true, only show what would be removed
                    backup: If true, create backup before removal

                Returns:
                    JSON string with removal results
                """
                try:
                    result = await file_remover.call({
                        "repository_path": repository_path,
                        "files_to_remove": files_to_remove,
                        "dry_run": dry_run,
                        "backup": backup
                    })
                    return json.dumps(result, indent=2)
                except Exception as e:
                    return json.dumps({"error": str(e)}, indent=2)

        except ImportError as e:
            logger.warning(f"Could not load file_remover: {e}")

        try:
            from .tools.git_manager import GitManager
            git_manager = GitManager(self.config)

            @self.server.tool()
            async def git_manager_tool(repository_path: str, operation: str,
                                     branch_name: str = "", commit_message: str = "",
                                     remote_name: str = "origin") -> str:
                """Git repository management operations

                Args:
                    repository_path: Path to the Git repository
                    operation: Operation to perform (status, commit, push, pull, branch)
                    branch_name: Branch name for branch operations
                    commit_message: Commit message for commit operations
                    remote_name: Remote name for push/pull operations

                Returns:
                    JSON string with git operation results
                """
                try:
                    result = await git_manager.call({
                        "repository_path": repository_path,
                        "operation": operation,
                        "branch_name": branch_name,
                        "commit_message": commit_message,
                        "remote_name": remote_name
                    })
                    return json.dumps(result, indent=2)
                except Exception as e:
                    return json.dumps({"error": str(e)}, indent=2)

        except ImportError as e:
            logger.warning(f"Could not load git_manager: {e}")

        try:
            from .tools.repo_analyzer import RepoAnalyzer
            repo_analyzer = RepoAnalyzer(self.config)

            @self.server.tool()
            async def repo_analyzer_tool(repository_path: str, analysis_type: str = "full") -> str:
                """Comprehensive repository analysis and health check

                Args:
                    repository_path: Path to the Git repository
                    analysis_type: Type of analysis (full, size, commits, branches)

                Returns:
                    JSON string with repository analysis results
                """
                try:
                    result = await repo_analyzer.call({
                        "repository_path": repository_path,
                        "analysis_type": analysis_type
                    })
                    return json.dumps(result, indent=2)
                except Exception as e:
                    return json.dumps({"error": str(e)}, indent=2)

        except ImportError as e:
            logger.warning(f"Could not load repo_analyzer: {e}")


# Create global server instance for MCP CLI tools
try:
    print("DEBUG: Creating Repo Cleanup Server...", flush=True)
    server_instance = RepoCleanupServer()
    app = server_instance.server
    print("DEBUG: Server instance created successfully", flush=True)
except Exception as e:
    print(f"DEBUG: Failed to create server instance: {e}", flush=True)
    logging.error(f"Failed to create server instance: {e}")
    import traceback
    traceback.print_exc()
    app = None

# For MCP stdio transport, the app object should be available for import
# When run directly, start the stdio server
if __name__ == "__main__":
    import asyncio
    if app:
        print("Starting Repo Cleanup MCP Server...", flush=True)
        try:
            # Run the server using stdio transport for MCP
            asyncio.run(app.run_stdio_async())
        except Exception as e:
            print(f"Server failed: {e}", flush=True)
            import traceback
            traceback.print_exc()
    else:
        print("Server app not available", flush=True)