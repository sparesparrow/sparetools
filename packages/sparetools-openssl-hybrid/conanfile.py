from conan import ConanFile
from conan.tools.files import copy, get
import os
import subprocess

class SpareToolsOpenSSLHybrid(ConanFile):
    """
    OpenSSL built with multi-stage approach:
    Stage 1: Perl Configure (proven)
    Stage 2: Python enhancement (your script)
    Stage 3: Build
    """
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
    
    def source(self):
        get(self,
            "https://github.com/openssl/openssl/archive/refs/tags/openssl-3.3.2.tar.gz",
            strip_root=True)
        
        # Copy your Python configure.py for enhancement step
        configure_py = os.path.join(self.recipe_folder, "..", "..", "openssl", "configure.py")
        if os.path.exists(configure_py):
            copy(self, "configure.py", os.path.dirname(configure_py), self.source_folder)
    
    def build(self):
        """Multi-stage build with Python enhancement"""
        
        # Stage 1: Perl Configure (generates correct headers/dependencies)
        self.output.info("Stage 1: Perl Configure (proven method)")
        configure_args = [
            "linux-x86_64",
            "no-shared" if not self.options.shared else "shared",
            f"--prefix={self.package_folder}",
            f"--openssldir={self.package_folder}/ssl",
        ]
        self.run(f"perl Configure {' '.join(configure_args)}", cwd=self.source_folder)
        
        # Stage 2: Python enhancement (adds SpareTools features)
        configure_py = os.path.join(self.source_folder, "configure.py")
        if os.path.exists(configure_py):
            self.output.info("Stage 2: Python enhancement (SpareTools features)")
            self.run(f"python3 {configure_py} enhance --makefile-only", 
                    cwd=self.source_folder, ignore_errors=True)
        
        # Stage 3: Build
        self.output.info("Stage 3: Build")
        try:
            nproc_result = subprocess.run(['nproc'], capture_output=True, text=True)
            nproc = nproc_result.stdout.strip() if nproc_result.returncode == 0 else '4'
        except:
            nproc = '4'
        
        self.run(f"make -j{nproc}", cwd=self.source_folder)
        self.run("make test", cwd=self.source_folder, ignore_errors=True)
    
    def package(self):
        self.run("make install", cwd=self.source_folder)
    
    def package_info(self):
        self.cpp_info.libs = ["ssl", "crypto"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.bindirs = ["bin"]
