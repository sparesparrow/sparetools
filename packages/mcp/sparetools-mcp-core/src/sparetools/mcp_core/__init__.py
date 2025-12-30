"""SpareTools MCP Core - Reusable MCP utilities.

This package provides core utilities for building MCP (Model Context Protocol)
applications, including templates, prompts, diagrams, device detection, and
deployment orchestration.
"""

__version__ = "1.0.0"

from sparetools.mcp_core.templates import (
    BaseTemplate,
    TemplateRenderer,
    TemplateType,
    TemplateCategory,
    TemplateMetadata,
    TemplateFile,
)
from sparetools.mcp_core.prompts import (
    PromptManager,
    PromptLoader,
    PromptTemplate,
    PromptMetadata,
    PromptCategory,
)
from sparetools.mcp_core.diagrams import (
    MermaidGenerator,
    DiagramType,
    DiagramConfig,
    RenderFormat,
)
from sparetools.mcp_core.devices import (
    DeviceDetector,
    DeviceIdentifier,
    DeviceInfo,
    SerialConnection,
)
from sparetools.mcp_core.deployment import (
    DeploymentOrchestrator,
    ConanProfileManager,
    DeploymentTarget,
)
from sparetools.mcp_core.server import (
    BaseMCPServer,
    ServerComposer,
)
from sparetools.mcp_core.core import (
    MCPConfig,
    Settings,
    MCPException,
    ErrorCode,
)

__all__ = [
    # Version
    "__version__",
    # Templates
    "BaseTemplate",
    "TemplateRenderer",
    "TemplateType",
    "TemplateCategory",
    "TemplateMetadata",
    "TemplateFile",
    # Prompts
    "PromptManager",
    "PromptLoader",
    "PromptTemplate",
    "PromptMetadata",
    "PromptCategory",
    # Diagrams
    "MermaidGenerator",
    "DiagramType",
    "DiagramConfig",
    "RenderFormat",
    # Devices
    "DeviceDetector",
    "DeviceIdentifier",
    "DeviceInfo",
    "SerialConnection",
    # Deployment
    "DeploymentOrchestrator",
    "ConanProfileManager",
    "DeploymentTarget",
    # Server
    "BaseMCPServer",
    "ServerComposer",
    # Core
    "MCPConfig",
    "Settings",
    "MCPException",
    "ErrorCode",
]
