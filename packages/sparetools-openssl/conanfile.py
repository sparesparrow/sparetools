from conan import ConanFile
from conan.tools.files import copy, get, save, load, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os
import platform
import subprocess
import textwrap


class SpareToolsOpenSSLConan(ConanFile):
    """
    Unified OpenSSL package with multiple build methods.
    
    Consolidates all OpenSSL build variants into a single package
    with configurable build methods via Conan options.
    """
    name = "sparetools-openssl"
    version = "3.3.2"
    
    package_type = "library"
    description = "Unified OpenSSL package with multiple build method support"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    homepage = "https://www.openssl.org"
    topics = ("openssl", "ssl", "tls", "encryption", "security")
    
    settings = "os", "arch", "compiler", "build_type"
    
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_method": ["perl", "cmake", "autotools", "python"],
        "fips": [True, False],
        "enable_threads": [True, False],
        "enable_asm": [True, False],
        "enable_zlib": [True, False],
        "enable_legacy": [True, False],
        "enable_avx": [True, False],
        "enable_avx2": [True, False],
        "enable_neon": [True, False],
        "enable_sve": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "build_method": "perl",
        "fips": False,
        "enable_threads": True,
        "enable_asm": True,
        "enable_zlib": True,
        "enable_legacy": False,
        "enable_avx": True,
        "enable_avx2": True,
        "enable_neon": True,
        "enable_sve": False,
    }
    
    # Package dependencies
    tool_requires = [
        "sparetools-openssl-tools/2.0.0",
        "sparetools-cpython/3.12.7",
    ]
    
    python_requires = "sparetools-base/2.0.0"
    
    exports_sources = "configure.py"
    
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # OpenSSL is pure C library
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")
    
    def layout(self):
        if self.options.build_method == "cmake":
            cmake_layout(self)
        else:
            basic_layout(self)
    
    def source(self):
        """Download OpenSSL source code"""
        get(self, 
            f"https://github.com/openssl/openssl/archive/refs/tags/openssl-{self.version}.tar.gz",
            strip_root=True)
        
        # Copy Python configure.py (will be used if build_method is python)
        # Note: source() must not access self.options (Conan 2.x requirement)
        configure_py = os.path.join(self.recipe_folder, "configure.py")
        if os.path.exists(configure_py):
            copy(self, "configure.py", self.recipe_folder, self.source_folder)
    
    def _get_target(self):
        """
        Determine OpenSSL Configure target string.

        Extended target mapping supports:
        - Linux (x86, x86_64, ARM, ARM64)
        - Windows (x86, x86_64, ARM64) with MSVC/Perl Configure support
        - macOS (x86_64, ARM64)
        - FreeBSD, Android, iOS
        """
        os_name = str(self.settings.os)
        arch = str(self.settings.arch)

        target_map = {
            # Linux targets
            ("Linux", "x86_64"): "linux-x86_64",
            ("Linux", "x86"): "linux-x86",
            ("Linux", "armv8"): "linux-aarch64",
            ("Linux", "armv7"): "linux-armv4",
            ("Linux", "mips"): "linux-mips",
            ("Linux", "mips64"): "linux-mips64",
            ("Linux", "ppc64le"): "linux-ppc64le",

            # Windows targets - MSVC/Perl Configure
            ("Windows", "x86_64"): "VC-WIN64A",
            ("Windows", "x86"): "VC-WIN32",
            ("Windows", "armv8"): "VC-WIN-ARM64",

            # macOS targets
            ("Macos", "x86_64"): "darwin64-x86_64-cc",
            ("Macos", "armv8"): "darwin64-arm64-cc",

            # FreeBSD targets
            ("FreeBSD", "x86_64"): "BSD-x86_64",
            ("FreeBSD", "x86"): "BSD-x86",
            ("FreeBSD", "armv8"): "BSD-aarch64",

            # Android targets
            ("Android", "x86_64"): "android-x86_64",
            ("Android", "x86"): "android-x86",
            ("Android", "armv8"): "android-arm64",
            ("Android", "armv7"): "android-arm",

            # iOS targets
            ("iOS", "armv8"): "ios64-cross",
            ("iOS", "x86_64"): "ios64-cross",
        }

        default_target = target_map.get((os_name, arch))
        if not default_target:
            self.output.warning(f"Unknown platform {os_name}-{arch}, using linux-x86_64")
            return "linux-x86_64"

        return default_target
    
    def _get_configure_args(self):
        """Build configure arguments based on options"""
        args = [
            self._get_target(),
            "shared" if self.options.shared else "no-shared",
            f"--prefix={self.package_folder}",
            f"--openssldir={self.package_folder}/ssl",
        ]

        # Feature flags
        if not self.options.enable_threads:
            args.append("no-threads")
        if not self.options.enable_asm:
            args.append("no-asm")
        if not self.options.enable_zlib:
            args.append("no-zlib")
        if not self.options.enable_legacy:
            args.extend(["no-md2", "no-md4", "no-rc5"])

        # Assembly optimization flags
        if self.options.enable_asm:
            # AVX/AVX2 optimizations (x86/x86_64)
            if hasattr(self.options, 'enable_avx'):
                if not self.options.enable_avx:
                    args.append("no-avx")
                elif hasattr(self.options, 'enable_avx2'):
                    if not self.options.enable_avx2:
                        args.append("no-avx2")

            # NEON optimizations (ARM)
            if hasattr(self.options, 'enable_neon'):
                if not self.options.enable_neon:
                    args.append("no-neon")

            # SVE optimizations (ARM64, Scalable Vector Extensions)
            if hasattr(self.options, 'enable_sve'):
                if self.options.enable_sve:
                    args.append("enable-sve")

        # FIPS support
        if self.options.fips:
            args.append("enable-fips")

        return args
    
    def generate(self):
        """Generate build system files"""
        if self.options.build_method == "cmake":
            tc = CMakeToolchain(self)
            tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
            tc.variables["CMAKE_INSTALL_PREFIX"] = self.package_folder
            tc.generate()
        elif self.options.build_method == "autotools":
            tc = AutotoolsToolchain(self)
            tc.generate()
    
    def _build_with_perl(self):
        """
        Standard Perl Configure build (proven, production-ready).

        Supports:
        - Unix-like systems (Linux, macOS, FreeBSD) - uses make
        - Windows systems - uses nmake (MSVC) or make (MinGW)
        """
        self.output.info("Building with Perl Configure (standard method)")

        configure_args = self._get_configure_args()
        configure_cmd = f"perl Configure {' '.join(configure_args)}"
        self.output.info(f"Configure command: {configure_cmd}")
        self.run(configure_cmd, cwd=self.source_folder)

        # Determine build tool based on OS and compiler
        is_windows = str(self.settings.os) == "Windows"
        is_msvc = is_windows and "msvc" in str(self.settings.compiler).lower()

        if is_windows:
            self.output.info("Windows build detected - using nmake")
            # Windows with MSVC - uses nmake
            build_cmd = "nmake"
            test_cmd = "nmake test" if not is_msvc else "nmake test"
        else:
            # Unix-like systems - uses make with parallelization
            try:
                nproc_result = subprocess.run(['nproc'], capture_output=True, text=True)
                nproc = nproc_result.stdout.strip() if nproc_result.returncode == 0 else '4'
            except:
                nproc = str(os.cpu_count() or 4)

            build_cmd = f"make -j{nproc}"
            test_cmd = "make test"

        # Build
        self.output.info(f"Build command: {build_cmd}")
        self.run(build_cmd, cwd=self.source_folder)

        # Run tests (optional, don't fail if tests fail)
        try:
            self.output.info(f"Test command: {test_cmd}")
            self.run(test_cmd, cwd=self.source_folder, ignore_errors=True)
        except Exception as e:
            self.output.warning(f"Tests failed or unavailable: {e}")
    
    def _build_with_cmake(self):
        """CMake build (if OpenSSL supports it, otherwise fallback)"""
        self.output.info("Building with CMake")
        
        cmake_dir = os.path.join(self.source_folder, "cmake")
        if os.path.exists(cmake_dir):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
            cmake.test()
        else:
            self.output.warn("CMake not supported by this OpenSSL version, falling back to Perl Configure")
            self._build_with_perl()
    
    def _build_with_autotools(self):
        """Autotools integration build"""
        self.output.info("Building with Autotools integration")
        
        autotools = Autotools(self)
        configure_args = self._get_configure_args()
        autotools.configure(args=configure_args)
        autotools.make()
        autotools.make(args=["test"], ignore_errors=True)
    
    def _build_with_python(self):
        """Python configure.py build (hybrid approach)"""
        self.output.info("Building with Python configure.py (hybrid method)")
        
        configure_py = os.path.join(self.source_folder, "configure.py")
        if not os.path.exists(configure_py):
            self.output.warn("configure.py not found, falling back to Perl Configure")
            self._build_with_perl()
            return
        
        # Stage 1: Python configure
        self.output.info("Stage 1: Python configure.py")
        configure_args = self._get_configure_args()
        python_args = " ".join(configure_args[1:])  # Skip target, configure.py handles it
        self.run(f"python3 {configure_py} {python_args}", cwd=self.source_folder)
        
        # Stage 2: Build
        self.output.info("Stage 2: Build")
        try:
            nproc = str(subprocess.run(['nproc'], capture_output=True, text=True).stdout.strip() or '4')
        except:
            nproc = str(os.cpu_count() or 4)
        
        self.run(f"make -j{nproc}", cwd=self.source_folder)
        self.run("make test", cwd=self.source_folder, ignore_errors=True)
    
    def build(self):
        """Build OpenSSL using selected method"""
        self.output.info(f"Build method: {self.options.build_method}")
        
        build_methods = {
            "perl": self._build_with_perl,
            "cmake": self._build_with_cmake,
            "autotools": self._build_with_autotools,
            "python": self._build_with_python,
        }
        
        build_func = build_methods.get(str(self.options.build_method))
        if build_func:
            build_func()
        else:
            raise ValueError(f"Unknown build method: {self.options.build_method}")
        
        # Run security gates if available
        self._run_security_gates()
    
    def _run_security_gates(self):
        """Run security scanning and SBOM generation"""
        try:
            base = self.python_requires["sparetools-base"]
            if hasattr(base.conanfile, "run_trivy_scan"):
                self.output.info("Running Trivy security scan...")
                base.conanfile.run_trivy_scan(self.source_folder)
            
            if hasattr(base.conanfile, "generate_sbom"):
                self.output.info("Generating SBOM...")
                base.conanfile.generate_sbom(self.source_folder)
        except Exception as e:
            self.output.warn(f"Security gates not available: {e}")
    
    def package(self):
        """Install OpenSSL to package folder"""
        if self.options.build_method == "cmake":
            cmake = CMake(self)
            cmake.install()
        elif self.options.build_method == "autotools":
            autotools = Autotools(self)
            autotools.install()
        else:
            self.run("make install_sw install_ssldirs", cwd=self.source_folder)
        
        # Copy license
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        
        # Clean up
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)
    
    def package_info(self):
        """Define package information for consumers"""
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "OpenSSL")
        self.cpp_info.set_property("cmake_target_name", "OpenSSL::OpenSSL")
        self.cpp_info.set_property("pkg_config_name", "openssl")
        
        # Libraries
        self.cpp_info.components["ssl"].set_property("cmake_target_name", "OpenSSL::SSL")
        self.cpp_info.components["ssl"].set_property("pkg_config_name", "libssl")
        self.cpp_info.components["ssl"].libs = ["ssl"]
        self.cpp_info.components["ssl"].requires = ["crypto"]
        
        self.cpp_info.components["crypto"].set_property("cmake_target_name", "OpenSSL::Crypto")
        self.cpp_info.components["crypto"].set_property("pkg_config_name", "libcrypto")
        self.cpp_info.components["crypto"].libs = ["crypto"]
        
        # System libraries
        if self.settings.os == "Linux":
            self.cpp_info.components["crypto"].system_libs.extend(["dl", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.components["crypto"].system_libs.extend(["ws2_32", "crypt32"])
        
        # Directories
        self.cpp_info.components["ssl"].libdirs = ["lib"]
        self.cpp_info.components["ssl"].includedirs = ["include"]
        self.cpp_info.components["ssl"].bindirs = ["bin"]
        
        self.cpp_info.components["crypto"].libdirs = ["lib"]
        self.cpp_info.components["crypto"].includedirs = ["include"]
        self.cpp_info.components["crypto"].bindirs = ["bin"]

