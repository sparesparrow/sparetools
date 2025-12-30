#!/usr/bin/env python3
"""
Version Increment Validation Script

This script validates that Conan package versions have been properly incremented
according to semantic versioning rules and prevents version conflicts.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple, List


class VersionValidator:
    """Validates Conan package version increments."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.version_pattern = re.compile(r'version\s*=\s*["\']([^"\']+)["\']')

    def extract_version_from_conanfile(self, conanfile_path: Path) -> Optional[str]:
        """Extract version from conanfile.py."""
        try:
            with open(conanfile_path, 'r', encoding='utf-8') as f:
                content = f.read()

            match = self.version_pattern.search(content)
            return match.group(1) if match else None
        except Exception as e:
            print(f"Error reading {conanfile_path}: {e}")
            return None

    def get_current_branch(self) -> str:
        """Get current git branch name."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True, text=True, check=True, cwd=self.repo_root
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return 'unknown'

    def get_commit_messages_since_last_version_change(self, conanfile_path: Path) -> List[str]:
        """Get commit messages since the last version change."""
        try:
            # Find the last commit that changed the version
            result = subprocess.run(
                ['git', 'log', '--oneline', '--follow', '-p', '--', str(conanfile_path)],
                capture_output=True, text=True, cwd=self.repo_root
            )

            if result.returncode != 0:
                return []

            lines = result.stdout.split('\n')
            commits = []

            for line in lines:
                if line.startswith('commit ') and len(line.split()) >= 2:
                    commit_hash = line.split()[1]
                    # Get the commit message
                    msg_result = subprocess.run(
                        ['git', 'log', '--format=%B', '-n', '1', commit_hash],
                        capture_output=True, text=True, cwd=self.repo_root
                    )
                    if msg_result.returncode == 0:
                        commits.append(msg_result.stdout.strip())

            return commits
        except Exception:
            return []

    def parse_version(self, version: str) -> Tuple[int, int, int, Optional[str]]:
        """Parse semantic version into components."""
        # Handle versions like 1.0.0, 1.0.0-dev, 2.0.3-alpha.1
        parts = version.split('-')
        main_version = parts[0]
        pre_release = parts[1] if len(parts) > 1 else None

        try:
            major, minor, patch = map(int, main_version.split('.'))
            return major, minor, patch, pre_release
        except ValueError:
            raise ValueError(f"Invalid version format: {version}")

    def compare_versions(self, old_version: str, new_version: str) -> int:
        """Compare two versions semantically. Returns -1, 0, or 1."""
        try:
            old_major, old_minor, old_patch, old_pre = self.parse_version(old_version)
            new_major, new_minor, new_patch, new_pre = self.parse_version(new_version)

            # Compare major, minor, patch
            for old, new in [(old_major, new_major), (old_minor, new_minor), (old_patch, new_patch)]:
                if old != new:
                    return -1 if old > new else 1

            # If versions are equal, check pre-release
            if old_pre != new_pre:
                # Any pre-release is less than no pre-release
                if old_pre and not new_pre:
                    return -1
                elif not old_pre and new_pre:
                    return 1
                else:
                    # Both have pre-release, compare lexicographically
                    return -1 if old_pre < new_pre else 1

            return 0  # Versions are equal
        except ValueError as e:
            raise ValueError(f"Error comparing versions: {e}")

    def should_increment_version(self, conanfile_path: Path, current_version: str) -> Tuple[bool, str]:
        """
        Determine if version should be incremented based on:
        - Branch type
        - Commit messages since last version change
        - Current version state
        """
        branch = self.get_current_branch()

        # Always require version increment on feature branches
        if branch not in ['main', 'master', 'develop']:
            commits = self.get_commit_messages_since_last_version_change(conanfile_path)

            # Check for version bump commits
            version_bump_found = any(
                'bump' in msg.lower() or
                'version' in msg.lower() or
                'release' in msg.lower()
                for msg in commits
            )

            if not version_bump_found:
                return True, f"Feature branch '{branch}' requires version increment for changes"

        # Check if we're on a release branch or tag
        if branch.startswith(('release/', 'hotfix/')):
            return True, f"Release branch '{branch}' should increment version"

        return False, "Version increment not required for this branch"

    def validate_version_increment(self, conanfile_path: Path) -> Tuple[bool, str]:
        """
        Validate that version has been properly incremented if required.
        Returns (is_valid, message)
        """
        try:
            current_version = self.extract_version_from_conanfile(conanfile_path)
            if not current_version:
                return False, f"Could not extract version from {conanfile_path}"

            # Get the version from the last commit
            try:
                result = subprocess.run(
                    ['git', 'show', 'HEAD~1:{conanfile_path}', '--', str(conanfile_path)],
                    capture_output=True, text=True, cwd=self.repo_root
                )

                if result.returncode == 0:
                    old_content = result.stdout
                    old_match = self.version_pattern.search(old_content)
                    old_version = old_match.group(1) if old_match else None

                    if old_version:
                        comparison = self.compare_versions(old_version, current_version)
                        if comparison == 0:
                            # Versions are the same - check if increment is required
                            should_increment, reason = self.should_increment_version(conanfile_path, current_version)
                            if should_increment:
                                return False, f"Version not incremented: {reason}"
                        elif comparison < 0:
                            # Version decreased - not allowed
                            return False, f"Version decreased from {old_version} to {current_version}"
                        # comparison > 0 means version increased - this is good

            except subprocess.CalledProcessError:
                # Probably the first commit or file didn't exist
                pass

            return True, f"Version validation passed: {current_version}"

        except Exception as e:
            return False, f"Version validation error: {e}"

    def validate_all_conanfiles(self) -> Tuple[bool, List[str]]:
        """Validate version increments for all conanfile.py files."""
        conanfiles = list(self.repo_root.rglob('conanfile.py'))
        results = []
        all_valid = True

        for conanfile in conanfiles:
            is_valid, message = self.validate_version_increment(conanfile)
            results.append(f"{'✅' if is_valid else '❌'} {conanfile.relative_to(self.repo_root)}: {message}")

            if not is_valid:
                all_valid = False

        return all_valid, results


def main():
    parser = argparse.ArgumentParser(description='Validate Conan package version increments')
    parser.add_argument('--conanfile', help='Specific conanfile.py to validate')
    parser.add_argument('--all', action='store_true', help='Validate all conanfile.py files')
    parser.add_argument('--strict', action='store_true', help='Strict mode: always require version increment')

    args = parser.parse_args()

    repo_root = Path.cwd()
    validator = VersionValidator(repo_root)

    if args.conanfile:
        conanfile_path = Path(args.conanfile)
        if not conanfile_path.exists():
            print(f"❌ Conanfile not found: {conanfile_path}")
            sys.exit(1)

        is_valid, message = validator.validate_version_increment(conanfile_path)
        print(f"{'✅' if is_valid else '❌'} {message}")

        if not is_valid:
            sys.exit(1)

    elif args.all:
        all_valid, results = validator.validate_all_conanfiles()

        for result in results:
            print(result)

        if not all_valid:
            print("\n❌ Version validation failed!")
            sys.exit(1)
        else:
            print("\n✅ All version validations passed!")

    else:
        # Default: validate all
        all_valid, results = validator.validate_all_conanfiles()

        for result in results:
            print(result)

        if not all_valid:
            print("\n❌ Version validation failed!")
            sys.exit(1)
        else:
            print("\n✅ All version validations passed!")


if __name__ == '__main__':
    main()