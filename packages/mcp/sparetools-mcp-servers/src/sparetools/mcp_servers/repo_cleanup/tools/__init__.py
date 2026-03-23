"""Tools for the repository cleanup MCP server."""

from typing import Dict, Any

# Tool imports will be added as they are implemented
def get_tools(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get all available tools.

    Args:
        config: Configuration dictionary

    Returns:
        Dictionary mapping tool names to tool instances
    """
    tools = {}

    # Import and initialize tools as they are implemented
    try:
        from .cleanup_scanner import CleanupScanner
        tools["cleanup_scanner"] = CleanupScanner(config)
        print(f"✓ Loaded cleanup_scanner tool")
    except ImportError as e:
        print(f"⚠ Could not load cleanup_scanner: {e}")

    try:
        from .file_remover import FileRemover
        tools["file_remover"] = FileRemover(config)
        print(f"✓ Loaded file_remover tool")
    except ImportError as e:
        print(f"⚠ Could not load file_remover: {e}")

    try:
        from .gitignore_updater import GitignoreUpdater
        tools["gitignore_updater"] = GitignoreUpdater(config)
        print(f"✓ Loaded gitignore_updater tool")
    except ImportError as e:
        print(f"⚠ Could not load gitignore_updater: {e}")

    try:
        from .git_manager import GitManager
        tools["git_manager"] = GitManager(config)
        print(f"✓ Loaded git_manager tool")
    except ImportError as e:
        print(f"⚠ Could not load git_manager: {e}")

    try:
        from .repo_analyzer import RepoAnalyzer
        tools["repo_analyzer"] = RepoAnalyzer(config)
        print(f"✓ Loaded repo_analyzer tool")
    except ImportError as e:
        print(f"⚠ Could not load repo_analyzer: {e}")

    try:
        from .backup_manager import BackupManager
        tools["backup_manager"] = BackupManager(config)
        print(f"✓ Loaded backup_manager tool")
    except ImportError as e:
        print(f"⚠ Could not load backup_manager: {e}")

    try:
        from .github_manager import GitHubManager
        tools["github_manager"] = GitHubManager(config)
        print(f"✓ Loaded github_manager tool")
    except ImportError as e:
        print(f"⚠ Could not load github_manager: {e}")

    return tools