from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake
from conan.tools.layout import basic_layout
from conan.tools.files import copy
import os

class SpareToolsBpmSchemasConan(ConanFile):
    """SpareTools BPM Schemas - FlatBuffers schemas for BPM detection protocol."""

    name = "sparetools-bpm-schemas"
    version = "2.0.0"
    package_type = "header-library"

    # SpareTools foundation package with security mixins
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    # Optional metadata
    license = "MIT"
    author = "SpareTools Team"
    url = "https://github.com/sparesparrow/sparetools"
    description = "FlatBuffers schemas for BPM detection protocol (SpareTools foundation)"
    topics = ("flatbuffers", "schemas", "bpm", "protocol", "sparetools", "foundation")

    # Header-only package - minimal settings
    settings = "os", "compiler", "build_type", "arch"

    exports_sources = "schemas/*", "CMakeLists.txt"

    def layout(self):
        basic_layout(self)

    def requirements(self):
        # FlatBuffers library for CMake config files
        self.requires("flatbuffers/24.3.25")

    def build_requirements(self):
        # SpareTools FlatBuffers compiler tool
        self.tool_requires("sparetools-flatbuffers/24.3.25")
        # Build tools
        self.tool_requires("cmake/[>=3.25]")
        # Bundled Python for any build scripts
        self.tool_requires("sparetools-cpython/3.12.7")
    
    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # Copy schema files
        copy(self, "*.fbs",
             src=os.path.join(self.source_folder, "schemas"),
             dst=os.path.join(self.package_folder, "schemas"))

        # Copy generated headers
        copy(self, "*.h",
             src=os.path.join(self.build_folder, "generated", "cpp"),
             dst=os.path.join(self.package_folder, "include"))

        # Copy generated Python bindings (if generated)
        python_gen_path = os.path.join(self.build_folder, "generated", "python")
        if os.path.exists(python_gen_path):
            copy(self, "*.py",
                 src=python_gen_path,
                 dst=os.path.join(self.package_folder, "python"))

    def package_info(self):
        # Header-only package - clear platform-specific settings
        self.cpp_info.libs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []

        # Include directory for generated headers
        self.cpp_info.includedirs = ["include"]

        # Define schema version for compile-time checks
        self.cpp_info.defines = ["BPM_SCHEMA_VERSION=1", "SPARETOOLS_BPM_SCHEMAS"]

        # Python bindings path (if available)
        if os.path.exists(os.path.join(self.package_folder, "python")):
            # Add python directory to environment for runtime access
            self.runenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "python"))

    def package_id(self):
        # Make package ID platform-independent (typical for header-only)
        self.info.clear()


