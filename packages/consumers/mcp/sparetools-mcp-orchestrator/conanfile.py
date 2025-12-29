import os
import sys
from conan import ConanFile
from conan.tools.files import copy


class SpareToolsMcpOrchestratorConan(ConanFile):
    # Use SpareTools base utilities (Conan 2.x pattern)
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    """MCP Orchestrator - AI-powered development orchestration using Model Context Protocol."""

    name = "sparetools-mcp-orchestrator"
    version = "2.0.0"
    package_type = "python-require"
    description = "MCP orchestrator with FastMCP integration, project orchestration, and AI-powered development tools"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("mcp", "ai", "orchestration", "fastmcp", "development-tools")

    # Declare consumer context
    consumer_domain = "mcp"

    # Runtime dependencies
    requires = (
        "sparetools-cpython/3.12.7",
        # Optional: OpenSSL for secure MCP connections
        # "sparetools-openssl/3.3.2",
    )

    # Source files to export
    exports_sources = (
        "src/*",
        "scripts/*",
        "docs/*",
    )

    def package(self):
        """Package MCP orchestrator components."""
        # Copy Python modules
        copy(self, "*.py", self.source_folder, os.path.join(self.package_folder, "src"), keep_path=True)

        # Copy scripts
        copy(self, "*", os.path.join(self.source_folder, "scripts"), os.path.join(self.package_folder, "bin"), keep_path=False)

        # Copy documentation
        copy(self, "*", os.path.join(self.source_folder, "docs"), os.path.join(self.package_folder, "docs"), keep_path=True)

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        """Provide MCP orchestrator information."""
        self.cpp_info.libs = []

        # Add Python path
        self.buildenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "src"))

        # Add scripts to PATH
        self.buildenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))

        # Environment for MCP
        self.runenv_info.define("MCP_ROOT", self.package_folder)

        # Conf info for MCP discovery
        self.conf_info.define("user.mcp:root", self.package_folder)
        self.conf_info.define("user.mcp:scripts", os.path.join(self.package_folder, "bin"))