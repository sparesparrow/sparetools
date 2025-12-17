from conan import ConanFile
from conan.tools.python import PythonDeps
import os


class MiaProjectTestPackage(ConanFile):
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
            from mia_project import MiaProject, __version__

            # Test basic functionality
            instance = MiaProject()
            info = instance.get_info()

            assert info["name"] == "mia-project"
            assert info["version"] == "1.0.0"
            assert __version__ == "1.0.0"

            # Test processing
            result = instance.process("test data")
            assert "test data" in result
            assert "mia-project" in result

            self.output.info("✅ All tests passed!")

        except ImportError as e:
            self.output.error(f"❌ Import failed: {e}")
            raise