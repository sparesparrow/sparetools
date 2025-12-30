#!/usr/bin/env python3
"""
Update all conanfile.py files to use git-based versioning strategy.

This script updates conanfile.py files to:
1. Use CONAN_BUILD_VERSION environment variable with fallback
2. Add import os if not present
3. Ensure version follows the pattern: os.environ.get('CONAN_BUILD_VERSION', 'fallback_version')
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


def find_conanfiles(root_dir: Path) -> List[Path]:
    """Find all conanfile.py files."""
    conanfiles = []
    for conanfile in root_dir.rglob('conanfile.py'):
        # Skip test_env and other build directories
        if 'test_env' in str(conanfile) or '__pycache__' in str(conanfile):
            continue
        conanfiles.append(conanfile)
    return conanfiles


def extract_version_from_conanfile(conanfile_path: Path) -> Tuple[str, bool]:
    """
    Extract current version from conanfile.py.
    
    Returns:
        Tuple of (version_string, has_os_import)
    """
    try:
        content = conanfile_path.read_text(encoding='utf-8')
        
        # Check if os is imported
        has_os_import = 'import os' in content or 'from os import' in content
        
        # Try to find version assignment
        # Pattern: version = "1.0.0" or version = '1.0.0'
        version_pattern = r'version\s*=\s*["\']([^"\']+)["\']'
        match = re.search(version_pattern, content)
        
        if match:
            return match.group(1), has_os_import
        
        # Try: version = 1.0.0 (without quotes)
        version_pattern_no_quotes = r'version\s*=\s*([0-9]+\.[0-9]+\.[0-9]+(?:\.[0-9]+)?)'
        match = re.search(version_pattern_no_quotes, content)
        
        if match:
            return match.group(1), has_os_import
            
    except Exception as e:
        print(f"Error reading {conanfile_path}: {e}")
    
    return None, False


def update_conanfile_versioning(conanfile_path: Path, dry_run: bool = False) -> bool:
    """
    Update conanfile.py to use git-based versioning.
    
    Returns:
        True if file was updated, False otherwise
    """
    try:
        content = conanfile_path.read_text(encoding='utf-8')
        original_content = content
        
        # Extract current version
        current_version, has_os_import = extract_version_from_conanfile(conanfile_path)
        
        if not current_version:
            print(f"⚠️  Could not extract version from {conanfile_path}")
            return False
        
        # Check if already using git-based versioning
        if "CONAN_BUILD_VERSION" in content:
            print(f"✓  {conanfile_path} already uses git-based versioning")
            return False
        
        # Add os import if needed
        if not has_os_import:
            # Find the first import statement
            import_pattern = r'^(import |from )'
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                if re.match(import_pattern, line):
                    insert_pos = i + 1
                    break
            
            # Insert os import
            if insert_pos > 0:
                lines.insert(insert_pos, 'import os')
            else:
                # No imports found, add at the beginning
                lines.insert(0, 'import os')
            content = '\n'.join(lines)
        
        # Replace version assignment
        # Pattern 1: version = "1.0.0"
        pattern1 = r'version\s*=\s*["\']([^"\']+)["\']'
        replacement1 = f"version = os.environ.get('CONAN_BUILD_VERSION', '{current_version}')"
        content = re.sub(pattern1, replacement1, content)
        
        # Pattern 2: version = 1.0.0 (without quotes)
        pattern2 = r'version\s*=\s*([0-9]+\.[0-9]+\.[0-9]+(?:\.[0-9]+)?)'
        replacement2 = f"version = os.environ.get('CONAN_BUILD_VERSION', '{current_version}')"
        content = re.sub(pattern2, replacement2, content)
        
        # Check if content changed
        if content != original_content:
            if not dry_run:
                conanfile_path.write_text(content, encoding='utf-8')
                print(f"✓  Updated {conanfile_path}")
            else:
                print(f"[DRY RUN] Would update {conanfile_path}")
            return True
        else:
            print(f"⚠️  No changes needed for {conanfile_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {conanfile_path}: {e}")
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Update all conanfile.py files to use git-based versioning'
    )
    parser.add_argument(
        '--root',
        type=str,
        default='.',
        help='Root directory to search (default: current directory)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )
    parser.add_argument(
        '--exclude',
        nargs='+',
        default=[],
        help='Directories to exclude (e.g., test_env __pycache__)'
    )
    
    args = parser.parse_args()
    
    root_dir = Path(args.root).resolve()
    if not root_dir.exists():
        print(f"Error: Root directory does not exist: {root_dir}")
        sys.exit(1)
    
    print(f"Searching for conanfile.py files in {root_dir}...")
    conanfiles = find_conanfiles(root_dir)
    
    # Filter excluded directories
    if args.exclude:
        conanfiles = [
            cf for cf in conanfiles
            if not any(exclude in str(cf) for exclude in args.exclude)
        ]
    
    print(f"Found {len(conanfiles)} conanfile.py files")
    print()
    
    updated_count = 0
    for conanfile in conanfiles:
        if update_conanfile_versioning(conanfile, dry_run=args.dry_run):
            updated_count += 1
    
    print()
    print(f"Summary: {updated_count} files {'would be ' if args.dry_run else ''}updated")


if __name__ == '__main__':
    main()
