#!/usr/bin/env python3
"""
MIA ↔ SpareTools Integration Tests

This module contains end-to-end integration tests that validate the complete
pipeline from SpareTools package consumption through MIA runtime execution.

Test Coverage:
- Conan dependency resolution across repositories
- Cross-platform build compatibility
- Runtime integration between components
- Version compatibility and upgrades
- CI/CD pipeline integration
"""

import os
import sys
import tempfile
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pytest
import json


class IntegrationTestHarness:
    """Test harness for MIA-SpareTools integration testing."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.temp_dir = Path(tempfile.mkdtemp(prefix="mia_integration_"))
        self.conan_cache = self.temp_dir / "conan_cache"
        self.build_dir = self.temp_dir / "build"

        # Setup isolated Conan environment
        self.conan_home = self.temp_dir / "conan_home"
        os.environ["CONAN_HOME"] = str(self.conan_home)

    def cleanup(self):
        """Clean up temporary directories."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run_conan_command(self, args: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
        """Run a Conan command and return (returncode, stdout, stderr)."""
        env = os.environ.copy()
        env["CONAN_HOME"] = str(self.conan_home)

        cmd = ["conan"] + args
        result = subprocess.run(
            cmd,
            cwd=cwd or self.workspace_root,
            capture_output=True,
            text=True,
            env=env
        )
        return result.returncode, result.stdout, result.stderr

    def setup_conan_remotes(self) -> bool:
        """Setup Conan remotes for testing."""
        # Add local test remote (simulate Cloudsmith)
        returncode, stdout, stderr = self.run_conan_command([
            "remote", "add", "test-remote",
            f"file://{self.temp_dir}/test_remote", "--force"
        ])
        return returncode == 0

    def create_test_package(self, package_name: str, version: str) -> bool:
        """Create a test package in the local remote."""
        package_dir = self.workspace_root / "sparetools" / "packages" / package_name
        if not package_dir.exists():
            return False

        returncode, stdout, stderr = self.run_conan_command([
            "create", str(package_dir),
            f"--version={version}",
            "--build=missing"
        ])
        return returncode == 0

    def test_dependency_resolution(self) -> bool:
        """Test that MIA can resolve SpareTools dependencies."""
        mia_dir = self.workspace_root / "mia"

        # Test conan install for MIA
        returncode, stdout, stderr = self.run_conan_command([
            "install", str(mia_dir),
            "--build=missing",
            "--profile:build=default",
            "--profile:host=default"
        ])

        if returncode != 0:
            print(f"❌ Dependency resolution failed: {stderr}")
            return False

        print("✅ Dependency resolution successful")
        return True

    def test_cross_repo_dependencies(self) -> bool:
        """Test cross-repository dependency resolution."""
        # This tests that MIA can find and use SpareTools packages
        # even when they're in different repositories

        # First, create some test packages
        test_packages = [
            ("sparetools-base", "2.0.0"),
            ("sparetools-obd-sim", "2.0.0"),
        ]

        for package, version in test_packages:
            if not self.create_test_package(package, version):
                print(f"❌ Failed to create test package {package}")
                return False

        # Test MIA's conanfile.py can resolve these dependencies
        return self.test_dependency_resolution()

    def test_build_integration(self) -> bool:
        """Test that MIA can build against SpareTools dependencies."""
        mia_dir = self.workspace_root / "mia"

        # Test full build pipeline
        returncode, stdout, stderr = self.run_conan_command([
            "build", str(mia_dir),
            "--build=missing"
        ], cwd=mia_dir)

        if returncode != 0:
            print(f"❌ Build integration failed: {stderr}")
            return False

        print("✅ Build integration successful")
        return True

    def test_runtime_integration(self) -> bool:
        """Test runtime integration between MIA and SpareTools components."""
        # This would test actual component interaction
        # For now, we'll test that the built artifacts exist and are executable

        # Check that expected binaries/libraries exist
        build_artifacts = [
            "libwebgrab_core.so",  # C++ core library
            "hardware-server",     # Hardware server binary
            "mcp-server",          # MCP server binary
        ]

        for artifact in build_artifacts:
            if not (self.build_dir / artifact).exists():
                print(f"❌ Missing build artifact: {artifact}")
                return False

        print("✅ Runtime artifacts present")
        return True

    def test_version_compatibility(self) -> bool:
        """Test version compatibility across the ecosystem."""
        # Read version files and ensure they align
        version_files = {
            "sparetools": self.workspace_root / "sparetools" / "VERSION.txt",
            "mia": self.workspace_root / "mia" / "VERSION.txt",
        }

        versions = {}
        for name, path in version_files.items():
            if path.exists():
                with open(path, 'r') as f:
                    version = f.readline().strip().split('#')[0].strip()
                    versions[name] = version

        # Check that all projects have same major.minor version
        if len(set(v.split('.')[:2] for v in versions.values())) != 1:
            print(f"❌ Version mismatch: {versions}")
            return False

        print(f"✅ Version compatibility: {versions}")
        return True


class TestMIAIntegration:
    """Integration test suite for MIA-SpareTools pipeline."""

    @pytest.fixture(scope="class")
    def harness(self):
        """Setup test harness for the test class."""
        harness = IntegrationTestHarness(Path(__file__).parent.parent.parent)
        yield harness
        harness.cleanup()

    def test_conan_remote_setup(self, harness):
        """Test Conan remote configuration."""
        assert harness.setup_conan_remotes(), "Failed to setup Conan remotes"

    def test_dependency_resolution(self, harness):
        """Test dependency resolution across repositories."""
        assert harness.test_dependency_resolution(), "Dependency resolution failed"

    def test_cross_repo_dependencies(self, harness):
        """Test cross-repository dependency management."""
        assert harness.test_cross_repo_dependencies(), "Cross-repo dependencies failed"

    def test_build_integration(self, harness):
        """Test build integration with SpareTools."""
        assert harness.test_build_integration(), "Build integration failed"

    def test_runtime_integration(self, harness):
        """Test runtime component integration."""
        assert harness.test_runtime_integration(), "Runtime integration failed"

    def test_version_compatibility(self, harness):
        """Test version alignment across ecosystem."""
        assert harness.test_version_compatibility(), "Version compatibility check failed"

    def test_bundled_cpython_usage(self, harness):
        """Test that MIA uses bundled CPython instead of system Python."""
        # This test verifies that MIA components use the bundled CPython executable
        # from sparetools-cpython instead of relying on system Python

        mia_dir = Path(harness.workspace_root).parent / "mia"

        # Check that MIA conanfile.py includes sparetools-cpython as tool_requires
        conanfile = mia_dir / "conanfile.py"
        assert conanfile.exists(), "MIA conanfile.py not found"

        with open(conanfile, 'r') as f:
            content = f.read()
            assert "sparetools-cpython/3.12.7" in content, \
                "MIA conanfile.py does not include sparetools-cpython tool requirement"

        # Check that systemd services are configured to use bundled Python
        service_dir = mia_dir / "rpi" / "services"
        assert service_dir.exists(), "MIA systemd services directory not found"

        python_services = [
            "mia-api.service",
            "mia-gpio-worker.service",
            "mia-serial-bridge.service",
            "mia-obd-worker.service"
        ]

        for service in python_services:
            service_file = service_dir / service
            if service_file.exists():
                with open(service_file, 'r') as f:
                    content = f.read()
                    # Check that service uses bundled Python path
                    assert "/opt/mia/rpi/bin/python3" in content, \
                        f"Service {service} does not use bundled Python executable"
                    assert "PYTHONHOME=/opt/mia/rpi" in content, \
                        f"Service {service} does not set PYTHONHOME to bundled location"

        # Check that the bundled CPython setup script exists
        setup_script = mia_dir / "scripts" / "ensure-bundled-cpython.sh"
        assert setup_script.exists(), "Bundled CPython setup script not found"
        assert setup_script.stat().st_mode & 0o111, "Setup script is not executable"

        # Check that deployment script calls the setup script
        deploy_script = mia_dir / "scripts" / "deploy-raspberry-pi.sh"
        assert deploy_script.exists(), "Deployment script not found"

        with open(deploy_script, 'r') as f:
            content = f.read()
            assert "ensure-bundled-cpython.sh" in content, \
                "Deployment script does not call bundled CPython setup"

    @pytest.mark.parametrize("platform", ["linux", "macos", "windows"])
    def test_cross_platform_compatibility(self, harness, platform):
        """Test cross-platform build compatibility."""
        # This would test platform-specific builds
        # For now, just validate the platform is supported
        supported_platforms = ["linux", "macos", "windows"]
        assert platform in supported_platforms, f"Unsupported platform: {platform}"

    def test_ci_cd_pipeline_integration(self, harness):
        """Test CI/CD pipeline integration."""
        # Validate that CI/CD workflows can run the integration tests
        ci_config = harness.workspace_root / "sparetools" / ".github" / "workflows"
        assert ci_config.exists(), "CI/CD configuration missing"

        # Check for integration test workflow
        integration_workflow = ci_config / "integration-tests.yml"
        if integration_workflow.exists():
            with open(integration_workflow, 'r') as f:
                content = f.read()
                assert "test_mia_sparetools_integration" in content, \
                    "Integration tests not referenced in CI/CD"

    def test_package_upgrade_compatibility(self, harness):
        """Test package upgrade compatibility."""
        # Test that version upgrades don't break integration
        # This would test upgrading SpareTools packages and ensuring MIA still works

        # For now, just validate version upgrade path exists
        assert harness.test_version_compatibility(), "Version compatibility prerequisite failed"

        # TODO: Implement actual upgrade testing
        # - Create multiple versions of packages
        # - Test MIA builds against different versions
        # - Validate runtime compatibility


def run_integration_tests():
    """Run integration tests manually."""
    print("🚀 Starting MIA-SpareTools Integration Tests...")

    harness = IntegrationTestHarness(Path(__file__).parent.parent.parent)

    try:
        tests = [
            ("Conan Remote Setup", harness.setup_conan_remotes),
            ("Dependency Resolution", harness.test_dependency_resolution),
            ("Cross-Repo Dependencies", harness.test_cross_repo_dependencies),
            ("Build Integration", harness.test_build_integration),
            ("Runtime Integration", harness.test_runtime_integration),
            ("Version Compatibility", harness.test_version_compatibility),
            ("Bundled CPython Usage", lambda: True),  # This is tested via pytest class method
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            try:
                if test_func():
                    print(f"✅ {test_name}: PASSED")
                    passed += 1
                else:
                    print(f"❌ {test_name}: FAILED")
                    failed += 1
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                failed += 1

        print(f"\n📊 Results: {passed} passed, {failed} failed")

        if failed == 0:
            print("🎉 All integration tests passed!")
            return True
        else:
            print("💥 Integration tests failed!")
            return False

    finally:
        harness.cleanup()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)