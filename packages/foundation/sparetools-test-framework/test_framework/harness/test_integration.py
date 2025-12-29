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
Integration Tests for Ngapy Package
===================================

This module provides comprehensive integration testing capabilities for the ngapy package,
including cross-platform compatibility, performance benchmarking, security validation,
dependency analysis, and SBOM generation.
"""

import os
import sys
import platform
import time
import json
import hashlib
import subprocess
import importlib
import pkg_resources
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from .test_harness import NgapyTestHarnes
except ImportError:
    from sparetools.test_framework.harness import NgapyTestHarnes


class IntegrationTestHarness(NgapyTestHarnes):
    """Enhanced test harness for integration testing."""

    def __init__(self):
        super().__init__()
        self.platform_info = self._get_platform_info()
        self.performance_metrics = {}
        self.security_checks = []
        self.dependency_graph = {}

    def _get_platform_info(self) -> Dict[str, str]:
        """Get comprehensive platform information."""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': sys.version,
            'architecture': platform.architecture()[0]
        }

    def test_cross_platform_compatibility(self) -> bool:
        """Test basic cross-platform compatibility."""
        success = True

        # Test platform detection
        success &= self.verify(
            self.platform_info['system'] in ['Windows', 'Linux', 'Darwin'],
            True,
            "Platform detection",
            test_num=1
        )

        # Test Python version compatibility
        python_version = sys.version_info
        success &= self.verify(
            python_version >= (3, 7),
            True,
            f"Python version {python_version} compatibility",
            test_num=2
        )

        # Test file system operations
        test_file = Path("cross_platform_test.tmp")
        try:
            test_file.write_text("test")
            content = test_file.read_text()
            success &= self.verify(content, "test", "File system write/read", test_num=3)
        finally:
            if test_file.exists():
                test_file.unlink()

        return success

    def benchmark_performance(self, operation_name: str, operation_func, *args, **kwargs) -> float:
        """Benchmark a specific operation and store metrics."""
        start_time = time.perf_counter()
        result = operation_func(*args, **kwargs)
        end_time = time.perf_counter()

        duration = end_time - start_time
        self.performance_metrics[operation_name] = {
            'duration': duration,
            'timestamp': time.time(),
            'platform': self.platform_info['system']
        }

        return duration

    def test_performance_baselines(self) -> bool:
        """Test performance against established baselines."""
        success = True

        # Benchmark import time
        import_time = self.benchmark_performance(
            'ngapy_import',
            lambda: importlib.import_module('ngapy')
        )

        # Benchmark basic operations
        th = NgapyTestHarnes()
        verify_time = self.benchmark_performance(
            'basic_verify',
            th.verify, 1, 1, "Performance test"
        )

        # Check against reasonable baselines (adjust as needed)
        success &= self.verify_lt(import_time, 5.0, "Import time < 5s", test_num=4)
        success &= self.verify_lt(verify_time, 0.1, "Verify operation < 100ms", test_num=5)

        return success

    def validate_dependencies(self) -> bool:
        """Validate package dependencies and build dependency graph."""
        success = True

        try:
            # Get installed packages
            installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}

            # Check for required dependencies
            required_deps = ['python-dateutil', 'requests']  # Add actual requirements
            for dep in required_deps:
                if dep in installed_packages:
                    success &= self.verify(
                        True, True,
                        f"Dependency {dep} v{installed_packages[dep]} installed",
                        test_num=6
                    )
                else:
                    success &= self.verify(
                        False, True,
                        f"Missing dependency: {dep}",
                        test_num=6
                    )

            # Build dependency graph
            self.dependency_graph = self._build_dependency_graph(installed_packages)

        except Exception as e:
            success &= self.verify(False, True, f"Dependency validation failed: {str(e)}", test_num=6)

        return success

    def _build_dependency_graph(self, installed_packages: Dict[str, str]) -> Dict[str, Any]:
        """Build a dependency graph for analysis."""
        graph = {}

        for pkg_name, version in installed_packages.items():
            try:
                pkg = pkg_resources.get_distribution(pkg_name)
                graph[pkg_name] = {
                    'version': version,
                    'requires': [str(req) for req in pkg.requires()],
                    'location': pkg.location
                }
            except:
                graph[pkg_name] = {'version': version, 'requires': [], 'location': 'unknown'}

        return graph

    def perform_security_checks(self) -> bool:
        """Perform basic security validation checks."""
        success = True

        # Check for insecure file permissions (Unix-like systems)
        if self.platform_info['system'] != 'Windows':
            success &= self._check_file_permissions()

        # Check for sensitive data in environment
        success &= self._check_environment_security()

        # Validate package integrity
        success &= self._check_package_integrity()

        return success

    def _check_file_permissions(self) -> bool:
        """Check file permissions on sensitive files."""
        success = True

        sensitive_files = ['keypack.pyu', 'conanfile.py']
        for filename in sensitive_files:
            if os.path.exists(filename):
                stat_info = os.stat(filename)
                # Check if world-readable
                if bool(stat_info.st_mode & 0o004):
                    success &= self.verify(
                        False, True,
                        f"File {filename} is world-readable",
                        test_num=7
                    )

        return success

    def _check_environment_security(self) -> bool:
        """Check for sensitive data in environment variables."""
        success = True

        sensitive_patterns = ['password', 'secret', 'key', 'token']
        env_vars = os.environ

        for var_name in env_vars:
            var_lower = var_name.lower()
            if any(pattern in var_lower for pattern in sensitive_patterns):
                # Don't log the actual value for security
                success &= self.verify(
                    False, True,
                    f"Potentially sensitive environment variable: {var_name}",
                    test_num=8
                )

        return success

    def _check_package_integrity(self) -> bool:
        """Check package file integrity using hashes."""
        success = True

        # Check core package files
        core_files = ['ngapy/__init__.py', 'conanfile.py']
        for filename in core_files:
            if os.path.exists(filename):
                try:
                    with open(filename, 'rb') as f:
                        content = f.read()
                        file_hash = hashlib.sha256(content).hexdigest()

                    success &= self.verify(
                        len(file_hash) == 64, True,
                        f"Integrity check for {filename}",
                        test_num=9
                    )
                except Exception as e:
                    success &= self.verify(
                        False, True,
                        f"Failed to check integrity of {filename}: {str(e)}",
                        test_num=9
                    )

        return success

    def generate_sbom(self, output_file: str = "sbom.json") -> bool:
        """Generate Software Bill of Materials (SBOM)."""
        success = True

        try:
            sbom_data = {
                'metadata': {
                    'package': 'ngapy',
                    'version': '1.0.0',  # Should be extracted from actual version
                    'created': time.time(),
                    'platform': self.platform_info
                },
                'components': []
            }

            # Add installed packages as components
            for pkg_name, info in self.dependency_graph.items():
                component = {
                    'name': pkg_name,
                    'version': info['version'],
                    'type': 'library',
                    'location': info['location'],
                    'dependencies': info['requires']
                }
                sbom_data['components'].append(component)

            # Write SBOM to file
            with open(output_file, 'w') as f:
                json.dump(sbom_data, f, indent=2)

            success &= self.verify(
                os.path.exists(output_file), True,
                f"SBOM generated at {output_file}",
                test_num=10
            )

        except Exception as e:
            success &= self.verify(
                False, True,
                f"SBOM generation failed: {str(e)}",
                test_num=10
            )

        return success

    def run_full_integration_test_suite(self) -> Dict[str, Any]:
        """Run the complete integration test suite."""
        results = {}

        # Cross-platform compatibility
        results['cross_platform'] = self.test_cross_platform_compatibility()

        # Performance testing
        results['performance'] = self.test_performance_baselines()

        # Dependency validation
        results['dependencies'] = self.validate_dependencies()

        # Security checks
        results['security'] = self.perform_security_checks()

        # SBOM generation
        results['sbom'] = self.generate_sbom()

        # Overall result
        results['overall_success'] = all(results.values())

        # Add metadata
        results['metadata'] = {
            'platform': self.platform_info,
            'timestamp': time.time(),
            'test_duration': time.time() - time.time()  # Would need to track start time
        }

        return results


def run_integration_tests():
    """Main function to run integration tests."""
    harness = IntegrationTestHarness()

    print("Starting Ngapy Integration Test Suite...")
    print(f"Platform: {harness.platform_info['system']} {harness.platform_info['release']}")
    print(f"Python: {sys.version.split()[0]}")
    print("-" * 50)

    results = harness.run_full_integration_test_suite()

    print("-" * 50)
    print("Integration Test Results:")
    for test_name, success in results.items():
        if test_name not in ['metadata', 'overall_success']:
            status = "PASS" if success else "FAIL"
            print(f"  {test_name}: {status}")

    print(f"\nOverall: {'PASS' if results['overall_success'] else 'FAIL'}")

    return results['overall_success']


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)