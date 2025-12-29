"""Cleanup rules resource for providing configuration to tools."""

import json
from pathlib import Path
from typing import Any, Dict, List

try:
    from mcp import Resource
except ImportError:
    from ..mcp_mock import Resource


class CleanupRules(Resource):
    """Resource providing cleanup rules and patterns configuration."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the cleanup rules resource.

        Args:
            config: Configuration dictionary
        """
        self.config = config

        super().__init__(
            uri="repo-cleanup://rules",
            name="Repository Cleanup Rules",
            description="Configuration rules and patterns for repository cleanup",
            mime_type="application/json"
        )

    async def read(self) -> str:
        """Read the cleanup rules.

        Returns:
            JSON string containing cleanup rules
        """
        # Load default rules
        rules_path = Path(__file__).parent.parent / ".." / "config" / "default_cleanup_rules.json"
        rules = {}

        if rules_path.exists():
            with open(rules_path, 'r') as f:
                rules = json.load(f)

        # Load language patterns
        lang_patterns_path = Path(__file__).parent.parent / ".." / "config" / "language_patterns.json"
        lang_patterns = {}

        if lang_patterns_path.exists():
            with open(lang_patterns_path, 'r') as f:
                lang_patterns = json.load(f)

        # Combine rules
        result = {
            "cleanup_rules": rules,
            "language_patterns": lang_patterns,
            "version": "1.0",
            "last_updated": "2024-01-01T00:00:00Z"
        }

        return json.dumps(result, indent=2)


def get_resources(config: Dict[str, Any]) -> Dict[str, Resource]:
    """Get all available resources.

    Args:
        config: Configuration dictionary

    Returns:
        Dictionary mapping resource URIs to resource instances
    """
    return {
        "repo-cleanup://rules": CleanupRules(config)
    }