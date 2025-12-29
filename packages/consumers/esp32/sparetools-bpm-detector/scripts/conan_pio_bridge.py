#!/usr/bin/env python3
"""
ESP32 BPM Detector Conan-PlatformIO Bridge Script

Project-specific bridge script for ESP32 BPM Detector that integrates with
the enterprise-grade SpareTools Conan-PlatformIO bridge system.

This script configures the build environment for BPM Detector firmware,
including FlatBuffers schema integration, audio processing, and networking.
"""

import os
import sys
import json
from pathlib import Path

# Add SpareTools shared dev tools to path
sparetools_root = Path(__file__).parent.parent.parent.parent.parent.parent
shared_dev_tools = sparetools_root / "packages" / "foundation" / "sparetools-shared-dev-tools"

if str(shared_dev_tools) not in sys.path:
    sys.path.insert(0, str(shared_dev_tools))

try:
    from shared_dev_tools.conan_pio_bridge import ConanPIOBridge
except ImportError:
    print("ERROR: SpareTools shared dev tools not found. Make sure SpareTools is properly installed.")
    sys.exit(1)


class BpmDetectorBridge:
    """
    ESP32 BPM Detector-specific Conan-PlatformIO bridge implementation.

    This class extends the generic bridge with BPM Detector-specific configurations
    for FlatBuffers schemas, audio processing, and networking features.
    """

    def __init__(self):
        self.bridge = ConanPIOBridge(sparetools_root)
        self.bpm_config = self._load_bpm_config()

    def _load_bpm_config(self):
        """Load ESP32 BPM Detector-specific configuration."""
        config_file = Path(__file__).parent.parent / "bpm_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)

        # Default configuration
        return {
            "schema_packages": ["sparesparrow-protocols/1.0.0"],
            "hal_packages": ["sparetools-hal-sunton/1.0.0"],
            "target_board": "esp32s3",
            "features": {
                "networking": True,
                "websocket": True,
                "display": True,
                "audio_calibration": True
            }
        }

    def get_packages_for_env(self, pio_env):
        """
        Get Conan packages required for the given PlatformIO environment.

        Args:
            pio_env: PlatformIO environment name

        Returns:
            List of ConanPackage objects
        """
        from shared_dev_tools.conan_pio_bridge import ConanPackage

        packages = []

        # Core protocol schemas - BPM detector's foundation
        for pkg_ref in self.bpm_config["schema_packages"]:
            name, version = pkg_ref.split("/")
            packages.append(ConanPackage(name, version))

        # HAL packages for display support
        if self.bpm_config["features"]["display"]:
            for pkg_ref in self.bpm_config["hal_packages"]:
                name, version = pkg_ref.split("/")
                packages.append(ConanPackage(name, version))

        return packages

    def bridge_environment(self, pio_env):
        """
        Bridge the Conan dependencies for the given PlatformIO environment.

        Args:
            pio_env: PlatformIO environment name

        Returns:
            Generated PlatformIO configuration string
        """
        # Determine Conan profile based on environment
        conan_profile_map = {
            "esp32-s3": "esp32_sunton_v3",
            "esp32-s3-debug": "esp32_sunton_v3",
            "esp32-s3-release": "esp32_sunton_v3",
            "esp32-s3-ci": "esp32_sunton_v3",
            "esp32": "esp32_base",
        }

        conan_profile = conan_profile_map.get(pio_env, "esp32_base")
        conan_profile_path = f"../conan_profiles/{conan_profile}.prof"

        # Get packages for this environment
        packages = self.get_packages_for_env(pio_env)

        # Execute bridge
        return self.bridge.bridge(conan_profile_path, pio_env, packages)


def main():
    """Main entry point for the BPM Detector bridge script."""
    import argparse

    parser = argparse.ArgumentParser(description="ESP32 BPM Detector Conan-PlatformIO Bridge")
    parser.add_argument("--env", required=True, help="PlatformIO environment name")

    args = parser.parse_args()

    try:
        bpm_bridge = BpmDetectorBridge()
        config = bpm_bridge.bridge_environment(args.env)
        print(config)

    except Exception as e:
        print(f"ERROR: Bridge operation failed: {e}", file=sys.stderr)
        sys.exit(1)


# PlatformIO pre-build hook
def pre_build(env):
    """
    PlatformIO pre-build hook for ESP32 BPM Detector.

    This function is called by PlatformIO before building and sets up
    the Conan dependencies and build environment.
    """
    print("ESP32 BPM Detector pre-build hook: Setting up Conan dependencies...")

    try:
        # Get current environment
        pio_env = env["PIOENV"] if "PIOENV" in env else "esp32-s3"

        # Execute bridge
        bpm_bridge = BpmDetectorBridge()
        config = bpm_bridge.bridge_environment(pio_env)

        # Apply BPM Detector specific configuration
        env.Append(CPPDEFINES=[
            ("SPARETOOLS_ECOSYSTEM", "1"),
            ("BPM_DETECTOR_FIRMWARE", "1"),
            ("FLATBUFFERS_PROTOCOL", "1"),
        ])

        # Add BPM detector feature flags
        bpm_config = bpm_bridge.bpm_config
        if bpm_config["features"]["networking"]:
            env.Append(CPPDEFINES=["BPM_NETWORKING_ENABLED"])
        if bpm_config["features"]["websocket"]:
            env.Append(CPPDEFINES=["BPM_WEBSOCKET_ENABLED"])
        if bpm_config["features"]["display"]:
            env.Append(CPPDEFINES=["BPM_DISPLAY_ENABLED"])
        if bpm_config["features"]["audio_calibration"]:
            env.Append(CPPDEFINES=["BPM_AUDIO_CALIBRATION_ENABLED"])

        # Add include paths from Conan (FlatBuffers headers, etc.)
        if "include_paths" in config:
            for path in config["include_paths"]:
                env.Append(CPPPATH=[path])

        # Add library paths (if any)
        if "lib_paths" in config:
            for path in config["lib_paths"]:
                env.Append(LIBPATH=[path])

        # Add libraries (if any)
        if "libs" in config:
            env.Append(LIBS=config["libs"])

        print("✅ ESP32 BPM Detector Conan dependencies configured")

    except Exception as e:
        print(f"❌ Pre-build hook failed: {e}")
        env.Exit(1)


if __name__ == "__main__":
    main()