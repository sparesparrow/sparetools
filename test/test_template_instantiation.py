"""End-to-end tests for template instantiation."""

import os
import tempfile
import subprocess
import pytest
from pathlib import Path

# Import bootstrap functions
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bootstrap_obd import instantiate_template


class TestTemplateInstantiation:
    """End-to-end template instantiation tests."""

    @pytest.mark.parametrize("template", ["generic", "mia", "mcp", "android"])
    def test_full_template_instantiation(self, template):
        """Test complete template instantiation for all templates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_name = f"test-{template}-full"

            success = instantiate_template(template, project_name, tmpdir)
            assert success, f"Full instantiation failed for {template}"

            project_dir = Path(tmpdir) / project_name
            assert project_dir.exists()

            # Verify essential files exist
            essential_files = {
                "generic": ["README.md", "CMakeLists.txt", "conanfile.py"],
                "mia": ["README.md", "pyproject.toml", "conanfile.py"],
                "mcp": ["README.md", "pyproject.toml", "conanfile.py"],
                "android": ["README.md", "build.gradle.kts", "settings.gradle.kts"]
            }

            for file in essential_files[template]:
                file_path = project_dir / file
                assert file_path.exists(), f"Essential file {file} missing for {template}"

    def test_generic_template_build(self):
        """Test that generic template can be built after instantiation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_name = "test-generic-build"
            template = "generic"

            success = instantiate_template(template, project_name, tmpdir)
            assert success

            project_dir = Path(tmpdir) / project_name

            # Check that CMakeLists.txt is valid
            cmake_file = project_dir / "CMakeLists.txt"
            assert cmake_file.exists()

            # Basic CMake syntax check (this would require cmake to be installed)
            content = cmake_file.read_text()
            assert "cmake_minimum_required" in content
            assert "project(" in content

            # Check conanfile.py syntax
            conanfile = project_dir / "conanfile.py"
            assert conanfile.exists()

            # Try to import/parse the conanfile
            import ast
            with open(conanfile, 'r') as f:
                content = f.read()
            ast.parse(content)  # Should not raise SyntaxError

    def test_mia_template_python_setup(self):
        """Test that MIA template has valid Python setup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_name = "test-mia-python"
            template = "mia"

            success = instantiate_template(template, project_name, tmpdir)
            assert success

            project_dir = Path(tmpdir) / project_name

            # Check pyproject.toml
            pyproject = project_dir / "pyproject.toml"
            assert pyproject.exists()

            content = pyproject.read_text()
            assert "[build-system]" in content
            assert "[project]" in content
            assert "[tool.setuptools]" in content

            # Check Python package structure
            src_dir = project_dir / "src"
            assert src_dir.exists()

            # Should have a module directory
            module_dirs = [d for d in src_dir.iterdir() if d.is_dir()]
            assert len(module_dirs) > 0, "No Python module directory found"

            # Check __init__.py exists
            module_dir = module_dirs[0]
            init_file = module_dir / "__init__.py"
            assert init_file.exists()

            # Check conanfile.py
            conanfile = project_dir / "conanfile.py"
            assert conanfile.exists()

            import ast
            with open(conanfile, 'r') as f:
                ast.parse(f.read())

    def test_mcp_template_server_setup(self):
        """Test that MCP template has valid server setup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_name = "test-mcp-server"
            template = "mcp"

            success = instantiate_template(template, project_name, tmpdir)
            assert success

            project_dir = Path(tmpdir) / project_name

            # Check server.py exists
            server_file = project_dir / "src" / project_name.replace("-", "_") / "server.py"
            assert server_file.exists()

            content = server_file.read_text()
            assert "class" in content and "Server" in content
            assert "async def" in content

            # Check tools and resources directories
            tools_dir = project_dir / "src" / project_name.replace("-", "_") / "tools"
            resources_dir = project_dir / "src" / project_name.replace("-", "_") / "resources"
            assert tools_dir.exists()
            assert resources_dir.exists()

            # Check Docker setup
            docker_dir = project_dir / "docker"
            assert docker_dir.exists()

            dockerfile = docker_dir / "Dockerfile"
            assert dockerfile.exists()

    def test_android_template_gradle_setup(self):
        """Test that Android template has valid Gradle setup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_name = "TestAndroidGradle"
            template = "android"

            success = instantiate_template(template, project_name, tmpdir)
            assert success

            project_dir = Path(tmpdir) / project_name

            # Check Gradle files
            root_gradle = project_dir / "build.gradle.kts"
            settings_gradle = project_dir / "settings.gradle.kts"
            app_gradle = project_dir / "app" / "build.gradle.kts"

            assert root_gradle.exists()
            assert settings_gradle.exists()
            assert app_gradle.exists()

            # Check Android manifest
            manifest = project_dir / "app" / "src" / "main" / "AndroidManifest.xml"
            assert manifest.exists()

            content = manifest.read_text()
            assert "manifest" in content
            assert "application" in content

            # Check native setup
            cpp_dir = project_dir / "app" / "src" / "main" / "cpp"
            assert cpp_dir.exists()

            cmake_file = cpp_dir / "CMakeLists.txt"
            assert cmake_file.exists()

    def test_variable_replacement_comprehensive(self):
        """Test comprehensive variable replacement across all templates."""
        test_vars = {
            "project_name": "comprehensive-test",
            "class_name": "ComprehensiveTest",
            "module_name": "comprehensive_test",
            "version": "3.1.4",
            "author": "Comprehensive Tester",
            "author_email": "test@comprehensive.example",
            "description": "A comprehensive test project",
            "license": "BSD-3-Clause",
            "repository_url": "https://github.com/test/comprehensive-test",
            "homepage_url": "https://comprehensive-test.example",
            "year": "2024",
            "topic1": "testing",
            "topic2": "comprehensive"
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            for template in ["generic", "mia", "mcp", "android"]:
                project_name = f"test-{template}-comprehensive"

                success = instantiate_template(template, project_name, tmpdir, test_vars)
                assert success, f"Comprehensive instantiation failed for {template}"

                project_dir = Path(tmpdir) / project_name

                # Check that variables were replaced in key files
                readme = project_dir / "README.md"
                content = readme.read_text()

                assert "Comprehensive Tester" in content
                assert "3.1.4" in content
                assert "BSD-3-Clause" in content

                if template == "mia" or template == "mcp":
                    pyproject = project_dir / "pyproject.toml"
                    pyproject_content = pyproject.read_text()
                    assert "Comprehensive Tester" in pyproject_content
                    assert "test@comprehensive.example" in pyproject_content

                elif template == "android":
                    settings_gradle = project_dir / "settings.gradle.kts"
                    settings_content = settings_gradle.read_text()
                    # Settings should reference the project name
                    assert project_name in settings_content

    def test_template_instantiation_isolation(self):
        """Test that template instantiations don't interfere with each other."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Instantiate all templates in the same directory
            instantiated_projects = []

            for template in ["generic", "mia", "mcp", "android"]:
                project_name = f"isolated-{template}"

                success = instantiate_template(template, project_name, tmpdir)
                assert success, f"Isolated instantiation failed for {template}"

                instantiated_projects.append(project_name)

            # Verify all projects exist and are distinct
            for project_name in instantiated_projects:
                project_dir = Path(tmpdir) / project_name
                assert project_dir.exists()

                # Check that each has its own README
                readme = project_dir / "README.md"
                assert readme.exists()

                content = readme.read_text()
                # Each README should mention its own project name
                assert project_name in content

    def test_template_error_handling(self):
        """Test error handling in template instantiation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test nonexistent template
            success = instantiate_template("nonexistent", "test", tmpdir)
            assert not success

            # Test empty project name
            success = instantiate_template("generic", "", tmpdir)
            assert not success

            # Test invalid variables JSON
            success = instantiate_template("generic", "test", tmpdir, "invalid json{")
            assert not success

            # Verify no partial directories were created
            for item in Path(tmpdir).iterdir():
                # Should not have created any directories for failed instantiations
                assert not item.name.startswith("test")

    def test_template_file_permissions(self):
        """Test that instantiated files have correct permissions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            success = instantiate_template("generic", "test-permissions", tmpdir)
            assert success

            project_dir = Path(tmpdir) / "test-permissions"

            # Check file permissions (basic check)
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    file_path = Path(root) / file
                    # Files should be readable
                    assert os.access(file_path, os.R_OK), f"File {file_path} is not readable"

                    # Python files should be executable (at least on Unix-like systems)
                    if file_path.suffix == ".py":
                        # On Windows, this might not be set, so we'll skip this check
                        if os.name != 'nt':
                            assert os.access(file_path, os.X_OK), f"Python file {file_path} is not executable"


if __name__ == "__main__":
    pytest.main([__file__])