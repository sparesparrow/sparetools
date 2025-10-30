"""
Foundation utilities for OpenSSL tools
"""

import os
from pathlib import Path


class VersionManager:
    """Manages version information for OpenSSL tools"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.python_version = "3.12.7"
        self.conan_version = "2.21.0"
    
    def get_version(self):
        """Get current version"""
        return self.version
    
    def get_python_version(self):
        """Get bundled Python version"""
        return self.python_version
    
    def get_conan_version(self):
        """Get Conan version"""
        return self.conan_version


# Global instance
version_manager = VersionManager()