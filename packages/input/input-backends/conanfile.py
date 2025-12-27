#!/usr/bin/env python3
"""
Input Backends Conan Package Recipe
Multi-platform input simulation system
"""

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake


class SparetoolsInputBackendsConan(ConanFile):
    name = "sparetools-input-backends"
    version = "1.0.0"
    description = "Multi-platform input simulation backends"
    homepage = "https://github.com/sparesparrow/sparetools"
    url = "https://github.com/sparesparrow/sparetools"
    license = "MIT"
    topics = ("input", "simulation", "backends", "x11", "wayland", "linux")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_x11": [True, False],
        "with_wayland": [True, False],
        "with_kde": [True, False],
        "with_sdl2": [True, False],
        "with_uinput": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_x11": True,
        "with_wayland": True,
        "with_kde": True,
        "with_sdl2": True,
        "with_uinput": True,
    }

    generators = "CMakeDeps", "CMakeToolchain"
    test_requires = "gtest/1.14.0"

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
        self.cpp_info.libs = ["input_backends"]

        # System library dependencies
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["pthread"])

            if self.options.with_x11:
                self.cpp_info.system_libs.extend(["X11", "Xtst"])

            if self.options.with_wayland:
                self.cpp_info.system_libs.extend(["wayland-client"])

            if self.options.with_sdl2:
                self.cpp_info.system_libs.extend(["SDL2"])

        # Define components for different backends
        self.cpp_info.components["core"].libs = ["input_backends"]

        if self.options.with_x11:
            self.cpp_info.components["x11"].libs = []
            self.cpp_info.components["x11"].system_libs = ["X11", "Xtst"]

        if self.options.with_wayland:
            self.cpp_info.components["wayland"].libs = []
            self.cpp_info.components["wayland"].system_libs = ["wayland-client"]

        if self.options.with_sdl2:
            self.cpp_info.components["sdl2"].libs = []
            self.cpp_info.components["sdl2"].system_libs = ["SDL2"]