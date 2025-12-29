import os
import sys
from conan import ConanFile
from conan.tools.files import copy, get, save
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.cmake import CMakeToolchain, CMake
from conan.tools.microsoft import MSBuildToolchain, MSBuild
from conan.errors import ConanException

class SpareToolsOpenSSLConan(ConanFile):
    """Production-grade OpenSSL with multiple build methods for SpareTools ecosystem."""

    name = "sparetools-openssl"
    version = "3.3.2"
    package_type = "library"
    description = "OpenSSL with multiple build methods (Perl Configure, CMake, Autotools)"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    topics = ("openssl", "cryptography", "ssl", "tls", "security")

    # Declare consumer context
    consumer_domain = "openssl"

    # Use SpareTools base utilities
    python_requires = "sparetools-base/2.0.3"
    python_requires_extend = "sparetools-base.SpareToolsSecurityMixin"

    # Build method selection
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_method": ["perl-configure", "cmake", "autotools"],
        "fips": [True, False],
        "no_threads": [True, False],
        "no_stdlib_check": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_method": "perl-configure",
        "fips": False,
        "no_threads": False,
        "no_stdlib_check": False,
    }

    # Platform settings
    settings = "os", "arch", "compiler", "build_type"

    # Source and export configuration
    exports_sources = (
        "src/*",
        "build-methods/*",
        "profiles/*",
        "CMakeLists.txt",
        "configure.ac",
    )

    def configure(self):
        """Apply OpenSSL-specific configuration."""
        # Platform-specific settings
        if self.settings.os == "Windows":
            # Windows doesn't support fPIC
            self.options.rm_safe("fPIC")

        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        """Set up build layout based on build method."""
        method = str(self.options.build_method)

        if method == "cmake":
            from conan.tools.cmake import cmake_layout
            cmake_layout(self)
        elif method == "autotools":
            from conan.tools.layout import basic_layout
            basic_layout(self)
        else:  # perl-configure (default)
            from conan.tools.layout import basic_layout
            basic_layout(self)

    def source(self):
        """Download OpenSSL source."""
        get(self,
            f"https://www.openssl.org/source/openssl-{self.version}.tar.gz",
            strip_root=True)

    def generate(self):
        """Generate build files based on selected method."""
        method = str(self.options.build_method)

        if method == "cmake":
            self._generate_cmake()
        elif method == "autotools":
            self._generate_autotools()
        else:  # perl-configure
            self._generate_perl_configure()

    def _generate_cmake(self):
        """Generate CMake build files."""
        tc = CMakeToolchain(self)

        # OpenSSL CMake variables
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["OPENSSL_BUILD_TYPE"] = str(self.settings.build_type).lower()
        tc.variables["OPENSSL_WITH_FIPS"] = self.options.fips
        tc.variables["OPENSSL_NO_THREADS"] = self.options.no_threads

        # Platform-specific settings
        if self.settings.os == "Windows":
            tc.variables["OPENSSL_TARGET"] = "VC-WIN64A" if self.settings.arch == "x86_64" else "VC-WIN32"

        tc.generate()

        from conan.tools.cmake import CMakeDeps
        deps = CMakeDeps(self)
        deps.generate()

    def _generate_autotools(self):
        """Generate Autotools build files."""
        tc = AutotoolsToolchain(self)
        tc.generate()

        from conan.tools.gnu import AutotoolsDeps
        deps = AutotoolsDeps(self)
        deps.generate()

    def _generate_perl_configure(self):
        """Generate Perl Configure build files."""
        tc = AutotoolsToolchain(self)
        tc.generate()

        from conan.tools.gnu import AutotoolsDeps
        deps = AutotoolsDeps(self)
        deps.generate()

    def build(self):
        """Build OpenSSL using selected method."""
        method = str(self.options.build_method)

        self.output.info(f"Building OpenSSL {self.version} using {method} method")

        if method == "cmake":
            self._build_cmake()
        elif method == "autotools":
            self._build_autotools()
        else:  # perl-configure
            self._build_perl_configure()

    def _build_cmake(self):
        """Build using CMake."""
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _build_autotools(self):
        """Build using Autotools."""
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def _build_perl_configure(self):
        """Build using Perl Configure (OpenSSL's native build system)."""
        # Use build-methods/perl_configure.py for the actual build logic
        build_script = os.path.join(self.source_folder, "build-methods", "perl_configure.py")
        if os.path.exists(build_script):
            # Import and run the build method
            sys.path.insert(0, os.path.join(self.source_folder, "build-methods"))
            try:
                import perl_configure
                perl_configure.build_openssl(self)
            finally:
                sys.path.remove(os.path.join(self.source_folder, "build-methods"))
        else:
            # Fallback to direct Perl Configure
            self._perl_configure_fallback()

    def _perl_configure_fallback(self):
        """Fallback Perl Configure build."""
        # Determine target based on platform
        target = self._get_openssl_target()

        configure_args = [
            f"--prefix={self.package_folder}",
            f"--openssldir={os.path.join(self.package_folder, 'ssl')}",
            "no-tests",  # Skip tests for faster builds
        ]

        if self.options.shared:
            configure_args.append("shared")
        else:
            configure_args.append("no-shared")

        if self.options.fips:
            configure_args.append("enable-fips")

        if self.options.no_threads:
            configure_args.append("no-threads")

        if self.options.no_stdlib_check:
            configure_args.append("-Wno-stdlib-check")

        # Run Perl Configure
        self.run(f"perl Configure {target} {' '.join(configure_args)}")

        # Build
        autotools = Autotools(self)
        autotools.make()
        autotools.install()

    def _get_openssl_target(self):
        """Get OpenSSL target string based on platform."""
        os_name = str(self.settings.os)
        arch = str(self.settings.arch)

        if os_name == "Linux":
            if arch == "x86_64":
                return "linux-x86_64"
            elif arch == "armv8":
                return "linux-aarch64"
            elif arch == "armv7":
                return "linux-armv4"
        elif os_name == "Macos":
            if arch == "x86_64":
                return "darwin64-x86_64"
            elif arch == "arm64":
                return "darwin64-arm64"
        elif os_name == "Windows":
            if arch == "x86_64":
                return "VC-WIN64A"
            else:
                return "VC-WIN32"

        # Default fallback
        return "linux-x86_64"

    def package(self):
        """Package OpenSSL binaries and headers."""
        # Copy built files to package folder
        if self.options.build_method == "cmake":
            cmake = CMake(self)
            cmake.install()
        elif self.options.build_method == "autotools":
            autotools = Autotools(self)
            autotools.install()
        # For perl-configure, files are already installed in _build_perl_configure

        # Copy additional files
        copy(self, "*.h", os.path.join(self.build_folder, "include"), os.path.join(self.package_folder, "include"), keep_path=True)
        copy(self, "*.a", os.path.join(self.build_folder, "lib"), os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.so*", os.path.join(self.build_folder, "lib"), os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib*", os.path.join(self.build_folder, "lib"), os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dll*", os.path.join(self.build_folder, "lib"), os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.lib", os.path.join(self.build_folder, "lib"), os.path.join(self.package_folder, "lib"), keep_path=False)

        # Copy SSL configuration
        copy(self, "*", os.path.join(self.build_folder, "ssl"), os.path.join(self.package_folder, "ssl"), keep_path=True)

        # Apply security gates and generate SBOM
        self.apply_security_gates()
        self.generate_sbom()

    def package_id(self):
        """Package ID based on options but not build settings."""
        # Clear build settings to make packages portable
        self.info.clear()

    def package_info(self):
        """Provide OpenSSL library information."""
        self.cpp_info.libs = ["ssl", "crypto"]

        # Include directories
        self.cpp_info.includedirs = ["include"]

        # System libraries that OpenSSL needs
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl", "pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "crypt32", "advapi32"]

        # Set OpenSSL environment
        self.runenv_info.define_path("OPENSSL_ROOT_DIR", self.package_folder)
        self.runenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))

        # Conf info for explicit discovery
        self.conf_info.define("user.openssl:executable", os.path.join(self.package_folder, "bin", "openssl"))
        self.conf_info.define("user.openssl:root", self.package_folder)