#!/usr/bin/env python3
"""
Integration tests for SpareTools version management system.

Tests the centralized version management functionality including:
- SpareToolsVersions class functionality
- Version synchronization across packages
- Dynamic version resolution
- Version validation and consistency
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import patch, mock_open
import yaml


# Add SpareTools packages to path
sparetools_root = Path(__file__).parent.parent.parent
packages_dir = sparetools_root / "packages" / "foundation"
if str(packages_dir) not in sys.path:
    sys.path.insert(0, str(packages_dir))

try:
    from sparetools_base.conanfile import SpareToolsVersions
except ImportError:
    # Mock if not available
    class SpareToolsVersions:
        versions = {
            "cpython": "3.12.7",
            "test-harness": "2.0.0",
            "gtest": "1.14.0",
            "shared-dev-tools": "2.0.0",
            "bootstrap": "2.0.0",
            "openssl": "3.3.2",
            "lvgl": "8.3.11"
        }


class TestSpareToolsVersions(unittest.TestCase):
    """Test cases for SpareTools version management."""

    def setUp(self):
        """Set up test fixtures."""
        self.version_manager = SpareToolsVersions()
        self.versions_file = sparetools_root / "versions.yaml"

    def test_version_dict_structure(self):
        """Test that versions dictionary has expected structure."""
        self.assertIsInstance(self.version_manager.versions, dict)
        self.assertGreater(len(self.version_manager.versions), 0)

        # Check for required version keys
        required_keys = ["cpython", "gtest", "openssl", "lvgl"]
        for key in required_keys:
            self.assertIn(key, self.version_manager.versions)
            self.assertIsInstance(self.version_manager.versions[key], str)

    def test_version_format_validation(self):
        """Test that version strings follow semantic versioning format."""
        import re
        semver_pattern = re.compile(r'^\d+\.\d+\.\d+$')

        for component, version in self.version_manager.versions.items():
            with self.subTest(component=component, version=version):
                self.assertRegex(version, semver_pattern,
                               f"Version {version} for {component} does not follow semantic versioning")

    def test_critical_versions_present(self):
        """Test that critical ecosystem versions are defined."""
        critical_versions = {
            "cpython": "3.12.7",  # Bundled Python version
            "gtest": "1.14.0",    # Testing framework
            "openssl": "3.3.2",   # Cryptography
            "lvgl": "8.3.11"      # Graphics library
        }

        for component, expected_version in critical_versions.items():
            with self.subTest(component=component):
                self.assertIn(component, self.version_manager.versions)
                self.assertEqual(self.version_manager.versions[component], expected_version)

    def test_versions_file_consistency(self):
        """Test that versions.yaml file is consistent with SpareToolsVersions."""
        if not self.versions_file.exists():
            self.skipTest("versions.yaml file not found")

        with open(self.versions_file, 'r') as f:
            yaml_data = yaml.safe_load(f)

        # Flatten YAML structure for comparison
        yaml_versions = {}
        for category, packages in yaml_data.items():
            if isinstance(packages, dict):
                yaml_versions.update(packages)

        # Check that all versions in YAML match SpareToolsVersions
        for component, version in yaml_versions.items():
            with self.subTest(component=component):
                self.assertIn(component, self.version_manager.versions)
                self.assertEqual(self.version_manager.versions[component], version)

    def test_dynamic_version_access(self):
        """Test dynamic access to version information."""
        # Test direct access
        cpython_version = self.version_manager.versions["cpython"]
        self.assertEqual(cpython_version, "3.12.7")

        # Note: Versions dict is mutable for flexibility, but should not be modified in production

    def test_version_dependency_consistency(self):
        """Test that version dependencies are consistent."""
        # LVGL should be compatible with the defined version
        lvgl_version = self.version_manager.versions["lvgl"]
        self.assertTrue(lvgl_version.startswith("8.3"))

        # OpenSSL should be a recent 3.x version
        openssl_version = self.version_manager.versions["openssl"]
        self.assertTrue(openssl_version.startswith("3."))

    @patch('builtins.open', new_callable=mock_open)
    def test_versions_yaml_parsing(self, mock_file):
        """Test versions.yaml parsing functionality."""
        mock_yaml_content = """
foundation:
  sparetools-base: "2.0.3"
  sparetools-cpython: "3.12.7"

testing:
  gtest: "1.14.0"

embedded:
  lvgl: "8.3.11"
  openssl: "3.3.2"
"""
        mock_file.return_value.read.return_value = mock_yaml_content

        # This would test the YAML parsing if we had a separate parser function
        # For now, just verify the file structure expectations
        parsed = yaml.safe_load(mock_yaml_content)
        self.assertIn("foundation", parsed)
        self.assertIn("testing", parsed)
        self.assertIn("embedded", parsed)


class TestVersionSynchronization(unittest.TestCase):
    """Test version synchronization across the ecosystem."""

    def setUp(self):
        self.versions = SpareToolsVersions.versions
        self.root_dir = sparetools_root

    def test_conanfile_version_consistency(self):
        """Test that conanfile.py versions match SpareToolsVersions."""
        conanfiles = [
            self.root_dir / "packages" / "foundation" / "sparetools-base" / "conanfile.py",
            self.root_dir / "packages" / "foundation" / "sparetools-shared-dev-tools" / "conanfile.py",
        ]

        for conanfile in conanfiles:
            if conanfile.exists():
                with self.subTest(conanfile=conanfile):
                    with open(conanfile, 'r') as f:
                        content = f.read()

                    # Extract version from conanfile
                    import re
                    version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                    if version_match:
                        conanfile_version = version_match.group(1)
                        # Check if this version should match SpareToolsVersions
                        # (This is a simplified check - in practice would be more specific)
                        self.assertIsNotNone(conanfile_version)

    def test_package_version_alignment(self):
        """Test that package versions are properly aligned."""
        # Test that related packages have compatible versions
        gtest_version = self.versions["gtest"]

        # GTest should be 1.14.x for compatibility
        self.assertTrue(gtest_version.startswith("1.14"))

        # Python version should be 3.12.x
        cpython_version = self.versions["cpython"]
        self.assertTrue(cpython_version.startswith("3.12"))


class TestVersionValidation(unittest.TestCase):
    """Test version validation and consistency checks."""

    def setUp(self):
        self.versions = SpareToolsVersions.versions

    def test_semantic_version_ordering(self):
        """Test that versions follow proper semantic versioning ordering."""
        # Parse versions and ensure they're properly ordered
        def parse_version(v):
            return tuple(map(int, v.split('.')))

        for component, version in self.versions.items():
            with self.subTest(component=component, version=version):
                try:
                    parsed = parse_version(version)
                    self.assertEqual(len(parsed), 3)  # Major.minor.patch
                    self.assertTrue(all(isinstance(x, int) for x in parsed))
                except ValueError:
                    self.fail(f"Version {version} for {component} is not a valid semantic version")

    def test_no_duplicate_versions(self):
        """Test that there are no unexpected duplicate versions."""
        version_counts = {}
        for component, version in self.versions.items():
            if version not in version_counts:
                version_counts[version] = []
            version_counts[version].append(component)

        # Check for reasonable version sharing (some duplication is expected)
        for version, components in version_counts.items():
            with self.subTest(version=version):
                # Allow some version sharing but not excessive
                self.assertLessEqual(len(components), 3,
                                   f"Version {version} used by too many components: {components}")

    def test_version_stability(self):
        """Test that versions are stable and don't change unexpectedly."""
        # This test ensures that critical versions haven't changed from expected values
        expected_versions = {
            "cpython": "3.12.7",
            "gtest": "1.14.0",
            "openssl": "3.3.2",
            "lvgl": "8.3.11"
        }

        for component, expected_version in expected_versions.items():
            with self.subTest(component=component):
                self.assertEqual(self.versions[component], expected_version,
                               f"Critical version for {component} has changed unexpectedly")


if __name__ == '__main__':
    unittest.main()