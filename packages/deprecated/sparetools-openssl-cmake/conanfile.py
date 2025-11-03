from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os

class SpareToolsOpenSSLCMake(ConanFile):
    """OpenSSL built with CMake (if supported)"""
    name = "sparetools-openssl-cmake"
    version = "3.3.2"
    
    package_type = "library"
    description = "OpenSSL built with CMake build system"
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
        cmake_layout(self)
    
    def source(self):
        get(self, 
            "https://github.com/openssl/openssl/archive/refs/tags/openssl-3.3.2.tar.gz",
            strip_root=True)
    
    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["CMAKE_INSTALL_PREFIX"] = self.package_folder
        tc.generate()
    
    def build(self):
        """Try CMake build, fallback to Perl Configure if needed"""
        cmake_dir = self.source_folder / "cmake"
        
        if cmake_dir.exists():
            # OpenSSL has CMake support
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
            cmake.test()
        else:
            # Fallback to Perl Configure
            self.output.warn("CMake not available, using Perl Configure")
            self.run("perl Configure linux-x86_64 no-shared --prefix=%s" % self.package_folder)
            self.run(f"make -j{os.cpu_count() or 4}")
    
    def package(self):
        cmake = CMake(self)
        cmake.install()
    
    def package_info(self):
        self.cpp_info.libs = ["ssl", "crypto"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]
