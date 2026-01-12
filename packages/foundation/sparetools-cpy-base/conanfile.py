import os
import json
from conan import ConanFile
from conan.tools.files import save


class SpareToolsCpyBaseConan(ConanFile):
    """CPY Base Environment - Python 3.12.7 + shared-dev-tools aggregator"""

    name = "sparetools-cpy-base"
    version = "1.0.0"
    package_type = "application"
    description = "Base CPython environment with shared-dev-tools for modular CPY system"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"

    # Use SpareTools base utilities (Conan 2.x pattern)
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    def requirements(self):
        """Aggregate CPython and shared-dev-tools"""
        self.requires("sparetools-cpython/3.12.7")
        self.requires("sparetools-shared-dev-tools/2.0.4")

    def package(self):
        """
        Store dependency references for setup script.
        This is a zero-copy package - no actual files are copied,
        only metadata for the setup script to create symlinks.
        """
        # Collect dependency information
        deps_info = {
            "cpython": {
                "ref": "sparetools-cpython/3.12.7",
                "package_folder": self.dependencies["sparetools-cpython"].package_folder
            },
            "shared_dev_tools": {
                "ref": "sparetools-shared-dev-tools/2.0.4",
                "package_folder": self.dependencies["sparetools-shared-dev-tools"].package_folder
            }
        }

        # Save metadata for setup script
        save(self,
             os.path.join(self.package_folder, "dependencies.json"),
             json.dumps(deps_info, indent=2))

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        """Expose dependency paths to consumers and environment"""
        cpython_folder = self.dependencies["sparetools-cpython"].package_folder
        shared_dev_tools_folder = self.dependencies["sparetools-shared-dev-tools"].package_folder

        # Build environment setup (for Conan consumers)
        self.buildenv_info.define_path("PYTHONHOME", cpython_folder)
        self.buildenv_info.prepend_path("PATH", os.path.join(cpython_folder, "bin"))

        # Runtime environment setup
        self.runenv_info.append_path("PYTHONPATH", shared_dev_tools_folder)

        # Configuration info for downstream packages
        self.conf_info.define("user.cpy-base:cpython_folder", cpython_folder)
        self.conf_info.define("user.cpy-base:shared_dev_tools_folder", shared_dev_tools_folder)
        self.conf_info.define("user.cpy-base:python_version", "3.12.7")
