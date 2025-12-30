"""Core utilities for SpareTools MCP Core.

This module provides base classes, configuration management, and exception handling.
"""

from sparetools.mcp_core.core.config import MCPConfig, Settings
from sparetools.mcp_core.core.exceptions import (
    MCPException,
    ErrorCode,
    TemplateError,
    PromptError,
    MermaidError,
    ConfigError,
    ValidationError,
    ResourceError,
    DeviceError,
    DeploymentError,
)
from sparetools.mcp_core.core.base import (
    BaseComponent,
    BaseManager,
    BaseOrchestrator,
)

__all__ = [
    "MCPConfig",
    "Settings",
    "MCPException",
    "ErrorCode",
    "TemplateError",
    "PromptError",
    "MermaidError",
    "ConfigError",
    "ValidationError",
    "ResourceError",
    "DeviceError",
    "DeploymentError",
    "BaseComponent",
    "BaseManager",
    "BaseOrchestrator",
]
