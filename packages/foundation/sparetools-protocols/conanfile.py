from conan import ConanFile
from conan.errors import ConanException
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.layout import basic_layout
from conan.tools.files import copy
import os


class SparetoolsProtocolsConan(ConanFile):
    """SpareTools Protocols - Consolidated FlatBuffers schemas for SpareTools ecosystem."""

    name = "sparetools-protocols"
    version = "1.0.0"
    package_type = "header-library"

    # SpareTools foundation package with security mixins
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    # Optional metadata
    license = "MIT"
    author = "SpareTools Team"
    url = "https://github.com/sparesparrow/sparetools"
    description = "Consolidated FlatBuffers protocol schemas for SpareTools ecosystem"
    topics = ("flatbuffers", "schemas", "protocols", "sparetools", "foundation")

    # Settings for header-only library
    settings = "os", "compiler", "build_type", "arch"

    # Export all schema files and build configuration
    exports_sources = "schemas/**/*.fbs", "CMakeLists.txt", "README.md"

    def layout(self):
        basic_layout(self)

    def requirements(self):
        # FlatBuffers runtime for generated code
        self.requires("flatbuffers/24.3.25")

    def build_requirements(self):
        # Use SpareTools FlatBuffers tool package
        self.tool_requires("sparetools-flatbuffers/24.3.25")
        # Build tools
        self.tool_requires("cmake/[>=3.25]")
        # Bundled Python for any build scripts
        self.tool_requires("sparetools-cpython/3.12.7")

    def configure(self):
        # Header-only package
        pass

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # Copy all schema files organized by domain
        copy(self, "*.fbs",
             src=os.path.join(self.source_folder, "schemas"),
             dst=os.path.join(self.package_folder, "schemas"))

        # Copy subdirectories
        for subdir in ["common", "medical", "iot", "mcp", "embedded"]:
            schema_subdir = os.path.join(self.source_folder, "schemas", subdir)
            if os.path.exists(schema_subdir):
                copy(self, "*.fbs",
                     src=schema_subdir,
                     dst=os.path.join(self.package_folder, "schemas", subdir))

        # Copy generated headers from build directory
        copy(self, "*_generated.h",
             src=self.build_folder,
             dst=os.path.join(self.package_folder, "include"),
             keep_path=False)

        # Copy generated headers from subdirectories
        for root, dirs, files in os.walk(self.build_folder):
            for file in files:
                if file.endswith("_generated.h"):
                    rel_path = os.path.relpath(root, self.build_folder)
                    if rel_path != ".":
                        dst_dir = os.path.join(self.package_folder, "include", rel_path)
                        os.makedirs(dst_dir, exist_ok=True)
                        copy(self, file,
                             src=root,
                             dst=dst_dir,
                             keep_path=False)

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        # Header-only package - no libs or bins
        self.cpp_info.libs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []

        # Include directories for generated headers
        self.cpp_info.includedirs = ["include"]

        # Define components for different protocol domains
        # This allows consumers to only include headers they need

        # Core/common schemas
        self.cpp_info.components["common"].includedirs = ["include"]

        # IoT and embedded protocols
        self.cpp_info.components["iot"].includedirs = ["include"]
        self.cpp_info.components["embedded"].includedirs = ["include"]

        # Medical protocols
        self.cpp_info.components["medical"].includedirs = ["include"]

        # MCP (Model Context Protocol)
        self.cpp_info.components["mcp"].includedirs = ["include"]

        # Schema resource directories for consumers who need .fbs files
        self.cpp_info.resdirs = ["schemas"]

        # Version information
        self.cpp_info.defines = [f"SPARETOOLS_PROTOCOLS_VERSION={self.version}"]

        # Runtime dependency on FlatBuffers
        self.cpp_info.requires = ["flatbuffers::flatbuffers"]

    def package_id(self):
        # Platform-independent header-only package
        self.info.clear()

    def validate(self):
        # Ensure FlatBuffers runtime is available
        if not self.dependencies.get("flatbuffers"):
            raise ConanException("FlatBuffers dependency not found")

        # Validate that schemas exist (only if source_folder is available)
        if hasattr(self, 'source_folder') and self.source_folder:
            schemas_dir = os.path.join(self.source_folder, "schemas")
            if not os.path.exists(schemas_dir):
                raise ConanException(f"Schemas directory not found: {schemas_dir}")

            schema_files = []
            for root, dirs, files in os.walk(schemas_dir):
                schema_files.extend([os.path.join(root, f) for f in files if f.endswith('.fbs')])

            if not schema_files:
                raise ConanException("No .fbs schema files found in schemas directory")

            self.output.info(f"Found {len(schema_files)} schema files to process")