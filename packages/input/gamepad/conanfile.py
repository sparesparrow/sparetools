#!/usr/bin/env python3
"""
Gamepad Core Conan Package Recipe
Core gamepad mapping and device management functionality
"""

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake


class SparetoolsGamepadCoreConan(ConanFile):
    # Use SpareTools base utilities
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    name = "sparetools-gamepad-core"
    version = "1.0.0"
    description = "Core gamepad mapping and device management library"
    homepage = "https://github.com/sparesparrow/sparetools"
    url = "https://github.com/sparesparrow/sparetools"
    license = "MIT"
    topics = ("gamepad", "input", "mapping", "controller", "cpp")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "CMakeDeps", "CMakeToolchain"
    test_requires = "gtest/1.14.0"

    def requirements(self):
        """Add dependencies"""
        self.requires("nlohmann_json/3.11.2")

    def configure(self):
        """Configure package options"""
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        """Define the layout for generators"""
        self.folders.generators = "build"

    def export_sources(self):
        """Export source files"""
        self.copy("CMakeLists.txt", src=".", dst=".")
        self.copy("src/**", src=".", dst=".")
        self.copy("include/**", src=".", dst=".")
        self.copy("cmake/**", src=".", dst=".")

    def export_test_sources(self):
        """Export test sources"""
        self.copy("tests/**", src=".", dst=".")

    def build(self):
        """Build using CMake"""
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        """Package the built artifacts"""
        cmake = CMake(self)
        cmake.install()

        # Copy license
        self.copy("LICENSE", src=self.source_folder, dst="licenses")

    def test(self):
        """Run tests"""
        if self.conf.get("tools.cmake.cmaketoolchain:generator", default=False, check_type=str):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
            cmake.test()

    def package_info(self):
        """Package info"""
        self.cpp_info.libs = ["gamepad_core"]
        self.cpp_info.requires = ["nlohmann_json::nlohmann_json"]