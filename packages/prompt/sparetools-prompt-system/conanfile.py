#!/usr/bin/env python3
"""
Sparetools Prompt System Conan Package
Prompt rendering and web interface system
"""

import os
from conan import ConanFile


class SparetoolsPromptSystemConan(ConanFile):
    name = "sparetools-prompt-system"
    version = "1.0.0"
    description = "Prompt rendering and web interface system"
    homepage = "https://github.com/sparesparrow/sparetools"
    url = "https://github.com/sparesparrow/sparetools"
    license = "MIT"
    topics = ("prompt", "web-interface", "mcp", "templates")

    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        """Add dependencies from other sparetools packages"""
        self.requires("sparetools-base/[*]")
        self.requires("sparetools-mcp-orchestrator/[*]")

    def package(self):
        """Package the prompt system"""
        # Copy Python modules
        self.copy("*.py", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))

        # Copy configuration files
        self.copy("*.json", src=self.source_folder, dst=os.path.join(self.package_folder, "config"))

        # Copy templates (from sparetools root)
        self.copy("../templates/prompts/**", src=self.source_folder, dst=os.path.join(self.package_folder, "share/templates"))

        # Copy license
        self.copy("LICENSE", src=self.source_folder, dst="licenses")

    def package_info(self):
        """Package info - mostly scripts and configs"""
        pass