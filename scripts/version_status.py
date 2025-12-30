#!/usr/bin/env python3
"""
Version Status Checker

Quick status check for Conan package versions with actionable guidance.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional


def run_command(cmd: List[str]) -> tuple[int, str, str]:
    """Run command and return (returncode, stdout, stderr)."""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
    return result.returncode, result.stdout, result.stderr


def get_current_branch() -> str:
    """Get current git branch."""
    code, stdout, stderr = run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    return stdout.strip() if code == 0 else 'unknown'


def get_modified_conanfiles() -> List[Path]:
    """Get conanfile.py files modified in current changes."""
    code, stdout, stderr = run_command(['git', 'diff', '--name-only', '--cached'])
    if code != 0:
        return []

    modified_files = stdout.split('\n')
    conanfiles = []

    for file in modified_files:
        if file.strip() and file.endswith('conanfile.py'):
            conanfiles.append(Path(file.strip()))

    return conanfiles


def check_version_increment_needed() -> tuple[bool, str]:
    """Check if version increment is needed."""
    branch = get_current_branch()
    modified_conanfiles = get_modified_conanfiles()

    # Rules for when version increment is needed
    needs_increment = False
    reason = ""

    if branch in ['main', 'master', 'develop']:
        needs_increment = True
        reason = f"Protected branch '{branch}' requires version increment for all changes"
    elif branch.startswith(('feature/', 'bugfix/', 'hotfix/', 'release/')):
        needs_increment = True
        reason = f"Branch type '{branch}' requires version increment"
    elif modified_conanfiles:
        needs_increment = True
        reason = f"Modified {len(modified_conanfiles)} conanfile.py file(s)"

    return needs_increment, reason


def main():
    """Main status checker."""
    print("🔍 SpareTools Version Status Checker")
    print("=" * 40)

    # Basic info
    branch = get_current_branch()
    print(f"📋 Current branch: {branch}")

    # Check if version increment is needed
    needs_increment, reason = check_version_increment_needed()
    print(f"📦 Version increment needed: {'Yes' if needs_increment else 'No'}")
    if reason:
        print(f"   Reason: {reason}")

    # Check modified conanfiles
    modified_conanfiles = get_modified_conanfiles()
    if modified_conanfiles:
        print(f"📝 Modified conanfile.py files: {len(modified_conanfiles)}")
        for conanfile in modified_conanfiles[:3]:  # Show first 3
            print(f"   • {conanfile}")
        if len(modified_conanfiles) > 3:
            print(f"   ... and {len(modified_conanfiles) - 3} more")

    # Run validation if increment needed
    if needs_increment:
        print("\n🔧 Running version validation...")
        code, stdout, stderr = run_command([sys.executable, 'scripts/check_version_increment.py', '--all'])

        if code == 0:
            print("✅ Version validation passed!")
        else:
            print("❌ Version validation failed!")
            print("\nValidation output:")
            print(stdout)
            if stderr:
                print("Errors:")
                print(stderr)

            print("\n💡 Quick fix options:")
            print("  1. Auto-bump patch version:")
            print("     python3 scripts/bump_version.py patch")
            print("")
            print("  2. Auto-bump based on commits:")
            print("     python3 scripts/bump_version.py auto")
            print("")
            print("  3. Manual version edit:")
            print("     Edit conanfile.py version field")
            print("")
            print("  4. Check current versions:")
            print("     python3 scripts/check_version_increment.py --all")
            print("")
            print("📖 See docs/VERSION_MANAGEMENT.md for detailed guidance")

            return 1

    print("\n✅ Version status check completed successfully!")

    # Show next steps if increment was needed and passed
    if needs_increment:
        print("\n📋 Next steps:")
        print("  1. Review version changes: git diff")
        print("  2. Commit changes: git commit -m 'bump: version to X.Y.Z'")
        print("  3. Push changes: git push")

    return 0


if __name__ == '__main__':
    sys.exit(main())