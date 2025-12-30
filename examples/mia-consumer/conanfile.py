from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy


class MIAConsumerConan(ConanFile):
    """
    Example MIA consumer demonstrating how to use sparetools packages.
    
    This example shows:
    - How to import sparetools packages from Cloudsmith remote
    - Proper dependency declarations
    - Usage patterns for OpenSSL and other tools
    """
    
    name = "mia-consumer-example"
    version = "1.0.1"
    package_type = "application"
    
    settings = "os", "arch", "compiler", "build_type"
    
    # Dependencies on sparetools packages
    requires = [
        "sparetools-openssl/3.3.2",
    ]
    
    tool_requires = [
        "cmake/[>=3.20]",
    ]
    
    # Use sparetools utilities if needed
    python_requires = "sparetools-base/2.0.0"
    
    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def package(self):
        cmake = CMake(self)
        cmake.install()
    
    def package_info(self):
        self.cpp_info.libs = []
