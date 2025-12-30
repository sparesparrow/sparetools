"""Base classes for SpareTools MCP Core components.

This module provides abstract base classes that define the core interfaces
for templates, components, and managers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging


class BaseComponent(ABC):
    """Abstract base class for all MCP components."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a base component.

        Args:
            name: The name of the component
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"mcp_core.{name}")

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the component."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up component resources."""
        pass

    def log_info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(message)

    def log_error(self, message: str, error: Optional[Exception] = None) -> None:
        """Log an error message."""
        if error:
            self.logger.error(f"{message}: {error}")
        else:
            self.logger.error(message)

    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(message)

    def log_debug(self, message: str) -> None:
        """Log a debug message."""
        self.logger.debug(message)


class BaseManager(ABC):
    """Abstract base class for all MCP managers."""

    def __init__(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """Initialize a base manager.

        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = Path(config_path) if config_path else None
        self.components: Dict[str, BaseComponent] = {}
        self.logger = logging.getLogger(f"mcp_core.{self.__class__.__name__}")

    @abstractmethod
    async def load_config(self) -> None:
        """Load manager configuration."""
        pass

    @abstractmethod
    async def register_component(self, component: BaseComponent) -> None:
        """Register a new component with the manager.

        Args:
            component: The component to register
        """
        pass

    @abstractmethod
    async def get_component(self, name: str) -> Optional[BaseComponent]:
        """Get a registered component by name.

        Args:
            name: Name of the component

        Returns:
            The component if found, None otherwise
        """
        pass

    @abstractmethod
    async def list_components(self) -> List[str]:
        """List all registered components.

        Returns:
            List of component names
        """
        pass


class BaseOrchestrator(BaseComponent):
    """Base class for orchestrator components.

    This class provides a common interface for components that manage
    resources and interact with other parts of the system.
    """

    def __init__(self, config: Any) -> None:
        """Initialize a base orchestrator.

        Args:
            config: Configuration instance (MCPConfig or similar)
        """
        name = getattr(config, "name", "orchestrator")
        super().__init__(name=name)
        self.config = config
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the orchestrator."""
        self._initialized = True
        self.log_info(f"Initialized {self.name}")

    async def cleanup(self) -> None:
        """Clean up orchestrator resources."""
        self._initialized = False
        self.log_info(f"Cleaned up {self.name}")

    @property
    def is_initialized(self) -> bool:
        """Check if the orchestrator is initialized."""
        return self._initialized
