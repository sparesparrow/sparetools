from pathlib import Path
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import build_jobs
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout


class SpareToolsOpenSSLHybrid(ConanFile):
    """Hybrid OpenSSL build using Perl Configure plus Python enhancement."""

    name = "sparetools-openssl-hybrid"
    version = "3.3.2"

    package_type = "library"
    description = "OpenSSL built with hybrid Python-enhanced approach"
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

    python_requires = "sparetools-openssl-tools/1.1.0"

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(
            self,
            "https://github.com/openssl/openssl/archive/refs/tags/openssl-3.3.2.tar.gz",
            strip_root=True,
        )

    def build(self):
        openssl_tools = self.python_requires["sparetools-openssl-tools"].module
        hybrid = openssl_tools.openssl.hybrid_builder

        config = hybrid.HybridBuildConfig(
            source_dir=Path(self.source_folder),
            install_prefix=Path(self.package_folder),
            openssl_target=self._openssl_target,
            shared=bool(self.options.shared),
            enable_fips=False,
            jobs=build_jobs(self),
        )

        hybrid.run_hybrid_build(config)

    def package(self):
        copy(
            self,
            "LICENSE.txt",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
            keep_path=False,
        )

    def package_info(self):
        self.cpp_info.libs = ["ssl", "crypto"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]

    @property
    def _openssl_target(self) -> str:
        os_name = str(self.settings.os)
        arch = str(self.settings.arch)
        if os_name == "Linux" and arch == "x86_64":
            return "linux-x86_64"
        if os_name == "Linux" and arch in {"armv8", "aarch64"}:
            return "linux-aarch64"
        if os_name == "Macos" and arch == "x86_64":
            return "darwin64-x86_64-cc"
        if os_name == "Macos" and arch in {"armv8", "armv8.3", "arm64"}:
            return "darwin64-arm64-cc"
        raise ConanInvalidConfiguration(f"Unsupported platform combination: {os_name}/{arch}")
