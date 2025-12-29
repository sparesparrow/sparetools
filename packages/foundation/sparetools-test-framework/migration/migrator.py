#!/usr/bin/env python
"""
Migration completed: All ngapy references have been updated to sparetools.
"""

import ast
import os
import re
from typing import Dict, List


RENAME_MAP = {
    # Migration completed - all ngapy imports have been updated to sparetools
}


class ImportMigrator(ast.NodeTransformer):
    """AST transformer to update import statements"""

    def visit_ImportFrom(self, node):
        """Update From...import statements"""
        if node.module and node.module in RENAME_MAP:
            node.module = RENAME_MAP[node.module]
        return node

    def visit_Import(self, node):
        """Update import statements"""
        for alias in node.names:
            if alias.name in RENAME_MAP:
                alias.name = RENAME_MAP[alias.name]
        return node


def migrate_file(file_path: str) -> bool:
    """
    Update imports in a single file using AST parsing.

    Args:
        file_path: Path to the Python file to migrate

    Returns:
        True if file was modified, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Parse the AST
        tree = ast.parse(source, filename=file_path)

        # Apply transformations
        migrator = ImportMigrator()
        new_tree = migrator.visit(tree)

        # Convert back to source code
        new_source = ast.unparse(new_tree) if hasattr(ast, 'unparse') else source

        # Only write if there were changes
        if new_source != source:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_source)
            return True

        return False

    except Exception as e:
        print(f"Error migrating {file_path}: {e}")
        return False


def migrate_directory(directory: str, extensions: List[str] = None) -> int:
    """
    Migrate all files in a directory tree.

    Args:
        directory: Root directory to search
        extensions: File extensions to migrate (default: ['.py'])

    Returns:
        Number of files migrated
    """
    if extensions is None:
        extensions = ['.py']

    migrated_count = 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                if migrate_file(file_path):
                    migrated_count += 1
                    print(f"Migrated: {file_path}")

    return migrated_count


def find_ngapy_references(directory: str) -> List[str]:
    """
    Check for any remaining ngapy references (migration verification).

    Args:
        directory: Directory to search

    Returns:
        List of files with ngapy references
    """
    files_with_refs = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'ngapy.' in content or 'from ngapy' in content or 'import ngapy' in content:
                            files_with_refs.append(file_path)
                except Exception:
                    pass

    return files_with_refs


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Migrate ngapy imports to sparetools')
    parser.add_argument('directory', help='Directory to migrate')
    parser.add_argument('--check-only', action='store_true', help='Only check for remaining ngapy references')

    args = parser.parse_args()

    if args.check_only:
        refs = find_ngapy_references(args.directory)
        if refs:
            print("Files still containing ngapy references:")
            for ref in refs:
                print(f"  {ref}")
            print(f"\nTotal: {len(refs)} files")
        else:
            print("No ngapy references found!")
    else:
        count = migrate_directory(args.directory)
        print(f"Migrated {count} files")

        # Check for remaining references
        refs = find_ngapy_references(args.directory)
        if refs:
            print(f"\nWarning: {len(refs)} files still contain ngapy references")
            print("You may need to update these manually or add them to RENAME_MAP")