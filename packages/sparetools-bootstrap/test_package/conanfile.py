from conan import ConanFile
import os
import sys


class SparetoolsBootstrapTestConan(ConanFile):
    test_type = "explicit"
    python_requires = "sparetools-bootstrap/[>=2.0.0]", "sparetools-base/[>=2.0.0]"

    def test(self):
        # Test 1: Verify package folder exists
        package_folder = self.python_requires["sparetools-bootstrap"].package_folder
        if not os.path.exists(package_folder):
            raise Exception(f"Package folder not found: {package_folder}")

        self.output.info(f"Package folder: {package_folder}")

        # Test 2: Verify base dependency is accessible
        base_folder = self.python_requires["sparetools-base"].package_folder
        self.output.info(f"Base package folder: {base_folder}")

        # Test 3: Verify bootstrap module structure
        bootstrap_dir = os.path.join(package_folder, "bootstrap")
        if os.path.exists(bootstrap_dir):
            self.output.info(f"Bootstrap directory found: {bootstrap_dir}")

            # List subdirectories (agents)
            agents = [d for d in os.listdir(bootstrap_dir)
                     if os.path.isdir(os.path.join(bootstrap_dir, d)) and not d.startswith('__')]
            self.output.info(f"Available bootstrap agents: {', '.join(agents)}")
        else:
            self.output.warning(f"Bootstrap directory not found: {bootstrap_dir}")

        # Test 4: Try importing bootstrap module
        sys.path.insert(0, package_folder)

        try:
            import bootstrap
            self.output.info(f"Bootstrap module loaded from: {bootstrap.__file__}")
        except ImportError as e:
            self.output.warning(f"Could not import bootstrap module: {e}")

        # Test 5: Check for OpenSSL-specific bootstrap components
        openssl_bootstrap = os.path.join(package_folder, "bootstrap", "openssl")
        if os.path.exists(openssl_bootstrap):
            self.output.info(f"OpenSSL bootstrap found: {openssl_bootstrap}")

            # Check for FIPS validator
            fips_validator = os.path.join(openssl_bootstrap, "fips_validator.py")
            if os.path.exists(fips_validator):
                self.output.info("FIPS validator present")
        else:
            self.output.warning(f"OpenSSL bootstrap not found: {openssl_bootstrap}")

        # Test 6: Check for scripts directory
        scripts_dir = os.path.join(package_folder, "scripts")
        if os.path.exists(scripts_dir):
            scripts = [f for f in os.listdir(scripts_dir) if f.endswith(('.py', '.sh'))]
            self.output.info(f"Available scripts ({len(scripts)}): {', '.join(scripts[:5])}")

        self.output.success("Bootstrap package validation complete!")
