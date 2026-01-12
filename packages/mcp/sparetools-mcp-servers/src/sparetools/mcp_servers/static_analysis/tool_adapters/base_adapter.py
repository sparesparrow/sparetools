"""
Base Tool Adapter

This module defines the abstract base class for all tool adapters,
providing a unified interface for tool execution, result normalization,
and capability reporting.
"""

import abc
import asyncio
import json
import logging
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration constants
DEFAULT_TIMEOUT_SECONDS = 300  # 5 minutes
DEFAULT_MAX_OUTPUT_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_THREAD_POOL_SIZE = 4


class ToolCategory(Enum):
    """Categories of development tools"""
    STATIC_ANALYSIS = "static_analysis"
    DYNAMIC_ANALYSIS = "dynamic_analysis"
    TESTING = "testing"
    DEBUGGING = "debugging"
    PROFILING = "profiling"
    CONTAINERIZATION = "containerization"
    BUILD_SYSTEM = "build_system"


class Severity(Enum):
    """Standardized severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ToolIssue:
    """Standardized issue representation"""
    file: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    severity: Severity = Severity.INFO
    message: str = ""
    rule_id: Optional[str] = None
    category: Optional[str] = None
    context: Optional[str] = None
    suggestion: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    """Standardized tool execution result"""
    tool_name: str
    success: bool
    exit_code: Optional[int] = None
    execution_time: Optional[float] = None
    issues: List[ToolIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    raw_output: Optional[str] = None
    error_message: Optional[str] = None
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'tool_name': self.tool_name,
            'success': self.success,
            'exit_code': self.exit_code,
            'execution_time': self.execution_time,
            'issues': [issue.__dict__ for issue in self.issues],
            'metrics': self.metrics,
            'raw_output': self.raw_output,
            'error_message': self.error_message,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolResult':
        """Create from dictionary"""
        data_copy = data.copy()
        data_copy['issues'] = [ToolIssue(**issue) for issue in data.get('issues', [])]
        data_copy['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data_copy)


@dataclass
class ToolCapabilities:
    """Tool capabilities and supported features"""
    name: str
    version: Optional[str] = None
    category: ToolCategory = ToolCategory.STATIC_ANALYSIS
    supported_platforms: List[str] = field(default_factory=lambda: ['linux', 'macos', 'windows'])
    supported_languages: List[str] = field(default_factory=list)
    supported_file_types: List[str] = field(default_factory=list)
    can_analyze_directories: bool = True
    can_analyze_files: bool = True
    requires_compilation: bool = False
    supports_custom_rules: bool = False
    supports_parallel_execution: bool = False
    has_timeout_support: bool = True
    output_formats: List[str] = field(default_factory=lambda: ['json', 'xml', 'text'])
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseToolAdapter(abc.ABC):
    """
    Abstract base class for tool adapters.

    This class provides the interface that all tool adapters must implement,
    ensuring consistent behavior across different development tools.
    """

    def __init__(self, name: str, executable: Optional[str] = None):
        self.name = name
        self.executable = executable or name
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self._capabilities: Optional[ToolCapabilities] = None

    @property
    @abc.abstractmethod
    def tool_category(self) -> ToolCategory:
        """Return the category of this tool"""
        pass

    @abc.abstractmethod
    def get_capabilities(self) -> ToolCapabilities:
        """
        Get tool capabilities and supported features.

        This method should detect the tool version and capabilities
        by inspecting the installed tool.
        """
        pass

    @abc.abstractmethod
    def is_available(self) -> Tuple[bool, Optional[str]]:
        """
        Check if the tool is available on the system.

        Returns:
            Tuple of (available: bool, version: Optional[str])
        """
        pass

    @abc.abstractmethod
    def build_command(self, target: Union[str, Path], **kwargs) -> List[str]:
        """
        Build the command to execute the tool.

        Args:
            target: File or directory to analyze
            **kwargs: Tool-specific arguments

        Returns:
            List of command arguments
        """
        pass

    @abc.abstractmethod
    def parse_output(self, stdout: str, stderr: str, exit_code: int) -> ToolResult:
        """
        Parse tool output into standardized ToolResult format.

        Args:
            stdout: Standard output from tool
            stderr: Standard error from tool
            exit_code: Tool exit code

        Returns:
            Standardized ToolResult object
        """
        pass

    def execute_sync(self,
                    target: Union[str, Path],
                    timeout: int = DEFAULT_TIMEOUT_SECONDS,
                    **kwargs) -> ToolResult:
        """
        Execute the tool synchronously.

        Args:
            target: Target file or directory
            timeout: Timeout in seconds
            **kwargs: Tool-specific arguments

        Returns:
            ToolResult object
        """
        start_time = time.time()

        try:
            # Build command
            cmd = self.build_command(target, **kwargs)

            # Execute command
            self.logger.debug(f"Executing: {' '.join(cmd)}")

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=kwargs.get('cwd')
            )

            execution_time = time.time() - start_time

            # Parse results
            result = self.parse_output(
                process.stdout,
                process.stderr,
                process.returncode
            )

            # Update execution metadata
            result.execution_time = execution_time
            result.exit_code = process.returncode
            result.raw_output = process.stdout + process.stderr

            return result

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return ToolResult(
                tool_name=self.name,
                success=False,
                execution_time=execution_time,
                error_message=f"Tool execution timed out after {timeout} seconds"
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Tool execution failed: {e}")
            return ToolResult(
                tool_name=self.name,
                success=False,
                execution_time=execution_time,
                error_message=str(e)
            )

    async def execute_async(self,
                           target: Union[str, Path],
                           timeout: int = DEFAULT_TIMEOUT_SECONDS,
                           **kwargs) -> ToolResult:
        """
        Execute the tool asynchronously.

        Args:
            target: Target file or directory
            timeout: Timeout in seconds
            **kwargs: Tool-specific arguments

        Returns:
            ToolResult object
        """
        loop = asyncio.get_event_loop()

        # Run synchronous execution in thread pool
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = loop.run_in_executor(
                executor,
                self.execute_sync,
                target,
                timeout,
                kwargs
            )
            return await future

    def execute_parallel(self,
                        targets: List[Union[str, Path]],
                        timeout: int = DEFAULT_TIMEOUT_SECONDS,
                        max_workers: int = DEFAULT_THREAD_POOL_SIZE,
                        **kwargs) -> List[ToolResult]:
        """
        Execute the tool on multiple targets in parallel.

        Args:
            targets: List of targets to analyze
            timeout: Timeout per target in seconds
            max_workers: Maximum number of parallel workers
            **kwargs: Tool-specific arguments

        Returns:
            List of ToolResult objects
        """
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_target = {
                executor.submit(self.execute_sync, target, timeout, **kwargs): target
                for target in targets
            }

            # Collect results as they complete
            for future in as_completed(future_to_target):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    target = future_to_target[future]
                    self.logger.error(f"Failed to analyze {target}: {e}")
                    results.append(ToolResult(
                        tool_name=self.name,
                        success=False,
                        error_message=f"Execution failed: {str(e)}"
                    ))

        return results

    def validate_target(self, target: Union[str, Path]) -> Tuple[bool, Optional[str]]:
        """
        Validate that the target is suitable for this tool.

        Args:
            target: Target to validate

        Returns:
            Tuple of (valid: bool, error_message: Optional[str])
        """
        path = Path(target)

        # Check if target exists
        if not path.exists():
            return False, f"Target does not exist: {target}"

        # Get capabilities for validation
        capabilities = self.get_capabilities()

        # Check file vs directory support
        if path.is_file() and not capabilities.can_analyze_files:
            return False, f"Tool does not support file analysis: {self.name}"

        if path.is_dir() and not capabilities.can_analyze_directories:
            return False, f"Tool does not support directory analysis: {self.name}"

        # Check file type support
        if path.is_file() and capabilities.supported_file_types:
            if path.suffix not in capabilities.supported_file_types:
                return False, f"Unsupported file type {path.suffix} for tool {self.name}"

        return True, None

    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration for this tool.

        Returns:
            Dictionary of default configuration options
        """
        return {
            'timeout': DEFAULT_TIMEOUT_SECONDS,
            'max_output_size': DEFAULT_MAX_OUTPUT_SIZE,
            'enabled': True,
        }

    def sanitize_arguments(self, **kwargs) -> Dict[str, Any]:
        """
        Sanitize and validate tool-specific arguments.

        This method should be overridden by subclasses to handle
        tool-specific argument validation and sanitization.

        Args:
            **kwargs: Raw arguments

        Returns:
            Sanitized arguments dictionary
        """
        return kwargs