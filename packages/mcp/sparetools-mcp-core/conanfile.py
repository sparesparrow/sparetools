from conan import ConanFile
from conan.tools.files import copy, save
import os


class SparetoolsMcpCoreConan(ConanFile):
    name = "sparetools-mcp-core"
    version = "1.0.1"
    description = "Core MCP utilities: templates, prompts, diagrams, device detection"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("mcp", "templates", "prompts", "mermaid", "devices", "generic")

    # SpareTools foundation with bundled CPython
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"
    tool_requires = "sparetools-cpython/3.12.7"

    package_type = "python-require"

    exports_sources = "src/**/*.py", "pyproject.toml", "README.md"

    def package(self):
        """Package the Python sources.

        Ships the source tree under a 'python' folder and exposes it via
        PYTHONPATH using the run environment so consumers can import the
        package directly.
        """
        copy(
            self,
            "*.py",
            src=os.path.join(self.source_folder, "src"),
            dst=os.path.join(self.package_folder, "python"),
        )
        copy(
            self,
            "README.md",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "res"),
        )

        # Apply security gates if available from mixin
        if hasattr(self, "apply_security_gates"):
            self.apply_security_gates()
        if hasattr(self, "generate_sbom"):
            self.generate_sbom()

    def package_info(self):
        """Expose run-time environment for consumers."""
        python_path = os.path.join(self.package_folder, "python")
        self.runenv_info.append_path("PYTHONPATH", python_path)
        self.buildenv_info.append_path("PYTHONPATH", python_path)
        self.conf_info.define("user.mcp-core:python_path", python_path)

    def package_id(self):
        """Platform-independent Python package."""
        self.info.clear()
