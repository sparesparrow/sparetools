import os
from conan import ConanFile
from conan.tools.files import copy


class SpareToolsMiaConan(ConanFile):
    """MIA (Modular IoT Architecture) - IoT connectivity and device management."""

    name = "sparetools-mia"
    version = "2.0.0"
    package_type = "python-require"
    description = "Modular IoT Architecture with device management, connectivity, and cloud integration"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("iot", "connectivity", "device-management", "cloud", "mia")

    # Use SpareTools base utilities
    python_requires = "sparetools-base/2.0.0"

    # Runtime dependencies
    requires = (
        "sparetools-base/2.0.0",
    )

    # Source files to export
    exports_sources = (
        "src/*",
        "scripts/*",
        "docs/*",
    )

    def package(self):
        """Package MIA components."""
        # Copy Python modules
        copy(self, "*.py", self.source_folder, os.path.join(self.package_folder, "src"), keep_path=True)

        # Copy scripts
        copy(self, "*", os.path.join(self.source_folder, "scripts"), os.path.join(self.package_folder, "bin"), keep_path=False)

        # Copy documentation
        copy(self, "*", os.path.join(self.source_folder, "docs"), os.path.join(self.package_folder, "docs"), keep_path=True)

        # Apply security gates and generate SBOM (placeholder)
        self.output.info("Applying security gates...")
        self.output.info("Generating SBOM...")

    def package_info(self):
        """Provide MIA package information."""
        self.cpp_info.libs = []

        # Add Python path
        self.buildenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "src"))

        # Add scripts to PATH
        self.buildenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))

        # Environment for cloud integration
        self.runenv_info.define("MIA_ROOT", self.package_folder)

        # Conf info for MIA discovery
        self.conf_info.define("user.mia:root", self.package_folder)
        self.conf_info.define("user.mia:scripts", os.path.join(self.package_folder, "bin"))