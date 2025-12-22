#!/usr/bin/env python3
"""
Version Consistency Validator for SpareTools Ecosystem

This script validates that all projects in the MIA ecosystem maintain
consistent versioning according to the VERSIONING.md strategy.
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple


class VersionValidator:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def read_version_file(self, path: Path) -> str:
        """Read version from a VERSION.txt file."""
        if not path.exists():
            return None
        with open(path, 'r') as f:
            # Read first line and strip comments
            line = f.readline().strip()
            if '#' in line:
                line = line.split('#')[0].strip()
            return line

    def extract_version_from_conanfile(self, path: Path) -> str:
        """Extract version from conanfile.py."""
        if not path.exists():
            return None
        with open(path, 'r') as f:
            content = f.read()
            # Look for version = "X.Y.Z" pattern
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            return match.group(1) if match else None

    def extract_version_from_pyproject(self, path: Path) -> str:
        """Extract version from pyproject.toml."""
        if not path.exists():
            return None
        with open(path, 'r') as f:
            content = f.read()
            # Look for version = "X.Y.Z" pattern
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            return match.group(1) if match else None

    def validate_ecosystem_version(self) -> str:
        """Validate and return the ecosystem version."""
        version_file = self.workspace_root / "sparetools" / "VERSION.txt"
        ecosystem_version = self.read_version_file(version_file)

        if not ecosystem_version:
            self.errors.append("Missing sparetools/VERSION.txt")
            return None

        # Validate semantic version format
        if not re.match(r'^\d+\.\d+\.\d+$', ecosystem_version):
            self.errors.append(f"Invalid ecosystem version format: {ecosystem_version}")
            return None

        return ecosystem_version

    def validate_project_versions(self, ecosystem_version: str) -> None:
        """Validate all project versions align with ecosystem version."""
        projects = [
            ("mia", "mia/VERSION.txt"),
            ("mia-project", "mia-project/pyproject.toml"),
        ]

        for project_name, version_path in projects:
            full_path = self.workspace_root / version_path

            if version_path.endswith("VERSION.txt"):
                version = self.read_version_file(full_path)
            elif version_path.endswith("pyproject.toml"):
                version = self.extract_version_from_pyproject(full_path)
            else:
                version = None

            if not version:
                self.errors.append(f"Missing version in {version_path}")
                continue

            # Projects should have same major.minor as ecosystem
            ecosystem_major_minor = '.'.join(ecosystem_version.split('.')[:2])
            project_major_minor = '.'.join(version.split('.')[:2])

            if ecosystem_major_minor != project_major_minor:
                self.errors.append(
                    f"{project_name} version {version} doesn't align with "
                    f"ecosystem version {ecosystem_version} (expected {ecosystem_major_minor}.X)"
                )

    def validate_conan_packages(self) -> None:
        """Validate Conan package versions."""
        conanfiles = list(self.workspace_root.glob("**/conanfile.py"))

        for conanfile in conanfiles:
            version = self.extract_version_from_conanfile(conanfile)
            if not version:
                continue

            # Special cases for version-specific packages
            if "cpython" in str(conanfile):
                # Python version should be 3.12.X
                if not version.startswith("3.12."):
                    self.warnings.append(f"cpython version {version} should be 3.12.X")
            elif "openssl" in str(conanfile):
                # OpenSSL version should be 3.3.X
                if not version.startswith("3.3."):
                    self.warnings.append(f"openssl version {version} should be 3.3.X")
            else:
                # Other packages should be semantic versions
                if not re.match(r'^\d+\.\d+\.\d+$', version):
                    self.warnings.append(f"Invalid semantic version in {conanfile}: {version}")

    def validate_package_json_versions(self) -> None:
        """Validate package.json version consistency."""
        import json

        package_jsons = list(self.workspace_root.glob("**/package.json"))

        for pj_path in package_jsons:
            try:
                with open(pj_path, 'r') as f:
                    data = json.load(f)

                version = data.get('version')
                if version and not re.match(r'^\d+\.\d+\.\d+$', version):
                    self.warnings.append(f"Invalid version in {pj_path}: {version}")
            except json.JSONDecodeError:
                self.errors.append(f"Invalid JSON in {pj_path}")

    def run_validation(self) -> bool:
        """Run all validation checks."""
        print("🔍 Validating SpareTools Ecosystem Version Consistency...")

        # Validate ecosystem version
        ecosystem_version = self.validate_ecosystem_version()
        if not ecosystem_version:
            return False

        print(f"📋 Ecosystem version: {ecosystem_version}")

        # Validate project versions
        self.validate_project_versions(ecosystem_version)

        # Validate Conan packages
        self.validate_conan_packages()

        # Validate package.json files
        self.validate_package_json_versions()

        # Report results
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All version checks passed!")
            return True
        elif not self.errors:
            print(f"\n✅ No errors found ({len(self.warnings)} warnings)")
            return True
        else:
            print(f"\n❌ {len(self.errors)} errors found ({len(self.warnings)} warnings)")
            return False


def main():
    workspace_root = Path(__file__).parent.parent.parent
    validator = VersionValidator(workspace_root)
    success = validator.run_validation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()