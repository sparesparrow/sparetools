"""MCP Orchestrator - AI-powered development orchestration.

This module provides MCP (Model Context Protocol) server integration,
FastMCP compatibility, and AI-powered project orchestration for the
SpareTools ecosystem.
"""

__version__ = "2.0.0"

from .mcp_server import McpServer
from .fastmcp_integration import FastMcpIntegration
from .project_orchestration import ProjectOrchestrator
from .mermaid_generator import MermaidGenerator

__all__ = [
    "McpServer",
    "FastMcpIntegration",
    "ProjectOrchestrator",
    "MermaidGenerator",
]