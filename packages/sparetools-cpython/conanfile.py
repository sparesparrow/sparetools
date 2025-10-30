import os
from conan import ConanFile
from conan.tools.files import copy, save


class CPythonToolConan(ConanFile):
    """Prebuilt CPython 3.12.7 for OpenSSL DevOps ecosystem"""
    
    name = "sparetools-cpython"
    version = "3.12.7"
    package_type = "application"
    description = "Prebuilt CPython 3.12.7 with OpenSSL support for DevOps"
    license = "Python-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    
    # Optional: Use sparetools-base utilities if needed
    # python_requires = "sparetools-base/1.0.0"
    
    settings = "os", "arch", "compiler", "build_type"
    
    def export_sources(self):
        """No sources needed for prebuilt package"""
        pass
    
    def package(self):
        """Package prebuilt CPython from staging directory"""
        staging = "/tmp/cpython-3.12.7-staging/usr/local"
        
        if not os.path.exists(staging):
            raise Exception(
                f"Staging directory not found: {staging}"
                f"Run: make install DESTDIR=/tmp/cpython-3.12.7-staging"
            )
        
        # Copy all files using Conan's copy tool
        copy(self, "*", src=staging, dst=self.package_folder, keep_path=True)
        
        # Add metadata files
        save(self, os.path.join(self.package_folder, "VERSION"), f"{self.version}")
        save(self, os.path.join(self.package_folder, "BUILD_INFO"),
             "Built with --enable-optimizations --with-lto --enable-shared")
        
        # Create convenience symlinks
        bin_dir = os.path.join(self.package_folder, "bin")
        python3_12_bin = os.path.join(bin_dir, "python3.12")
        python3_bin = os.path.join(bin_dir, "python3")
        python_bin = os.path.join(bin_dir, "python")
        
        # python3 → python3.12
        if os.path.exists(python3_12_bin) and not os.path.exists(python3_bin):
            os.symlink("python3.12", python3_bin)
        
        # python → python3.12 (for bare 'python' command)
        if os.path.exists(python3_12_bin) and not os.path.exists(python_bin):
            os.symlink("python3.12", python_bin)


    def package_id(self):
        """Package ID depends on OS and architecture only"""
        self.info.clear()    

    def package_info(self):
        """Expose package information and environment setup"""
    
        # Paths for binary discovery
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libdirs = ["lib"]
    
        # Build environment (for packages that depend on this at build time)
        self.buildenv_info.define_path("PYTHONHOME", self.package_folder)
        self.buildenv_info.prepend_path("PATH", os.path.join(self.package_folder, "bin"))
        self.buildenv_info.prepend_path("LD_LIBRARY_PATH", os.path.join(self.package_folder, "lib"))
    
        # Runtime environment (Conan 2.x API - replaces env_info)
        self.runenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "lib", "python3.12"))
        self.runenv_info.prepend_path("PATH", os.path.join(self.package_folder, "bin"))
        self.runenv_info.prepend_path("LD_LIBRARY_PATH", os.path.join(self.package_folder, "lib"))
    
        # Optional: Custom conf for explicit Python discovery (safe namespace)
        python_exec = os.path.join(self.package_folder, "bin", "python3.12")
        self.conf_info.define("user.python:executable", python_exec)
        self.conf_info.define("user.python:home", self.package_folder)

