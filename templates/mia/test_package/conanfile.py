from conan import ConanFile
from conan.tools.python import PythonDeps
import os


class {{class_name}}TestPackage(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        self.folders.generators = "conan"

    def generate(self):
        py_deps = PythonDeps(self)
        py_deps.generate()

    def test(self):
        # Import and test the package
        import sys
        sys.path.insert(0, self.dependencies[self.tested_reference_str].cpp_info.libdirs[0])

        try:
            from {{module_name}} import {{class_name}}, __version__

            # Test basic functionality
            instance = {{class_name}}()
            info = instance.get_info()

            assert info["name"] == "{{project_name}}"
            assert info["version"] == "{{version}}"
            assert __version__ == "{{version}}"

            # Test processing
            result = instance.process("test data")
            assert "test data" in result
            assert "{{project_name}}" in result

            self.output.info("✅ All tests passed!")

        except ImportError as e:
            self.output.error(f"❌ Import failed: {e}")
            raise