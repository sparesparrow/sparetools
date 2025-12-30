#!/usr/bin/env python3
"""
Validate that conanfile.py files use git-based versioning pattern.

This script checks that all conanfile.py files follow the pattern:
    version = os.environ.get('CONAN_BUILD_VERSION', 'fallback_version')
"""

import re
import sys
from pathlib import Path


def validate_conanfile_versioning(conanfile_path: Path) -> tuple[bool, str]:
    """
    Validate that conanfile.py uses git-based versioning.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        content = conanfile_path.read_text(encoding='utf-8')
        
        # Check if file has version assignment
        if 'version' not in content:
            return True, ""  # No version field, skip
        
        # Check if using git-based versioning pattern
        git_version_pattern = r'version\s*=\s*os\.environ\.get\([\'"]CONAN_BUILD_VERSION[\'"]'
        
        if re.search(git_version_pattern, content):
            return True, ""
        
        # Check if os is imported
        has_os_import = 'import os' in content or 'from os import' in content
        
        # Find version assignment
        version_pattern = r'version\s*=\s*["\']?([^"\'\n]+)["\']?'
        match = re.search(version_pattern, content)
        
        if match:
            version_value = match.group(1).strip()
            error_msg = (
                f"{conanfile_path}: Version does not use git-based pattern.\n"
                f"  Found: version = {version_value}\n"
                f"  Expected: version = os.environ.get('CONAN_BUILD_VERSION', '{version_value}')\n"
            )
            if not has_os_import:
                error_msg += "  Also missing: import os\n"
            return False, error_msg
        
        return True, ""
        
    except Exception as e:
        return False, f"{conanfile_path}: Error reading file: {e}\n"


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        # No files provided, check all conanfile.py files
        root_dir = Path.cwd()
        conanfiles = list(root_dir.rglob('conanfile.py'))
        # Filter out test_env and build directories
        conanfiles = [
            cf for cf in conanfiles
            if 'test_env' not in str(cf) and '__pycache__' not in str(cf)
        ]
    else:
        # Files provided via pre-commit
        conanfiles = [Path(f) for f in sys.argv[1:] if f.endswith('conanfile.py')]
    
    if not conanfiles:
        sys.exit(0)  # No conanfiles to check
    
    errors = []
    for conanfile in conanfiles:
        is_valid, error_msg = validate_conanfile_versioning(conanfile)
        if not is_valid:
            errors.append(error_msg)
    
    if errors:
        print("❌ Git-based versioning validation failed:\n")
        for error in errors:
            print(error)
        print("\nTo fix, run: python3 scripts/update_conanfiles_versioning.py")
        sys.exit(1)
    
    print("✅ All conanfile.py files use git-based versioning")
    sys.exit(0)


if __name__ == '__main__':
    main()
