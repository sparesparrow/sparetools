#!/usr/bin/env python3
"""
NucleusESP32 Conan-PlatformIO Bridge Script

Project-specific bridge script for NucleusESP32 that integrates with
the enterprise-grade SpareTools Conan-PlatformIO bridge system.

This script configures the build environment for NucleusESP32 firmware,
including HAL integration, crypto suites, and security hardening.
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


class NucleusESP32Bridge:
    """
    NucleusESP32-specific Conan-PlatformIO bridge implementation.

    This class extends the generic bridge with Nucleus-specific configurations
    for HAL integration, crypto suites, and security features.
    """

    def __init__(self):
        self.bridge = ConanPIOBridge(sparetools_root)
        self.nucleus_config = self._load_nucleus_config()

    def _load_nucleus_config(self):
        """Load NucleusESP32-specific configuration."""
        config_file = Path(__file__).parent.parent / "nucleus_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)

        # Default configuration
        return {
            "hal_packages": ["sparetools-hal-sunton/1.0.0"],
            "crypto_packages": ["sparetools-crypto-suite/1.0.0"],
            "security_profile": "enterprise",
            "target_board": "esp32s3"
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

        # Base dependencies
        packages.extend([
            ConanPackage("gtest", "1.14.0"),
            ConanPackage("lvgl", "8.3.11"),
        ])

        # HAL packages for display-equipped boards
        if "sunton" in pio_env or self.nucleus_config["target_board"] == "esp32s3":
            for pkg_ref in self.nucleus_config["hal_packages"]:
                name, version = pkg_ref.split("/")
                packages.append(ConanPackage(name, version))

        # Crypto packages
        for pkg_ref in self.nucleus_config["crypto_packages"]:
            name, version = pkg_ref.split("/")
            packages.append(ConanPackage(name, version))

            # Configure crypto options based on security profile
            if self.nucleus_config["security_profile"] == "enterprise":
                packages[-1].options = {
                    "enable_hw_acceleration": "True",
                    "enable_secure_boot": "True",
                    "enable_flash_encryption": "True",
                    "crypto_backend": "mbedTLS",
                    "enable_fips": "True"
                }

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
            "esp32s3_sunton": "esp32_sunton_v3",
            "esp32": "esp32_base",
            "esp32c3": "esp32_base",
            "esp32c6": "esp32_base",
        }

        conan_profile = conan_profile_map.get(pio_env, "esp32_base")
        conan_profile_path = f"../conan_profiles/{conan_profile}.prof"

        # Get packages for this environment
        packages = self.get_packages_for_env(pio_env)

        # Execute bridge
        return self.bridge.bridge(conan_profile_path, pio_env, packages)


def main():
    """Main entry point for the NucleusESP32 bridge script."""
    import argparse

    parser = argparse.ArgumentParser(description="NucleusESP32 Conan-PlatformIO Bridge")
    parser.add_argument("--env", required=True, help="PlatformIO environment name")

    args = parser.parse_args()

    try:
        nucleus_bridge = NucleusESP32Bridge()
        config = nucleus_bridge.bridge_environment(args.env)
        print(config)

    except Exception as e:
        print(f"ERROR: Bridge operation failed: {e}", file=sys.stderr)
        sys.exit(1)


# PlatformIO pre-build hook
def pre_build(env):
    """
    PlatformIO pre-build hook for NucleusESP32.

    This function is called by PlatformIO before building and sets up
    the Conan dependencies and build environment.
    """
    print("NucleusESP32 pre-build hook: Setting up Conan dependencies...")

    try:
        # Get current environment
        pio_env = env["PIOENV"] if "PIOENV" in env else "esp32s3_sunton"

        # Execute bridge
        nucleus_bridge = NucleusESP32Bridge()
        config = nucleus_bridge.bridge_environment(pio_env)

        # Apply configuration to environment
        env.Append(CPPDEFINES=[
            ("SPARETOOLS_ECOSYSTEM", "1"),
            ("NUCLEUS_ESP32", "1"),
        ])

        # Add include paths from Conan
        if "include_paths" in config:
            for path in config["include_paths"]:
                env.Append(CPPPATH=[path])

        # Add library paths
        if "lib_paths" in config:
            for path in config["lib_paths"]:
                env.Append(LIBPATH=[path])

        # Add libraries
        if "libs" in config:
            env.Append(LIBS=config["libs"])

        print("✅ NucleusESP32 Conan dependencies configured")

    except Exception as e:
        print(f"❌ Pre-build hook failed: {e}")
        env.Exit(1)


if __name__ == "__main__":
    main()