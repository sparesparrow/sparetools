import os
from conan import ConanFile
from conan.tools.files import copy


class SpareToolsBaseConan(ConanFile):
    """Shared utilities and helpers for SpareTools ecosystem"""
    
    name = "sparetools-base"
    version = "1.0.0"
    package_type = "python-require"
    description = "Foundation utilities for SpareTools ecosystem (python_requires)"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    
    exports = "*.py", "extensions/*", "profiles/*"
    exports_sources = "*.py", "extensions/*", "profiles/*"
    
    def export(self):
        """Export all Python utilities to Conan cache"""
        copy(self, "*.py", src=self.recipe_folder, dst=self.export_folder)
        copy(self, "extensions/*", src=self.recipe_folder, dst=self.export_folder)
        copy(self, "profiles/*", src=self.recipe_folder, dst=self.export_folder)
    
    def package(self):
        """Package Python utilities"""
        copy(self, "*.py", src=self.source_folder, dst=self.package_folder)
        copy(self, "extensions/*", src=self.source_folder, dst=self.package_folder)
        copy(self, "profiles/*", src=self.source_folder, dst=self.package_folder)
    
    def package_info(self):
        """Expose package paths for python_require() consumers"""
        # Add package folder to Python path
        self.cpp_info.libs = []
        self.env_info.PYTHONPATH.append(self.package_folder)
