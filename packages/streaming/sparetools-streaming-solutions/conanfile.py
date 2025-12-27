#!/usr/bin/env python3
"""
Sparetools Streaming Solutions Conan Package
Real-time streaming solutions for screen casting and media streaming
"""

import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake


class SparetoolsStreamingSolutionsConan(ConanFile):
    name = "sparetools-streaming-solutions"
    version = "1.0.0"
    description = "Real-time streaming solutions for screen casting and media streaming"
    homepage = "https://github.com/sparesparrow/sparetools"
    url = "https://github.com/sparesparrow/sparetools"
    license = "MIT"
    topics = ("streaming", "screen-casting", "rtsp", "hls", "media", "upnp", "dlna")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_rtsp": [True, False],
        "with_hls": [True, False],
        "with_continuous": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_rtsp": True,
        "with_hls": True,
        "with_continuous": True,
    }

    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        """Add dependencies from other sparetools packages"""
        self.requires("sparetools-base/[*]")
        self.requires("sparetools-shared-dev-tools/[*]")

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

    def build(self):
        """Build using CMake"""
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        """Package the built artifacts"""
        cmake = CMake(self)
        cmake.install()

        # Copy scripts and shared utilities
        self.copy("shared/**", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))
        self.copy("implementations/**", src=self.source_folder, dst=os.path.join(self.package_folder, "share"))

        # Copy license
        self.copy("LICENSE", src=self.source_folder, dst="licenses")

    def package_info(self):
        """Package info"""
        self.cpp_info.libs = ["streaming_solutions"]

        # Define components for different streaming protocols
        if self.options.with_rtsp:
            self.cpp_info.components["rtsp"].libs = ["rtsp_streaming"]

        if self.options.with_hls:
            self.cpp_info.components["hls"].libs = ["hls_streaming"]

        if self.options.with_continuous:
            self.cpp_info.components["continuous"].libs = ["continuous_streaming"]