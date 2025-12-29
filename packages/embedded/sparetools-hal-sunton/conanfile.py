import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import copy

# Use SpareTools base utilities
python_requires = "sparetools-base/2.0.3"

class SpareToolsHalSuntonConan(ConanFile):
    name = "sparetools-hal-sunton"
    version = "1.0.0"
    package_type = "library"
    description = "Hardware Abstraction Layer for Sunton ESP32-2432S028Rv3 displays"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("esp32", "hal", "display", "sunton", "lvgl", "embedded")

    # Use sparetools-base utilities
    python_requires = "sparetools-base/2.0.3"

    # Export sources
    exports_sources = "CMakeLists.txt", "include/**", "src/**"

    # Settings and options
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_lvgl": [True, False],
        "with_touch": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_lvgl": True,
        "with_touch": True,
    }

    # Dependencies
    def requirements(self):
        if self.options.with_lvgl:
            self.requires("lvgl/8.3.11@sparetools/stable")
        # Add other HAL dependencies as needed

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        # Generate CMake toolchain and dependencies
        tc = CMakeToolchain(self)
        tc.variables["SPARETOOLS_HAL_SUNTON_WITH_LVGL"] = self.options.with_lvgl
        tc.variables["SPARETOOLS_HAL_SUNTON_WITH_TOUCH"] = self.options.with_touch
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

        # Copy additional files
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"), keep_path=True)
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"), keep_path=True)

        # Apply security gates and generate SBOM (placeholder)
        # self.apply_security_gates()
        # self.generate_sbom()

    def package_info(self):
        self.cpp_info.libs = ["sparetools-hal-sunton"]

        # Define components
        self.cpp_info.components["display"].libs = ["sparetools-hal-sunton-display"]
        self.cpp_info.components["display"].requires = ["lvgl::lvgl"] if self.options.with_lvgl else []

        if self.options.with_touch:
            self.cpp_info.components["touch"].libs = ["sparetools-hal-sunton-touch"]
            self.cpp_info.components["touch"].requires = ["display"]

        # Include directories
        self.cpp_info.includedirs = ["include"]

        # Definitions
        self.cpp_info.defines = [
            "SUNTON_ESP32_2432S028=1",
            "TFT_WIDTH=240",
            "TFT_HEIGHT=320"
        ]

        # ESP32 specific configuration
        if self.settings.os == "baremetal" or str(self.settings.os).startswith("esp"):
            self.cpp_info.defines.extend([
                "ESP32=1",
                "CONFIG_IDF_TARGET_ESP32=1"
            ])