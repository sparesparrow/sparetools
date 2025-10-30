from conan import ConanFile
from conan.tools.files import copy

class SpareToolsBaseConan(ConanFile):
    name = "sparetools-base"
    version = "1.0.0"
    package_type = "python-require"
    description = "Foundation utilities for SpareTools ecosystem"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    
    exports_sources = "*.py"
    
    def package(self):
        copy(self, "*.py", src=self.source_folder, dst=self.package_folder, keep_path=True)
    
    def package_info(self):
        self.cpp_info.libs = []
        self.env_info.PYTHONPATH.append(self.package_folder)
