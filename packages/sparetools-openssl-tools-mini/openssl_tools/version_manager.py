"""
Version Manager for OpenSSL packages
Provides dynamic version detection and fallback logic
"""

import os
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class VersionInfo:
    """Version information container"""
    version: str
    source: str  # 'git', 'file', 'fallback'
    confidence: float  # 0.0 to 1.0


class VersionManager:
    """
    Manages OpenSSL version detection and fallback logic

    Supports multiple version sources:
    - Git tags
    - VERSION.dat file
    - Manual specification
    - Fallback versions
    """

    def __init__(self, recipe_folder: Optional[str] = None):
        self.recipe_folder = Path(recipe_folder) if recipe_folder else Path.cwd()
        self.fallback_versions = ["4.0.0", "3.6.0", "3.4.1", "3.2.0"]

    def get_version(self) -> Optional[str]:
        """
        Get the best available OpenSSL version using fallback logic

        Returns:
            Version string or None if no version found
        """
        version_sources = [
            self._get_version_from_git,
            self._get_version_from_file,
            self._get_version_from_env,
        ]

        for source_func in version_sources:
            try:
                version_info = source_func()
                if version_info and version_info.version:
                    print(f"Version detected from {version_info.source}: {version_info.version}")
                    return version_info.version
            except Exception as e:
                print(f"Version detection failed for {source_func.__name__}: {e}")
                continue

        # Use fallback version
        fallback = self.fallback_versions[0]
        print(f"Using fallback version: {fallback}")
        return fallback

    def _get_version_from_git(self) -> Optional[VersionInfo]:
        """Get version from git tags"""
        try:
            import subprocess

            # Get latest tag
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                cwd=self.recipe_folder,
                capture_output=True,
                text=True,
                check=True
            )

            version = result.stdout.strip()
            if version:
                # Clean up version (remove 'v' prefix if present)
                version = version.lstrip('v')
                return VersionInfo(version=version, source="git", confidence=1.0)

        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        return None

    def _get_version_from_file(self) -> Optional[VersionInfo]:
        """Get version from VERSION.dat file"""
        version_file = self.recipe_folder / "VERSION.dat"
        if not version_file.exists():
            return None

        try:
            with open(version_file, 'r') as f:
                content = f.read().strip()

            # Parse VERSION.dat format (MAJOR.MINOR.PATCH)
            # Example: 3.4.1 or 4.0.0-dev
            version_match = re.search(r'(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?)', content)
            if version_match:
                version = version_match.group(1)
                return VersionInfo(version=version, source="file", confidence=0.9)

        except Exception:
            pass

        return None

    def _get_version_from_env(self) -> Optional[VersionInfo]:
        """Get version from environment variable"""
        version = os.getenv("OPENSSL_VERSION")
        if version:
            return VersionInfo(version=version, source="env", confidence=0.8)

        return None

    def get_available_versions(self) -> List[str]:
        """Get list of available OpenSSL versions"""
        return self.fallback_versions.copy()

    def validate_version(self, version: str) -> bool:
        """Validate version string format"""
        # Semantic version pattern
        semver_pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$'
        return bool(re.match(semver_pattern, version))

    def get_version_info(self, version: str) -> Dict[str, Any]:
        """Get detailed information about a version"""
        return {
            "version": version,
            "is_stable": "-" not in version,
            "is_dev": "-dev" in version or "-alpha" in version or "-beta" in version,
            "major": int(version.split(".")[0]) if "." in version else 0,
            "minor": int(version.split(".")[1]) if len(version.split(".")) > 1 else 0,
            "patch": int(version.split(".")[2].split("-")[0]) if len(version.split(".")) > 2 else 0,
        }