from conan import ConanFile
from conan.tools.files import copy

class SpareToolsOpenSSLToolsMiniConan(ConanFile):
    name = "sparetools-openssl-tools-mini"
    version = "1.0.1"
    package_type = "python-require"
    description = "Minimal OpenSSL tools for SpareTools ecosystem"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    
    exports_sources = "openssl_tools/**", "scripts/**"
    
    def package(self):
        copy(self, "*.py", src=self.source_folder, dst=self.package_folder, keep_path=True)
        copy(self, "*.sh", src=self.source_folder, dst=self.package_folder, keep_path=True)
    
    def package_info(self):
        self.cpp_info.libs = []
        # Conan 2.x API: Use buildenv_info for build-time Python modules
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)
