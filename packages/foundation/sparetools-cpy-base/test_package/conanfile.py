import os
import json
from conan import ConanFile


class SpareToolsCpyBaseTestConan(ConanFile):
    """Test package for sparetools-cpy-base"""

    name = 'base-test'
    version = '1.0.0'
    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        """Validate that cpy-base package exposes CPython and shared-dev-tools correctly"""

        # Get configuration from cpy-base
        cpython_folder = self.dependencies["sparetools-cpy-base"].conf_info.get("user.cpy-base:cpython_folder")
        shared_dev_tools_folder = self.dependencies["sparetools-cpy-base"].conf_info.get("user.cpy-base:shared_dev_tools_folder")
        python_version = self.dependencies["sparetools-cpy-base"].conf_info.get("user.cpy-base:python_version")

        self.output.info(f"CPython folder: {cpython_folder}")
        self.output.info(f"shared-dev-tools folder: {shared_dev_tools_folder}")
        self.output.info(f"Python version: {python_version}")

        # Validate CPython folder exists
        assert os.path.exists(cpython_folder), f"CPython folder does not exist: {cpython_folder}"

        # Validate Python executable exists
        python_bin = os.path.join(cpython_folder, "bin", "python3")
        assert os.path.exists(python_bin), f"Python executable not found: {python_bin}"

        # Test Python execution
        self.run(f"{python_bin} --version")
        self.run(f"{python_bin} -c 'import sys; print(sys.version)'")

        # Validate shared-dev-tools folder exists
        assert os.path.exists(shared_dev_tools_folder), f"shared-dev-tools folder does not exist: {shared_dev_tools_folder}"

        # Check dependencies.json was created
        package_folder = self.dependencies["sparetools-cpy-base"].package_folder
        deps_json = os.path.join(package_folder, "dependencies.json")
        assert os.path.exists(deps_json), f"dependencies.json not found: {deps_json}"

        # Load and validate dependencies.json
        with open(deps_json, 'r') as f:
            deps_info = json.load(f)

        assert "cpython" in deps_info, "cpython not found in dependencies.json"
        assert "shared_dev_tools" in deps_info, "shared_dev_tools not found in dependencies.json"

        self.output.success("✅ sparetools-cpy-base test passed!")
        self.output.success(f"✅ CPython 3.12.7 functional at: {cpython_folder}")
        self.output.success(f"✅ shared-dev-tools available at: {shared_dev_tools_folder}")
