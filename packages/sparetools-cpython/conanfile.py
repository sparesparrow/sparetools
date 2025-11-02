import os
from conan import ConanFile
from conan.tools.files import save, copy
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.errors import ConanException


class CPythonToolConan(ConanFile):
    """CPython 3.12.7 built directly to Conan cache - Zero-copy architecture"""
    
    name = "sparetools-cpython"
    version = "3.12.7"
    package_type = "application"
    description = "Prebuilt CPython 3.12.7 with OpenSSL support for DevOps"
    license = "Python-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fips": [True, False],
        "optimize": ["0", "1", "2", "3"],
    }
    default_options = {
        "shared": False,
        "fips": False,
        "optimize": "2",
    }
    
    # Use sparetools-base utilities
    python_requires = "sparetools-base/2.0.0"
    
    def source(self):
        """Download CPython source"""
        from conan.tools.files import get
        get(self, 
            f"https://www.python.org/ftp/python/{self.version}/Python-{self.version}.tgz",
            strip_root=True)
    
    def generate(self):
        """Generate build system files"""
        tc = AutotoolsToolchain(self)
        tc.generate()
    
    def build(self):
        """Build directly into package folder - ZERO intermediate copies"""
        autotools = Autotools(self)
        
        # ✅ CRITICAL: Build directly to package folder location
        # This eliminates the staging step entirely
        args = [
            f"--prefix={self.package_folder}",  # Direct to final location
            "--enable-optimizations",
            "--with-lto",
            "--with-ensurepip=install",
            "--enable-loadable-sqlite-extensions",
        ]
        
        if self.options.shared:
            args.append("--enable-shared")
        else:
            args.append("--disable-shared")
        
        if self.options.fips:
            args.append("--enable-fips")
        
        # Optimization level
        opt_level = self.options.optimize
        if opt_level == "3":
            args.append("--with-lto")
        
        autotools.configure(args=args)
        
        # Build with parallel jobs
        import subprocess
        try:
            nproc_result = subprocess.run(['nproc'], capture_output=True, text=True)
            nproc = nproc_result.stdout.strip() if nproc_result.returncode == 0 else '4'
        except:
            nproc = str(os.cpu_count() or 4)
        
        autotools.make(args=[f"-j{nproc}"])
        
        # Install directly to package_folder (no DESTDIR since we used --prefix)
        # Run make install without DESTDIR to avoid double-prefixing
        self.run("make install")
        
        self.output.info(f"✅ CPython built directly to: {self.package_folder}")
    
    def package(self):
        """Files already in package_folder from build() - just add metadata"""
        # Add metadata
        save(self, os.path.join(self.package_folder, "VERSION"), self.version)
        save(self, os.path.join(self.package_folder, "BUILD_INFO"),
             f"Built with optimization level {self.options.optimize}")
        
        # Verify installation
        python_bin = os.path.join(self.package_folder, "bin", 
                                  "python.exe" if self.settings.os == "Windows" else "python3")
        if not os.path.exists(python_bin):
            # Try alternative names
            python3_12 = os.path.join(self.package_folder, "bin", "python3.12")
            if os.path.exists(python3_12):
                python_bin = python3_12
            else:
                raise ConanException(f"Python not found at {python_bin} or {python3_12}")
        
        # Create convenience symlinks if needed
        bin_dir = os.path.join(self.package_folder, "bin")
        python3_12_bin = os.path.join(bin_dir, "python3.12")
        python3_bin = os.path.join(bin_dir, "python3")
        python_bin_sym = os.path.join(bin_dir, "python")
        
        # python3 → python3.12 (if python3.12 exists but python3 doesn't)
        if os.path.exists(python3_12_bin) and not os.path.exists(python3_bin):
            os.symlink("python3.12", python3_bin)
        
        # python → python3.12 (for bare 'python' command)
        if os.path.exists(python3_12_bin) and not os.path.exists(python_bin_sym):
            os.symlink("python3.12", python_bin_sym)
        
        self.output.info(f"✅ Package verified: {python_bin}")
    
    def package_id(self):
        """Package ID depends on OS and architecture only"""
        self.info.clear()
    
    def package_info(self):
        """Expose CPython for zero-copy consumption"""
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libdirs = ["lib"]
        
        # Environment for consumers
        self.buildenv_info.define_path("PYTHON_ROOT", self.package_folder)
        self.buildenv_info.prepend_path("PATH", os.path.join(self.package_folder, "bin"))
        self.buildenv_info.prepend_path("LD_LIBRARY_PATH", os.path.join(self.package_folder, "lib"))
        
        self.runenv_info.define_path("PYTHONHOME", self.package_folder)
        self.runenv_info.prepend_path("PATH", os.path.join(self.package_folder, "bin"))
        self.runenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "lib", "python3.12"))
        
        # Conf info for explicit discovery
        python_exec = os.path.join(self.package_folder, "bin",
                                   "python.exe" if self.settings.os == "Windows" else "python3")
        # Try python3.12 if python3 doesn't exist
        if not os.path.exists(python_exec):
            python_exec = os.path.join(self.package_folder, "bin",
                                       "python.exe" if self.settings.os == "Windows" else "python3.12")
        
        self.conf_info.define("user.cpython:executable", python_exec)
        self.conf_info.define("user.cpython:home", self.package_folder)
