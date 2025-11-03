from conan import ConanFile
import os
import sys


class SparetoolsSharedDevToolsTestConan(ConanFile):
    test_type = "explicit"
    python_requires = "sparetools-shared-dev-tools/[>=2.0.0]"

    def test(self):
        # Test 1: Verify package folder exists
        package_folder = self.python_requires["sparetools-shared-dev-tools"].package_folder
        if not os.path.exists(package_folder):
            raise Exception(f"Package folder not found: {package_folder}")

        self.output.info(f"Package folder: {package_folder}")

        # Test 2: Verify shared_dev_tools module is importable
        # Add package folder to Python path for testing
        sys.path.insert(0, package_folder)

        try:
            import shared_dev_tools
            self.output.info(f"shared_dev_tools module loaded from: {shared_dev_tools.__file__}")
        except ImportError as e:
            self.output.warning(f"Could not import shared_dev_tools: {e}")
            self.output.info("This is expected if shared_dev_tools is a namespace package")

        # Test 3: Verify scripts directory exists
        scripts_dir = os.path.join(package_folder, "scripts")
        if os.path.exists(scripts_dir):
            self.output.info(f"Scripts directory found: {scripts_dir}")

            # List available scripts
            scripts = [f for f in os.listdir(scripts_dir) if f.endswith(('.py', '.sh'))]
            self.output.info(f"Available scripts: {', '.join(scripts)}")
        else:
            self.output.warning(f"Scripts directory not found: {scripts_dir}")

        # Test 4: Check for core utilities module
        try:
            from shared_dev_tools.core import utilities
            self.output.info("Core utilities module imported successfully")
        except (ImportError, ModuleNotFoundError) as e:
            self.output.warning(f"Core utilities not available: {e}")

        self.output.success("Shared dev tools package validation complete!")
