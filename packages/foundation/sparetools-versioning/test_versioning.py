"""
Comprehensive test suite for SpareTools versioning utilities.

Tests all edge cases and scenarios for git-based versioning.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import modules to test
try:
    from sparetools_versioning.git.git_handler import GitHandler, get_repository_sha
    from sparetools_versioning.conan.conan_versioning import (
        get_package_name_version,
        python_version_sort,
        ConanVersionManager,
    )
    from sparetools_versioning.versioning.git_to_conan_collector import (
        GitToConanCollector,
        get_tags,
        get_branches,
        get_branches_remote,
        Options,
    )
except ImportError:
    # Fallback for testing without package installed
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from git.git_handler import GitHandler, get_repository_sha
    from conan.conan_versioning import (
        get_package_name_version,
        python_version_sort,
        ConanVersionManager,
    )
    from versioning.git_to_conan_collector import (
        GitToConanCollector,
        get_tags,
        get_branches,
        get_branches_remote,
        Options,
    )


class TestGitHandler(unittest.TestCase):
    """Test GitHandler class."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.git_path = Path(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_repository_sha_nonexistent(self):
        """Test getting SHA from non-existent repository."""
        result = get_repository_sha(str(self.git_path))
        self.assertIsNone(result)

    @patch('sparetools_versioning.git.git_handler.HAS_GITPYTHON', False)
    def test_git_handler_without_gitpython(self):
        """Test GitHandler when GitPython is not available."""
        handler = GitHandler()
        handler.open_repository(str(self.git_path))
        # Should not raise exception, just log warning


class TestConanVersioning(unittest.TestCase):
    """Test Conan versioning utilities."""

    def test_get_package_name_version_with_provides(self):
        """Test extracting name/version from package with provides."""
        package = Mock()
        package.display_name = "my-package/1.2.3@user/channel"
        package.provides = ["my-package"]
        
        name, version = get_package_name_version(package)
        self.assertEqual(name, "my-package")
        self.assertEqual(version, "1.2.3@user/channel")

    def test_get_package_name_version_without_provides(self):
        """Test extracting name/version from package without provides."""
        package = Mock()
        package.display_name = "my-package/1.2.3"
        package.provides = []
        
        name, version = get_package_name_version(package)
        self.assertEqual(name, "my-package")
        self.assertEqual(version, "1.2.3")

    def test_python_version_sort_basic(self):
        """Test version sorting with basic versions."""
        versions = ["1.0.0", "2.0.0", "1.1.0", "1.0.1"]
        sorted_versions = sorted(versions, key=python_version_sort)
        self.assertEqual(sorted_versions, ["1.0.0", "1.0.1", "1.1.0", "2.0.0"])

    def test_python_version_sort_with_dev(self):
        """Test version sorting with +dev suffix."""
        versions = ["3.10.6", "3.10.6+dev1", "3.10.7"]
        sorted_versions = sorted(versions, key=python_version_sort)
        # +dev should be treated as higher than base version
        self.assertEqual(sorted_versions[0], "3.10.6")
        self.assertIn("3.10.6+dev1", sorted_versions)

    def test_conan_version_manager_track_package(self):
        """Test tracking package usage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConanVersionManager(conan_home=temp_dir)
            manager.track_package("my-package", "1.0.0")
            
            tracked = manager.get_tracked_packages()
            self.assertIn("my-package/1.0.0", tracked)


class TestGitToConanCollector(unittest.TestCase):
    """Test Git-to-Conan collector."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.git_path = Path(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_options_creation(self):
        """Test Options class creation."""
        options = Options()
        self.assertEqual(options.git_path, '')
        self.assertEqual(options.package_name, '')
        self.assertFalse(options.parse_tags)

    @patch('sparetools_versioning.versioning.git_to_conan_collector.execute_command')
    def test_get_tags_success(self, mock_execute):
        """Test getting tags successfully."""
        mock_execute.return_value = (0, ["v1.0.0", "v1.1.0", "v2.0.0"])
        
        rc, tags = get_tags(str(self.git_path))
        self.assertEqual(rc, 0)
        self.assertEqual(len(tags), 3)
        self.assertIn("v1.0.0", tags)

    @patch('sparetools_versioning.versioning.git_to_conan_collector.execute_command')
    def test_get_tags_failure(self, mock_execute):
        """Test getting tags with failure."""
        mock_execute.return_value = (1, ["error: not a git repository"])
        
        rc, tags = get_tags(str(self.git_path))
        self.assertEqual(rc, 1)

    @patch('sparetools_versioning.versioning.git_to_conan_collector.execute_command')
    def test_get_branches_success(self, mock_execute):
        """Test getting branches successfully."""
        mock_execute.return_value = (0, ["  main", "  develop", "* feature/new"])
        
        rc, branches = get_branches(str(self.git_path))
        self.assertEqual(rc, 0)
        # Should filter out current branch marker
        self.assertGreater(len(branches), 0)

    def test_collector_initialization(self):
        """Test collector initialization."""
        options = Options()
        collector = GitToConanCollector(options)
        self.assertIsNotNone(collector.version_manager)


class TestVersioningEdgeCases(unittest.TestCase):
    """Test edge cases and error scenarios."""

    def test_version_sort_empty_string(self):
        """Test sorting empty version string."""
        result = python_version_sort("")
        self.assertEqual(result, 0)

    def test_version_sort_non_numeric(self):
        """Test sorting version with non-numeric parts."""
        result = python_version_sort("1.0.0-alpha")
        # Should not raise exception
        self.assertIsInstance(result, int)

    def test_get_package_name_version_dict(self):
        """Test extracting from dict-like object."""
        package = {"reference": "my-package/1.0.0"}
        name, version = get_package_name_version(package)
        self.assertEqual(name, "my-package")
        self.assertEqual(version, "1.0.0")

    def test_get_package_name_version_unknown(self):
        """Test extracting from unknown object type."""
        package = object()
        name, version = get_package_name_version(package)
        self.assertEqual(name, "unknown")
        self.assertEqual(version, "unknown")

    @patch('sparetools_versioning.conan.conan_versioning.get_conan_home')
    def test_version_manager_no_conan_home(self, mock_home):
        """Test version manager when Conan home is not available."""
        mock_home.return_value = None
        manager = ConanVersionManager()
        # Should use default fallback
        self.assertIsNotNone(manager.conan_home)


class TestConanfileVersioningPattern(unittest.TestCase):
    """Test conanfile.py versioning pattern validation."""

    def test_pattern_matching(self):
        """Test that version pattern matches expected format."""
        import re
        
        # Valid patterns
        valid_patterns = [
            'version = os.environ.get(\'CONAN_BUILD_VERSION\', \'1.0.0\')',
            'version = os.environ.get("CONAN_BUILD_VERSION", "1.0.0")',
            'version=os.environ.get(\'CONAN_BUILD_VERSION\',\'1.0.0\')',
        ]
        
        pattern = r'version\s*=\s*os\.environ\.get\([\'"]CONAN_BUILD_VERSION[\'"]'
        
        for valid in valid_patterns:
            self.assertTrue(re.search(pattern, valid), f"Pattern should match: {valid}")

    def test_pattern_not_matching_static(self):
        """Test that static version pattern does not match."""
        import re
        
        invalid_patterns = [
            'version = "1.0.0"',
            'version = \'1.0.0\'',
            'version = 1.0.0',
        ]
        
        pattern = r'version\s*=\s*os\.environ\.get\([\'"]CONAN_BUILD_VERSION[\'"]'
        
        for invalid in invalid_patterns:
            self.assertFalse(re.search(pattern, invalid), f"Pattern should not match: {invalid}")


if __name__ == '__main__':
    unittest.main()
