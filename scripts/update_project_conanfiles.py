#!/usr/bin/env python3
"""
SpareTools Project Conanfile Update Script

Updates project conanfiles to include appropriate SpareTools dependencies
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set
import shutil


class ConanfileUpdater:
    """Updates project conanfiles with SpareTools dependencies"""

    def __init__(self):
        # Standard dependency versions (should match what's uploaded)
        self.versions = {
            'sparetools-base': '2.0.3',
            'sparetools-bootstrap': '2.0.3',
            'sparetools-recipe-base': '2.0.3',
            'sparetools-cpython': '3.12.7',
            'sparetools-flatbuffers': '24.3.25',
            'sparetools-shared-dev-tools': '2.0.3',
            'sparetools-embedded': '1.0.0',
            'sparetools-mcp-core': '1.0.0',
            'sparetools-protocols': '1.0.0',
            'sparesparrow-protocols': '1.0.0',
            'sparetools-bpm-schemas': '2.0.0',
            'sparetools-mcp-ecosystem': '1.0.0',
            'sparetools-mcp-prompts': '3.13.0',
            'sparetools-mcp-servers': '1.0.0',
            'sparetools-mia': '2.0.0',
            'sparetools-bpm-detector': '0.1.0',
            'sparetools-nucleus': '0.1.0',
            'sparetools-openssl': '3.3.2',
            'sparetools-hal-sunton': '1.0.0',
            'sparetools-lvgl': '8.3.11',
            'sparetools-icd': '2.0.0'
        }

    def create_backup(self, conanfile_path: Path) -> Path:
        """Create a backup of the conanfile"""
        backup_path = conanfile_path.with_suffix('.py.backup')
        shutil.copy2(conanfile_path, backup_path)
        return backup_path

    def get_project_dependencies(self, project_path: Path) -> Dict[str, List[str]]:
        """Get the appropriate dependencies for a project based on its type"""

        project_name = project_path.name
        parent_name = project_path.parent.name if project_path.parent.name != project_path.name else ""

        # Base dependencies that almost all projects need
        base_deps = {
            'python_requires': [
                "sparetools-base/2.0.3"
            ],
            'tool_requires': [
                "sparetools-cpython/3.12.7",
                "sparetools-flatbuffers/24.3.25"
            ],
            'requires': [
                "sparetools-embedded/1.0.0",
                "sparetools-mcp-core/1.0.0",
                "sparetools-protocols/1.0.0"
            ]
        }

        # ESP32 projects
        if 'esp32' in str(project_path).lower() or 'ESP32' in str(project_path):
            base_deps['requires'].extend([
                "sparetools-bpm-schemas/2.0.0",
                "sparesparrow-protocols/1.0.0"
            ])

        # MCP-specific projects
        elif 'mcp' in str(project_path).lower():
            base_deps['requires'].extend([
                "sparetools-mcp-ecosystem/1.0.0",
                "sparetools-mcp-prompts/3.13.0",
                "sparetools-mcp-servers/1.0.0"
            ])

        # MIA projects
        elif 'mia' in str(project_path).lower() or project_name == 'mia':
            base_deps['requires'].extend([
                "sparesparrow-protocols/1.0.0",
                "sparetools-bpm-schemas/2.0.0",
                "sparetools-mcp-ecosystem/1.0.0",
                "sparetools-mcp-prompts/3.13.0",
                "sparetools-mcp-servers/1.0.0",
                "sparetools-mia/2.0.0"
            ])

        # Projects that might need hardware
        if any(keyword in str(project_path).lower() for keyword in ['rpi', 'hardware', 'embedded']):
            base_deps['requires'].extend([
                "sparetools-hal-sunton/1.0.0",
                "sparetools-lvgl/8.3.11"
            ])

        return base_deps

    def update_conanfile(self, conanfile_path: Path) -> bool:
        """Update a single conanfile with SpareTools dependencies"""
        try:
            with open(conanfile_path, 'r') as f:
                content = f.read()

            # Create backup
            backup_path = self.create_backup(conanfile_path)
            print(f"Created backup: {backup_path}")

            # Get project dependencies
            deps = self.get_project_dependencies(conanfile_path.parent)

            # Check what dependencies are already present
            existing_deps = self.extract_existing_dependencies(content)

            # Prepare additions
            additions = []

            for dep_type, packages in deps.items():
                for package in packages:
                    package_name = package.split('/')[0]
                    if package_name not in existing_deps:
                        additions.append(f"    \"{package}\",")

                        # Insert the dependency in the right section
                        section_pattern = rf'({dep_type}\s*=\s*\[)'
                        if re.search(section_pattern, content):
                            # Add to existing section
                            content = re.sub(
                                section_pattern,
                                rf'\1\n    "{package}",',
                                content,
                                count=1
                            )
                        else:
                            # Create new section
                            # Find a good place to insert (after class definition)
                            class_match = re.search(r'(class\s+\w+.*?:.*?\n)', content, re.DOTALL)
                            if class_match:
                                insert_pos = class_match.end()
                                content = content[:insert_pos] + f'\n    {dep_type} = [\n        "{package}",\n    ]\n' + content[insert_pos:]

            if additions:
                print(f"Adding dependencies to {conanfile_path}:")
                for addition in additions:
                    print(f"  {addition.strip()}")

                # Write updated content
                with open(conanfile_path, 'w') as f:
                    f.write(content)

                return True
            else:
                print(f"No updates needed for {conanfile_path}")
                return False

        except Exception as e:
            print(f"Error updating {conanfile_path}: {e}")
            return False

    def extract_existing_dependencies(self, content: str) -> Set[str]:
        """Extract existing SpareTools dependencies from conanfile content"""
        existing = set()

        # Find all dependency declarations
        dep_patterns = [
            r'python_requires\s*=.*?\[(.*?)\]',
            r'tool_requires\s*=.*?\[(.*?)\]',
            r'build_requires\s*=.*?\[(.*?)\]',
            r'test_requires\s*=.*?\[(.*?)\]',
            r'requires\s*=.*?\[(.*?)\]'
        ]

        for pattern in dep_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                # Extract package names from quoted strings
                packages = re.findall(r'["\']([^"\']+)["\']', match)
                for package in packages:
                    package_name = package.split('/')[0].split('@')[0]
                    if package_name.startswith('sparetools-') or package_name.startswith('sparesparrow-'):
                        existing.add(package_name)

        return existing

    def update_all_projects(self, project_dirs: List[Path]) -> Dict[str, bool]:
        """Update all project conanfiles"""
        results = {}

        for project_dir in project_dirs:
            if not project_dir.exists():
                continue

            for conanfile_path in project_dir.rglob('conanfile.py'):
                # Skip test_package directories
                if 'test_package' in str(conanfile_path):
                    continue

                # Skip packages directory
                if 'packages' in str(conanfile_path):
                    continue

                # Skip build directories
                if '.buildenv' in str(conanfile_path) or 'build' in str(conanfile_path):
                    continue

                project_name = conanfile_path.parent.name
                print(f"\n--- Updating {project_name} ---")
                print(f"Conanfile: {conanfile_path}")

                success = self.update_conanfile(conanfile_path)
                results[str(conanfile_path)] = success

        return results


def main():
    updater = ConanfileUpdater()

    # Project directories to update
    project_dirs = [
        Path('/home/sparrow/projects/embedded-systems'),
        Path('/home/sparrow/projects/portfolio')
    ]

    print("=== Updating Project Conanfiles with SpareTools Dependencies ===")
    print()

    results = updater.update_all_projects(project_dirs)

    print("\n=== Update Summary ===")
    updated = sum(1 for success in results.values() if success)
    total = len(results)

    print(f"Total conanfiles processed: {total}")
    print(f"Successfully updated: {updated}")
    print(f"No changes needed: {total - updated}")

    if results:
        print("\nUpdated files:")
        for conanfile, success in results.items():
            if success:
                print(f"  ✅ {conanfile}")

        print("\nBackup files created (.py.backup):")
        for conanfile in results.keys():
            backup = conanfile + '.backup'
            if os.path.exists(backup):
                print(f"  💾 {backup}")


if __name__ == '__main__':
    main()
