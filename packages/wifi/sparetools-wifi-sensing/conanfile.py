#!/usr/bin/env python3
"""
Sparetools WiFi Sensing Conan Package
WiFi sensing and CSI processing toolkit
"""

import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake


class SparetoolsWifiSensingConan(ConanFile):
    name = "sparetools-wifi-sensing"
    version = "1.0.1"
    description = "WiFi sensing and CSI processing toolkit"
    homepage = "https://github.com/sparesparrow/sparetools"
    url = "https://github.com/sparesparrow/sparetools"
    license = "MIT"
    topics = ("wifi", "csi", "sensing", "signal-processing", "motion-detection")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_csi": [True, False],
        "with_motion_detection": [True, False],
        "with_research_tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_csi": True,
        "with_motion_detection": True,
        "with_research_tools": True,
    }

    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        """Add dependencies from other sparetools packages"""
        self.requires("sparetools-base/[*]")
        self.requires("sparetools-shared-dev-tools/[*]")

        if self.options.with_research_tools:
            self.requires("sparetools-test-harness/[*]")

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

        # Copy scripts and research materials
        self.copy("scripts/**", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))
        self.copy("research/**", src=self.source_folder, dst=os.path.join(self.package_folder, "share"))

        # Copy license
        self.copy("LICENSE", src=self.source_folder, dst="licenses")

    def package_info(self):
        """Package info"""
        self.cpp_info.libs = ["wifi_sensing"]

        # Define components
        if self.options.with_csi:
            self.cpp_info.components["csi"].libs = ["csi_processor"]

        if self.options.with_motion_detection:
            self.cpp_info.components["motion"].libs = ["motion_detector"]