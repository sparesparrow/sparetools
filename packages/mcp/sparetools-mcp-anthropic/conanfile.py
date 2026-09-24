from conan import ConanFile
from conan.tools.files import copy
import os


class SparetoolsMcpAnthropicConan(ConanFile):
    name = "sparetools-mcp-anthropic"
    version = "1.0.0"
    description = "Anthropic Claude API integration for SpareTools MCP ecosystem"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("mcp", "anthropic", "claude", "ai", "llm", "code-review")

    python_requires = "sparetools-base/2.0.4"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"
    tool_requires = "sparetools-cpython/3.12.7"

    package_type = "python-require"

    exports_sources = "src/**/*.py", "pyproject.toml", "README.md", "requirements.txt"

    def package(self):
        copy(
            self,
            "*.py",
            src=os.path.join(self.source_folder, "src"),
            dst=os.path.join(self.package_folder, "python"),
        )
        copy(
            self,
            "requirements.txt",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "res"),
        )
        copy(
            self,
            "README.md",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "res"),
        )

    def package_info(self):
        self.runenv_info.append_path(
            "PYTHONPATH", os.path.join(self.package_folder, "python")
        )
