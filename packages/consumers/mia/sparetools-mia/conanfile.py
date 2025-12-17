import os
import sys
from conan import ConanFile
from conan.tools.files import copy

# Import base class from shared scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../scripts'))
from recipe_base import ConsumerPackageConan


class SpareToolsMiaConan(ConsumerPackageConan):
    """MIA (Modular IoT Architecture) - IoT connectivity and device management."""

    name = "sparetools-mia"
    version = "2.0.0"
    package_type = "python-require"
    description = "Modular IoT Architecture with device management, connectivity, and cloud integration"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("iot", "connectivity", "device-management", "cloud", "mia")

    # Declare consumer context
    consumer_domain = "mia"

    # Use SpareTools base utilities
    python_requires = "sparetools-base/2.0.0"

    # Runtime dependencies
    requires = (
        "sparetools-openssl/3.3.2",
        "sparetools-cpython/3.12.7",
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

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

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