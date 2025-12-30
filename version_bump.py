#!/usr/bin/env python3
"""
SpareTools Version Bumping Script

Automatically bumps versions for SpareTools packages and updates all references.

Usage:
    python version_bump.py --package <package_name> --type <major|minor|patch>
    python version_bump.py --all --type <major|minor|patch>
    python version_bump.py --set <package_name> <version>

Examples:
    python version_bump.py --package sparetools-base --type minor
    python version_bump.py --all --type patch
    python version_bump.py --set sparetools-cpython 3.12.8
"""

import argparse
import os
import re
import yaml
from pathlib import Path
from typing import Dict, Optional


class VersionBumper:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.versions_file = self.root_dir / "versions.yaml"
        self.versions = self._load_versions()

    def _load_versions(self) -> Dict:
        """Load versions from the central versions.yaml file."""
        if not self.versions_file.exists():
            raise FileNotFoundError(f"Versions file not found: {self.versions_file}")

        with open(self.versions_file, 'r') as f:
            return yaml.safe_load(f)

    def _save_versions(self):
        """Save versions back to the versions.yaml file."""
        with open(self.versions_file, 'w') as f:
            yaml.dump(self.versions, f, default_flow_style=False, sort_keys=False)

        print(f"✅ Updated {self.versions_file}")

    def _bump_version(self, version: str, bump_type: str) -> str:
        """Bump a semantic version string."""
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)(.*)$', version)
        if not match:
            raise ValueError(f"Invalid version format: {version}")

        major, minor, patch, suffix = match.groups()
        major, minor, patch = int(major), int(minor), int(patch)

        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump_type == 'minor':
            minor += 1
            patch = 0
        elif bump_type == 'patch':
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

        return f"{major}.{minor}.{patch}{suffix}"

    def _find_package_path(self, package_name: str) -> Optional[Path]:
        """Find the path to a package's conanfile.py."""
        # Remove sparetools- prefix if present for directory matching
        short_name = package_name.replace('sparetools-', '')

        # Search in subdirectories
        for root, dirs, files in os.walk(self.root_dir / "packages"):
            if 'conanfile.py' in files:
                # Check if this directory matches the package name
                dir_name = Path(root).name
                if dir_name == package_name or dir_name == short_name:
                    return Path(root) / 'conanfile.py'

        return None

    def _update_conanfile_version(self, conanfile_path: Path, new_version: str):
        """Update version in a conanfile.py."""
        with open(conanfile_path, 'r') as f:
            content = f.read()

        # Pattern to match version = "x.y.z" lines
        pattern = r'(version\s*=\s*)"[^"]*"'
        replacement = rf'\1"{new_version}"'

        new_content = re.sub(pattern, replacement, content)

        if new_content != content:
            with open(conanfile_path, 'w') as f:
                f.write(new_content)
            print(f"✅ Updated {conanfile_path} to version {new_version}")
        else:
            print(f"⚠️  No version found to update in {conanfile_path}")

    def bump_package(self, package_name: str, bump_type: str):
        """Bump version for a specific package."""
        # Find the package in versions.yaml
        package_found = False
        for category, packages in self.versions.items():
            if isinstance(packages, dict):
                for pkg_name, version in packages.items():
                    full_pkg_name = f"sparetools-{pkg_name}" if not pkg_name.startswith('sparetools-') else pkg_name
                    if full_pkg_name == package_name or pkg_name == package_name:
                        # Bump the version
                        new_version = self._bump_version(version, bump_type)
                        self.versions[category][pkg_name] = new_version

                        # Update conanfile.py if it exists
                        conanfile_path = self._find_package_path(package_name)
                        if conanfile_path:
                            self._update_conanfile_version(conanfile_path, new_version)

                        package_found = True
                        print(f"✅ Bumped {package_name} from {version} to {new_version}")
                        break
            if package_found:
                break

        if not package_found:
            raise ValueError(f"Package '{package_name}' not found in versions.yaml")

        self._save_versions()

    def bump_all(self, bump_type: str):
        """Bump versions for all packages."""
        print(f"Bumping all packages with type: {bump_type}")
        for category, packages in self.versions.items():
            if isinstance(packages, dict):
                for pkg_name, version in packages.items():
                    try:
                        new_version = self._bump_version(version, bump_type)
                        self.versions[category][pkg_name] = new_version

                        # Update conanfile.py if it exists
                        full_pkg_name = f"sparetools-{pkg_name}" if not pkg_name.startswith('sparetools-') else pkg_name
                        conanfile_path = self._find_package_path(full_pkg_name)
                        if conanfile_path:
                            self._update_conanfile_version(conanfile_path, new_version)

                        print(f"✅ Bumped {pkg_name} from {version} to {new_version}")
                    except ValueError as e:
                        print(f"⚠️  Skipping {pkg_name}: {e}")

        self._save_versions()

    def set_version(self, package_name: str, new_version: str):
        """Set a specific version for a package."""
        package_found = False
        for category, packages in self.versions.items():
            if isinstance(packages, dict):
                for pkg_name, version in packages.items():
                    full_pkg_name = f"sparetools-{pkg_name}" if not pkg_name.startswith('sparetools-') else pkg_name
                    if full_pkg_name == package_name or pkg_name == package_name:
                        self.versions[category][pkg_name] = new_version

                        # Update conanfile.py if it exists
                        conanfile_path = self._find_package_path(package_name)
                        if conanfile_path:
                            self._update_conanfile_version(conanfile_path, new_version)

                        package_found = True
                        print(f"✅ Set {package_name} to version {new_version}")
                        break
            if package_found:
                break

        if not package_found:
            raise ValueError(f"Package '{package_name}' not found in versions.yaml")

        self._save_versions()


def main():
    parser = argparse.ArgumentParser(description="SpareTools Version Bumping Script")
    parser.add_argument('--package', help='Package name to bump')
    parser.add_argument('--all', action='store_true', help='Bump all packages')
    parser.add_argument('--type', choices=['major', 'minor', 'patch'], help='Type of version bump')
    parser.add_argument('--set', nargs=2, metavar=('PACKAGE', 'VERSION'), help='Set specific version')

    args = parser.parse_args()

    if not any([args.package, args.all, args.set]):
        parser.error("Must specify --package, --all, or --set")

    if args.set and (args.package or args.all or args.type):
        parser.error("--set cannot be combined with other options")

    if (args.package or args.all) and not args.type:
        parser.error("--type is required when using --package or --all")

    bumper = VersionBumper('.')

    try:
        if args.set:
            bumper.set_version(args.set[0], args.set[1])
        elif args.all:
            bumper.bump_all(args.type)
        else:
            bumper.bump_package(args.package, args.type)
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())

