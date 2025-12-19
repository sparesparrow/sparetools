import os
import sys
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy

# Use SpareTools base utilities
python_requires = "sparetools-base/2.0.3"


class SpareToolsMcpServerCppConan(ConanFile):
    """MCP Server C++ - High-performance MCP server implementation in C++."""

    name = "sparetools-mcpserver-cpp"
    version = "2.0.0"
    package_type = "library"
    description = "High-performance MCP (Model Context Protocol) server implementation in C++"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("mcp", "cpp", "server", "high-performance", "json-rpc")

    # Declare consumer context
    consumer_domain = "mcp"

    # Use SpareTools base utilities
    python_requires = "sparetools-base/2.0.3"

    # Runtime dependencies
    requires = (
        "sparetools-openssl/3.3.2",
    )

    # Settings
    settings = "os", "arch", "compiler", "build_type"

    # Options
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    # Source and export configuration
    exports_sources = (
        "src/*",
        "include/*",
        "CMakeLists.txt",
    )

    def configure(self):
        """Apply C++-specific configuration."""
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        """Set up build layout."""
        from conan.tools.cmake import cmake_layout
        cmake_layout(self)

    def generate(self):
        """Generate build files."""
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        """Build the C++ MCP server."""
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        """Package the C++ MCP server."""
        cmake = CMake(self)
        cmake.install()

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        """Provide C++ MCP server information."""
        self.cpp_info.libs = ["mcpserver"]

        # Include directories
        self.cpp_info.includedirs = ["include"]

        # Dependencies
        self.cpp_info.requires = ["sparetools-openssl::sparetools-openssl"]