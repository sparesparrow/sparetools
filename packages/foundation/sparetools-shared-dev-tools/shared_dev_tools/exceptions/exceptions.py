"""
Custom Exception Classes

Provides specialized exception classes for different types of errors
that can occur in the shared development tools.
"""


class SharedDevToolsError(Exception):
    """Base exception class for all shared development tools errors."""
    pass


class ConfigurationError(SharedDevToolsError):
    """Raised when there are configuration-related errors."""
    pass


class ConanError(SharedDevToolsError):
    """Raised when Conan operations fail."""
    pass


class FileOperationError(SharedDevToolsError):
    """Raised when file operations fail."""
    pass


class BuildError(SharedDevToolsError):
    """Raised when build operations fail."""
    pass


class ValidationError(SharedDevToolsError):
    """Raised when validation fails."""
    pass


class NetworkError(SharedDevToolsError):
    """Raised when network operations fail."""
    pass


class AuthenticationError(SharedDevToolsError):
    """Raised when authentication fails."""
    pass