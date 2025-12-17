from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.layout import basic_layout
from conan.tools.files import copy
import os


class SpareToolsNucleusConan(ConanFile):
    """NucleusESP32 Conan package - SpareTools ESP32 consumer implementation."""

    name = "sparetools-nucleus"
    version = "0.1.0"
    package_type = "application"

    # This is an ESP32 consumer package in the SpareTools ecosystem
    python_requires = "sparetools-base/2.0.0"

    # Optional metadata
    license = "MIT"
    author = "SpareTools Team"
    url = "https://github.com/sparesparrow/NucleusESP32"
    description = "NucleusESP32 - ESP32-based multi-tool device firmware (SpareTools consumer)"
    topics = ("esp32", "embedded", "rf", "nfc", "iot", "sparetools", "consumer")

    # Binary configuration - focus on host testing, not ESP32 cross-compilation
    settings = "os", "compiler", "build_type", "arch"

    # Sources are located in the same place as this recipe
    exports_sources = "CMakeLists.txt", "src/*", "include/*", "test/*", "test_harness/*"

    def layout(self):
        basic_layout(self, src_folder=".")

    def build_requirements(self):
        # ESP32 consumer foundation packages
        self.tool_requires("sparetools-cpython/3.12.7")
        self.tool_requires("sparetools-test-harness/2.0.0")
        self.tool_requires("sparetools-shared-dev-tools/2.0.0")
        # Note: bootstrap is used at environment setup time, not build time

    def requirements(self):
        # Testing framework for host-based C++ unit tests
        self.requires("gtest/1.14.0")

    def generate(self):
        # Generate CMake toolchain and dependencies for host testing
        tc = CMakeToolchain(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        # Copy test harness Python modules
        if os.path.exists(os.path.join(self.source_folder, "test_harness")):
            copy(self, "test_harness/**/*.py",
                 src=self.source_folder,
                 dst=os.path.join(self.package_folder, "test_harness"))

    def package_info(self):
        # Define components for different modules (when built)
        # self.cpp_info.components["rf_module"].libs = ["rf"]
        # self.cpp_info.components["nfc_module"].libs = ["nfc"]
        # self.cpp_info.components["ir_module"].libs = ["ir"]

        # Python test environment setup
        self.buildenv_info.define("NUCLEUS_PACKAGE_DIR", self.package_folder)
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)
        if os.path.exists(os.path.join(self.package_folder, "test_harness")):
            self.buildenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "test_harness"))

        self.runenv_info.define("NUCLEUS_PACKAGE_DIR", self.package_folder)
        self.runenv_info.append_path("PYTHONPATH", self.package_folder)
        if os.path.exists(os.path.join(self.package_folder, "test_harness")):
            self.runenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "test_harness"))

        # Mark as development package
        self.cpp_info.libs = []