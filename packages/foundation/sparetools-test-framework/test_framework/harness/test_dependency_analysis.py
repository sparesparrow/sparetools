#
# DATA_RIGHTS:  HONEYWELL CONFIDENTIAL & PROPRIETARY
#              THIS WORK CONTAINS VALUABLE CONFIDENTIAL AND PROPRIETARY
#              INFORMATION. DISCLOSURE, USE OR REPRODUCTION OUTSIDE OF
#              HONEYWELL INTERNATIONAL, INC. IS PROHIBITED EXCEPT AS
#              AUTHORIZED IN WRITING. THIS UNPUBLISHED WORK IS PROTECTED BY
#              THE LAWS OF THE UNITED STATES AND OTHER COUNTRIES. IN THE
#              EVENT OF PUBLICATION, THE FOLLOWING NOTICE SHALL APPLY:
#              COPR. 2020-2021 HONEYWELL INTERNATIONAL, INC. ALL RIGHTS RESERVED.
#

"""
Dependency Analysis and SBOM Generation Tests for Ngapy
======================================================

This module provides dependency analysis and Software Bill of Materials (SBOM)
generation capabilities for the ngapy package.
"""

import os
import sys
import json
import hashlib
import pkg_resources
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import subprocess

try:
    from .test_harness import NgapyTestHarnes
except ImportError:
    from sparetools.test_framework.harness import NgapyTestHarnes


class DependencyAnalysisHarness(NgapyTestHarnes):
    """Test harness for dependency analysis and SBOM generation."""

    def __init__(self):
        super().__init__()
        self.dependency_graph = {}
        self.sbom_data = {}

    def analyze_package_dependencies(self) -> bool:
        """Analyze package dependencies and build dependency graph."""
        success = True

        try:
            # Get all installed packages
            installed_packages = {}
            for pkg in pkg_resources.working_set:
                installed_packages[pkg.key] = {
                    'version': pkg.version,
                    'location': pkg.location,
                    'requires': [str(req) for req in pkg.requires()],
                    'metadata': self._get_package_metadata(pkg)
                }

            self.dependency_graph = installed_packages

            # Validate core dependencies
            core_deps = ['python-dateutil', 'requests']  # Add actual core dependencies
            for dep in core_deps:
                if dep not in installed_packages:
                    success &= self.verify(
                        False, True,
                        f"Missing core dependency: {dep}",
                        test_num=1
                    )
                else:
                    success &= self.verify(
                        True, True,
                        f"Core dependency present: {dep} v{installed_packages[dep]['version']}",
                        test_num=1
                    )

        except Exception as e:
            success &= self.verify(
                False, True,
                f"Dependency analysis failed: {str(e)}",
                test_num=1
            )

        return success

    def _get_package_metadata(self, pkg) -> Dict[str, Any]:
        """Get additional metadata for a package."""
        metadata = {}

        try:
            if hasattr(pkg, 'get_metadata'):
                # Try to get PKG-INFO
                pkg_info = pkg.get_metadata('PKG-INFO')
                metadata['pkg_info'] = pkg_info[:500]  # First 500 chars
        except:
            pass

        # Add license info if available
        try:
            metadata['license'] = pkg.get_metadata('LICENSE')[:200] if hasattr(pkg, 'get_metadata') else 'Unknown'
        except:
            metadata['license'] = 'Unknown'

        # Add homepage
        metadata['homepage'] = getattr(pkg, 'homepage', 'Unknown')

        return metadata

    def validate_dependency_integrity(self) -> bool:
        """Validate integrity of installed packages."""
        success = True

        for pkg_name, pkg_info in self.dependency_graph.items():
            try:
                pkg_location = pkg_info['location']

                if pkg_location and os.path.exists(pkg_location):
                    # Calculate hash of package files
                    pkg_hash = self._calculate_package_hash(pkg_location)

                    success &= self.verify(
                        len(pkg_hash) > 0, True,
                        f"Package integrity check: {pkg_name}",
                        test_num=2
                    )

                    # Store hash for SBOM
                    pkg_info['integrity_hash'] = pkg_hash

                else:
                    success &= self.verify(
                        False, True,
                        f"Package location not found: {pkg_name} at {pkg_location}",
                        test_num=2
                    )

            except Exception as e:
                success &= self.verify(
                    False, True,
                    f"Integrity check failed for {pkg_name}: {str(e)}",
                    test_num=2
                )

        return success

    def _calculate_package_hash(self, pkg_location: str) -> str:
        """Calculate SHA256 hash of package files."""
        if not os.path.isdir(pkg_location):
            return ""

        hash_obj = hashlib.sha256()

        try:
            for root, dirs, files in os.walk(pkg_location):
                # Skip __pycache__ and other irrelevant directories
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git']]

                for file in sorted(files):
                    if file.endswith(('.py', '.pyc', '.so', '.pyd', '.egg-info')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'rb') as f:
                                while chunk := f.read(8192):
                                    hash_obj.update(chunk)
                        except:
                            continue  # Skip files that can't be read

        except Exception:
            return ""

        return hash_obj.hexdigest()

    def check_dependency_conflicts(self) -> bool:
        """Check for dependency version conflicts."""
        success = True

        # Build reverse dependency map
        reverse_deps = {}
        for pkg_name, pkg_info in self.dependency_graph.items():
            for req in pkg_info['requires']:
                req_name = req.split()[0]  # Get package name from requirement string
                if req_name not in reverse_deps:
                    reverse_deps[req_name] = []
                reverse_deps[req_name].append(pkg_name)

        # Check for multiple versions of same package
        package_versions = {}
        for pkg_name, pkg_info in self.dependency_graph.items():
            if pkg_name not in package_versions:
                package_versions[pkg_name] = []
            package_versions[pkg_name].append(pkg_info['version'])

        for pkg_name, versions in package_versions.items():
            if len(set(versions)) > 1:
                success &= self.verify(
                    False, True,
                    f"Version conflict for {pkg_name}: {versions}",
                    test_num=3
                )

        return success

    def analyze_dependency_tree(self) -> bool:
        """Analyze the dependency tree structure."""
        success = True

        try:
            # Calculate dependency depth
            max_depth = self._calculate_max_dependency_depth()
            success &= self.verify_lt(
                max_depth, 10,  # Reasonable limit
                f"Dependency tree depth: {max_depth}",
                test_num=4
            )

            # Check for circular dependencies
            circular_deps = self._detect_circular_dependencies()
            if circular_deps:
                success &= self.verify(
                    False, True,
                    f"Circular dependencies detected: {circular_deps}",
                    test_num=4
                )
            else:
                success &= self.verify(
                    True, True,
                    "No circular dependencies detected",
                    test_num=4
                )

        except Exception as e:
            success &= self.verify(
                False, True,
                f"Dependency tree analysis failed: {str(e)}",
                test_num=4
            )

        return success

    def _calculate_max_dependency_depth(self) -> int:
        """Calculate maximum depth of dependency tree."""
        max_depth = 0

        def get_depth(pkg_name: str, visited: Set[str] = None) -> int:
            if visited is None:
                visited = set()

            if pkg_name in visited:
                return 0  # Circular dependency, return 0 to avoid infinite recursion

            visited.add(pkg_name)

            if pkg_name not in self.dependency_graph:
                return 1

            pkg_info = self.dependency_graph[pkg_name]
            if not pkg_info['requires']:
                return 1

            max_child_depth = 0
            for req in pkg_info['requires']:
                req_name = req.split()[0]
                child_depth = get_depth(req_name, visited.copy())
                max_child_depth = max(max_child_depth, child_depth)

            return 1 + max_child_depth

        for pkg_name in self.dependency_graph.keys():
            depth = get_depth(pkg_name)
            max_depth = max(max_depth, depth)

        return max_depth

    def _detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the dependency graph."""
        circular_deps = []

        def dfs(pkg_name: str, path: List[str], visited: Set[str]):
            if pkg_name in path:
                # Found circular dependency
                cycle_start = path.index(pkg_name)
                circular_deps.append(path[cycle_start:] + [pkg_name])
                return

            if pkg_name in visited:
                return

            visited.add(pkg_name)
            path.append(pkg_name)

            if pkg_name in self.dependency_graph:
                pkg_info = self.dependency_graph[pkg_name]
                for req in pkg_info['requires']:
                    req_name = req.split()[0]
                    dfs(req_name, path.copy(), visited.copy())

            path.pop()

        visited = set()
        for pkg_name in self.dependency_graph.keys():
            if pkg_name not in visited:
                dfs(pkg_name, [], visited)

        return circular_deps

    def generate_sbom(self, output_file: str = "sbom.json") -> bool:
        """Generate Software Bill of Materials (SBOM)."""
        success = True

        try:
            # Build SBOM data
            sbom = {
                'bomFormat': 'CycloneDX',
                'specVersion': '1.4',
                'version': 1,
                'metadata': {
                    'timestamp': self._get_iso_timestamp(),
                    'tools': [{
                        'vendor': 'Honeywell',
                        'name': 'Ngapy Test Harness',
                        'version': '1.0.0'
                    }],
                    'component': {
                        'type': 'application',
                        'name': 'ngapy',
                        'version': self._get_ngapy_version(),
                        'description': 'NGA Python testing framework'
                    }
                },
                'components': []
            }

            # Add components from dependency graph
            for pkg_name, pkg_info in self.dependency_graph.items():
                component = {
                    'type': 'library',
                    'name': pkg_name,
                    'version': pkg_info['version'],
                    'purl': f"pkg:pypi/{pkg_name}@{pkg_info['version']}",
                    'properties': [
                        {
                            'name': 'location',
                            'value': pkg_info['location']
                        }
                    ]
                }

                # Add license if available
                if pkg_info['metadata'].get('license') and pkg_info['metadata']['license'] != 'Unknown':
                    component['licenses'] = [{
                        'license': {
                            'name': pkg_info['metadata']['license']
                        }
                    }]

                # Add integrity hash if available
                if 'integrity_hash' in pkg_info:
                    component['hashes'] = [{
                        'alg': 'SHA-256',
                        'content': pkg_info['integrity_hash']
                    }]

                sbom['components'].append(component)

            # Write SBOM to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(sbom, f, indent=2, ensure_ascii=False)

            self.sbom_data = sbom

            success &= self.verify(
                os.path.exists(output_file), True,
                f"SBOM generated successfully: {output_file}",
                test_num=5
            )

        except Exception as e:
            success &= self.verify(
                False, True,
                f"SBOM generation failed: {str(e)}",
                test_num=5
            )

        return success

    def _get_iso_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

    def _get_ngapy_version(self) -> str:
        """Get ngapy version."""
        try:
            # Try to get version from package
            return pkg_resources.get_distribution('ngapy').version
        except:
            return '1.0.0'  # Default version

    def validate_sbom(self) -> bool:
        """Validate the generated SBOM."""
        success = True

        if not self.sbom_data:
            success &= self.verify(
                False, True,
                "No SBOM data available for validation",
                test_num=6
            )
            return success

        # Validate SBOM structure
        required_fields = ['bomFormat', 'specVersion', 'version', 'metadata', 'components']
        for field in required_fields:
            if field not in self.sbom_data:
                success &= self.verify(
                    False, True,
                    f"SBOM missing required field: {field}",
                    test_num=6
                )

        # Validate components
        if 'components' in self.sbom_data:
            for i, component in enumerate(self.sbom_data['components']):
                required_comp_fields = ['type', 'name', 'version']
                for field in required_comp_fields:
                    if field not in component:
                        success &= self.verify(
                            False, True,
                            f"Component {i} missing required field: {field}",
                            test_num=6
                        )

        # Check component count
        component_count = len(self.sbom_data.get('components', []))
        success &= self.verify_gt(
            component_count, 0,
            f"SBOM contains {component_count} components",
            test_num=6
        )

        return success

    def run_dependency_analysis(self) -> bool:
        """Run complete dependency analysis and SBOM generation."""
        print("Running Dependency Analysis and SBOM Generation...")

        results = []

        results.append(("Package Dependencies", self.analyze_package_dependencies()))
        results.append(("Dependency Integrity", self.validate_dependency_integrity()))
        results.append(("Dependency Conflicts", self.check_dependency_conflicts()))
        results.append(("Dependency Tree", self.analyze_dependency_tree()))
        results.append(("SBOM Generation", self.generate_sbom()))
        results.append(("SBOM Validation", self.validate_sbom()))

        print("\nDependency Analysis Results:")
        all_passed = True
        for test_name, passed in results:
            status = "PASS" if passed else "FAIL"
            print(f"  {test_name}: {status}")
            all_passed &= passed

        return all_passed


def run_dependency_analysis():
    """Main function to run dependency analysis."""
    harness = DependencyAnalysisHarness()
    success = harness.run_dependency_analysis()

    print(f"\nOverall Dependency Analysis: {'PASS' if success else 'FAIL'}")
    return success


if __name__ == "__main__":
    success = run_dependency_analysis()
    sys.exit(0 if success else 1)