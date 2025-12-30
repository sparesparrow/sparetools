from conan import ConanFile
from conan.tools.files import copy
import os

class SparetoolsMonorepoConan(ConanFile):
    name = "sparetools-monorepo"
    version = "1.0.1"
    description = "Meta-package for SpareTools monorepo - includes all shared components"
    license = "Apache-2.0"
    author = "SpareSparrow"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("monorepo", "embedded", "protocols", "utilities", "conan")

    # This is a meta-package that depends on all SpareTools packages
    def requirements(self):
        # Core protocol schemas
        self.requires("sparesparrow-protocols/1.0.0@sparesparrow/stable")

        # Embedded utilities
        self.requires("sparetools-embedded/1.0.0@sparesparrow/stable")

        # Python utilities
        self.requires("sparetools-py/1.0.0@sparesparrow/stable")

        # CPython extensions
        self.requires("sparetools-cpython/1.0.0@sparesparrow/stable")

        # MCP servers for development workflows
        self.requires("sparetools-mcp-servers/1.0.0@sparesparrow/stable")

    def package_info(self):
        # Meta-package doesn't provide libraries directly
        # Consumers get components through individual package requirements
        self.cpp_info.libs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []

        # Provide information about included components
        self.user_info = {
            "protocols": "sparesparrow-protocols/1.0.0",
            "embedded": "sparetools-embedded/1.0.0",
            "python": "sparetools-py/1.0.0",
            "cpython": "sparetools-cpython/1.0.0",
            "mcp_servers": "sparetools-mcp-servers/1.0.0"
        }

    def layout(self):
        # Basic layout for meta-package
        pass

    def package(self):
        # Meta-package doesn't package files
        # Copy documentation and examples
        copy(self, "*.md", src=self.source_folder, dst=self.package_folder)
        copy(self, "README.md", src=self.source_folder, dst=self.package_folder)

    def package_id(self):
        # Meta-package ID is determined by its requirements
        # Don't make it platform-specific
        self.info.clear()