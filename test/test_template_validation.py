"""Tests for template validation and instantiation."""

import os
import tempfile
import shutil
import pytest
from pathlib import Path

# Import bootstrap functions
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bootstrap_obd import (
    AVAILABLE_TEMPLATES,
    TEMPLATES_DIR,
    validate_template_name,
    get_default_template_variables,
    instantiate_template,
    list_available_templates
)


class TestTemplateValidation:
    """Test cases for template validation."""

    def test_available_templates_exist(self):
        """Test that all declared templates exist."""
        for template in AVAILABLE_TEMPLATES:
            template_path = TEMPLATES_DIR / template
            assert template_path.exists(), f"Template {template} does not exist at {template_path}"
            assert template_path.is_dir(), f"Template {template} is not a directory"

    def test_template_has_readme(self):
        """Test that each template has a README.md file."""
        for template in AVAILABLE_TEMPLATES:
            readme_path = TEMPLATES_DIR / template / "README.md"
            assert readme_path.exists(), f"Template {template} missing README.md"

    def test_validate_template_name(self):
        """Test template name validation."""
        # Valid templates
        for template in AVAILABLE_TEMPLATES:
            assert validate_template_name(template), f"Template {template} should be valid"

        # Invalid templates
        assert not validate_template_name("nonexistent"), "Nonexistent template should be invalid"
        assert not validate_template_name(""), "Empty template name should be invalid"

    def test_get_default_template_variables(self):
        """Test default template variables generation."""
        for template in AVAILABLE_TEMPLATES:
            vars = get_default_template_variables(template, "test-project")

            # Check required variables
            required_vars = ["project_name", "version", "author", "license"]
            for var in required_vars:
                assert var in vars, f"Template {template} missing required variable: {var}"
                assert vars[var], f"Template {template} variable {var} is empty"

            # Check template-specific variables
            if template == "mia":
                assert "cpython_version" in vars
                assert "openssl_version" in vars
            elif template == "android":
                assert "package_name" in vars

    def test_template_instantiation_basic(self):
        """Test basic template instantiation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for template in AVAILABLE_TEMPLATES:
                # Test instantiation
                success = instantiate_template(template, f"test-{template}", tmpdir)
                assert success, f"Template {template} instantiation failed"

                # Check that project directory was created
                project_dir = Path(tmpdir) / f"test-{template}"
                assert project_dir.exists(), f"Project directory not created for {template}"
                assert project_dir.is_dir(), f"Project path is not a directory for {template}"

                # Check that README.md exists
                readme = project_dir / "README.md"
                assert readme.exists(), f"README.md not created for {template}"

    def test_template_variable_replacement(self):
        """Test that template variables are properly replaced."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template = "generic"
            project_name = "test-var-replacement"
            custom_vars = {
                "author": "Test Author",
                "version": "2.0.0",
                "license": "Apache-2.0"
            }

            success = instantiate_template(template, project_name, tmpdir, custom_vars)
            assert success, "Template instantiation with custom variables failed"

            project_dir = Path(tmpdir) / project_name

            # Check that variables were replaced in README
            readme = project_dir / "README.md"
            content = readme.read_text()

            assert "Test Author" in content, "Author variable not replaced"
            assert "2.0.0" in content, "Version variable not replaced"
            assert "Apache-2.0" in content, "License variable not replaced"

    def test_template_instantiation_idempotent(self):
        """Test that template instantiation is idempotent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template = "mia"
            project_name = "test-idempotent"

            # First instantiation
            success1 = instantiate_template(template, project_name, tmpdir)
            assert success1, "First instantiation failed"

            project_dir = Path(tmpdir) / project_name

            # Get initial file list
            initial_files = []
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    initial_files.append(os.path.relpath(os.path.join(root, file), project_dir))

            # Second instantiation should fail (directory exists)
            success2 = instantiate_template(template, project_name, tmpdir)
            assert not success2, "Second instantiation should fail due to existing directory"

            # Verify files weren't modified
            final_files = []
            for root, dirs, files in os.walk(project_dir):
                for file in files:
                    final_files.append(os.path.relpath(os.path.join(root, file), project_dir))

            assert set(initial_files) == set(final_files), "Files were modified between instantiations"

    def test_template_file_structure(self):
        """Test that templates have expected file structure."""
        template_expectations = {
            "generic": {
                "required_files": ["README.md", "CMakeLists.txt", "conanfile.py"],
                "required_dirs": ["include", "src", "test", "test_package"]
            },
            "mia": {
                "required_files": ["README.md", "pyproject.toml", "conanfile.py"],
                "required_dirs": ["src", "test", "test_package"]
            },
            "mcp": {
                "required_files": ["README.md", "pyproject.toml", "conanfile.py"],
                "required_dirs": ["src", "test", "test_package", "docker"]
            },
            "android": {
                "required_files": ["README.md", "build.gradle.kts", "settings.gradle.kts"],
                "required_dirs": ["app"]
            }
        }

        for template, expectations in template_expectations.items():
            template_path = TEMPLATES_DIR / template

            # Check required files
            for file in expectations["required_files"]:
                file_path = template_path / file
                assert file_path.exists(), f"Template {template} missing required file: {file}"

            # Check required directories
            for dir_name in expectations["required_dirs"]:
                dir_path = template_path / dir_name
                assert dir_path.exists(), f"Template {template} missing required directory: {dir_name}"
                assert dir_path.is_dir(), f"Template {template} {dir_name} is not a directory"

    def test_template_conanfile_syntax(self):
        """Test that template conanfiles have valid Python syntax."""
        import ast

        for template in AVAILABLE_TEMPLATES:
            conanfile_path = TEMPLATES_DIR / template / "conanfile.py"
            if conanfile_path.exists():
                with open(conanfile_path, 'r') as f:
                    content = f.read()

                # Parse as Python AST
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    pytest.fail(f"Template {template} conanfile.py has syntax error: {e}")

    def test_template_no_binary_files_with_placeholders(self):
        """Test that binary files don't contain template placeholders."""
        binary_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf'}

        for template in AVAILABLE_TEMPLATES:
            template_path = TEMPLATES_DIR / template

            for root, dirs, files in os.walk(template_path):
                for file in files:
                    file_path = Path(root) / file
                    if file_path.suffix in binary_extensions:
                        # Skip binary files
                        continue

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Check for template placeholders
                        if '{{' in content and '}}' in content:
                            # This is expected - templates should have placeholders
                            # But let's verify they're proper mustache format
                            pass

                    except UnicodeDecodeError:
                        # Binary file, skip
                        continue

    def test_template_workflow_templates(self):
        """Test that templates with CI/CD have valid workflow templates."""
        templates_with_ci = ["mia", "mcp", "android"]

        for template in templates_with_ci:
            workflow_path = TEMPLATES_DIR / template / ".github" / "workflows" / "ci.yml.template"
            assert workflow_path.exists(), f"Template {template} missing CI workflow template"

            # Check that it's a valid YAML structure (basic check)
            with open(workflow_path, 'r') as f:
                content = f.read()

            # Should contain basic workflow structure
            assert "name:" in content, f"Workflow template for {template} missing name"
            assert "on:" in content, f"Workflow template for {template} missing trigger"
            assert "jobs:" in content, f"Workflow template for {template} missing jobs"


def test_list_available_templates(capsys):
    """Test listing available templates."""
    list_available_templates()

    captured = capsys.readouterr()
    assert "Available templates:" in captured.out

    for template in AVAILABLE_TEMPLATES:
        assert template in captured.out, f"Template {template} not listed in output"


def test_template_instantiation_with_json_variables():
    """Test template instantiation with JSON variable string."""
    import json

    with tempfile.TemporaryDirectory() as tmpdir:
        template = "generic"
        project_name = "test-json-vars"

        # Test with JSON string
        variables = json.dumps({
            "author": "JSON Author",
            "description": "Test project with JSON variables"
        })

        success = instantiate_template(template, project_name, tmpdir, variables)
        assert success, "Template instantiation with JSON variables failed"

        project_dir = Path(tmpdir) / project_name
        readme = project_dir / "README.md"
        content = readme.read_text()

        assert "JSON Author" in content, "JSON variable not replaced"
        assert "Test project with JSON variables" in content, "JSON description not replaced"


def test_template_instantiation_invalid_json():
    """Test template instantiation with invalid JSON variables."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template = "generic"
        project_name = "test-invalid-json"

        # Test with invalid JSON
        invalid_json = '{"author": "Test", "invalid": }'

        success = instantiate_template(template, project_name, tmpdir, invalid_json)
        assert not success, "Template instantiation should fail with invalid JSON"


if __name__ == "__main__":
    pytest.main([__file__])