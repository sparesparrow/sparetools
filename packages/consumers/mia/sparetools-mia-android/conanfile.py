from conan import ConanFile
from conan.tools.files import copy, save
import os


class SparetoolsMiaAndroidConan(ConanFile):
    """MIA Android-specific utilities and resources."""

    name = "sparetools-mia-android"
    version = "2.0.0"
    description = "MIA Android-specific utilities, device workspace, and demo scripts"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("mia", "android", "mobile", "iot", "device-workspace")

    # SpareTools foundation with bundled CPython
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"
    tool_requires = "sparetools-cpython/3.12.7"

    package_type = "python-require"

    exports_sources = "src/**/*.py", "src/**/*.txt", "src/**/*.json", "pyproject.toml", "README.md"

    def package(self):
        """Package the MIA Android utilities."""
        # Copy all Python files and resources
        copy(
            self,
            "*.py",
            src=os.path.join(self.source_folder, "src"),
            dst=os.path.join(self.package_folder, "python"),
        )
        copy(
            self,
            "*.txt",
            src=os.path.join(self.source_folder, "src"),
            dst=os.path.join(self.package_folder, "python"),
        )
        copy(
            self,
            "*.json",
            src=os.path.join(self.source_folder, "src"),
            dst=os.path.join(self.package_folder, "config"),
        )
        copy(
            self,
            "README.md",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "res"),
        )

        # Apply security gates if available from mixin
        if hasattr(self, "apply_security_gates"):
            self.apply_security_gates()
        if hasattr(self, "generate_sbom"):
            self.generate_sbom()

    def package_info(self):
        """Expose run-time environment for consumers."""
        python_path = os.path.join(self.package_folder, "python")
        self.runenv_info.append_path("PYTHONPATH", python_path)
        self.buildenv_info.append_path("PYTHONPATH", python_path)
        self.conf_info.define("user.mia-android:python_path", python_path)

        # Config and resources paths
        self.conf_info.define("user.mia-android:config_path", os.path.join(self.package_folder, "config"))

    def package_id(self):
        """Platform-independent Python package."""
        self.info.clear()