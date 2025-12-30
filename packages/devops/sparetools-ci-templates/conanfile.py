import os
from conan import ConanFile
from conan.tools.files import copy

# Use SpareTools base utilities
python_requires = "sparetools-base/2.0.3"

class SpareToolsCiTemplatesConan(ConanFile):
    name = "sparetools-ci-templates"
    version = "1.0.1"
    package_type = "python-require"
    description = "Reusable GitHub Actions workflows and CI/CD templates for SpareTools ecosystem"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("ci", "cd", "github-actions", "workflows", "templates", "devops")

    # Use sparetools-base utilities
    python_requires = "sparetools-base/2.0.3"

    exports_sources = "templates/**", "examples/**", "*.md"

    def package(self):
        # Copy all template files
        copy(self, "*", src=self.source_folder, dst=self.package_folder, keep_path=True)

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        self.cpp_info.libs = []
        # Conan 2.x API: Use buildenv_info for build-time Python modules
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)

    def package_id(self):
        # This package doesn't affect binary compatibility
        self.info.clear()