"""Resources for the repository cleanup MCP server."""

from typing import Dict, Any

# Resource imports will be added as they are implemented
def get_resources(config: Dict[str, Any]) -> Dict[str, Any]:
    """Get all available resources.

    Args:
        config: Configuration dictionary

    Returns:
        Dictionary mapping resource URIs to resource instances
    """
    resources = {}

    # Import and initialize resources as they are implemented
    try:
        from .cleanup_rules import get_resources as get_rules_resources
        resources.update(get_rules_resources(config))
    except ImportError:
        pass

    try:
        from .prompts import get_resources as get_prompts_resources
        resources.update(get_prompts_resources(config))
    except ImportError:
        pass

    return resources