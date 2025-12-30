#!/usr/bin/env python3
"""
Automatic Version Bumping Script for SpareTools

This script automatically increments Conan package versions according to
semantic versioning rules based on commit messages or manual specification.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple, List


class VersionBumper:
    """Handles automatic version bumping for Conan packages."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.version_pattern = re.compile(r'(version\s*=\s*["\'])([^"\']+)(["\'])')

    def parse_version(self, version: str) -> Tuple[int, int, int, Optional[str]]:
        """Parse semantic version into components."""
        parts = version.split('-')
        main_version = parts[0]
        pre_release = parts[1] if len(parts) > 1 else None

        try:
            major, minor, patch = map(int, main_version.split('.'))
            return major, minor, patch, pre_release
        except ValueError:
            raise ValueError(f"Invalid version format: {version}")

    def format_version(self, major: int, minor: int, patch: int, pre_release: Optional[str] = None) -> str:
        """Format version components back into string."""
        version = f"{major}.{minor}.{patch}"
        if pre_release:
            version += f"-{pre_release}"
        return version

    def bump_patch(self, version: str) -> str:
        """Increment patch version."""
        major, minor, patch, pre = self.parse_version(version)
        return self.format_version(major, minor, patch + 1, pre)

    def bump_minor(self, version: str) -> str:
        """Increment minor version."""
        major, minor, patch, pre = self.parse_version(version)
        return self.format_version(major, minor + 1, 0, pre)

    def bump_major(self, version: str) -> str:
        """Increment major version."""
        major, minor, patch, pre = self.parse_version(version)
        return self.format_version(major + 1, 0, 0, pre)

    def get_commit_messages_since_last_tag(self) -> List[str]:
        """Get commit messages since last version tag."""
        try:
            # Get the last tag
            result = subprocess.run(
                ['git', 'describe', '--tags', '--abbrev=0'],
                capture_output=True, text=True, cwd=self.repo_root
            )

            if result.returncode == 0:
                last_tag = result.stdout.strip()
                # Get commits since last tag
                result = subprocess.run(
                    ['git', 'log', '--oneline', f'{last_tag}..HEAD'],
                    capture_output=True, text=True, cwd=self.repo_root
                )
                if result.returncode == 0:
                    return result.stdout.strip().split('\n')
            else:
                # No tags yet, get all commits
                result = subprocess.run(
                    ['git', 'log', '--oneline'],
                    capture_output=True, text=True, cwd=self.repo_root
                )
                if result.returncode == 0:
                    return result.stdout.strip().split('\n')

        except subprocess.CalledProcessError:
            pass

        return []

    def determine_bump_type_from_commits(self, commits: List[str]) -> str:
        """Determine version bump type from commit messages."""
        has_breaking = False
        has_feature = False

        for commit in commits:
            commit_lower = commit.lower()

            # Breaking changes
            if any(keyword in commit_lower for keyword in ['breaking', 'break', 'major', 'incompatible']):
                has_breaking = True

            # New features
            if any(keyword in commit_lower for keyword in ['feat', 'feature', 'add', 'new']):
                has_feature = True

        if has_breaking:
            return 'major'
        elif has_feature:
            return 'minor'
        else:
            return 'patch'

    def bump_version_in_file(self, file_path: Path, new_version: str) -> bool:
        """Update version in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace version
            new_content = self.version_pattern.sub(f'\\g<1>{new_version}\\g<3>', content)

            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True

        except Exception as e:
            print(f"Error updating {file_path}: {e}")

        return False

    def get_current_version_from_file(self, file_path: Path) -> Optional[str]:
        """Get current version from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            match = self.version_pattern.search(content)
            return match.group(2) if match else None
        except Exception:
            return None

    def bump_conanfile_versions(self, bump_type: str, conanfile_path: Optional[Path] = None) -> List[Tuple[Path, str, str]]:
        """Bump versions in conanfile.py files."""
        updated_files = []

        if conanfile_path:
            conanfiles = [conanfile_path]
        else:
            conanfiles = list(self.repo_root.rglob('conanfile.py'))

        for conanfile in conanfiles:
            current_version = self.get_current_version_from_file(conanfile)
            if not current_version:
                print(f"⚠️  Could not read version from {conanfile}")
                continue

            # Bump version
            if bump_type == 'major':
                new_version = self.bump_major(current_version)
            elif bump_type == 'minor':
                new_version = self.bump_minor(current_version)
            elif bump_type == 'patch':
                new_version = self.bump_patch(current_version)
            else:
                print(f"❌ Unknown bump type: {bump_type}")
                continue

            # Update file
            if self.bump_version_in_file(conanfile, new_version):
                updated_files.append((conanfile, current_version, new_version))
                print(f"📦 {conanfile.relative_to(self.repo_root)}: {current_version} → {new_version}")
            else:
                print(f"⚠️  Failed to update {conanfile}")

        return updated_files

    def update_version_file(self, new_version: str):
        """Update the VERSION file if it exists."""
        version_file = self.repo_root / 'VERSION'
        if version_file.exists():
            with open(version_file, 'w', encoding='utf-8') as f:
                f.write(new_version + '\n')
            print(f"📝 Updated VERSION file to {new_version}")


def main():
    parser = argparse.ArgumentParser(description='Bump Conan package versions')
    parser.add_argument('bump_type', choices=['major', 'minor', 'patch', 'auto'],
                       help='Version bump type (auto determines from commits)')
    parser.add_argument('--conanfile', help='Specific conanfile.py to bump')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--all', action='store_true', help='Bump all conanfile.py files')

    args = parser.parse_args()

    repo_root = Path.cwd()
    bumper = VersionBumper(repo_root)

    # Determine bump type
    if args.bump_type == 'auto':
        commits = bumper.get_commit_messages_since_last_tag()
        bump_type = bumper.determine_bump_type_from_commits(commits)
        print(f"🤖 Auto-detected bump type: {bump_type} (from {len(commits)} commits)")
    else:
        bump_type = args.bump_type

    # Determine which files to bump
    if args.conanfile:
        conanfile_path = Path(args.conanfile)
        if not conanfile_path.exists():
            print(f"❌ Conanfile not found: {conanfile_path}")
            sys.exit(1)
        conanfiles = [conanfile_path]
    elif args.all:
        conanfiles = list(repo_root.rglob('conanfile.py'))
    else:
        # Default: bump all
        conanfiles = list(repo_root.rglob('conanfile.py'))

    if args.dry_run:
        print(f"🔍 Dry run: Would bump {len(conanfiles)} files with type '{bump_type}'")
        for conanfile in conanfiles[:5]:  # Show first 5
            current = bumper.get_current_version_from_file(conanfile)
            if current:
                if bump_type == 'major':
                    new = bumper.bump_major(current)
                elif bump_type == 'minor':
                    new = bumper.bump_minor(current)
                else:
                    new = bumper.bump_patch(current)
                print(f"  📦 {conanfile.relative_to(repo_root)}: {current} → {new}")
        if len(conanfiles) > 5:
            print(f"  ... and {len(conanfiles) - 5} more files")
        return

    # Perform the bump
    print(f"🚀 Bumping {len(conanfiles)} files with type '{bump_type}'...")

    updated_files = []
    for conanfile in conanfiles:
        result = bumper.bump_conanfile_versions(bump_type, conanfile)
        updated_files.extend(result)

    if updated_files:
        # Update VERSION file if we bumped the main package
        main_conanfile = repo_root / 'packages' / 'foundation' / 'sparetools-base' / 'conanfile.py'
        if any(f[0] == main_conanfile for f in updated_files):
            main_new_version = next(f[2] for f in updated_files if f[0] == main_conanfile)
            bumper.update_version_file(main_new_version)

        print(f"\n✅ Successfully bumped {len(updated_files)} files!")
        print("\n📋 Files updated:")
        for conanfile, old_ver, new_ver in updated_files:
            print(f"  📦 {conanfile.relative_to(repo_root)}: {old_ver} → {new_ver}")

        print("\n💡 Next steps:")
        print("  1. Review the changes: git diff")
        print("  2. Test the changes: python scripts/check_version_increment.py --all")
        print("  3. Commit the changes: git add -A && git commit -m 'bump: version to X.Y.Z'")
        print("  4. Push the changes")

    else:
        print("❌ No files were updated")
        sys.exit(1)


if __name__ == '__main__':
    main()