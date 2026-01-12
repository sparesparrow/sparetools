"""
SpareTools Versioning - Conan Package Definition

Provides git-based versioning utilities for Conan packages:
- Git-to-Conan collector for building packages from git tags/branches
- Version management and tracking
- Conan package versioning utilities
"""

from conan import ConanFile
from conan.tools.files import copy
import os
from pathlib import Path


class SparetoolsVersioningConan(ConanFile):
    name = "sparetools-versioning"
    # Use CONAN_BUILD_VERSION from environment (set by git-to-conan collector)
    # Fallback to static version for local development
    version = '1.0.0'
    package_type = "python-require"
    description = "Git-based versioning utilities for SpareTools Conan packages"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    author = "SpareTools Team"

    # Dependencies
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    exports_sources = "sparetools_versioning/**/*.py", "README.md"

    def package(self):
        """Package the Python source files."""
        copy(
            self,
            "*.py",
            src=os.path.join(self.source_folder, "sparetools_versioning"),
            dst=os.path.join(self.package_folder, "sparetools_versioning"),
            keep_path=True,
        )
        copy(self, "README.md", src=self.source_folder, dst=self.package_folder)

    def package_info(self):
        """Export package information."""
        # Add Python path for importing
        self.buildenv_info.append_path(
            "PYTHONPATH",
            self.package_folder,
        )
        self.runenv_info.append_path(
            "PYTHONPATH",
            self.package_folder,
        )

        # Package is pure Python
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
