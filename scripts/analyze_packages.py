#!/usr/bin/env python3
"""
SpareTools Package Analysis Script

Analyzes all SpareTools packages to:
1. Categorize packages by type
2. Extract dependencies from each conanfile.py
3. Build dependency graph for build order
4. Determine package versions
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


class PackageAnalyzer:
    """Analyzes SpareTools packages and their dependencies"""

    def __init__(self, packages_root: Path):
        self.packages_root = packages_root
        self.packages: Dict[str, Dict] = {}

    def extract_package_info(self, conanfile_path: Path) -> Optional[Dict]:
        """Extract package information from a conanfile.py"""
        try:
            with open(conanfile_path, 'r') as f:
                content = f.read()

            # Extract basic package info
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)

            if not name_match or not version_match:
                return None

            package_name = name_match.group(1)
            package_version = version_match.group(1)

            # Extract dependencies using AST parsing
            tree = ast.parse(content)

            dependencies = {
                'python_requires': [],
                'tool_requires': [],
                'build_requires': [],
                'test_requires': [],
                'requires': []
            }

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
                                        elif isinstance(item, ast.Constant) and isinstance(item.value, str):
                                            deps.append(item.value)
                                    dependencies[attr_name] = deps
                                elif isinstance(node.value, ast.Str) or isinstance(node.value, ast.Constant):
                                    value = node.value.s if hasattr(node.value, 's') else str(node.value.value)
                                    dependencies[attr_name] = [value]

            return {
                'name': package_name,
                'version': package_version,
                'path': conanfile_path.parent,
                'conanfile': conanfile_path,
                'dependencies': dependencies,
                'category': self.categorize_package(package_name, conanfile_path)
            }

        except Exception as e:
            print(f"Error parsing {conanfile_path}: {e}")
            return None

    def categorize_package(self, name: str, path: Path) -> str:
        """Categorize package based on name and path"""

        # Foundation packages
        if any(keyword in name for keyword in ['base', 'bootstrap', 'cpython', 'recipe-base', 'shared-dev-tools', 'test-harness', 'test-framework', 'flatbuffers', 'protocols', 'icd', 'schema-tests', 'voice-fsm']):
            return 'foundation'

        # Embedded packages
        if any(keyword in name for keyword in ['embedded', 'hal-sunton', 'lvgl']):
            return 'embedded'

        # Schema packages
        if any(keyword in name for keyword in ['bpm-schemas', 'schemas']):
            return 'schemas'

        # MCP packages
        if any(keyword in name for keyword in ['mcp-core', 'mcp-ecosystem', 'mcp-prompts', 'mcp-servers']):
            return 'mcp'

        # Consumer packages
        if 'consumers' in str(path):
            return 'consumers'

        # Other categories
        if 'python' in str(path) or any(keyword in name for keyword in ['fs-tools', 'proc-tools', 'py']):
            return 'python_tools'
        elif 'streaming' in str(path):
            return 'streaming'
        elif 'wifi' in str(path):
            return 'wifi'
        elif 'sdr' in str(path):
            return 'sdr'
        elif 'security' in str(path):
            return 'security'
        elif 'input' in str(path):
            return 'input'
        elif 'prompt' in str(path):
            return 'prompt'
        elif 'devops' in str(path):
            return 'devops'
        elif 'firmware' in str(path):
            return 'firmware'
        elif 'pentest' in str(path):
            return 'pentest'
        elif 'deprecated' in str(path):
            return 'deprecated'

        return 'other'

    def analyze_all_packages(self) -> Dict[str, Dict]:
        """Analyze all packages in the packages directory"""
        packages = {}

        # Find all conanfile.py files
        for conanfile_path in self.packages_root.rglob('conanfile.py'):
            # Skip test_package directories
            if 'test_package' in str(conanfile_path):
                continue

            package_info = self.extract_package_info(conanfile_path)
            if package_info:
                packages[package_info['name']] = package_info

        self.packages = packages
        return packages

    def build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build dependency graph for build order"""
        graph = {}

        for package_name, package_info in self.packages.items():
            deps = set()

            # Add all dependencies to the set
            for dep_type, dep_list in package_info['dependencies'].items():
                for dep in dep_list:
                    # Extract package name (before @ or /)
                    dep_name = dep.split('@')[0].split('/')[0]
                    if dep_name.startswith('sparetools-') or dep_name in ['flatbuffers', 'cmake']:
                        deps.add(dep_name)

            graph[package_name] = list(deps)

        return graph

    def get_build_order(self) -> List[str]:
        """Get packages in build order based on dependencies"""
        graph = self.build_dependency_graph()

        # Simple topological sort
        visited = set()
        temp_visited = set()
        order = []

        def visit(node):
            if node in temp_visited:
                return  # Cycle detected, skip
            if node in visited:
                return

            temp_visited.add(node)

            for dep in graph.get(node, []):
                if dep in self.packages:  # Only visit SpareTools packages
                    visit(dep)

            temp_visited.remove(node)
            visited.add(node)
            order.append(node)

        # Visit all nodes
        for package in self.packages:
            if package not in visited:
                visit(package)

        return order

    def categorize_by_type(self) -> Dict[str, List[str]]:
        """Group packages by category"""
        categories = {}

        for package_name, package_info in self.packages.items():
            category = package_info['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(package_name)

        return categories

    def print_analysis(self):
        """Print analysis results"""
        print("=== SpareTools Package Analysis ===")
        print()

        # Print categorized packages
        categories = self.categorize_by_type()
        for category, packages in sorted(categories.items()):
            print(f"{category.upper()} PACKAGES ({len(packages)}):")
            for package in sorted(packages):
                if package in self.packages:
                    version = self.packages[package]['version']
                    print(f"  - {package} v{version}")
            print()

        # Print dependency graph
        print("DEPENDENCY GRAPH:")
        graph = self.build_dependency_graph()
        for package, deps in sorted(graph.items()):
            if deps:
                print(f"  {package} -> {', '.join(sorted(deps))}")
        print()

        # Print build order
        print("BUILD ORDER:")
        build_order = self.get_build_order()
        for i, package in enumerate(build_order, 1):
            if package in self.packages:
                category = self.packages[package]['category']
                print(f"  {i:2d}. {package} ({category})")


def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_packages.py <packages_root>")
        sys.exit(1)

    packages_root = Path(sys.argv[1])
    if not packages_root.exists():
        print(f"Error: {packages_root} does not exist")
        sys.exit(1)

    analyzer = PackageAnalyzer(packages_root)
    packages = analyzer.analyze_all_packages()

    if not packages:
        print("No packages found!")
        sys.exit(1)

    analyzer.print_analysis()


if __name__ == '__main__':
    main()
