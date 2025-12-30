"""Conan profile management for embedded systems.

This module provides utilities for managing Conan profiles
for cross-compilation and embedded development.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from sparetools.mcp_core.core.exceptions import DeploymentError, ErrorCode


@dataclass
class ProfileConfig:
    """Configuration for a Conan profile."""

    name: str
    platform: str
    arch: str = "xtensa"
    compiler: str = "gcc"
    compiler_version: str = "11"
    build_type: str = "Release"
    os_name: str = "baremetal"
    settings: Dict[str, str] = field(default_factory=dict)
    options: Dict[str, str] = field(default_factory=dict)
    env: Dict[str, str] = field(default_factory=dict)
    tool_requires: List[str] = field(default_factory=list)

    def to_profile_content(self) -> str:
        """Generate Conan profile content.

        Returns:
            Conan profile file content
        """
        lines = []

        # Settings section
        lines.append("[settings]")
        lines.append(f"os={self.os_name}")
        lines.append(f"arch={self.arch}")
        lines.append(f"compiler={self.compiler}")
        lines.append(f"compiler.version={self.compiler_version}")
        lines.append(f"build_type={self.build_type}")

        for key, value in self.settings.items():
            lines.append(f"{key}={value}")

        # Options section
        if self.options:
            lines.append("")
            lines.append("[options]")
            for key, value in self.options.items():
                lines.append(f"{key}={value}")

        # Environment section
        if self.env:
            lines.append("")
            lines.append("[buildenv]")
            for key, value in self.env.items():
                lines.append(f"{key}={value}")

        # Tool requires section
        if self.tool_requires:
            lines.append("")
            lines.append("[tool_requires]")
            for tool in self.tool_requires:
                lines.append(tool)

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format.

        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "platform": self.platform,
            "arch": self.arch,
            "compiler": self.compiler,
            "compiler_version": self.compiler_version,
            "build_type": self.build_type,
            "os_name": self.os_name,
            "settings": self.settings,
            "options": self.options,
            "env": self.env,
            "tool_requires": self.tool_requires,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProfileConfig":
        """Create from dictionary.

        Args:
            data: Dictionary containing profile configuration

        Returns:
            ProfileConfig instance
        """
        return cls(**data)


# Pre-defined profile configurations
ESP32S3_PROFILE = ProfileConfig(
    name="esp32s3",
    platform="esp32-s3",
    arch="xtensa",
    compiler="gcc",
    compiler_version="11",
    build_type="Release",
    os_name="baremetal",
    settings={
        "compiler.cppstd": "20",
        "compiler.libcxx": "libstdc++11",
    },
    options={
        "*:fPIC": "True",
    },
    env={
        "IDF_PATH": "${IDF_PATH}",
        "IDF_TARGET": "esp32s3",
    },
    tool_requires=[
        "sparetools-cpython/3.12.7",
    ],
)

ESP32_PROFILE = ProfileConfig(
    name="esp32",
    platform="esp32",
    arch="xtensa",
    compiler="gcc",
    compiler_version="11",
    build_type="Release",
    os_name="baremetal",
    settings={
        "compiler.cppstd": "20",
        "compiler.libcxx": "libstdc++11",
    },
    env={
        "IDF_PATH": "${IDF_PATH}",
        "IDF_TARGET": "esp32",
    },
)

ARDUINO_UNO_PROFILE = ProfileConfig(
    name="arduino_uno",
    platform="arduino-uno",
    arch="avr",
    compiler="avr-gcc",
    compiler_version="7",
    build_type="Release",
    os_name="baremetal",
    settings={
        "compiler.cppstd": "11",
    },
)


class ConanProfileManager:
    """Manager for Conan profiles."""

    def __init__(self, profiles_dir: Optional[Union[str, Path]] = None) -> None:
        """Initialize the profile manager.

        Args:
            profiles_dir: Directory containing profiles
        """
        self.profiles_dir = Path(profiles_dir) if profiles_dir else Path("conan-profiles")
        self._profiles: Dict[str, ProfileConfig] = {}
        self._load_predefined()

    def _load_predefined(self) -> None:
        """Load pre-defined profile configurations."""
        self._profiles["esp32s3"] = ESP32S3_PROFILE
        self._profiles["esp32"] = ESP32_PROFILE
        self._profiles["arduino_uno"] = ARDUINO_UNO_PROFILE

    def list_profiles(self, profiles_dir: Optional[str] = None) -> str:
        """List available Conan profiles.

        Args:
            profiles_dir: Optional directory to list profiles from

        Returns:
            JSON string with profile list
        """
        result = {
            "predefined": list(self._profiles.keys()),
            "files": [],
        }

        directory = Path(profiles_dir) if profiles_dir else self.profiles_dir
        if directory.exists():
            result["files"] = [
                p.stem for p in directory.glob("*.profile")
            ] + [
                p.stem for p in directory.glob("*") if p.is_file() and not p.suffix
            ]

        return json.dumps(result, indent=2)

    def get_profile(self, name: str) -> Optional[ProfileConfig]:
        """Get a profile configuration by name.

        Args:
            name: Profile name

        Returns:
            Profile configuration or None
        """
        return self._profiles.get(name)

    def generate(
        self,
        platform: str,
        output_path: Optional[str] = None,
    ) -> str:
        """Generate Conan profile for target platform.

        Args:
            platform: Target platform name
            output_path: Optional path to save the profile

        Returns:
            Generated profile content
        """
        profile = self._profiles.get(platform)

        if profile is None:
            # Try to create a basic profile
            profile = ProfileConfig(
                name=platform,
                platform=platform,
                arch="x86_64",
                compiler="gcc",
                compiler_version="11",
            )

        content = profile.to_profile_content()

        if output_path:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)

        return content

    def save_profile(self, config: ProfileConfig, directory: Optional[Path] = None) -> Path:
        """Save a profile configuration to disk.

        Args:
            config: Profile configuration to save
            directory: Directory to save to

        Returns:
            Path to saved profile
        """
        directory = directory or self.profiles_dir
        directory.mkdir(parents=True, exist_ok=True)

        profile_path = directory / f"{config.name}.profile"
        profile_path.write_text(config.to_profile_content())

        # Also save JSON metadata
        json_path = directory / f"{config.name}.json"
        with open(json_path, "w") as f:
            json.dump(config.to_dict(), f, indent=2)

        return profile_path

    def load_profile(self, path: Union[str, Path]) -> ProfileConfig:
        """Load a profile from disk.

        Args:
            path: Path to profile file

        Returns:
            Profile configuration

        Raises:
            DeploymentError: If loading fails
        """
        path = Path(path)

        if not path.exists():
            raise DeploymentError(
                f"Profile not found: {path}",
                profile=str(path),
                code=ErrorCode.PROFILE_NOT_FOUND,
            )

        # Try JSON first
        json_path = path.with_suffix(".json")
        if json_path.exists():
            with open(json_path) as f:
                data = json.load(f)
            return ProfileConfig.from_dict(data)

        # Parse profile file format
        # This is a simplified parser
        raise DeploymentError(
            f"Cannot parse profile file: {path}",
            profile=str(path),
            code=ErrorCode.PROFILE_INVALID,
        )

    def register_profile(self, config: ProfileConfig) -> None:
        """Register a new profile configuration.

        Args:
            config: Profile configuration to register
        """
        self._profiles[config.name] = config

    def create_profile_for_device(
        self,
        device_type: str,
        variant: str = "",
        build_type: str = "Release",
    ) -> ProfileConfig:
        """Create a profile configuration for a device.

        Args:
            device_type: Device type (e.g., "esp32", "arduino")
            variant: Device variant (e.g., "s3", "uno")
            build_type: Build type

        Returns:
            Generated profile configuration
        """
        # Check for existing profile
        key = f"{device_type}_{variant}" if variant else device_type
        if key in self._profiles:
            return self._profiles[key]

        # Create based on device type
        if device_type == "esp32":
            arch = "xtensa"
            if variant in ("c3", "c6"):
                arch = "riscv32"
            return ProfileConfig(
                name=key,
                platform=f"esp32-{variant}" if variant else "esp32",
                arch=arch,
                compiler="gcc",
                compiler_version="11",
                build_type=build_type,
                os_name="baremetal",
                env={"IDF_TARGET": variant if variant else "esp32"},
            )
        elif device_type == "arduino":
            return ProfileConfig(
                name=key,
                platform=f"arduino-{variant}" if variant else "arduino",
                arch="avr",
                compiler="avr-gcc",
                compiler_version="7",
                build_type=build_type,
                os_name="baremetal",
            )
        else:
            # Generic profile
            return ProfileConfig(
                name=key,
                platform=device_type,
                arch="x86_64",
                compiler="gcc",
                compiler_version="11",
                build_type=build_type,
            )
