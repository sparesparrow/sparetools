"""
Tool Adapters Package

This package provides a unified interface for various development tools
through adapter classes that normalize their behavior and results.
"""

from .base_adapter import BaseToolAdapter, ToolResult, ToolCapabilities
from .cppcheck_adapter import CppcheckAdapter
from .clang_tidy_adapter import ClangTidyAdapter
from .valgrind_adapter import ValgrindAdapter
from .gdb_adapter import GdbAdapter
from .strace_adapter import StraceAdapter
from .pytest_adapter import PytestAdapter
from .gtest_adapter import GtestAdapter
from .jest_adapter import JestAdapter
from .docker_adapter import DockerAdapter

__all__ = [
    'BaseToolAdapter',
    'ToolResult',
    'ToolCapabilities',
    'CppcheckAdapter',
    'ClangTidyAdapter',
    'ValgrindAdapter',
    'GdbAdapter',
    'StraceAdapter',
    'PytestAdapter',
    'GtestAdapter',
    'JestAdapter',
    'DockerAdapter',
]