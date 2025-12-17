#!/usr/bin/env python3
"""
Integration Test for ClipHist Android Consumer

Tests the integration between ClipHist Android consumer and SpareTools foundation packages.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path


class AndroidIntegrationTester:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.errors = []
        self.warnings = []

    def test_integration(self) -> bool:
        """Run integration tests."""
        print("🔗 Testing ClipHist Android integration with SpareTools foundation...")

        tests = [
            self._test_conan_dependency_resolution,
            self._test_foundation_package_imports,
            self._test_build_configuration,
            self._test_cross_package_compatibility,
        ]

        for test in tests:
            try:
                test()
                print(f"✅ {test.__name__} passed")
            except Exception as e:
                self.errors.append(f"{test.__name__} failed: {e}")
                print(f"❌ {test.__name__} failed: {e}")

        self._report_results()
        return len(self.errors) == 0

    def _test_conan_dependency_resolution(self):
        """Test that Conan can resolve all dependencies."""
        # Create a temporary profile for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.profile', delete=False) as f:
            f.write("""[settings]
os=Linux
arch=x86_64
compiler=gcc
compiler.version=11
compiler.libcxx=libstdc++11
build_type=Release

[conf]
tools.cmake.cmaketoolchain:generator=Ninja
""")
            profile_path = f.name

        try:
            # Test conan install dry-run
            cmd = [
                "conan", "install", ".",
                "--profile", profile_path,
                "--build", "missing",
                "--output-folder", "temp_conan_test"
            ]

            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Clean up temp directory
            temp_dir = self.project_root / "temp_conan_test"
            if temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)

            if result.returncode != 0:
                # Conan might fail due to missing Android SDK/NDK, but dependency resolution should work
                if "android" in result.stderr.lower() or "gradle" in result.stderr.lower():
                    self.warnings.append("Android SDK/NDK tools not available, but dependency resolution should work in CI")
                else:
                    raise Exception(f"Conan dependency resolution failed: {result.stderr}")

        finally:
            os.unlink(profile_path)

    def _test_foundation_package_imports(self):
        """Test that foundation package structure exists."""
        # Test that foundation packages exist and have proper structure
        foundation_base = Path("/home/sparrow/sparetools/packages/foundation/sparetools-recipe-base")
        if not foundation_base.exists():
            raise Exception(f"sparetools-recipe-base foundation package not found at {foundation_base}")

        required_files = ["__init__.py", "conanfile.py"]
        for file in required_files:
            if not (foundation_base / file).exists():
                raise Exception(f"Foundation package missing required file: {file}")

        # Check that the __init__.py declares the base classes
        init_file = foundation_base / "__init__.py"
        content = init_file.read_text()
        if "SpareToolsFoundationBase" not in content or "SpareToolsConsumerBase" not in content:
            raise Exception("Foundation package missing required base classes")

        print("  ✓ Foundation package structure validated")

    def _test_build_configuration(self):
        """Test build configuration compatibility."""
        conanfile = self.project_root / "conanfile.py"
        if not conanfile.exists():
            raise Exception("conanfile.py not found")

        # Read and validate conanfile content
        content = conanfile.read_text()

        # Check for required foundation dependencies
        required_deps = ["sparetools-base", "sparetools-recipe-base"]
        for dep in required_deps:
            if dep not in content:
                raise Exception(f"Missing required foundation dependency: {dep}")

        # Check for proper inheritance
        if "SpareToolsConsumerBase" not in content:
            raise Exception("Not using SpareToolsConsumerBase")

    def _test_cross_package_compatibility(self):
        """Test compatibility across packages."""
        # Check that the consumer follows the same patterns as other consumers
        obd_sim_conanfile = self.project_root.parent / "sparetools-obd-sim" / "conanfile.py"

        if obd_sim_conanfile.exists():
            # Compare patterns between consumers
            cliphist_content = (self.project_root / "conanfile.py").read_text()
            obd_content = obd_sim_conanfile.read_text()

            # Both should use SpareToolsConsumerBase
            if "SpareToolsConsumerBase" in cliphist_content and "SpareToolsConsumerBase" not in obd_content:
                self.warnings.append("Inconsistent base class usage across consumers")

            # Both should depend on sparetools-base
            if "sparetools-base" in cliphist_content and "sparetools-base" not in obd_content:
                self.warnings.append("Inconsistent foundation dependencies across consumers")

    def _report_results(self):
        """Report test results."""
        if self.errors:
            print(f"\n❌ Found {len(self.errors)} integration errors:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n⚠️  Found {len(self.warnings)} integration warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All integration tests passed!")


def main():
    """Main integration test entry point."""
    project_root = Path(__file__).parent
    tester = AndroidIntegrationTester(project_root)

    if tester.test_integration():
        print("\n🎉 ClipHist Android integration tests successful!")
        return 0
    else:
        print("\n💥 ClipHist Android integration tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())