#!/usr/bin/env python3
"""
Gamepad Mapper Conan Package Recipe
Multi-backend input simulation system with fallback support
"""

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.files import copy
from conan.errors import ConanInvalidConfiguration
import os


class SparetoolsGamepadMapperConan(ConanFile):
    name = "sparetools-gamepad-mapper"
    version = "1.0.0"
    test_type = "explicit"

    # Package metadata
    description = "Multi-backend gamepad to keyboard/mouse input mapper"
    homepage = "https://github.com/sparesparrow/sparetools"
    url = "https://github.com/sparesparrow/sparetools"
    license = "MIT"
    topics = ("gamepad", "input", "mapper", "simulation", "linux")
    # Package configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_x11": [True, False],
        "with_wayland": [True, False],
        "with_kde": [True, False],
        "with_sdl2": [True, False],
        "with_uinput": [True, False],
        "with_mcp": [True, False],
        "with_bluetooth": [True, False],
        "with_clipboard": [True, False],
        "with_alsa": [True, False],
        "with_pulseaudio": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_x11": True,
        "with_wayland": True,
        "with_kde": True,
        "with_sdl2": True,
        "with_uinput": True,
        "with_mcp": False,
        "with_bluetooth": False,
        "with_clipboard": True,
        "with_alsa": True,
        "with_pulseaudio": True,
    }

    generators = "CMakeDeps", "CMakeToolchain"
    test_requires = "gtest/1.14.0"

    def configure(self):
        """Configure package options"""
        if self.options.shared:
            del self.options.fPIC

        # SDL2 requires shared libraries on some platforms
        if self.options.with_sdl2 and not self.options.shared:
            self.options["sdl2"].shared = True

    def requirements(self):
        """Add dependencies based on enabled backends"""
        # Core dependencies
        self.requires("nlohmann_json/3.11.2")
        self.requires("jsoncpp/1.9.5")
        self.requires("libcurl/8.4.0")

        # Backend-specific dependencies with fallbacks
        # X11 libraries will be found via pkg-config on the system

        # Wayland libraries will be found via pkg-config on the system

        # SDL2 not available in Conan Center, will use system library

        if self.options.with_mcp:
            # TinyMCP includes its own dependencies
            pass

    def validate(self):
        """Validate configuration"""
        if self.settings.os not in ["Linux"]:
            raise ConanInvalidConfiguration("Gamepad Mapper currently only supports Linux")

        # Ensure at least one backend is enabled
        backends = [
            self.options.with_x11,
            self.options.with_wayland,
            self.options.with_kde,
            self.options.with_sdl2,
            self.options.with_uinput,
            self.options.with_bluetooth
        ]

        if not any(backends):
            raise ConanInvalidConfiguration("At least one input backend must be enabled")

    def layout(self):
        """Define the layout for generators"""
        self.folders.generators = "build"

    def export_sources(self):
        """Export source files"""
        copy(self, "CMakeLists.txt", src=".", dst=self.export_sources_folder)
        copy(self, "src/**", src=".", dst=self.export_sources_folder)
        copy(self, "include/**", src=".", dst=self.export_sources_folder)
        copy(self, "config/**", src=".", dst=self.export_sources_folder)
        copy(self, "external/**", src=".", dst=self.export_sources_folder)
        copy(self, "gamepad-mapper.pc.in", src=".", dst=self.export_sources_folder)

    def export_test_sources(self):
        """Export test sources for testing the package"""
        copy(self, "tests/**", src=".", dst=self.export_test_sources_folder)

    def build(self):
        """Build using CMake"""
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        """Package the built artifacts"""
        cmake = CMake(self)
        cmake.install()

        # Copy config files
        copy(self, "config/**", src=self.source_folder, dst=os.path.join(self.package_folder, "config"))

        # Copy license
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def test(self):
        """Run tests for the package"""
        if self.conf.get("tools.cmake.cmaketoolchain:generator", default=False, check_type=str):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
            cmake.test()

    def deploy(self):
        """Deploy the package to the local cache"""
        copy(self, "*.h", src=os.path.join(self.package_folder, "include"), dst="include")
        copy(self, "*.lib", src=os.path.join(self.package_folder, "lib"), dst="lib", keep_path=False)
        copy(self, "*.dll", src=os.path.join(self.package_folder, "bin"), dst="bin", keep_path=False)
        copy(self, "*.dylib*", src=os.path.join(self.package_folder, "lib"), dst="lib", keep_path=False)
        copy(self, "*.so", src=os.path.join(self.package_folder, "lib"), dst="lib", keep_path=False)
        copy(self, "*.a", src=os.path.join(self.package_folder, "lib"), dst="lib", keep_path=False)
        copy(self, "*", src=os.path.join(self.package_folder, "bin"), dst="bin", keep_path=False)
        copy(self, "**/config/**", src=os.path.join(self.package_folder, "config"), dst="config", keep_path=False)

    def package_info(self):
        """Package info"""
        self.cpp_info.libs = ["gamepad_mapper"]

        if self.options.with_mcp:
            self.cpp_info.libs.append("mcp_server")

        # Backend-specific libraries
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["udev", "pthread"])

            if self.options.with_uinput:
                self.cpp_info.system_libs.append("udev")

        # Define components for different backends
        self.cpp_info.components["core"].libs = ["gamepad_mapper"]
        self.cpp_info.components["core"].requires = ["nlohmann_json::nlohmann_json"]

        if self.options.with_mcp:
            self.cpp_info.components["mcp"].libs = ["mcp_server"]
            self.cpp_info.components["mcp"].requires = [
                "boost::boost",
                "openssl::openssl",
                "nlohmann_json::nlohmann_json",
                "jsoncpp::jsoncpp"
            ]

        # Backend components
        if self.options.with_x11:
            self.cpp_info.components["x11"].requires = ["xorg::xorg"]

        if self.options.with_wayland:
            self.cpp_info.components["wayland"].requires = [
                "wayland::wayland",
                "wayland-protocols::wayland-protocols"
            ]

        if self.options.with_sdl2:
            self.cpp_info.components["sdl2"].requires = ["sdl2::sdl2"]
