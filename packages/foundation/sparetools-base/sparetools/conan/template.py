"""
SpareTools Base Template for Conan Recipes

Provides a base ConanFile class with common SpareTools functionality including:
- Python detection and setup
- Security gates
- Environment management
- Common build patterns
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.files import copy
from conan.tools.env import VirtualRunEnv


class SpareToolsBaseTemplate(ConanFile):
    """
    Base template for SpareTools Conan recipes.

    Provides common functionality for:
    - Python runtime detection and setup
    - Security gate execution
    - Environment management
    - Standard build patterns
    """

    # Default settings that can be overridden
    settings = "os", "compiler", "build_type", "arch"

    def _get_python_exe(self) -> str:
        """
        Get the Python executable path.

        Returns the Python executable from environment or system default.
        """
        python_exe = os.environ.get("PYTHON_EXE")
        if python_exe:
            return python_exe

        # Try common Python executable names
        for exe in ["python3", "python", "python.exe"]:
            try:
                import subprocess
                result = subprocess.run([exe, "--version"],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return exe
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue

        # Fallback to sys.executable
        return sys.executable

    def _setup_python_environment(self) -> None:
        """
        Set up Python environment for the build.

        Configures PYTHONPATH and ensures Python is available.
        """
        python_exe = self._get_python_exe()

        # Set PYTHON_EXE environment variable
        self.runenv.define("PYTHON_EXE", python_exe)

        # Add package source to PYTHONPATH if it exists
        if hasattr(self, 'source_folder') and self.source_folder:
            pythonpath = os.environ.get("PYTHONPATH", "")
            if pythonpath:
                pythonpath = f"{self.source_folder}:{pythonpath}"
            else:
                pythonpath = self.source_folder
            self.runenv.define("PYTHONPATH", pythonpath)

    def run_security_gates(self) -> None:
        """
        Run security gates for the project.

        This method can be overridden by subclasses to implement
        custom security checks.
        """
        self.output.info("Running security gates...")

        # Default security checks - can be extended by subclasses
        python_exe = self._get_python_exe()
        self.output.info(f"Using Python executable: {python_exe}")

        # Check if we're in a CI environment
        ci_env = os.environ.get("CI", "").lower() in ("true", "1")
        if ci_env:
            self.output.info("Running in CI environment")
        else:
            self.output.info("Running in local environment")

    def _create_activation_scripts(self) -> None:
        """
        Create environment activation scripts.

        Generates scripts to activate the Conan environment.
        """
        if hasattr(self, 'generators'):
            # Use VirtualRunEnv to create activation scripts
            virtual_run_env = VirtualRunEnv(self)
            virtual_run_env.generate()

    def _setup_hil_environment(self) -> None:
        """
        Set up Hardware-in-Loop testing environment.

        Configures environment variables and paths needed for HIL testing.
        """
        self.output.info("Setting up HIL environment...")

        # Set common HIL environment variables
        hil_vars = {
            "HIL_MODE": "enabled",
            "HIL_LOG_LEVEL": "INFO",
            "HIL_CONFIG_PATH": str(Path(self.source_folder or ".") / "hil_config"),
        }

        for key, value in hil_vars.items():
            self.runenv.define(key, value)

    def export_sources(self) -> None:
        """
        Export source files needed for building.

        Default implementation exports common source patterns.
        Subclasses can override or extend this.
        """
        # Export Python source files
        copy(self, "*.py", src=self.source_folder, dst=self.export_sources_folder)

        # Export common configuration files
        for pattern in ["*.txt", "*.md", "*.json", "*.yaml", "*.yml"]:
            copy(self, pattern, src=self.source_folder, dst=self.export_sources_folder)

    def layout(self) -> None:
        """
        Define the package layout.

        Uses basic layout by default. Subclasses can override for custom layouts.
        """
        from conan.tools.layout import basic_layout
        basic_layout(self)

    def generate(self) -> None:
        """
        Generate files needed for building.

        Sets up Python environment and creates activation scripts.
        """
        self._setup_python_environment()
        self._create_activation_scripts()

    def build(self) -> None:
        """
        Build the package.

        Default implementation runs security gates.
        Subclasses should override for actual build logic.
        """
        self.run_security_gates()

    def package(self) -> None:
        """
        Package the build artifacts.

        Copies common files to the package folder.
        """
        # Copy Python files
        copy(self, "*.py", src=self.source_folder, dst=self.package_folder)

        # Copy documentation
        copy(self, "*.md", src=self.source_folder, dst=self.package_folder)
        copy(self, "*.txt", src=self.source_folder, dst=self.package_folder)

        # Copy configuration files
        for pattern in ["*.json", "*.yaml", "*.yml"]:
            copy(self, pattern, src=self.source_folder, dst=self.package_folder)

    def package_info(self) -> None:
        """
        Define package information.

        Sets up environment variables and paths.
        """
        # Set PYTHONPATH to include package
        self.runenv.define_path("PYTHONPATH", self.package_folder)

        # Set common environment variables
        self.runenv.define("SPARETOOLS_BASE_VERSION", getattr(self, 'version', 'unknown'))

    def validate(self) -> None:
        """
        Validate the package configuration.

        Performs basic validation checks.
        """
        # Check that Python is available
        python_exe = self._get_python_exe()
        if not python_exe:
            raise ConanException("Python executable not found")

        # Validate version format
        if hasattr(self, 'version'):
            # Basic version format check
            import re
            if not re.match(r'^\d+\.\d+\.\d+', str(self.version)):
                self.output.warn(f"Version '{self.version}' does not follow semantic versioning")

    def configure(self) -> None:
        """
        Configure the package.

        Default configuration setup.
        """
        pass

    def requirements(self) -> None:
        """
        Define package requirements.

        Empty by default - subclasses should override.
        """
        pass

    def build_requirements(self) -> None:
        """
        Define build requirements.

        Empty by default - subclasses should override.
        """
        pass
