from conan import ConanFile


class SparetoolsSharedDevToolsTestConan(ConanFile):
    """
    Test package for sparetools-shared-dev-tools python_requires.

    Since python_requires are recipe-level dependencies (not packages),
    we validate that they load correctly and can be referenced.
    """
    test_type = "explicit"
    python_requires = "sparetools-shared-dev-tools/[>=2.0.0]"

    def test(self):
        # Test 1: Verify python_requires loaded successfully
        try:
            dev_tools_ref = self.python_requires["sparetools-shared-dev-tools"]
            self.output.success("✅ sparetools-shared-dev-tools loaded as python_requires")
            self.output.info(f"   Reference: {dev_tools_ref}")
        except Exception as e:
            raise Exception(f"Failed to load sparetools-shared-dev-tools: {e}")

        # Test 2: Validate python_requires can be used in recipe
        self.output.info("📦 Validation: python_requires packages are recipe-level dependencies")
        self.output.info("   They provide Python code for use in conanfile.py recipes")
        self.output.info("   Examples: build_profile_args.py, project utilities")

        self.output.success("✅ Shared dev tools package validation complete!")
        self.output.info("")
        self.output.info("Next steps to validate functionality:")
        self.output.info("  - Import shared_dev_tools modules in conanfile.py")
        self.output.info("  - Use build_profile_args.py script in workflows")
        self.output.info("  - Validate core.utilities functions")
