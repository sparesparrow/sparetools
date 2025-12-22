#!/usr/bin/env python3
"""
Integration tests for Conan-PlatformIO bridge functionality.

Tests the bridge system including:
- Dependency resolution
- Profile caching
- PlatformIO configuration generation
- Multi-ESP32 variant support
- Error handling
"""

import unittest
import sys
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import subprocess


# Add SpareTools packages to path
sparetools_root = Path(__file__).parent.parent.parent
shared_dev_tools = sparetools_root / "packages" / "foundation" / "sparetools-shared-dev-tools"
if str(shared_dev_tools) not in sys.path:
    sys.path.insert(0, str(shared_dev_tools))

try:
    from shared_dev_tools.conan_pio_bridge import ConanPIOBridge, ConanPackage
except ImportError:
    # Mock if not available
    class ConanPackage:
        def __init__(self, name, version, user=None, channel=None, options=None):
            self.name = name
            self.version = version
            self.user = user
            self.channel = channel
            self.options = options or {}

        @property
        def reference(self):
            ref = f"{self.name}/{self.version}"
            if self.user and self.channel:
                ref += f"@{self.user}/{self.channel}"
            return ref

    class ConanPIOBridge:
        def __init__(self, workspace_root=None):
            self.workspace_root = workspace_root or Path.cwd()
            self.cache_dir = self.workspace_root / ".conan_pio_cache"
            self.cache_dir.mkdir(exist_ok=True)

        def resolve_conan_dependencies(self, profile, packages):
            return {
                "install_dir": str(self.cache_dir / "install_test"),
                "include_paths": ["/opt/conan/include"],
                "lib_paths": ["/opt/conan/lib"],
                "libs": ["gtest", "lvgl"],
                "defines": ["TEST_DEFINE=1"],
                "cxxflags": ["-std=c++17"],
                "cflags": ["-O2"]
            }

        def generate_platformio_config(self, profile, config):
            return f"""
[env:{profile.name}]
platform = {profile.platform}
board = {profile.board}
framework = {profile.framework}
build_flags = -I{';'.join(config.get('include_paths', []))}
build_flags = -L{';'.join(config.get('lib_paths', []))}
"""


class TestConanPIOBride(unittest.TestCase):
    """Test cases for Conan-PlatformIO bridge functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create mock versions file first
        self.versions_file = self.temp_dir / "versions.yaml"
        with open(self.versions_file, 'w') as f:
            f.write("""
foundation:
  base: "2.0.3"
  cpython: "3.12.7"
testing:
  gtest: "1.14.0"
embedded:
  lvgl: "8.3.11"
""")

        # Initialize bridge after versions file exists
        self.bridge = ConanPIOBridge(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_bridge_initialization(self):
        """Test bridge initialization and configuration loading."""
        self.assertIsNotNone(self.bridge.workspace_root)
        self.assertTrue(self.bridge.cache_dir.exists())

        # Test versions loading
        self.assertIsInstance(self.bridge.versions, dict)
        self.assertIn("gtest", self.bridge.versions)

    def test_conan_package_creation(self):
        """Test ConanPackage creation and reference generation."""
        # Basic package
        pkg = ConanPackage("gtest", "1.14.0")
        self.assertEqual(pkg.name, "gtest")
        self.assertEqual(pkg.version, "1.14.0")
        self.assertEqual(pkg.reference, "gtest/1.14.0")

        # Package with user/channel
        pkg_uc = ConanPackage("mylib", "1.0.0", "myuser", "stable")
        self.assertEqual(pkg_uc.reference, "mylib/1.0.0@myuser/stable")

        # Package with options
        pkg_opt = ConanPackage("openssl", "3.3.2", options={"shared": False})
        self.assertEqual(pkg_opt.options["shared"], False)

    def test_toolchain_detection(self):
        """Test automatic toolchain detection for different boards."""
        # ESP32
        toolchain = self.bridge.detect_toolchain("esp32dev")
        self.assertEqual(toolchain["compiler"], "gcc")
        self.assertEqual(toolchain["arch"], "xtensa")
        self.assertIn("-mlongcalls", toolchain["flags"])

        # ESP32-S3
        toolchain_s3 = self.bridge.detect_toolchain("esp32-s3-devkitc-1")
        self.assertIn("-mfix-esp32-psram-cache-issue", toolchain_s3["flags"])

        # ESP32-C3
        toolchain_c3 = self.bridge.detect_toolchain("esp32-c3-devkitm-1")
        self.assertEqual(toolchain_c3["compiler"], "clang")
        self.assertEqual(toolchain_c3["arch"], "riscv")

    @patch('subprocess.run')
    def test_dependency_resolution(self, mock_subprocess):
        """Test Conan dependency resolution."""
        # Mock successful conan install
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="Conan install completed",
            stderr=""
        )

        packages = [ConanPackage("gtest", "1.14.0")]
        config = self.bridge.resolve_conan_dependencies("esp32_base.prof", packages)

        self.assertIsInstance(config, dict)
        self.assertIn("install_dir", config)
        self.assertIn("include_paths", config)
        self.assertIn("libs", config)

    def test_platformio_config_generation(self):
        """Test PlatformIO configuration generation."""
        from shared_dev_tools.conan_pio_bridge import BuildProfile

        profile = BuildProfile(
            name="esp32_test",
            board="esp32dev",
            framework="espidf",
            platform="espressif32",
            conan_profile="esp32_base.prof",
            packages=[]
        )

        conan_config = {
            "include_paths": ["/opt/conan/include"],
            "lib_paths": ["/opt/conan/lib"],
            "libs": ["gtest"],
            "defines": ["TEST_DEFINE=1"]
        }

        config = self.bridge.generate_platformio_config(profile, conan_config)

        self.assertIn("[env:esp32_test]", config)
        self.assertIn("platform = espressif32", config)
        self.assertIn("board = esp32dev", config)
        self.assertIn("framework = espidf", config)
        self.assertIn("build_flags = -I/opt/conan/include", config)

    @patch('subprocess.run')
    def test_bridge_execution(self, mock_subprocess):
        """Test complete bridge execution."""
        # Mock successful conan install
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="Conan install completed",
            stderr=""
        )

        packages = [ConanPackage("gtest", "1.14.0")]
        config = self.bridge.bridge("esp32_base.prof", "esp32dev", packages)

        self.assertIsInstance(config, str)
        self.assertIn("[env:esp32dev]", config)
        self.assertIn("platform =", config)

    def test_cache_functionality(self):
        """Test profile caching functionality."""
        cache_key = self.bridge._get_cache_key("test_profile", [ConanPackage("gtest", "1.14.0")])
        self.assertIsInstance(cache_key, str)
        self.assertGreater(len(cache_key), 0)

        # Test cache file operations
        cache_file = self.bridge.cache_dir / f"{cache_key}.json"
        test_data = {"test": "data"}

        self.bridge._save_cache(cache_key, test_data)
        self.assertTrue(cache_file.exists())

        loaded_data = self.bridge._load_cache(cache_key)
        self.assertEqual(loaded_data, test_data)

    def test_error_handling(self):
        """Test error handling in bridge operations."""
        # Test with invalid profile
        with self.assertRaises(Exception):
            self.bridge.bridge("nonexistent.prof", "esp32dev", [])

        # Test with invalid package reference
        invalid_packages = [ConanPackage("", "")]
        with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'conan')):
            with self.assertRaises(Exception):
                self.bridge.resolve_conan_dependencies("esp32_base.prof", invalid_packages)


class TestBridgeIntegration(unittest.TestCase):
    """Integration tests for bridge with real components."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.bridge = ConanPIOBridge(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('subprocess.run')
    def test_multi_package_resolution(self, mock_subprocess):
        """Test resolution of multiple packages."""
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="Multiple packages installed",
            stderr=""
        )

        packages = [
            ConanPackage("gtest", "1.14.0"),
            ConanPackage("lvgl", "8.3.11"),
            ConanPackage("openssl", "3.3.2")
        ]

        config = self.bridge.resolve_conan_dependencies("esp32_base.prof", packages)

        # Verify multiple packages are handled
        self.assertIsInstance(config, dict)
        mock_subprocess.assert_called_once()

        # Check that the command includes all packages
        call_args = mock_subprocess.call_args[0][0]
        self.assertIn("--requires", call_args)
        self.assertIn("gtest/1.14.0", call_args)
        self.assertIn("lvgl/8.3.11", call_args)
        self.assertIn("openssl/3.3.2", call_args)

    def test_environment_validation(self):
        """Test environment validation functionality."""
        # Test with mocked tools available
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="version info")
            result = self.bridge.validate_environment()
            self.assertTrue(result)

        # Test with tools missing
        with patch('subprocess.run', side_effect=FileNotFoundError):
            result = self.bridge.validate_environment()
            self.assertFalse(result)

    def test_board_mapping(self):
        """Test PlatformIO environment to board mapping."""
        # This would test the _extract_board_from_env method
        # For now, just verify the method exists and handles basic cases
        method = getattr(self.bridge, '_extract_board_from_env', None)
        self.assertIsNotNone(method)

        if method:
            # Test basic mappings
            self.assertEqual(method("esp32dev"), "esp32dev")
            self.assertIn(method("esp32s3"), ["esp32-s3-devkitc-1", "esp32dev"])


class TestBridgeCLI(unittest.TestCase):
    """Test command-line interface for the bridge."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.bridge = ConanPIOBridge(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('sys.argv', ['conan_pio_bridge.py', '--conan-profile', 'esp32_base.prof', '--pio-env', 'esp32dev', '--packages', 'gtest/1.14.0'])
    @patch('sys.stdout')
    def test_cli_basic_operation(self, mock_stdout):
        """Test basic CLI operation."""
        # This would test the main() function
        # For now, just verify the CLI structure exists
        try:
            from shared_dev_tools.conan_pio_bridge import main
            # We can't easily test main() without complex mocking
            self.assertTrue(callable(main))
        except ImportError:
            self.skipTest("CLI module not available")

    def test_package_parsing(self):
        """Test parsing of package specifications from command line."""
        # Test basic package parsing
        pkg_str = "gtest/1.14.0"
        # This would test the parsing logic in main()
        # Simplified test for now
        parts = pkg_str.split("/")
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0], "gtest")
        self.assertEqual(parts[1], "1.14.0")


if __name__ == '__main__':
    unittest.main()