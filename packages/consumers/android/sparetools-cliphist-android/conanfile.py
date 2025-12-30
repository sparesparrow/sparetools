import os
import sys
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy

# Import base class from shared scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../scripts'))
from recipe_base import ConsumerPackageConan


class SpareToolsClipHistAndroidConan(ConsumerPackageConan):
    name = "sparetools-cliphist-android"
    version = "1.0.1"
    package_type = "application"
    description = "ClipHist Android consumer application for SpareTools ecosystem"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("android", "clipboard", "encryption", "security")

    # Declare consumer context
    consumer_domain = "android"

    # Android-specific settings
    settings = "os", "arch", "compiler", "build_type"

    # Use SpareTools base utilities
    python_requires = "sparetools-base/2.0.3"

    # Android-specific tool requirements
    tool_requires = (
        "gradle/8.5",
        "android-ndk/r25b",
        "android-sdk/34"
    )

    # Source files to export
    exports_sources = (
        "CMakeLists.txt",
        "app/**",
        "build.gradle.kts",
        "settings.gradle.kts",
        "gradle/**",
        "src/**"
    )

    def layout(self):
        cmake_layout(self)

    def generate(self):
        # Generate CMake toolchain for Android
        tc = CMakeToolchain(self)
        tc.variables["ANDROID_ABI"] = self._get_android_abi()
        tc.variables["ANDROID_PLATFORM"] = "android-21"
        tc.variables["CMAKE_TOOLCHAIN_FILE"] = self._get_ndk_toolchain()
        tc.generate()

        # Generate dependencies
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        # Use Gradle to build Android APK
        if self.conf.get("tools.android:gradle_command", default="gradle", check_type=str):
            gradle_cmd = self.conf.get("tools.android:gradle_command")
        else:
            gradle_cmd = "gradle"

        self.run(f"{gradle_cmd} assembleDebug")

    def package(self):
        # Package the built APK and related files
        copy(self, "*.apk", src=os.path.join(self.build_folder, "app/build/outputs/apk/debug"),
             dst=os.path.join(self.package_folder, "apk"), keep_path=False)
        copy(self, "*.aar", src=os.path.join(self.build_folder, "app/build/outputs/aar"),
             dst=os.path.join(self.package_folder, "aar"), keep_path=False)

        # Copy source files for development
        super().package()

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def _get_android_abi(self):
        """Map Conan architecture to Android ABI."""
        arch_map = {
            "armv7": "armeabi-v7a",
            "armv8": "arm64-v8a",
            "x86": "x86",
            "x86_64": "x86_64"
        }
        return arch_map.get(str(self.settings.arch), "arm64-v8a")

    def _get_ndk_toolchain(self):
        """Get Android NDK toolchain file path."""
        ndk_path = self.dependencies["android-ndk"].package_folder
        return os.path.join(ndk_path, "build", "cmake", "android.toolchain.cmake")