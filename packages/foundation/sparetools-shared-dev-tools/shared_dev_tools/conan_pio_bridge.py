#!/usr/bin/env python3
"""
Conan ↔ PlatformIO Bridge Script

Enterprise-grade bridge for integrating Conan package management with PlatformIO
build system. Provides automatic toolchain detection, profile caching, and
comprehensive error handling for ESP32 development workflows.

Features:
- Automatic toolchain detection and configuration
- Profile caching for improved performance
- Comprehensive error handling and logging
- Support for multiple ESP32 variants
- Integration with SpareTools ecosystem
"""

import os
import sys
import json
import hashlib
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import yaml


@dataclass
class ConanPackage:
    """Represents a Conan package with its reference and options."""
    name: str
    version: str
    user: Optional[str] = None
    channel: Optional[str] = None
    options: Dict[str, Any] = None

    def __post_init__(self):
        if self.options is None:
            self.options = {}

    @property
    def reference(self) -> str:
        """Get the full Conan reference string."""
        ref = f"{self.name}/{self.version}"
        if self.user and self.channel:
            ref += f"@{self.user}/{self.channel}"
        return ref


@dataclass
class BuildProfile:
    """Represents a PlatformIO build profile with Conan dependencies."""
    name: str
    board: str
    framework: str
    platform: str
    conan_profile: str
    packages: List[ConanPackage]
    build_flags: List[str] = None
    defines: List[str] = None

    def __post_init__(self):
        if self.build_flags is None:
            self.build_flags = []
        if self.defines is None:
            self.defines = []


class ConanPIOBrideException(Exception):
    """Base exception for Conan-PlatformIO bridge operations."""
    pass


class ConanProfileNotFoundError(ConanPIOBrideException):
    """Raised when a specified Conan profile cannot be found."""
    pass


class PlatformIOConfigurationError(ConanPIOBrideException):
    """Raised when PlatformIO configuration is invalid."""
    pass


class ConanPIOBridge:
    """
    Enterprise-grade bridge between Conan and PlatformIO.

    This class provides comprehensive integration between Conan's package
    management and PlatformIO's build system, with features like:
    - Automatic toolchain detection
    - Profile caching
    - Error handling and logging
    - Multi-ESP32 variant support
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize the Conan-PlatformIO bridge.

        Args:
            workspace_root: Root directory of the workspace (defaults to current working directory)
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.cache_dir = self.workspace_root / ".conan_pio_cache"
        self.cache_dir.mkdir(exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger("ConanPIOBridge")
        self.logger.setLevel(logging.INFO)

        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Load SpareTools versions if available
        self.versions_file = self.workspace_root / "versions.yaml"
        self.versions = self._load_versions()

    def _load_versions(self) -> Dict[str, str]:
        """Load version configuration from versions.yaml if available."""
        if self.versions_file.exists():
            try:
                with open(self.versions_file, 'r') as f:
                    data = yaml.safe_load(f)
                    # Flatten the nested structure
                    versions = {}
                    for category, packages in data.items():
                        if isinstance(packages, dict):
                            versions.update(packages)
                    return versions
            except Exception as e:
                self.logger.warning(f"Failed to load versions.yaml: {e}")
        return {}

    def _get_cache_key(self, profile_name: str, packages: List[ConanPackage]) -> str:
        """Generate a cache key for the given profile and packages."""
        content = f"{profile_name}:{json.dumps([asdict(pkg) for pkg in packages], sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached configuration is still valid."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return False

        # Check if any conanfile.py has been modified more recently than cache
        conanfiles = list(self.workspace_root.glob("**/conanfile.py"))
        conanfiles.extend(self.workspace_root.glob("conanfile.py"))

        try:
            cache_mtime = cache_file.stat().st_mtime
            for conanfile in conanfiles:
                if conanfile.stat().st_mtime > cache_mtime:
                    return False
        except OSError:
            return False

        return True

    def _load_cache(self, cache_key: str) -> Optional[Dict]:
        """Load configuration from cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load cache: {e}")
        return None

    def _save_cache(self, cache_key: str, data: Dict):
        """Save configuration to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save cache: {e}")

    def detect_toolchain(self, board: str) -> Dict[str, Any]:
        """
        Detect appropriate toolchain for the given board.

        Args:
            board: PlatformIO board identifier

        Returns:
            Dictionary containing toolchain configuration
        """
        toolchain_config = {
            "compiler": "gcc",
            "arch": "xtensa",
            "flags": []
        }

        # ESP32 variants
        if board.startswith("esp32"):
            toolchain_config["arch"] = "xtensa"
            toolchain_config["flags"] = [
                "-mlongcalls",
                "-mtext-section-literals",
                "-fstrict-volatile-bitfields",
                "-fno-reorder-blocks",
                "-fno-defer-pop"
            ]

            if "s3" in board:
                toolchain_config["arch"] = "xtensa"
                toolchain_config["flags"].extend([
                    "-mfix-esp32-psram-cache-issue"
                ])
            elif "c3" in board:
                toolchain_config["arch"] = "riscv"
                toolchain_config["compiler"] = "clang"
            elif "c6" in board:
                toolchain_config["arch"] = "riscv"
                toolchain_config["compiler"] = "clang"

        return toolchain_config

    def resolve_conan_dependencies(self, conan_profile: str, packages: List[ConanPackage]) -> Dict[str, Any]:
        """
        Resolve Conan dependencies and generate configuration.

        Args:
            conan_profile: Name of the Conan profile to use
            packages: List of Conan packages to install

        Returns:
            Dictionary containing resolved dependency information
        """
        self.logger.info(f"Resolving Conan dependencies with profile: {conan_profile}")

        # Check cache first
        cache_key = self._get_cache_key(conan_profile, packages)
        if self._is_cache_valid(cache_key):
            cached = self._load_cache(cache_key)
            if cached:
                self.logger.info("Using cached Conan resolution")
                return cached

        # Install dependencies using Conan
        install_dir = self.cache_dir / f"install_{cache_key}"
        install_dir.mkdir(exist_ok=True)

        cmd = ["conan", "install", "--profile", conan_profile, "--install-folder", str(install_dir)]

        # Add package references
        for package in packages:
            cmd.extend(["--requires", package.reference])
            # Add options
            for key, value in package.options.items():
                cmd.extend(["--options", f"{package.name}:{key}={value}"])

        try:
            result = subprocess.run(cmd, cwd=self.workspace_root, capture_output=True, text=True, check=True)
            self.logger.info("Conan dependencies resolved successfully")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Conan install failed: {e}")
            self.logger.error(f"stdout: {e.stdout}")
            self.logger.error(f"stderr: {e.stderr}")
            raise ConanPIOBrideException(f"Failed to resolve Conan dependencies: {e}")

        # Parse conan install output to extract configuration
        config = self._parse_conan_install_output(install_dir, result.stdout, result.stderr)

        # Cache the result
        self._save_cache(cache_key, config)

        return config

    def _parse_conan_install_output(self, install_dir: Path, stdout: str, stderr: str) -> Dict[str, Any]:
        """Parse Conan install output to extract configuration information."""
        config = {
            "install_dir": str(install_dir),
            "include_paths": [],
            "lib_paths": [],
            "libs": [],
            "defines": [],
            "cxxflags": [],
            "cflags": [],
            "ldflags": []
        }

        # Read conanbuildinfo.cmake if available
        cmake_file = install_dir / "conanbuildinfo.cmake"
        if cmake_file.exists():
            config.update(self._parse_cmake_build_info(cmake_file))

        # Read conanbuildinfo.json if available
        json_file = install_dir / "conanbuildinfo.json"
        if json_file.exists():
            with open(json_file, 'r') as f:
                json_data = json.load(f)
                config.update(self._parse_json_build_info(json_data))

        return config

    def _parse_cmake_build_info(self, cmake_file: Path) -> Dict[str, Any]:
        """Parse CMake build info file."""
        config = {}
        try:
            with open(cmake_file, 'r') as f:
                content = f.read()

            # Extract include paths
            import re
            include_pattern = r'set\(CONAN_INCLUDE_DIRS_.*? "([^"]+)"\)'
            includes = re.findall(include_pattern, content)
            config["include_paths"] = includes

            # Extract library paths
            lib_pattern = r'set\(CONAN_LIB_DIRS_.*? "([^"]+)"\)'
            libs = re.findall(lib_pattern, content)
            config["lib_paths"] = libs

        except Exception as e:
            self.logger.warning(f"Failed to parse CMake build info: {e}")

        return config

    def _parse_json_build_info(self, json_data: Dict) -> Dict[str, Any]:
        """Parse JSON build info file."""
        config = {}
        try:
            if "dependencies" in json_data:
                for dep in json_data["dependencies"]:
                    if "include_paths" in dep:
                        config.setdefault("include_paths", []).extend(dep["include_paths"])
                    if "lib_paths" in dep:
                        config.setdefault("lib_paths", []).extend(dep["lib_paths"])
                    if "libs" in dep:
                        config.setdefault("libs", []).extend(dep["libs"])
                    if "defines" in dep:
                        config.setdefault("defines", []).extend(dep["defines"])
        except Exception as e:
            self.logger.warning(f"Failed to parse JSON build info: {e}")

        return config

    def generate_platformio_config(self, profile: BuildProfile, conan_config: Dict[str, Any]) -> str:
        """
        Generate PlatformIO configuration string.

        Args:
            profile: Build profile configuration
            conan_config: Resolved Conan configuration

        Returns:
            PlatformIO ini configuration as string
        """
        self.logger.info(f"Generating PlatformIO config for profile: {profile.name}")

        config_lines = [
            f"[env:{profile.name}]",
            f"platform = {profile.platform}",
            f"board = {profile.board}",
            f"framework = {profile.framework}",
            "",
            "; Conan-PlatformIO Bridge Configuration",
            f"; Generated for Conan profile: {profile.conan_profile}",
            "",
        ]

        # Add include paths
        if conan_config.get("include_paths"):
            includes = ";".join(conan_config["include_paths"])
            config_lines.append(f"build_flags = -I{includes}")

        # Add library paths
        if conan_config.get("lib_paths"):
            lib_paths = ";".join(conan_config["lib_paths"])
            config_lines.append(f"build_flags = -L{lib_paths}")

        # Add defines
        if conan_config.get("defines"):
            for define in conan_config["defines"]:
                config_lines.append(f"build_flags = -D{define}")

        # Add custom build flags from profile
        for flag in profile.build_flags:
            config_lines.append(f"build_flags = {flag}")

        # Add defines from profile
        for define in profile.defines:
            config_lines.append(f"build_flags = -D{define}")

        # Add library dependencies
        if conan_config.get("libs"):
            libs_str = " ".join(f"-l{lib}" for lib in conan_config["libs"])
            config_lines.append(f"build_flags = {libs_str}")

        return "\n".join(config_lines)

    def bridge(self, conan_profile: str, pio_env: str, packages: List[ConanPackage]) -> str:
        """
        Execute the Conan to PlatformIO bridge operation.

        Args:
            conan_profile: Conan profile to use
            pio_env: PlatformIO environment name
            packages: List of Conan packages to install

        Returns:
            Generated PlatformIO configuration
        """
        self.logger.info(f"Starting Conan-PlatformIO bridge for env: {pio_env}")

        try:
            # Resolve Conan dependencies
            conan_config = self.resolve_conan_dependencies(conan_profile, packages)

            # Create build profile
            profile = BuildProfile(
                name=pio_env,
                board=self._extract_board_from_env(pio_env),
                framework="espidf",
                platform="espressif32",
                conan_profile=conan_profile,
                packages=packages
            )

            # Generate PlatformIO configuration
            pio_config = self.generate_platformio_config(profile, conan_config)

            self.logger.info("Conan-PlatformIO bridge completed successfully")
            return pio_config

        except Exception as e:
            self.logger.error(f"Bridge operation failed: {e}")
            raise

    def _extract_board_from_env(self, pio_env: str) -> str:
        """Extract board name from PlatformIO environment name."""
        # Simple mapping - can be extended
        board_mappings = {
            "esp32dev": "esp32dev",
            "esp32s3": "esp32-s3-devkitc-1",
            "esp32c3": "esp32-c3-devkitm-1",
            "esp32c6": "esp32-c6-devkitc-1",
        }
        return board_mappings.get(pio_env, "esp32dev")

    def validate_environment(self) -> bool:
        """
        Validate that the environment has required tools installed.

        Returns:
            True if environment is valid, False otherwise
        """
        required_tools = ["conan", "platformio"]

        for tool in required_tools:
            try:
                result = subprocess.run([tool, "--version"],
                                      capture_output=True, text=True, check=True)
                self.logger.info(f"{tool} version: {result.stdout.strip()}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.logger.error(f"Required tool not found: {tool}")
                return False

        return True


def main():
    """Main entry point for the Conan-PlatformIO bridge script."""
    import argparse

    parser = argparse.ArgumentParser(description="Conan-PlatformIO Bridge")
    parser.add_argument("--conan-profile", required=True, help="Conan profile to use")
    parser.add_argument("--pio-env", required=True, help="PlatformIO environment name")
    parser.add_argument("--packages", nargs="+", help="Conan packages to install (name/version format)")
    parser.add_argument("--workspace-root", help="Workspace root directory")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    try:
        # Initialize bridge
        workspace_root = Path(args.workspace_root) if args.workspace_root else None
        bridge = ConanPIOBridge(workspace_root)

        # Validate environment
        if not bridge.validate_environment():
            sys.exit(1)

        # Parse packages
        packages = []
        if args.packages:
            for pkg_str in args.packages:
                # Parse name/version[@user/channel]
                parts = pkg_str.split("@")
                name_version = parts[0]
                user_channel = parts[1] if len(parts) > 1 else None

                pkg_parts = name_version.split("/")
                if len(pkg_parts) != 2:
                    raise ValueError(f"Invalid package format: {pkg_str}")

                name, version = pkg_parts
                user, channel = None, None
                if user_channel:
                    uc_parts = user_channel.split("/")
                    if len(uc_parts) == 2:
                        user, channel = uc_parts

                packages.append(ConanPackage(name=name, version=version, user=user, channel=channel))

        # Execute bridge
        config = bridge.bridge(args.conan_profile, args.pio_env, packages)

        # Output configuration
        print(config)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()