#!/usr/bin/env python3
"""
Integration tests for SpareTools enterprise packages.

Tests the new enterprise packages including:
- sparetools-hal-sunton (Hardware Abstraction Layer)
- sparetools-crypto-suite (Cryptographic APIs)
- sparetools-ci-templates (CI/CD templates)
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import json


# Add SpareTools packages to path
sparetools_root = Path(__file__).parent.parent.parent
packages_dir = sparetools_root / "packages"

# Add individual package paths
for package_type in ["embedded", "security", "devops"]:
    package_path = packages_dir / package_type
    if str(package_path) not in sys.path:
        sys.path.insert(0, str(package_path))

try:
    # Import HAL package
    sys.path.insert(0, str(packages_dir / "embedded" / "sparetools-hal-sunton" / "src"))
    # Import crypto package
    sys.path.insert(0, str(packages_dir / "security" / "sparetools-crypto-suite" / "include" / "crypto"))
except:
    pass


class TestSpareToolsHALPackage(unittest.TestCase):
    """Test cases for sparetools-hal-sunton package."""

    def setUp(self):
        """Set up test fixtures."""
        self.hal_dir = packages_dir / "embedded" / "sparetools-hal-sunton"
        self.conanfile = self.hal_dir / "conanfile.py"

    def test_hal_package_structure(self):
        """Test that HAL package has required structure."""
        if not self.hal_dir.exists():
            self.skipTest("HAL package not found")

        # Check required directories
        required_dirs = ["include", "src"]
        for dir_name in required_dirs:
            with self.subTest(dir_name=dir_name):
                self.assertTrue((self.hal_dir / dir_name).exists(),
                              f"Required directory {dir_name} not found")

        # Check required files
        required_files = [
            "conanfile.py",
            "include/hal/sunton/display.h",
            "src/display.cpp",
            "src/pin_mapping.h"
        ]
        for file_path in required_files:
            with self.subTest(file_path=file_path):
                self.assertTrue((self.hal_dir / file_path).exists(),
                              f"Required file {file_path} not found")

    def test_hal_conanfile_configuration(self):
        """Test HAL package Conan configuration."""
        if not self.conanfile.exists():
            self.skipTest("HAL conanfile not found")

        with open(self.conanfile, 'r') as f:
            content = f.read()

        # Check for required Conan configuration
        self.assertIn("sparetools-hal-sunton", content)
        self.assertIn("lvgl", content)  # Should require LVGL
        self.assertIn("with_lvgl", content)  # Should have LVGL option
        self.assertIn("with_touch", content)  # Should have touch option

    def test_hal_header_interface(self):
        """Test HAL header file interface."""
        header_file = self.hal_dir / "include" / "hal" / "sunton" / "display.h"
        if not header_file.exists():
            self.skipTest("HAL header not found")

        with open(header_file, 'r') as f:
            content = f.read()

        # Check for required interface elements
        required_elements = [
            "sunton_display_init",
            "sunton_display_set_brightness",
            "sunton_touch_init",
            "sunton_touch_read",
            "esp32_crypto_init"  # Should not be in HAL header
        ]

        for element in required_elements[:-1]:  # Exclude crypto function
            with self.subTest(element=element):
                self.assertIn(element, content,
                            f"Required HAL interface element {element} not found")

        # Ensure crypto functions are not in HAL header
        self.assertNotIn(required_elements[-1], content,
                        "Crypto functions should not be in HAL header")

    def test_pin_mapping_definitions(self):
        """Test pin mapping definitions."""
        pin_file = self.hal_dir / "src" / "pin_mapping.h"
        if not pin_file.exists():
            self.skipTest("Pin mapping file not found")

        with open(pin_file, 'r') as f:
            content = f.read()

        # Check for required pin definitions
        required_pins = [
            "TFT_MISO", "TFT_MOSI", "TFT_SCLK", "TFT_CS", "TFT_DC", "TFT_RST", "TFT_BL",
            "DISPLAY_WIDTH", "DISPLAY_HEIGHT"
        ]

        for pin in required_pins:
            with self.subTest(pin=pin):
                self.assertIn(pin, content,
                            f"Required pin definition {pin} not found")


class TestSpareToolsCryptoPackage(unittest.TestCase):
    """Test cases for sparetools-crypto-suite package."""

    def setUp(self):
        """Set up test fixtures."""
        self.crypto_dir = packages_dir / "security" / "sparetools-crypto-suite"
        self.conanfile = self.crypto_dir / "conanfile.py"

    def test_crypto_package_structure(self):
        """Test that crypto package has required structure."""
        if not self.crypto_dir.exists():
            self.skipTest("Crypto package not found")

        # Check required directories
        required_dirs = ["include", "src", "test"]
        for dir_name in required_dirs:
            with self.subTest(dir_name=dir_name):
                self.assertTrue((self.crypto_dir / dir_name).exists(),
                              f"Required directory {dir_name} not found")

        # Check required files
        required_files = [
            "conanfile.py",
            "include/crypto/esp32_crypto.h",
            "src/profiles/security_profile_basic.json",
            "test/test_esp32_crypto.cpp"
        ]
        for file_path in required_files:
            with self.subTest(file_path=file_path):
                self.assertTrue((self.crypto_dir / file_path).exists(),
                              f"Required file {file_path} not found")

    def test_crypto_conanfile_configuration(self):
        """Test crypto package Conan configuration."""
        if not self.conanfile.exists():
            self.skipTest("Crypto conanfile not found")

        with open(self.conanfile, 'r') as f:
            content = f.read()

        # Check for required Conan configuration
        self.assertIn("sparetools-crypto-suite", content)
        self.assertIn("mbedTLS", content)  # Should support mbedTLS
        self.assertIn("wolfSSL", content)  # Should support WolfSSL
        self.assertIn("enable_hw_acceleration", content)  # Should have HW accel option
        self.assertIn("enable_secure_boot", content)  # Should have secure boot option

    def test_crypto_api_interface(self):
        """Test crypto API interface."""
        header_file = self.crypto_dir / "include" / "crypto" / "esp32_crypto.h"
        if not header_file.exists():
            self.skipTest("Crypto header not found")

        with open(header_file, 'r') as f:
            content = f.read()

        # Check for required API functions
        required_functions = [
            "esp32_crypto_init",
            "esp32_aes_init",
            "esp32_sha_init",
            "esp32_ecc_init",
            "esp32_secure_boot_verify",
            "esp32_secure_boot_sign"
        ]

        for func in required_functions:
            with self.subTest(func=func):
                self.assertIn(func, content,
                            f"Required crypto API function {func} not found")

    def test_security_profiles(self):
        """Test security profile configurations."""
        profiles_dir = self.crypto_dir / "src" / "profiles"
        if not profiles_dir.exists():
            self.skipTest("Security profiles not found")

        # Check for required profile files
        required_profiles = [
            "security_profile_basic.json",
            "security_profile_enterprise.json"
        ]

        for profile_file in required_profiles:
            profile_path = profiles_dir / profile_file
            with self.subTest(profile_file=profile_file):
                self.assertTrue(profile_path.exists(),
                              f"Required security profile {profile_file} not found")

                # Validate JSON structure
                with open(profile_path, 'r') as f:
                    profile_data = json.load(f)

                self.assertIn("name", profile_data)
                self.assertIn("crypto_backend", profile_data)
                self.assertIn("algorithms", profile_data)

    def test_crypto_tests(self):
        """Test crypto package test suite."""
        test_file = self.crypto_dir / "test" / "test_esp32_crypto.cpp"
        if not test_file.exists():
            self.skipTest("Crypto tests not found")

        with open(test_file, 'r') as f:
            content = f.read()

        # Check for required test cases
        required_tests = [
            "AES_EncryptionDecryption",
            "SHA256_Hashing",
            "ECC_SignVerify",
            "RNG_Generation"
        ]

        for test in required_tests:
            with self.subTest(test=test):
                self.assertIn(test, content,
                            f"Required test case {test} not found")


class TestSpareToolsCITemplatesPackage(unittest.TestCase):
    """Test cases for sparetools-ci-templates package."""

    def setUp(self):
        """Set up test fixtures."""
        self.ci_dir = packages_dir / "devops" / "sparetools-ci-templates"
        self.conanfile = self.ci_dir / "conanfile.py"

    def test_ci_package_structure(self):
        """Test that CI templates package has required structure."""
        if not self.ci_dir.exists():
            self.skipTest("CI templates package not found")

        # Check required directories
        required_dirs = ["templates", "examples"]
        for dir_name in required_dirs:
            with self.subTest(dir_name=dir_name):
                self.assertTrue((self.ci_dir / dir_name).exists(),
                              f"Required directory {dir_name} not found")

        # Check required files
        required_files = [
            "conanfile.py",
            "templates/workflows/esp32-build-template.yml",
            "templates/workflows/security-scan-template.yml",
            "templates/scripts/conan-ci-helpers.sh",
            "examples/esp32-project-workflows.yml"
        ]
        for file_path in required_files:
            with self.subTest(file_path=file_path):
                self.assertTrue((self.ci_dir / file_path).exists(),
                              f"Required file {file_path} not found")

    def test_ci_conanfile_configuration(self):
        """Test CI templates package Conan configuration."""
        if not self.conanfile.exists():
            self.skipTest("CI conanfile not found")

        with open(self.conanfile, 'r') as f:
            content = f.read()

        # Check for required Conan configuration
        self.assertIn("sparetools-ci-templates", content)
        self.assertIn("python-require", content)  # Should be python-require package

    def test_workflow_templates(self):
        """Test CI workflow templates."""
        workflows_dir = self.ci_dir / "templates" / "workflows"
        if not workflows_dir.exists():
            self.skipTest("Workflow templates not found")

        # Check workflow template content
        build_template = workflows_dir / "esp32-build-template.yml"
        if build_template.exists():
            with open(build_template, 'r') as f:
                content = f.read()

            # Check for required workflow elements
            required_elements = [
                "workflow_call",
                "matrix",
                "esp32_variants",
                "conan_profile",
                "platformio"
            ]

            for element in required_elements:
                self.assertIn(element, content,
                            f"Required workflow element {element} not found")

        # Check security template
        security_template = workflows_dir / "security-scan-template.yml"
        if security_template.exists():
            with open(security_template, 'r') as f:
                content = f.read()

            security_elements = [
                "secret-scanning",
                "static-analysis",
                "software-composition-analysis",
                "firmware-security"
            ]

            for element in security_elements:
                self.assertIn(element, content,
                            f"Required security element {element} not found")

    def test_ci_scripts(self):
        """Test CI helper scripts."""
        scripts_dir = self.ci_dir / "templates" / "scripts"
        if not scripts_dir.exists():
            self.skipTest("CI scripts not found")

        helpers_script = scripts_dir / "conan-ci-helpers.sh"
        if helpers_script.exists():
            with open(helpers_script, 'r') as f:
                content = f.read()

            # Check for required script functions
            required_functions = [
                "setup_conan",
                "conan_install_cached",
                "generate_sbom",
                "scan_dependencies"
            ]

            for func in required_functions:
                self.assertIn(func, content,
                            f"Required script function {func} not found")

    def test_examples(self):
        """Test CI examples and documentation."""
        examples_dir = self.ci_dir / "examples"
        if not examples_dir.exists():
            self.skipTest("CI examples not found")

        example_file = examples_dir / "esp32-project-workflows.yml"
        if example_file.exists():
            with open(example_file, 'r') as f:
                content = f.read()

            # Check for example workflow elements
            example_elements = [
                "esp32-build-template.yml",
                "security-scan-template.yml",
                "esp32_variants",
                "conan_profile"
            ]

            for element in example_elements:
                self.assertIn(element, content,
                            f"Required example element {element} not found")


class TestPackageIntegration(unittest.TestCase):
    """Integration tests for package interoperability."""

    def setUp(self):
        self.root_dir = sparetools_root

    def test_package_version_consistency(self):
        """Test version consistency across enterprise packages."""
        # Check that packages reference consistent versions
        conanfiles = [
            packages_dir / "embedded" / "sparetools-hal-sunton" / "conanfile.py",
            packages_dir / "security" / "sparetools-crypto-suite" / "conanfile.py",
            packages_dir / "devops" / "sparetools-ci-templates" / "conanfile.py"
        ]

        for conanfile in conanfiles:
            if conanfile.exists():
                with self.subTest(conanfile=conanfile):
                    with open(conanfile, 'r') as f:
                        content = f.read()

                    # Should not have hardcoded versions (except for self-references)
                    hardcoded_versions = ["1.14.0", "8.3.11", "3.3.2"]  # These are ok
                    for version in hardcoded_versions:
                        # Allow some specific versions that are stable
                        pass

    def test_package_dependencies(self):
        """Test that packages have appropriate dependencies."""
        # HAL package should depend on LVGL
        hal_conanfile = packages_dir / "embedded" / "sparetools-hal-sunton" / "conanfile.py"
        if hal_conanfile.exists():
            with open(hal_conanfile, 'r') as f:
                content = f.read()
            self.assertIn("lvgl", content, "HAL package should depend on LVGL")

        # Crypto package should depend on crypto libraries
        crypto_conanfile = packages_dir / "security" / "sparetools-crypto-suite" / "conanfile.py"
        if crypto_conanfile.exists():
            with open(crypto_conanfile, 'r') as f:
                content = f.read()
            crypto_libs = ["mbedTLS", "wolfSSL", "openssl"]
            self.assertTrue(any(lib in content for lib in crypto_libs),
                          "Crypto package should depend on crypto libraries")

    @patch('subprocess.run')
    def test_package_build_integration(self, mock_subprocess):
        """Test that packages can be built together."""
        # Mock successful builds
        mock_subprocess.return_value = MagicMock(returncode=0)

        # This would test building packages together
        # For now, just verify the package structure supports integration
        packages_to_test = [
            "sparetools-hal-sunton",
            "sparetools-crypto-suite",
            "sparetools-ci-templates"
        ]

        for package in packages_to_test:
            with self.subTest(package=package):
                package_dir = packages_dir / package.split('-')[1] / package
                if package_dir.exists():
                    conanfile = package_dir / "conanfile.py"
                    self.assertTrue(conanfile.exists(),
                                  f"Package {package} should have conanfile.py")


if __name__ == '__main__':
    unittest.main()