import os
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools.files import copy

# Use SpareTools base utilities
python_requires = "sparetools-base/2.0.3"

class SpareToolsCryptoSuiteConan(ConanFile):
    name = "sparetools-crypto-suite"
    version = "1.0.0"
    package_type = "library"
    description = "Pre-configured cryptographic profiles for ESP32 with hardware acceleration"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("esp32", "cryptography", "security", "mbedTLS", "wolfSSL", "hardware-acceleration")

    # Use sparetools-base utilities
    python_requires = "sparetools-base/2.0.3"

    # Settings and options
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "crypto_backend": ["mbedTLS", "wolfSSL", "openssl"],
        "enable_hw_acceleration": [True, False],
        "enable_secure_boot": [True, False],
        "enable_flash_encryption": [True, False],
        "enable_psa_crypto": [True, False],
        "enable_fips": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "crypto_backend": "mbedTLS",
        "enable_hw_acceleration": True,
        "enable_secure_boot": False,
        "enable_flash_encryption": False,
        "enable_psa_crypto": True,
        "enable_fips": False,
    }

    # Dependencies
    def requirements(self):
        if self.options.crypto_backend == "mbedTLS":
            self.requires("mbedTLS/3.5.1")
        elif self.options.crypto_backend == "wolfSSL":
            self.requires("wolfSSL/5.6.6")
        elif self.options.crypto_backend == "openssl":
            self.requires("openssl/3.3.2")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        # Configure crypto backend options
        if self.options.crypto_backend == "mbedTLS":
            self.options["mbedTLS"].shared = self.options.shared
            self.options["mbedTLS"].enable_psa_crypto = self.options.enable_psa_crypto
            self.options["mbedTLS"].enable_fips = self.options.enable_fips
        elif self.options.crypto_backend == "wolfSSL":
            self.options["wolfSSL"].shared = self.options.shared
            self.options["wolfSSL"].enable_fips = self.options.enable_fips
        elif self.options.crypto_backend == "openssl":
            self.options["openssl"].shared = self.options.shared
            self.options["openssl"].fips = self.options.enable_fips

    def layout(self):
        cmake_layout(self)

    def generate(self):
        # Generate CMake toolchain and dependencies
        tc = CMakeToolchain(self)
        tc.variables["SPARETOOLS_CRYPTO_BACKEND"] = str(self.options.crypto_backend)
        tc.variables["SPARETOOLS_ENABLE_HW_ACCELERATION"] = self.options.enable_hw_acceleration
        tc.variables["SPARETOOLS_ENABLE_SECURE_BOOT"] = self.options.enable_secure_boot
        tc.variables["SPARETOOLS_ENABLE_FLASH_ENCRYPTION"] = self.options.enable_flash_encryption
        tc.variables["SPARETOOLS_ENABLE_PSA_CRYPTO"] = self.options.enable_psa_crypto
        tc.variables["SPARETOOLS_ENABLE_FIPS"] = self.options.enable_fips
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

        # Copy profile files
        copy(self, "*.json", src=os.path.join(self.source_folder, "src", "profiles"),
             dst=os.path.join(self.package_folder, "profiles"), keep_path=True)

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_info(self):
        self.cpp_info.libs = ["sparetools-crypto-suite"]

        # Define components based on crypto backend
        if self.options.crypto_backend == "mbedTLS":
            self.cpp_info.components["mbedTLS"].libs = ["sparetools-crypto-suite-mbedtls"]
            self.cpp_info.components["mbedTLS"].requires = ["mbedTLS::mbedTLS"]
        elif self.options.crypto_backend == "wolfSSL":
            self.cpp_info.components["wolfSSL"].libs = ["sparetools-crypto-suite-wolfssl"]
            self.cpp_info.components["wolfSSL"].requires = ["wolfSSL::wolfSSL"]
        elif self.options.crypto_backend == "openssl":
            self.cpp_info.components["openssl"].libs = ["sparetools-crypto-suite-openssl"]
            self.cpp_info.components["openssl"].requires = ["openssl::openssl"]

        # Include directories
        self.cpp_info.includedirs = ["include"]

        # Definitions
        defines = [
            f"SPARETOOLS_CRYPTO_BACKEND_{str(self.options.crypto_backend).upper()}=1",
        ]

        if self.options.enable_hw_acceleration:
            defines.append("SPARETOOLS_CRYPTO_HW_ACCELERATION=1")

        if self.options.enable_secure_boot:
            defines.append("SPARETOOLS_CRYPTO_SECURE_BOOT=1")

        if self.options.enable_flash_encryption:
            defines.append("SPARETOOLS_CRYPTO_FLASH_ENCRYPTION=1")

        if self.options.enable_psa_crypto:
            defines.append("SPARETOOLS_CRYPTO_PSA=1")

        if self.options.enable_fips:
            defines.append("SPARETOOLS_CRYPTO_FIPS=1")

        self.cpp_info.defines = defines

        # ESP32 specific configuration
        if self.settings.os == "baremetal" or str(self.settings.os).startswith("esp"):
            self.cpp_info.defines.extend([
                "ESP32=1",
                "CONFIG_IDF_TARGET_ESP32=1"
            ])

            if self.options.enable_hw_acceleration:
                self.cpp_info.defines.extend([
                    "CONFIG_MBEDTLS_HARDWARE_AES=1",
                    "CONFIG_MBEDTLS_HARDWARE_MPI=1",
                    "CONFIG_MBEDTLS_HARDWARE_SHA=1"
                ])