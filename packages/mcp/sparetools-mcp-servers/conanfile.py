from conan import ConanFile
from conan.tools.files import copy
import os


class SparetoolsMcpServersConan(ConanFile):
    name = "sparetools-mcp-servers"
    version = "1.0.1"
    description = "MCP (Model Context Protocol) servers for development workflows"
    license = "Apache-2.0"
    author = "SpareSparrow"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("mcp", "ai", "assistant", "automation", "development", "tools")

    # Use SpareTools foundation utilities
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    def requirements(self):
        # Require Python utilities from sparetools
        self.requires("sparetools-py/1.0.0")

    def layout(self):
        # Python package layout
        self.folders.source = "."
        self.folders.build = "build"

    def package(self):
        # Package Python modules
        copy(self, "*.py", src=os.path.join(self.source_folder, "src"),
             dst=os.path.join(self.package_folder, "python"))

        # Package documentation
        copy(self, "*.md", src=self.source_folder,
             dst=os.path.join(self.package_folder, "docs"))

        # Package license
        copy(self, "LICENSE*", src=self.source_folder,
             dst=self.package_folder)

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        # Add Python package to path
        python_path = os.path.join(self.package_folder, "python")
        self.runenv_info.append_path("PYTHONPATH", python_path)

        # Provide installation information
        self.conf_info.define("user.sparetools-mcp-servers:python_path", python_path)

    def package_id(self):
        # Make package platform-independent since it's primarily Python
        self.info.clear()
