#!/usr/bin/env python3
"""
Version bumping and validation script for SpareTools

Handles synchronized version updates across:
- VERSION.txt (main version)
- Conan recipe version fields
- Git tags for releases

Usage:
    python bump-version.py patch  # 1.0.0 -> 1.0.1
    python bump-version.py minor  # 1.0.0 -> 1.1.0
    python bump-version.py major  # 1.0.0 -> 2.0.0
    python bump-version.py validate  # Check version consistency
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import subprocess


class VersionManager:
    """Manages version synchronization across SpareTools files."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        # Only manage versions for packages that should be synchronized with main VERSION.txt
        # Foundation packages that are part of the core release
        self.version_files = {
            "VERSION.txt": self._update_version_txt,
            "packages/foundation/sparetools-base/conanfile.py": self._update_conanfile_version,
            "packages/foundation/sparetools-shared-dev-tools/conanfile.py": self._update_conanfile_version,
            "packages/foundation/sparetools-bootstrap/conanfile.py": self._update_conanfile_version,
            "packages/foundation/sparetools-recipe-base/conanfile.py": self._update_conanfile_version,
            "packages/foundation/sparetools-test-harness/conanfile.py": self._update_conanfile_version,
            # Consumer packages that follow main versioning
            "packages/consumers/sparetools-obd-sim/conanfile.py": self._update_conanfile_version,
            "packages/consumers/mcp/sparetools-mcp-orchestrator/conanfile.py": self._update_conanfile_version,
        }

        # Packages with independent versioning (don't validate against main VERSION.txt)
        self.independent_versions = {
            "packages/foundation/sparetools-cpython/conanfile.py": "3.12.7",  # Python version
            "packages/consumers/mia/sparetools-mia/conanfile.py": None,  # Independent
            "packages/consumers/android/sparetools-cliphist-android/conanfile.py": None,
            "packages/consumers/mcp/sparetools-mcpserver-cpp/conanfile.py": None,
            "packages/consumers/mcp/sparetools-tinymcp/conanfile.py": None,
            "packages/consumers/esp32/sparetools-nucleus/conanfile.py": None,
            "packages/python/sparetools-fs-tools/conanfile.py": None,
            "packages/python/sparetools-proc-tools/conanfile.py": None,
        }

    def get_current_version(self) -> str:
        """Get the current version from VERSION.txt."""
        version_file = self.repo_root / "VERSION.txt"
        if not version_file.exists():
            raise FileNotFoundError(f"VERSION.txt not found at {version_file}")

        with open(version_file, 'r') as f:
            version = f.read().strip().split('\n')[0].strip()

        if not self._is_valid_version(version):
            raise ValueError(f"Invalid version format in VERSION.txt: {version}")

        return version

    def bump_version(self, bump_type: str) -> str:
        """Bump the version according to the specified type."""
        current = self.get_current_version()
        major, minor, patch = map(int, current.split('.'))

        if bump_type == "patch":
            new_version = f"{major}.{minor}.{patch + 1}"
        elif bump_type == "minor":
            new_version = f"{major}.{minor + 1}.0"
        elif bump_type == "major":
            new_version = f"{major + 1}.0.0"
        else:
            raise ValueError(f"Invalid bump type: {bump_type}. Must be patch, minor, or major.")

        return new_version

    def validate_versions(self) -> List[str]:
        """Validate that all version files are consistent."""
        issues = []
        expected_version = self.get_current_version()

        # Validate synchronized version files
        for file_path, _ in self.version_files.items():
            full_path = self.repo_root / file_path
            if not full_path.exists():
                issues.append(f"Version file missing: {file_path}")
                continue

            try:
                file_version = self._extract_version_from_file(full_path)
                if file_version != expected_version:
                    issues.append(f"Version mismatch in {file_path}: expected {expected_version}, got {file_version}")
            except Exception as e:
                issues.append(f"Error reading version from {file_path}: {e}")

        # Validate independent version files (just check they exist and have valid versions)
        for file_path, expected_ver in self.independent_versions.items():
            full_path = self.repo_root / file_path
            if not full_path.exists():
                issues.append(f"Version file missing: {file_path}")
                continue

            try:
                file_version = self._extract_version_from_file(full_path)
                if expected_ver and file_version != expected_ver:
                    issues.append(f"Version mismatch in {file_path}: expected {expected_ver}, got {file_version}")
                elif not self._is_valid_version(file_version):
                    issues.append(f"Invalid version format in {file_path}: {file_version}")
            except Exception as e:
                issues.append(f"Error reading version from {file_path}: {e}")

        return issues

    def update_all_versions(self, new_version: str, dry_run: bool = False) -> List[str]:
        """Update all version files to the new version."""
        updates = []

        for file_path, update_func in self.version_files.items():
            full_path = self.repo_root / file_path
            if not full_path.exists():
                print(f"Warning: {file_path} not found, skipping")
                continue

            try:
                old_version = self._extract_version_from_file(full_path)
                if old_version == new_version:
                    continue  # Already at correct version

                if not dry_run:
                    update_func(full_path, new_version)

                updates.append(f"{file_path}: {old_version} -> {new_version}")

            except Exception as e:
                print(f"Error updating {file_path}: {e}")
                continue

        return updates

    def create_git_tag(self, version: str, message: Optional[str] = None) -> bool:
        """Create a git tag for the version."""
        tag_name = f"v{version}"
        tag_message = message or f"Release version {version}"

        try:
            # Check if tag already exists
            result = subprocess.run(
                ["git", "tag", "-l", tag_name],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )

            if result.stdout.strip():
                print(f"Tag {tag_name} already exists")
                return False

            # Create annotated tag
            result = subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", tag_message],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )

            if result.returncode == 0:
                print(f"Created tag {tag_name}")
                return True
            else:
                print(f"Failed to create tag: {result.stderr}")
                return False

        except Exception as e:
            print(f"Error creating git tag: {e}")
            return False

    def _is_valid_version(self, version: str) -> bool:
        """Check if version string is valid semver."""
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))

    def _extract_version_from_file(self, file_path: Path) -> str:
        """Extract version from a conanfile.py or VERSION.txt."""
        with open(file_path, 'r') as f:
            content = f.read()

        # Look for version = "X.Y.Z" pattern
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        if match:
            return match.group(1)

        # For VERSION.txt, just return the first line
        if file_path.name == "VERSION.txt":
            return content.strip().split('\n')[0].strip()

        raise ValueError(f"Could not find version in {file_path}")

    def _update_version_txt(self, file_path: Path, new_version: str):
        """Update VERSION.txt."""
        with open(file_path, 'w') as f:
            f.write(f"{new_version}\n")

    def _update_conanfile_version(self, file_path: Path, new_version: str):
        """Update version in a conanfile.py."""
        with open(file_path, 'r') as f:
            content = f.read()

        # Replace version = "X.Y.Z" pattern
        pattern = r'(version\s*=\s*)"[^"]*"'
        replacement = f'\\1"{new_version}"'

        new_content = re.sub(pattern, replacement, content)

        with open(file_path, 'w') as f:
            f.write(new_content)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Version bumping and validation for SpareTools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Bump patch version
  python bump-version.py patch

  # Bump minor version
  python bump-version.py minor

  # Validate current versions
  python bump-version.py validate

  # Dry run version bump
  python bump-version.py patch --dry-run
        """
    )

    parser.add_argument(
        "action",
        choices=["patch", "minor", "major", "validate"],
        help="Action to perform"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes"
    )

    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory"
    )

    parser.add_argument(
        "--create-tag",
        action="store_true",
        help="Create git tag after version bump"
    )

    args = parser.parse_args()

    # Initialize version manager
    try:
        vm = VersionManager(args.repo_root)
    except Exception as e:
        print(f"Error initializing version manager: {e}", file=sys.stderr)
        sys.exit(1)

    if args.action == "validate":
        # Validate versions
        print("🔍 Validating version consistency...")
        issues = vm.validate_versions()

        if issues:
            print("❌ Version validation failed:")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)
        else:
            current_version = vm.get_current_version()
            print(f"✅ All versions are consistent: {current_version}")

    else:
        # Bump version
        try:
            current_version = vm.get_current_version()
            new_version = vm.bump_version(args.action)

            print(f"📈 Bumping version: {current_version} -> {new_version}")

            if args.dry_run:
                print("🔍 Dry run - would update:")
                updates = vm.update_all_versions(new_version, dry_run=True)
                for update in updates:
                    print(f"  - {update}")
                print(f"  - Would create git tag: v{new_version}")
            else:
                # Perform actual updates
                updates = vm.update_all_versions(new_version, dry_run=False)
                print("✅ Updated files:")
                for update in updates:
                    print(f"  - {update}")

                # Create git tag if requested
                if args.create_tag:
                    if vm.create_git_tag(new_version):
                        print(f"🏷️  Created git tag: v{new_version}")
                    else:
                        print("⚠️  Failed to create git tag")
                        sys.exit(1)

                print(f"🎉 Version bump complete: {new_version}")

        except Exception as e:
            print(f"Error during version bump: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()

