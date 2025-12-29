from conan import ConanFile
from conan.tools.files import copy
import os


class SparetoolsMcpServersConan(ConanFile):
    name = "sparetools-mcp-servers"
    version = "1.0.0"
    description = "MCP (Model Context Protocol) servers for development workflows"
    license = "Apache-2.0"
    author = "SpareSparrow"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("mcp", "ai", "assistant", "automation", "development", "tools")

    # This package requires Python and MCP dependencies
    # It's primarily a Python package with some system dependencies

    def requirements(self):
        # Require Python utilities from sparetools
        self.requires("sparetools-py/1.0.0@sparesparrow/stable")

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

    def package_info(self):
        # Add Python package to path
        python_path = os.path.join(self.package_folder, "python")
        self.runenv_info.append("PYTHONPATH", python_path)

        # Provide installation information
        self.user_info = {
            "python_path": python_path,
            "package_version": self.version,
            "servers": [
                "esp32_serial_monitor",
                "android_dev_tools",
                "conan_cloudsmith",
                "repo_cleanup"
            ]
        }

    def package_id(self):
        # Make package platform-independent since it's primarily Python
        self.info.clear()