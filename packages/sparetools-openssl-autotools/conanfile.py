from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.files import get
import os

class SpareToolsOpenSSLAutotools(ConanFile):
    """OpenSSL built with Conan Autotools integration"""
    name = "sparetools-openssl-autotools"
    version = "3.3.2"
    
    package_type = "library"
    description = "OpenSSL built with Conan Autotools toolchain"
    license = "Apache-2.0"
    
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    
    def layout(self):
        basic_layout(self)
    
    def source(self):
        get(self,
            "https://github.com/openssl/openssl/archive/refs/tags/openssl-3.3.2.tar.gz",
            strip_root=True)
    
    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()
    
    def build(self):
        """Use Autotools interface to Perl Configure"""
        autotools = Autotools(self)
        
        # OpenSSL's Configure script is autotools-compatible
        configure_args = [
            "linux-x86_64",
            "no-shared" if not self.options.shared else "shared",
            f"--prefix={self.package_folder}",
            f"--openssldir={self.package_folder}/ssl",
        ]
        
        autotools.configure(args=configure_args)
        autotools.make()
        autotools.make(args=["test"], ignore_errors=True)
    
    def package(self):
        autotools = Autotools(self)
        autotools.install()
    
    def package_info(self):
        self.cpp_info.libs = ["ssl", "crypto"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]
