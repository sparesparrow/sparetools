import os
import sys
from conan import ConanFile
from conan.tools.files import copy

# Use SpareTools base utilities
python_requires = "sparetools-base/2.0.3"


class SpareToolsTinyMcpConan(ConanFile):
    """TinyMCP - Lightweight MCP client/server implementation."""

    name = "sparetools-tinymcp"
    version = "2.0.0"
    package_type = "python-require"
    description = "Lightweight MCP (Model Context Protocol) client/server for resource-constrained environments"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("mcp", "lightweight", "embedded", "iot", "client-server")

    # Declare consumer context
    consumer_domain = "mcp"

    # Use SpareTools base utilities
    python_requires = "sparetools-base/2.0.3"

    # Runtime dependencies
    requires = (
        "sparetools-cpython/3.12.7",
    )

    # Source files to export
    exports_sources = (
        "src/*",
    )

    def package(self):
        """Package TinyMCP components."""
        # Copy Python modules
        copy(self, "*.py", self.source_folder, os.path.join(self.package_folder, "src"), keep_path=True)

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        """Provide TinyMCP package information."""
        self.cpp_info.libs = []

        # Add Python path
        self.buildenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "src"))

        # Conf info for TinyMCP discovery
        self.conf_info.define("user.tinymcp:root", self.package_folder)