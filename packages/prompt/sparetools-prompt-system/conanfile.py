#!/usr/bin/env python3
"""
Sparetools Prompt System Conan Package
Prompt rendering and web interface system
"""

import os
from conan import ConanFile
from conan.tools.files import copy


class SparetoolsPromptSystemConan(ConanFile):
    name = "sparetools-prompt-system"
    version = "1.0.1"
    description = "Prompt rendering and web interface system"
    homepage = "https://github.com/sparesparrow/sparetools"
    url = "https://github.com/sparesparrow/sparetools"
    license = "MIT"
    topics = ("prompt", "web-interface", "mcp", "templates")

    # Use SpareTools foundation utilities
    python_requires = "sparetools-base/2.0.3"

    # This is a Python application package
    package_type = "python-require"

    def requirements(self):
        """Add dependencies from other sparetools packages"""
        self.requires("sparetools-mcp-orchestrator/[*]")

    def package(self):
        """Package the prompt system"""
        # Copy Python modules
        copy(self, "*.py", src=self.source_folder, dst=os.path.join(self.package_folder, "python"))

        # Copy configuration files
        copy(self, "*.json", src=self.source_folder, dst=os.path.join(self.package_folder, "config"))

        # Copy templates (from sparetools root) - if they exist
        templates_src = os.path.join(os.path.dirname(self.source_folder), "templates", "prompts")
        if os.path.exists(templates_src):
            copy(self, "**", src=templates_src, dst=os.path.join(self.package_folder, "templates"))

        # Copy license
        copy(self, "LICENSE", src=self.source_folder, dst=self.package_folder)

    def package_info(self):
        """Package info - expose Python modules"""
        python_path = os.path.join(self.package_folder, "python")
        self.runenv_info.append_path("PYTHONPATH", python_path)
        self.buildenv_info.append_path("PYTHONPATH", python_path)