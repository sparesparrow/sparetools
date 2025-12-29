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
        "protocols": "1.0.0"
    }


class SpareToolsBpmDetectorConan(ConanFile):
    """ESP32 BPM Detector Conan package - SpareTools ESP32 consumer implementation."""

    name = "sparetools-bpm-detector"
    version = "0.1.0"
    package_type = "application"

    # This is an ESP32 consumer package in the SpareTools ecosystem
    python_requires = "sparetools-base/2.0.3"

    # Optional metadata
    license = "MIT"
    author = "SpareTools Team"
    url = "https://github.com/sparesparrow/esp32-bpm-detector"
    description = "ESP32 BPM Detector - Real-time beat detection firmware (SpareTools consumer)"
    topics = ("esp32", "bpm", "audio", "embedded", "dsp", "sparetools", "consumer")

    # Binary configuration - focus on host testing, not ESP32 cross-compilation
    settings = "os", "compiler", "build_type", "arch"

    # Options for BPM detector-specific features
    options = {
        "with_display": [True, False],
        "with_networking": [True, False],
        "with_websocket": [True, False],
        "with_audio_calibration": [True, False],
        "target_board": ["esp32", "esp32s2", "esp32s3", "esp32c3"],
    }
    default_options = {
        "with_display": True,
        "with_networking": True,
        "with_websocket": True,
        "with_audio_calibration": True,
        "target_board": "esp32s3",
    }

    # Sources are located in the same place as this recipe
    exports_sources = "CMakeLists.txt", "src/*", "include/*", "test/*", "scripts/*", "platformio.ini"

    def layout(self):
        basic_layout(self, src_folder=".")

    def build_requirements(self):
        # ESP32 consumer foundation packages - use dynamic versions
        self.tool_requires(f"sparetools-cpython/{versions['cpython']}")
        self.tool_requires(f"sparetools-test-harness/{versions['test-harness']}")
        self.tool_requires(f"sparetools-shared-dev-tools/{versions['shared-dev-tools']}")
        # Note: bootstrap is used at environment setup time, not build time

    def requirements(self):
        # BPM protocol schemas from SpareTools foundation
        self.requires(f"sparetools-bpm-schemas/2.0.0")

        # Testing framework for host-based C++ unit tests - use dynamic version
        self.requires(f"gtest/{versions['gtest']}")

        # ESP32 firmware package (from existing consumer)
        self.requires("sparetools-hal-sunton/1.0.0@sparetools/stable")

        # Audio processing dependencies (if available)
        # self.requires("sparetools-dsp/1.0.0")  # Future package

    def configure(self):
        # Configure HAL for specific board
        if self.options.target_board == "esp32s3":
            self.options["sparetools-hal-sunton"].with_lvgl = self.options.with_display
            self.options["sparetools-hal-sunton"].with_touch = False  # BPM detector doesn't need touch

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

        # Copy test scripts and utilities
        if os.path.exists(os.path.join(self.source_folder, "scripts")):
            copy(self, "scripts/**/*.py",
                 src=self.source_folder,
                 dst=os.path.join(self.package_folder, "scripts"))

        if os.path.exists(os.path.join(self.source_folder, "tests")):
            copy(self, "tests/**/*.py",
                 src=self.source_folder,
                 dst=os.path.join(self.package_folder, "tests"))

    def package_info(self):
        # Define components for different modules (when built)
        # BPM detection core
        # self.cpp_info.components["bpm_core"].libs = ["bpm_detector"]
        # self.cpp_info.components["audio_processor"].libs = ["audio_processor"]
        # self.cpp_info.components["networking"].libs = ["network_handler"]

        # Python test environment setup
        self.buildenv_info.define("BPM_DETECTOR_PACKAGE_DIR", self.package_folder)
        self.buildenv_info.append_path("PYTHONPATH", self.package_folder)

        if os.path.exists(os.path.join(self.package_folder, "scripts")):
            self.buildenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "scripts"))

        if os.path.exists(os.path.join(self.package_folder, "tests")):
            self.buildenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "tests"))

        self.runenv_info.define("BPM_DETECTOR_PACKAGE_DIR", self.package_folder)
        self.runenv_info.append_path("PYTHONPATH", self.package_folder)

        if os.path.exists(os.path.join(self.package_folder, "scripts")):
            self.runenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "scripts"))

        if os.path.exists(os.path.join(self.package_folder, "tests")):
            self.runenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "tests"))

        # Mark as development package
        self.cpp_info.libs = []