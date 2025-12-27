#!/usr/bin/env python3
"""
Sparetools SDR Tools Conan Package
SDR, RF, and WiFi analysis tools
"""

import os
from conan import ConanFile


class SparetoolsSdrToolsConan(ConanFile):
    name = "sparetools-sdr-tools"
    version = "1.0.0"
    description = "SDR, RF, and WiFi analysis tools"
    homepage = "https://github.com/sparesparrow/sparetools"
    url = "https://github.com/sparesparrow/sparetools"
    license = "MIT"
    topics = ("sdr", "rf", "wifi", "analysis", "gnuradio")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "with_sdr": [True, False],
        "with_wifi": [True, False],
        "with_usb": [True, False],
    }
    default_options = {
        "with_sdr": True,
        "with_wifi": True,
        "with_usb": True,
    }

    def requirements(self):
        """Add dependencies from other sparetools packages"""
        self.requires("sparetools-base/[*]")
        if self.options.with_usb:
            self.requires("sparetools-input-backends/[*]")

    def package(self):
        """Package the SDR tools"""
        # Copy SDR scripts
        if self.options.with_sdr:
            self.copy("sdr_*.py", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))
            self.copy("sdr_*.sh", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))

        # Copy WiFi tools
        if self.options.with_wifi:
            self.copy("wifi_*.py", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))

        # Copy USB/gamepad tools
        if self.options.with_usb:
            self.copy("*gamepad*.py", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))
            self.copy("usb_monitor.sh", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"))

        # Copy license
        self.copy("LICENSE", src=self.source_folder, dst="licenses")

    def package_info(self):
        """Package info - mostly scripts"""
        pass