"""Anthropic SDK wrapper for SpareTools MCP ecosystem."""

import os
from typing import Optional

try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 4096


class AnthropicClient:
    """Thin wrapper around the Anthropic SDK with SpareTools defaults."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ):
        if not _ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic package not installed. Run: pip install anthropic>=0.40.0"
            )
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self._api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set and no api_key provided"
            )
        self._client = anthropic.Anthropic(api_key=self._api_key)
        self.model = model
        self.max_tokens = max_tokens

    def ask(self, system: str, user: str) -> str:
        """Send a single-turn message and return the text response."""
        message = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return message.content[0].text

    def ask_with_context(self, prompt: str, context: str) -> str:
        """Convenience helper: ask with provided context appended."""
        return self.ask(
            system="You are an expert software engineer working in the SpareTools ecosystem (Conan 2.x monorepo, C++, Python, embedded systems, AI/ML). Be concise and actionable.",
            user=f"{prompt}\n\n<context>\n{context}\n</context>",
        )
