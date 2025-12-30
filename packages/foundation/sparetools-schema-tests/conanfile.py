from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.layout import basic_layout
from conan.tools.files import copy
import os


class SparetoolsSchemaTestsConan(ConanFile):
    """SpareTools Schema Tests - Automated FlatBuffers schema compatibility testing."""

    name = "sparetools-schema-tests"
    version = "1.0.0"
    package_type = "application"

    # SpareTools foundation package with security mixins
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    # Optional metadata
    license = "MIT"
    author = "SpareTools Team"
    url = "https://github.com/sparesparrow/sparetools"
    description = "Automated testing framework for FlatBuffers schema compatibility"
    topics = ("testing", "flatbuffers", "schemas", "compatibility", "sparetools", "foundation")

    # Settings for cross-platform testing
    settings = "os", "compiler", "build_type", "arch"

    # Export test framework and schemas
    exports_sources = "src/*", "tests/*", "CMakeLists.txt", "schema_fixtures/*", "README.md"

    def layout(self):
        basic_layout(self)

    def requirements(self):
        # Protocol schemas to test
        self.requires("sparetools-protocols/1.0.0")
        # FlatBuffers runtime
        self.requires("flatbuffers/24.3.25")
        # Testing framework
        self.requires("gtest/1.14.0")

    def build_requirements(self):
        # FlatBuffers compiler for test generation
        self.tool_requires("sparetools-flatbuffers/24.3.25")
        # Build tools
        self.tool_requires("cmake/[>=3.25]")
        # Bundled Python for test scripts
        self.tool_requires("sparetools-cpython/3.12.7")

    def configure(self):
        # Test application
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
        # Package test executables
        copy(self, "schema_tests*", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        copy(self, "*.py", src=os.path.join(self.source_folder, "tests"), dst=os.path.join(self.package_folder, "tests"))

        # Package test fixtures and schemas
        copy(self, "*", src=os.path.join(self.source_folder, "schema_fixtures"), dst=os.path.join(self.package_folder, "fixtures"))
        copy(self, "*.fbs", src=os.path.join(self.source_folder, "schema_fixtures"), dst=os.path.join(self.package_folder, "schemas"))

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        # Test executables
        self.cpp_info.libs = []
        self.cpp_info.libdirs = []
        self.buildenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))

        # Python test environment
        python_path = os.path.join(self.package_folder, "tests")
        self.runenv_info.append_path("PYTHONPATH", python_path)
        self.buildenv_info.append_path("PYTHONPATH", python_path)

        # Schema fixtures path
        self.conf_info.define("user.schema-tests:fixtures", os.path.join(self.package_folder, "fixtures"))
        self.conf_info.define("user.schema-tests:schemas", os.path.join(self.package_folder, "schemas"))

    def package_id(self):
        # Test package - platform specific for executables
        self.info.clear()