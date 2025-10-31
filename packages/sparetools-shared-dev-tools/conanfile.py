from conan import ConanFile
from conan.tools.files import copy

class SpareToolsSharedDevToolsConan(ConanFile):
    name = "sparetools-shared-dev-tools"
    version = "2.0.0"
    package_type = "python-require"
    description = "Shared development tools for SpareTools ecosystem"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    
    exports_sources = "shared_dev_tools/**", "scripts/**"

    python_requires = "sparetools-base/2.0.0"

    def package(self):
        copy(self, "*.py", src=self.source_folder, dst=self.package_folder, keep_path=True)
        copy(self, "*.sh", src=self.source_folder, dst=self.package_folder, keep_path=True)
    
    def package_info(self):
        self.cpp_info.libs = []
        self.env_info.PYTHONPATH.append(self.package_folder)
