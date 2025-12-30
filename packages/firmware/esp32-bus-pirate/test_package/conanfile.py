import os
from pathlib import Path

from conans import ConanFile


class Esp32BusPirateTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def build_requirements(self):
        self.build_requires("esp32-bus-pirate/1.0.0")

    def test(self):
        """Test that the ESP32-Bus-Pirate package was created correctly"""
        # Check that firmware directory exists
        firmware_dir = Path(self.deps_env_info["esp32-bus-pirate"].package_dir) / "firmware"
        if not firmware_dir.exists():
            raise Exception(f"Firmware directory not found: {firmware_dir}")

        # Check for firmware binaries
        bin_files = list(firmware_dir.glob("esp32-bus-pirate-*.bin"))
        if not bin_files:
            self.output.warn("No firmware binaries found in package")
        else:
            self.output.info(f"Found {len(bin_files)} firmware binaries:")
            for bin_file in bin_files:
                self.output.info(f"  - {bin_file.name}")

        # Check for source files
        source_files = [
            "platformio.ini",
            "src/main.cpp",
            "README.md"
        ]

        package_dir = Path(self.deps_env_info["esp32-bus-pirate"].package_dir)
        for source_file in source_files:
            if not (package_dir / source_file).exists():
                raise Exception(f"Required source file not found: {source_file}")

        # Check for firmware info
        readme_file = firmware_dir / "README.md"
        if readme_file.exists():
            self.output.info("Firmware README found")
        else:
            self.output.warn("Firmware README not found")

        # Check user info
        if hasattr(self.deps_user_info["esp32-bus-pirate"], "firmware_version"):
            self.output.info(f"Firmware version: {self.deps_user_info['esp32-bus-pirate'].firmware_version}")

        if hasattr(self.deps_user_info["esp32-bus-pirate"], "board"):
            self.output.info(f"Board configuration: {self.deps_user_info['esp32-bus-pirate'].board}")

        self.output.success("ESP32-Bus-Pirate package validation completed successfully!")



