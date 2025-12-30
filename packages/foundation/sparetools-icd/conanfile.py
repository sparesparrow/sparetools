from conan import ConanFile
from conan.tools.files import copy

class SparetoolsIcdConan(ConanFile):
    name = "sparetools-icd"
    version = "2.0.1"
    package_type = "python-require"
    description = "Interface Control Document schemas and generators for SpareTools ecosystem"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"

    # Dependencies
    requires = "flatbuffers/23.5.26"
    tool_requires = "sparetools-cpython/3.12.7"
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    exports_sources = "*.py", "*.fbs"

    def package(self):
        copy(self, "*.py", src=self.source_folder, dst=self.package_folder, keep_path=True)
        copy(self, "*.fbs", src=self.source_folder, dst=self.package_folder, keep_path=True)
        copy(self, "**/*.py", src=self.source_folder, dst=self.package_folder, keep_path=True)
        copy(self, "**/*.fbs", src=self.source_folder, dst=self.package_folder, keep_path=True)

    def package_info(self):
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)