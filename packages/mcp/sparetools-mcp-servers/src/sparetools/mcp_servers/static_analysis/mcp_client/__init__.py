"""
MCP Client Package

This package provides integration with the MCP-Prompts server for
intelligent analysis interpretation and configuration management.
"""

from .prompts_client import MCPPromptsClient
from .interpretation_engine import InterpretationEngine

__all__ = ['MCPPromptsClient', 'InterpretationEngine']