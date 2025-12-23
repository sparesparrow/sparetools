from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake
from conan.tools.layout import basic_layout
from conan.tools.files import copy
import os

# Import SpareTools version management
try:
    from sparetools_base import SpareToolsVersions
    versions = SpareToolsVersions.versions
except ImportError:
    # Fallback versions if sparetools-base is not available
    versions = {
        "cpython": "3.12.7",
        "test-harness": "2.0.0",
        "gtest": "1.14.0",
        "shared-dev-tools": "2.0.0",
        "bootstrap": "2.0.0",
        "openssl": "3.3.2",
        "lvgl": "8.3.11"
    }


class SpareToolsNucleusConan(ConanFile):
    """NucleusESP32 Conan package - SpareTools ESP32 consumer implementation."""

    name = "sparetools-nucleus"
    version = "0.1.0"
    package_type = "application"

    # This is an ESP32 consumer package in the SpareTools ecosystem
    python_requires = "sparetools-base/2.0.3"

    # Optional metadata
    license = "MIT"
    author = "SpareTools Team"
    url = "https://github.com/sparesparrow/NucleusESP32"
    description = "NucleusESP32 - ESP32-based multi-tool device firmware (SpareTools consumer)"
    topics = ("esp32", "embedded", "rf", "nfc", "iot", "sparetools", "consumer")

    # Binary configuration - focus on host testing, not ESP32 cross-compilation
    settings = "os", "compiler", "build_type", "arch"

    # Options for ESP32-specific features
    options = {
        "with_display": [True, False],
        "with_crypto": [True, False],
        "with_secure_boot": [True, False],
        "target_board": ["esp32", "esp32s3", "esp32c3", "esp32c6"],
    }
    default_options = {
        "with_display": True,
        "with_crypto": True,
        "with_secure_boot": False,
        "target_board": "esp32s3",
    }

    # Sources are located in the same place as this recipe
    exports_sources = "CMakeLists.txt", "src/*", "include/*", "test/*", "test_harness/*", "platformio.ini"

    def layout(self):
        basic_layout(self, src_folder=".")

    def build_requirements(self):
        # ESP32 consumer foundation packages - use dynamic versions
        self.tool_requires(f"sparetools-cpython/{versions['cpython']}")
        self.tool_requires(f"sparetools-test-harness/{versions['test-harness']}")
        self.tool_requires(f"sparetools-shared-dev-tools/{versions['shared-dev-tools']}")
        # Note: bootstrap is used at environment setup time, not build time

    def requirements(self):
        # Testing framework for host-based C++ unit tests - use dynamic version
        self.requires(f"gtest/{versions['gtest']}")

        # Add new enterprise packages for ESP32 development
        if self.options.with_display:
            self.requires("sparetools-hal-sunton/1.0.0")
            self.requires(f"lvgl/{versions['lvgl']}")

        if self.options.with_crypto:
            self.requires("sparetools-crypto-suite/1.0.0")
            self.requires(f"openssl/{versions['openssl']}")

    def configure(self):
        # Configure crypto suite options based on security requirements
        if self.options.with_crypto:
            if self.options.with_secure_boot:
                self.options["sparetools-crypto-suite"].enable_secure_boot = True
                self.options["sparetools-crypto-suite"].enable_flash_encryption = True
                self.options["sparetools-crypto-suite"].crypto_backend = "mbedTLS"
                self.options["sparetools-crypto-suite"].enable_hw_acceleration = True
                self.options["sparetools-crypto-suite"].enable_fips = True

        # Configure HAL for specific board
        if self.options.with_display and self.options.target_board == "esp32s3":
            self.options["sparetools-hal-sunton"].with_lvgl = True
            self.options["sparetools-hal-sunton"].with_touch = True

    def generate(self):
        # Generate CMake toolchain and dependencies for host testing
        tc = CMakeToolchain(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        # Copy test harness Python modules
        if os.path.exists(os.path.join(self.source_folder, "test_harness")):
            copy(self, "test_harness/**/*.py",
                 src=self.source_folder,
                 dst=os.path.join(self.package_folder, "test_harness"))

    def package_info(self):
        # Define components for different modules (when built)
        # self.cpp_info.components["rf_module"].libs = ["rf"]
        # self.cpp_info.components["nfc_module"].libs = ["nfc"]
        # self.cpp_info.components["ir_module"].libs = ["ir"]

        # Python test environment setup
        self.buildenv_info.define("NUCLEUS_PACKAGE_DIR", self.package_folder)
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)
        if os.path.exists(os.path.join(self.package_folder, "test_harness")):
            self.buildenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "test_harness"))

        self.runenv_info.define("NUCLEUS_PACKAGE_DIR", self.package_folder)
        self.runenv_info.append_path("PYTHONPATH", self.package_folder)
        if os.path.exists(os.path.join(self.package_folder, "test_harness")):
            self.runenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "test_harness"))

        # Mark as development package
        self.cpp_info.libs = []