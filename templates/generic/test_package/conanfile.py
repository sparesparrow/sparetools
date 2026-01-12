from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake

class {{class_name}}TestPackage(ConanFile):
    name = 'generic-test'
    version = '1.0.0'
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        # Run tests if available
        cmake = CMake(self)
        cmake.test()