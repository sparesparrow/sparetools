"""
Static Code Analysis MCP Server

Provides tools for running, installing, checking progress, and analyzing results
of static code analysis tools: cppcheck, valgrind, gdb, strace, uiautomator.
"""

from .static_analysis_mcp_server import create_server

__all__ = ["create_server"]
