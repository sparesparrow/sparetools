from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake
import os


class SpareToolsOpenSSLTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"
    test_type = "explicit"
    options = {
        "test_provider": ["default", "legacy", "all"],
        "test_fips": [True, False]
    }
    default_options = {
        "test_provider": "default",
        "test_fips": False
    }

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            cmake = CMake(self)

            # Run basic test first
            bin_path = os.path.join(self.cpp.build.bindir, "test_openssl")
            self.run(bin_path, env="conanrun")

            # Run provider ordering tests if enabled
            if self.options.test_provider in ["default", "all"]:
                provider_test_path = os.path.join(self.cpp.build.bindir, "test_provider_ordering")
                self.run(provider_test_path, env="conanrun")

            # Run FIPS smoke tests if enabled
            if self.options.test_fips:
                fips_test_path = os.path.join(self.cpp.build.bindir, "test_fips_smoke")
                self.run(fips_test_path, env="conanrun")

            # Run all tests via ctest if available
            cmake.test()

