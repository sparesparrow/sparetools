from conan import ConanFile
from conan.tools.files import copy

class SpareToolsBootstrapConan(ConanFile):
    name = "sparetools-bootstrap"
    version = "2.0.0"
    package_type = "python-require"
    description = "Bootstrap utilities for SpareTools ecosystem"
    license = "Apache-2.0"
    url = "https://github.com/sparesparrow/sparetools"
    
    # CRITICAL FIX: Add missing foundation dependency
    python_requires = "sparetools-base/2.0.0"
    
    exports_sources = "bootstrap/**", "scripts/**"
    
    def package(self):
        copy(self, "*.py", src=self.source_folder, dst=self.package_folder, keep_path=True)
        copy(self, "*.sh", src=self.source_folder, dst=self.package_folder, keep_path=True)
    
    def package_info(self):
        self.cpp_info.libs = []
        self.env_info.PYTHONPATH.append(self.package_folder)
        
    def python_requires_extend(self):
        """Extend base functionality with bootstrap utilities"""
        base = self.python_requires["sparetools-base"]
        return {
            "run_trivy_scan": self._create_trivy_scanner(),
            "generate_sbom": self._create_sbom_generator(),
            "validate_fips": self._create_fips_validator()
        }
        
    def _create_trivy_scanner(self):
        """Create Trivy security scanner"""
        def run_trivy_scan(source_folder):
            try:
                import subprocess
                result = subprocess.run(
                    ["trivy", "fs", "--format", "json", source_folder],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    print("✅ Trivy scan completed successfully")
                else:
                    print(f"⚠️ Trivy scan warnings: {result.stderr}")
            except Exception as e:
                print(f"⚠️ Trivy scan unavailable: {e}")
        return run_trivy_scan
        
    def _create_sbom_generator(self):
        """Create SBOM generator"""
        def generate_sbom(source_folder):
            try:
                import subprocess
                result = subprocess.run(
                    ["syft", "packages", source_folder, "-o", "spdx-json=sbom.json"],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    print("✅ SBOM generated successfully")
                else:
                    print(f"⚠️ SBOM generation warnings: {result.stderr}")
            except Exception as e:
                print(f"⚠️ SBOM generation unavailable: {e}")
        return generate_sbom
        
    def _create_fips_validator(self):
        """Create FIPS validator"""
        def validate_fips(openssl_path="openssl"):
            try:
                import subprocess
                result = subprocess.run(
                    [openssl_path, "version", "-f"],
                    capture_output=True, text=True
                )
                if "fips" in result.stdout.lower():
                    print("✅ FIPS validation passed")
                    return True
                else:
                    print("ℹ️ FIPS not enabled in this build")
                    return False
            except Exception as e:
                print(f"⚠️ FIPS validation unavailable: {e}")
                return False
        return validate_fips