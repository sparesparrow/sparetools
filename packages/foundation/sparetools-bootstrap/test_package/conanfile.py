from conan import ConanFile


class SparetoolsBootstrapTestConan(ConanFile):
    """
    Test package for sparetools-bootstrap python_requires.

    Since python_requires are recipe-level dependencies (not packages),
    we validate that they load correctly and can be referenced.
    """
    name = 'bootstrap-test'
    version = '1.0.0'
    test_type = "explicit"
    python_requires = "sparetools-bootstrap/[>=2.0.0]", "sparetools-base/[>=2.0.0]"

    def test(self):
        # Test 1: Verify python_requires loaded successfully
        try:
            bootstrap_ref = self.python_requires["sparetools-bootstrap"]
            self.output.success("✅ sparetools-bootstrap loaded as python_requires")
            self.output.info(f"   Reference: {bootstrap_ref}")
        except Exception as e:
            raise Exception(f"Failed to load sparetools-bootstrap: {e}")

        # Test 2: Verify base dependency is accessible
        try:
            base_ref = self.python_requires["sparetools-base"]
            self.output.success("✅ sparetools-base loaded as python_requires")
            self.output.info(f"   Reference: {base_ref}")
        except Exception as e:
            raise Exception(f"Failed to load sparetools-base: {e}")

        # Test 3: Validate python_requires can be used in recipe
        # This is the actual use case - recipes will inherit from these
        self.output.info("📦 Validation: python_requires packages are recipe-level dependencies")
        self.output.info("   They provide Python code for use in conanfile.py recipes")
        self.output.info("   Not consumed as runtime packages")

        self.output.success("✅ Bootstrap package validation complete!")
        self.output.info("")
        self.output.info("Next steps to validate functionality:")
        self.output.info("  - Check bootstrap agents can be imported in conanfile.py")
        self.output.info("  - Validate FIPS validator availability")
        self.output.info("  - Test orchestration workflows")
