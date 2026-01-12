"""
Sparetools MCP Client - Unified client for knowledge and development tools

This module provides a unified interface to MCP servers, with fallback to
file-based storage when MCP servers are not available.
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class MCPConnection:
    """Represents an MCP server connection"""
    name: str
    available: bool
    client: Optional[Any] = None


class SparetoolsMCPClient:
    """
    Unified MCP client for Sparetools cognitive architecture

    Provides access to:
    - mcp-prompts: Knowledge storage and retrieval
    - unified-dev-tools: Development tool execution
    """

    def __init__(self, knowledge_base_path: Path):
        self.knowledge_base_path = knowledge_base_path
        self.connections = {
            'prompts': MCPConnection('mcp-prompts', False),
            'devtools': MCPConnection('unified-dev-tools', False)
        }

        # Initialize file-based fallback storage
        self.prompts_path = knowledge_base_path / "prompts"
        self.episodes_path = knowledge_base_path / "episodes"
        self.prompts_path.mkdir(parents=True, exist_ok=True)
        self.episodes_path.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """Initialize MCP connections with fallbacks"""
        print("🔌 Initializing Sparetools MCP connections...")

        # Try to connect to MCP servers
        try:
            # For now, we'll use file-based storage
            # TODO: Implement actual MCP server connections
            print("📁 Using file-based knowledge storage (MCP servers not yet connected)")
            self.connections['prompts'].available = True  # File-based fallback
            self.connections['devtools'].available = False  # Not implemented yet

        except Exception as e:
            print(f"⚠️  MCP initialization failed: {e}")
            print("📁 Falling back to file-based storage")

    async def query_development_knowledge(self, domain: str, topic: str) -> Dict:
        """
        Query development knowledge from MCP servers

        Args:
            domain: Development domain (esp32, android, python, etc.)
            topic: Specific topic to query

        Returns:
            Dictionary with knowledge results
        """
        if not self.connections['prompts'].available:
            return {"found": False, "error": "Knowledge service not available"}

        # Query file-based knowledge
        return self._query_file_knowledge(domain, topic)

    async def capture_development_learning(self, domain: str, pattern: str,
                                        context: str, tags: List[str]) -> Dict:
        """
        Capture successful development patterns

        Args:
            domain: Development domain
            pattern: The pattern that worked
            context: Context where it worked
            tags: Relevant tags for searchability
        """
        if not self.connections['prompts'].available:
            return {"stored": False, "error": "Knowledge service not available"}

        # Store in file-based system
        return self._store_file_pattern(domain, pattern, context, tags)

    async def store_prompt(self, name: str, description: str,
                          content: str, metadata: Dict) -> Dict:
        """
        Store a prompt in the knowledge base

        Args:
            name: Prompt name/identifier
            description: Human-readable description
            content: The actual prompt content
            metadata: Additional metadata (tags, layer, domain, etc.)
        """
        prompt_data = {
            "name": name,
            "description": description,
            "content": content,
            "layer": metadata.get("layer", "Procedural"),
            "domain": metadata.get("domain", "SoftwareDevelopment"),
            "tags": metadata.get("tags", []),
            "abstraction_level": metadata.get("abstraction_level", 5),
            "effectiveness": metadata.get("effectiveness_score", 0.8),
            "usage_count": metadata.get("usage_count", 0),
            "created_at": metadata.get("created_at", "now")
        }

        # Store as JSON file
        prompt_file = self.prompts_path / f"{name}.json"
        with open(prompt_file, 'w') as f:
            json.dump(prompt_data, f, indent=2)

        print(f"✓ Stored prompt: {name}")
        return {"stored": True, "name": name}

    async def get_prompt(self, name: str) -> Optional[Dict]:
        """
        Retrieve a prompt by name

        Args:
            name: Prompt name

        Returns:
            Prompt data or None if not found
        """
        prompt_file = self.prompts_path / f"{name}.json"
        if not prompt_file.exists():
            return None

        with open(prompt_file, 'r') as f:
            return json.load(f)

    async def list_prompts(self, tags: Optional[List[str]] = None) -> List[Dict]:
        """
        List available prompts, optionally filtered by tags

        Args:
            tags: Optional list of tags to filter by

        Returns:
            List of prompt summaries
        """
        prompts = []

        for prompt_file in self.prompts_path.glob("*.json"):
            with open(prompt_file, 'r') as f:
                prompt_data = json.load(f)

            # Filter by tags if specified
            if tags:
                prompt_tags = prompt_data.get("tags", [])
                if not any(tag in prompt_tags for tag in tags):
                    continue

            prompts.append({
                "name": prompt_data["name"],
                "description": prompt_data.get("description", ""),
                "tags": prompt_data.get("tags", []),
                "layer": prompt_data.get("layer", "Procedural"),
                "domain": prompt_data.get("domain", "General")
            })

        return prompts

    def _query_file_knowledge(self, domain: str, topic: str) -> Dict:
        """Query knowledge from file-based storage"""

        # Look for prompts matching domain and topic
        matching_prompts = []

        for prompt_file in self.prompts_path.glob("*.json"):
            with open(prompt_file, 'r') as f:
                prompt_data = json.load(f)

            # Check if domain matches
            prompt_domain = prompt_data.get("domain", "")
            if domain not in prompt_domain and prompt_domain not in domain:
                continue

            # Check if topic appears in description or content
            desc = prompt_data.get("description", "").lower()
            content = prompt_data.get("content", "").lower()
            topic_lower = topic.lower()

            # More flexible matching
            if (topic_lower in desc or
                topic_lower in content or
                any(topic_lower in tag.lower() for tag in prompt_data.get("tags", []))):
                matching_prompts.append(prompt_data)

        if matching_prompts:
            # Return the most effective one
            def get_effectiveness(p):
                eff = p.get("effectiveness", 0)
                if isinstance(eff, dict):
                    return eff.get("effectiveness_score", 0)
                return float(eff)

            best_match = max(matching_prompts, key=get_effectiveness)

            return {
                "found": True,
                "pattern": best_match,
                "confidence": get_effectiveness(best_match)
            }

        return {"found": False, "message": f"No knowledge found for {domain}/{topic}"}

    def _store_file_pattern(self, domain: str, pattern: str,
                           context: str, tags: List[str]) -> Dict:
        """Store a pattern in file-based storage"""

        # Generate a unique name
        import time
        timestamp = int(time.time())
        name = f"pattern-{domain}-{timestamp}"

        prompt_data = {
            "name": name,
            "description": f"Learned pattern for {domain}",
            "content": pattern,
            "context": context,
            "layer": "Procedural",
            "domain": domain,
            "tags": tags + [domain],
            "abstraction_level": 3,  # Concrete pattern
            "effectiveness": 0.8,  # Initial effectiveness
            "usage_count": 0,
            "created_at": timestamp
        }

        # Store the pattern
        pattern_file = self.prompts_path / f"{name}.json"
        with open(pattern_file, 'w') as f:
            json.dump(prompt_data, f, indent=2)

        print(f"✓ Captured pattern: {name}")
        return {"stored": True, "name": name}

    async def get_connection_status(self) -> Dict:
        """Get status of MCP connections"""
        return {
            "prompts": {
                "available": self.connections['prompts'].available,
                "type": "file-based" if self.connections['prompts'].available else "unavailable"
            },
            "devtools": {
                "available": self.connections['devtools'].available,
                "type": "unavailable"
            }
        }


# Global client instance
_mcp_client = None

def get_mcp_client(knowledge_base_path: Optional[Path] = None) -> SparetoolsMCPClient:
    """Get or create the global MCP client instance"""
    global _mcp_client

    if _mcp_client is None:
        if knowledge_base_path is None:
            knowledge_base_path = Path.home() / ".sparetools"
        _mcp_client = SparetoolsMCPClient(knowledge_base_path)

    return _mcp_client