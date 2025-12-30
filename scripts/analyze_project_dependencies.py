#!/usr/bin/env python3
"""
SpareTools Project Dependency Analysis Script

Analyzes project conanfiles to determine what SpareTools packages they need
and suggests appropriate dependency types (requires, tool_requires, python_requires)
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict


class ProjectDependencyAnalyzer:
    """Analyzes project conanfiles for SpareTools dependencies"""

    def __init__(self):
        # Known SpareTools packages by category
        self.sparetools_packages = {
            'foundation': {
                'sparetools-base', 'sparetools-bootstrap', 'sparetools-cpython',
                'sparetools-recipe-base', 'sparetools-shared-dev-tools',
                'sparetools-test-harness', 'sparetools-test-framework',
                'sparetools-flatbuffers', 'sparetools-protocols', 'sparetools-icd',
                'sparetools-schema-tests', 'sparetools-voice-fsm'
            },
            'embedded': {
                'sparetools-embedded', 'sparetools-hal-sunton', 'sparetools-lvgl'
            },
            'schemas': {
                'sparetools-bpm-schemas', 'sparesparrow-protocols'
            },
            'mcp': {
                'sparetools-mcp-core', 'sparetools-mcp-ecosystem',
                'sparetools-mcp-prompts', 'sparetools-mcp-servers'
            },
            'consumers': {
                'sparetools-mia', 'sparetools-bpm-detector', 'sparetools-nucleus',
                'sparetools-openssl', 'sparetools-openssl-tools', 'sparetools-obd-sim',
                'sparetools-cliphist-android', 'sparetools-mcp-orchestrator',
                'sparetools-tinymcp', 'sparetools-mcpserver-cpp'
            },
            'other': {
                'sparetools-py', 'sparetools-fs-tools', 'sparetools-proc-tools',
                'sparetools-streaming-solutions', 'sparetools-wifi-sensing',
                'sparetools-sdr-tools', 'sparetools-crypto-suite',
                'sparetools-gamepad-core', 'sparetools-input-backends',
                'sparetools-gamepad-mapper', 'sparetools-prompt-system',
                'sparetools-ci-templates', 'sparetools-pentest-toolkit',
                'esp32-bus-pirate'
            }
        }

        # Flatten for easy lookup
        self.all_packages = set()
        for category_packages in self.sparetools_packages.values():
            self.all_packages.update(category_packages)

    def extract_dependencies(self, conanfile_path: Path) -> Dict[str, List[str]]:
        """Extract dependencies from a conanfile.py"""
        try:
            with open(conanfile_path, 'r') as f:
                content = f.read()

            dependencies = {
                'python_requires': [],
                'tool_requires': [],
                'build_requires': [],
                'test_requires': [],
                'requires': []
            }

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            attr_name = target.id
                            if attr_name in dependencies:
                                if isinstance(node.value, ast.List):
                                    deps = []
                                    for item in node.value.elts:
                                        if isinstance(item, ast.Str):
                                            deps.append(item.s)
                                        elif hasattr(item, 'value') and isinstance(item.value, str):
                                            deps.append(item.value)
                                    dependencies[attr_name] = deps
                                elif isinstance(node.value, ast.Str) or hasattr(node.value, 'value'):
                                    value = node.value.s if hasattr(node.value, 's') else str(node.value.value)
                                    dependencies[attr_name] = [value]

            return dependencies

        except Exception as e:
            print(f"Error parsing {conanfile_path}: {e}")
            return {}

    def categorize_project(self, conanfile_path: Path) -> str:
        """Categorize project based on path and content"""
        path_str = str(conanfile_path)

        if 'esp32' in path_str or 'ESP32' in path_str:
            return 'esp32'
        elif 'mia' in path_str or 'MIA' in path_str:
            return 'mia'
        elif 'mcp' in path_str or 'MCP' in path_str:
            return 'mcp'
        elif 'android' in path_str:
            return 'android'
        elif 'rpi' in path_str:
            return 'rpi'
        else:
            return 'other'

    def analyze_missing_dependencies(self, current_deps: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Analyze what SpareTools dependencies are missing"""

        # Flatten current dependencies
        current_packages = set()
        for dep_list in current_deps.values():
            for dep in dep_list:
                # Extract package name (before @ or /)
                package_name = dep.split('@')[0].split('/')[0]
                current_packages.add(package_name)

        missing_deps = {
            'python_requires': [],
            'tool_requires': [],
            'requires': []
        }

        # Check each SpareTools package
        for package_name in self.all_packages:
            if package_name not in current_packages:
                dep_type = self.determine_dependency_type(package_name)
                if dep_type:
                    missing_deps[dep_type].append(package_name)

        return missing_deps

    def determine_dependency_type(self, package_name: str) -> Optional[str]:
        """Determine the appropriate dependency type for a package"""

        # Foundation packages that are typically python_requires
        python_requires_packages = {
            'sparetools-base', 'sparetools-bootstrap', 'sparetools-recipe-base'
        }

        # Build tool packages
        tool_requires_packages = {
            'sparetools-cpython', 'sparetools-flatbuffers', 'sparetools-shared-dev-tools'
        }

        # Runtime/library packages
        requires_packages = {
            'sparetools-embedded', 'sparetools-mcp-core', 'sparetools-protocols',
            'sparetools-icd', 'sparetools-bpm-schemas', 'sparesparrow-protocols',
            'sparetools-mcp-ecosystem', 'sparetools-mcp-prompts', 'sparetools-mcp-servers',
            'sparetools-mia', 'sparetools-bpm-detector', 'sparetools-nucleus',
            'sparetools-openssl', 'sparetools-hal-sunton', 'sparetools-lvgl'
        }

        if package_name in python_requires_packages:
            return 'python_requires'
        elif package_name in tool_requires_packages:
            return 'tool_requires'
        elif package_name in requires_packages:
            return 'requires'

        return None

    def generate_dependency_updates(self, conanfile_path: Path) -> Dict[str, List[str]]:
        """Generate dependency updates for a project"""
        current_deps = self.extract_dependencies(conanfile_path)
        missing_deps = self.analyze_missing_dependencies(current_deps)

        # Filter based on project type
        project_type = self.categorize_project(conanfile_path)

        # Customize recommendations based on project type
        if project_type == 'esp32':
            # ESP32 projects need embedded packages
            pass  # Keep all recommendations
        elif project_type == 'mia':
            # MIA projects are comprehensive, keep most recommendations
            pass
        elif project_type == 'mcp':
            # MCP projects focus on MCP packages
            missing_deps['requires'] = [pkg for pkg in missing_deps['requires']
                                      if 'mcp' in pkg or pkg in {'sparetools-embedded', 'sparetools-protocols'}]

        return missing_deps

    def analyze_all_projects(self, project_dirs: List[Path]) -> Dict[str, Dict]:
        """Analyze all projects in the given directories"""
        results = {}

        for project_dir in project_dirs:
            if not project_dir.exists():
                continue

            for conanfile_path in project_dir.rglob('conanfile.py'):
                # Skip test_package directories
                if 'test_package' in str(conanfile_path):
                    continue

                # Skip packages directory (we're analyzing projects, not packages)
                if 'packages' in str(conanfile_path):
                    continue

                project_name = conanfile_path.parent.name
                project_path = str(conanfile_path.parent)

                updates = self.generate_dependency_updates(conanfile_path)

                results[project_path] = {
                    'name': project_name,
                    'conanfile': str(conanfile_path),
                    'category': self.categorize_project(conanfile_path),
                    'current_dependencies': self.extract_dependencies(conanfile_path),
                    'suggested_updates': updates
                }

        return results


def main():
    analyzer = ProjectDependencyAnalyzer()

    # Project directories to analyze
    project_dirs = [
        Path('/home/sparrow/projects/embedded-systems'),
        Path('/home/sparrow/projects/portfolio')
    ]

    results = analyzer.analyze_all_projects(project_dirs)

    print("=== SpareTools Project Dependency Analysis ===")
    print()

    for project_path, info in sorted(results.items()):
        print(f"Project: {info['name']} ({info['category']})")
        print(f"Path: {project_path}")
        print(f"Conanfile: {info['conanfile']}")
        print()

        # Show current dependencies
        current = info['current_dependencies']
        if any(current.values()):
            print("Current dependencies:")
            for dep_type, deps in current.items():
                if deps:
                    print(f"  {dep_type}: {', '.join(deps)}")
            print()

        # Show suggested updates
        updates = info['suggested_updates']
        has_updates = any(updates.values())

        if has_updates:
            print("Suggested SpareTools dependency additions:")
            for dep_type, deps in updates.items():
                if deps:
                    print(f"  {dep_type}: {', '.join(sorted(deps))}")
            print()

        print("-" * 80)


if __name__ == '__main__':
    main()
