#!/usr/bin/env python3
"""
Build Profile Arguments for Conan

Generates Conan profile arguments using shared-dev-tools utilities.
Resolves profile paths correctly regardless of working directory.

This script should be run with Python from sparetools-cpython package,
which has shared-dev-tools installed via Conan package_info PYTHONPATH.
"""

import os
import sys
from pathlib import Path

# Try to import from installed shared-dev-tools (via Conan PYTHONPATH)
try:
    from shared_dev_tools.core.utilities import get_project_root
except ImportError:
    # Fallback: Try to find shared-dev-tools in source tree or Conan cache
    # Check if we're in a Conan environment with PYTHONPATH set
    pythonpath = os.environ.get('PYTHONPATH', '').split(os.pathsep)
    found = False
    
    for path in pythonpath:
        if path:
            tools_init = Path(path) / 'shared_dev_tools' / '__init__.py'
            if tools_init.exists():
                sys.path.insert(0, path)
                from shared_dev_tools.core.utilities import get_project_root
                found = True
                break
    
    if not found:
        # Last resort: try source tree
        tools_path = Path(__file__).parent.parent
        sys.path.insert(0, str(tools_path))
        try:
            from shared_dev_tools.core.utilities import get_project_root
        except ImportError:
            print("ERROR: Cannot import shared_dev_tools. Ensure sparetools-shared-dev-tools is installed via Conan.", file=sys.stderr)
            sys.exit(1)


def get_repo_root():
    """Get repository root using shared-dev-tools or GitHub workspace."""
    # Try GITHUB_WORKSPACE first (GitHub Actions)
    github_workspace = os.environ.get('GITHUB_WORKSPACE', '')
    if github_workspace and Path(github_workspace).exists():
        return Path(github_workspace)
    
    # Fall back to project root detection
    return get_project_root()


def build_profile_args(base_profile, method_profile, feature_profile=None):
    """
    Build Conan profile arguments with correctly resolved paths.
    
    Args:
        base_profile: Base profile path (e.g., 'base/linux-gcc11')
        method_profile: Build method profile (e.g., 'build-methods/perl-configure')
        feature_profile: Optional feature profile (e.g., 'features/fips-enabled')
    
    Returns:
        String of profile arguments for conan command
    """
    repo_root = get_repo_root()
    profiles_base = repo_root / 'packages' / 'sparetools-openssl-tools' / 'profiles'
    
    profiles = []
    
    # Base profile
    base_path = profiles_base / base_profile
    if not base_path.exists():
        print(f"⚠️ Profile not found: {base_path}, using default", file=sys.stderr)
    profiles.append(f"-pr:b {base_path.absolute()}")
    
    # Method profile
    method_path = profiles_base / method_profile
    if not method_path.exists():
        print(f"⚠️ Profile not found: {method_path}, using default", file=sys.stderr)
    profiles.append(f"-pr:b {method_path.absolute()}")
    
    # Feature profile (if provided)
    if feature_profile:
        feature_path = profiles_base / feature_profile
        if not feature_path.exists():
            print(f"⚠️ Profile not found: {feature_path}, using default", file=sys.stderr)
        profiles.append(f"-pr:b {feature_path.absolute()}")
    
    return ' '.join(profiles)


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print("Usage: build_profile_args.py <base_profile> <method_profile> [feature_profile]", file=sys.stderr)
        print("Example: build_profile_args.py base/linux-gcc11 build-methods/perl-configure features/fips-enabled", file=sys.stderr)
        sys.exit(1)
    
    base_profile = sys.argv[1]
    method_profile = sys.argv[2]
    feature_profile = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        profile_args = build_profile_args(base_profile, method_profile, feature_profile)
        print(profile_args)
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
