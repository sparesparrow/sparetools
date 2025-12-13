#!/usr/bin/env python3
"""
Profile Path Resolution Utility

Uses shared-dev-tools utilities to resolve Conan profile paths correctly
regardless of current working directory.
"""

import os
import sys
from pathlib import Path

# Try to import from installed shared-dev-tools (via Conan PYTHONPATH)
try:
    from shared_dev_tools.core.utilities import get_project_root
except ImportError:
    # Fallback: Check PYTHONPATH for Conan-installed package
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
        tools_path = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(tools_path))
        try:
            from shared_dev_tools.core.utilities import get_project_root
        except ImportError:
            raise ImportError(
                "Cannot import shared_dev_tools. "
                "Ensure sparetools-shared-dev-tools is installed via Conan and available in PYTHONPATH."
            )


def resolve_profile_path(profile_relative_path: str, base_path: str = None) -> str:
    """
    Resolve a relative profile path to an absolute path.
    
    Args:
        profile_relative_path: Relative path like 'packages/sparetools-bootstrap/profiles/base/linux-gcc11'
        base_path: Optional base path (defaults to project root)
    
    Returns:
        Absolute path to the profile
    """
    import os
    
    if base_path is None:
        # Try to use GITHUB_WORKSPACE first (GitHub Actions)
        github_workspace = os.environ.get('GITHUB_WORKSPACE', '')
        if github_workspace and Path(github_workspace).exists():
            base_path = Path(github_workspace)
        else:
            # Fall back to finding project root
            base_path = get_project_root()
    else:
        base_path = Path(base_path)
    
    profile_path = base_path / profile_relative_path
    
    if not profile_path.exists():
        raise FileNotFoundError(
            f"Profile not found: {profile_path}\n"
            f"Base path: {base_path}\n"
            f"Relative path: {profile_relative_path}"
        )
    
    return str(profile_path.absolute())


def main():
    """CLI entry point for profile path resolution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Resolve Conan profile paths to absolute paths'
    )
    parser.add_argument(
        'profile_path',
        help='Relative profile path (e.g., packages/sparetools-bootstrap/profiles/base/linux-gcc11)'
    )
    parser.add_argument(
        '--base-path',
        help='Base path for resolution (defaults to GITHUB_WORKSPACE or project root)'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check if profile exists and exit with error if not'
    )
    
    args = parser.parse_args()
    
    try:
        resolved = resolve_profile_path(args.profile_path, args.base_path)
        
        if args.check:
            if not Path(resolved).exists():
                print(f"ERROR: Profile does not exist: {resolved}", file=sys.stderr)
                sys.exit(1)
            print(f"OK: {resolved}")
        else:
            print(resolved)
        
        return 0
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
