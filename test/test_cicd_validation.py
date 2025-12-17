"""Tests for CI/CD workflow validation."""

import os
import yaml
import pytest
from pathlib import Path

# Import template configuration
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bootstrap_obd import AVAILABLE_TEMPLATES, TEMPLATES_DIR


class TestCICDValidation:
    """Test cases for CI/CD workflow validation."""

    def test_workflow_templates_exist(self):
        """Test that workflow templates exist for expected templates."""
        templates_with_workflows = ["mia", "mcp", "android", "generic"]

        for template in templates_with_workflows:
            workflow_path = TEMPLATES_DIR / template / ".github" / "workflows" / "ci.yml.template"
            assert workflow_path.exists(), f"Template {template} missing CI workflow template"

    def test_workflow_yaml_validity(self):
        """Test that workflow templates are valid YAML."""
        workflow_files = []

        # Find all workflow template files
        for template in AVAILABLE_TEMPLATES:
            workflow_path = TEMPLATES_DIR / template / ".github" / "workflows" / "ci.yml.template"
            if workflow_path.exists():
                workflow_files.append((template, workflow_path))

        for template, workflow_path in workflow_files:
            with open(workflow_path, 'r') as f:
                content = f.read()

            # Parse as YAML
            try:
                workflow_data = yaml.safe_load(content)
                assert workflow_data is not None, f"Workflow {template} parsed to None"
            except yaml.YAMLError as e:
                pytest.fail(f"Workflow {template} has invalid YAML: {e}")

    def test_workflow_required_structure(self):
        """Test that workflows have required GitHub Actions structure."""
        workflow_files = []

        for template in AVAILABLE_TEMPLATES:
            workflow_path = TEMPLATES_DIR / template / ".github" / "workflows" / "ci.yml.template"
            if workflow_path.exists():
                workflow_files.append((template, workflow_path))

        for template, workflow_path in workflow_files:
            with open(workflow_path, 'r') as f:
                workflow_data = yaml.safe_load(f)

            # Required top-level keys
            required_keys = ["name", "on", "jobs"]
            for key in required_keys:
                assert key in workflow_data, f"Workflow {template} missing required key: {key}"

            # Check that 'on' has valid triggers
            triggers = workflow_data["on"]
            assert isinstance(triggers, (dict, list)), f"Workflow {template} has invalid 'on' structure"

            # Check that jobs exist and are properly structured
            jobs = workflow_data["jobs"]
            assert isinstance(jobs, dict), f"Workflow {template} jobs is not a dict"
            assert len(jobs) > 0, f"Workflow {template} has no jobs"

            # Check each job has required structure
            for job_name, job_config in jobs.items():
                assert "runs-on" in job_config, f"Job {job_name} in {template} missing runs-on"
                assert "steps" in job_config, f"Job {job_name} in {template} missing steps"
                assert len(job_config["steps"]) > 0, f"Job {job_name} in {template} has no steps"

    def test_workflow_conan_integration(self):
        """Test that workflows properly integrate with Conan."""
        workflow_files = []

        for template in AVAILABLE_TEMPLATES:
            workflow_path = TEMPLATES_DIR / template / ".github" / "workflows" / "ci.yml.template"
            if workflow_path.exists():
                workflow_files.append((template, workflow_path))

        for template, workflow_path in workflow_files:
            with open(workflow_path, 'r') as f:
                content = f.read()

            # Should reference Conan in some way
            assert "conan" in content.lower(), f"Workflow {template} doesn't mention Conan"

            # Should have environment variables for versions
            assert "VERSION" in content, f"Workflow {template} missing version environment variables"

    def test_workflow_platform_matrix(self):
        """Test that workflows have appropriate platform matrices."""
        template_matrices = {
            "generic": ["ubuntu", "macos", "windows"],
            "mia": ["ubuntu", "macos", "windows"],
            "mcp": ["ubuntu", "macos"],
            "android": ["ubuntu"]
        }

        for template, expected_platforms in template_matrices.items():
            workflow_path = TEMPLATES_DIR / template / ".github" / "workflows" / "ci.yml.template"
            if workflow_path.exists():
                with open(workflow_path, 'r') as f:
                    content = f.read()

                # Check for matrix usage
                assert "matrix" in content, f"Workflow {template} should use matrix strategy"

                # Check for expected platforms
                for platform in expected_platforms:
                    assert platform in content, f"Workflow {template} missing platform {platform}"

    def test_workflow_step_structure(self):
        """Test that workflow steps have proper structure."""
        workflow_files = []

        for template in AVAILABLE_TEMPLATES:
            workflow_path = TEMPLATES_DIR / template / ".github" / "workflows" / "ci.yml.template"
            if workflow_path.exists():
                workflow_files.append((template, workflow_path))

        for template, workflow_path in workflow_files:
            with open(workflow_path, 'r') as f:
                workflow_data = yaml.safe_load(f)

            for job_name, job_config in workflow_data["jobs"].items():
                steps = job_config["steps"]

                for i, step in enumerate(steps):
                    assert isinstance(step, dict), f"Step {i} in job {job_name} is not a dict"

                    # Each step should have either 'run' or 'uses'
                    has_run = "run" in step
                    has_uses = "uses" in step

                    assert has_run or has_uses, f"Step {i} in job {job_name} has neither 'run' nor 'uses'"

                    # If it has 'uses', it should be a valid action reference
                    if has_uses:
                        uses = step["uses"]
                        assert "@" in uses, f"Step {i} in job {job_name} has invalid action reference: {uses}"

    def test_workflow_permissions(self):
        """Test that workflows have appropriate permissions."""
        workflow_files = []

        for template in AVAILABLE_TEMPLATES:
            workflow_path = TEMPLATES_DIR / template / ".github" / "workflows" / "ci.yml.template"
            if workflow_path.exists():
                workflow_files.append((template, workflow_path))

        for template, workflow_path in workflow_files:
            with open(workflow_path, 'r') as f:
                workflow_data = yaml.safe_load(f)

            # Should have permissions section
            assert "permissions" in workflow_data, f"Workflow {template} missing permissions"

            permissions = workflow_data["permissions"]
            assert isinstance(permissions, dict), f"Workflow {template} permissions is not a dict"

            # Should have basic permissions
            expected_perms = ["contents"]
            for perm in expected_perms:
                assert perm in permissions, f"Workflow {template} missing permission: {perm}"

    def test_workflow_variable_replacement(self):
        """Test that workflow templates use proper variable replacement."""
        workflow_files = []

        for template in AVAILABLE_TEMPLATES:
            workflow_path = TEMPLATES_DIR / template / ".github" / "workflows" / "ci.yml.template"
            if workflow_path.exists():
                workflow_files.append((template, workflow_path))

        for template, workflow_path in workflow_files:
            with open(workflow_path, 'r') as f:
                content = f.read()

            # Should use template variables
            template_vars = ["{{project_name}}", "{{version}}", "{{base_version}}", "{{cpython_version}}", "{{openssl_version}}"]

            for var in template_vars:
                assert var in content, f"Workflow {template} missing template variable: {var}"

    def test_workflow_artifact_handling(self):
        """Test that workflows handle artifacts appropriately."""
        workflow_files = []

        for template in AVAILABLE_TEMPLATES:
            workflow_path = TEMPLATES_DIR / template / ".github" / "workflows" / "ci.yml.template"
            if workflow_path.exists():
                workflow_files.append((template, workflow_path))

        for template, workflow_path in workflow_files:
            with open(workflow_path, 'r') as f:
                content = f.read()

            # Should use actions/upload-artifact for debugging
            if "failure()" in content:  # Only check workflows that handle failures
                assert "actions/upload-artifact" in content, f"Workflow {template} should upload failure artifacts"

    def test_workflow_summary_reporting(self):
        """Test that workflows provide job summaries."""
        workflow_files = []

        for template in AVAILABLE_TEMPLATES:
            workflow_path = TEMPLATES_DIR / template / ".github" / "workflows" / "ci.yml.template"
            if workflow_path.exists():
                workflow_files.append((template, workflow_path))

        for template, workflow_path in workflow_files:
            with open(workflow_path, 'r') as f:
                content = f.read()

            # Should use GitHub step summaries
            assert "$GITHUB_STEP_SUMMARY" in content, f"Workflow {template} should use step summaries"

    def test_workflow_caching_strategy(self):
        """Test that workflows use appropriate caching."""
        workflow_files = []

        for template in AVAILABLE_TEMPLATES:
            workflow_path = TEMPLATES_DIR / template / ".github" / "workflows" / "ci.yml.template"
            if workflow_path.exists():
                workflow_files.append((template, workflow_path))

        for template, workflow_path in workflow_files:
            with open(workflow_path, 'r') as f:
                content = f.read()

            # Should use actions/cache for Conan
            assert "actions/cache" in content, f"Workflow {template} should cache Conan packages"

            # Should have cache key strategy
            assert "hashFiles" in content, f"Workflow {template} should use hashFiles for cache keys"

    def test_template_specific_workflow_features(self):
        """Test template-specific workflow features."""
        # MIA-specific features
        mia_workflow = TEMPLATES_DIR / "mia" / ".github" / "workflows" / "ci.yml.template"
        if mia_workflow.exists():
            with open(mia_workflow, 'r') as f:
                content = f.read()

            # Should test Python versions
            assert "python-version" in content, "MIA workflow should test multiple Python versions"
            # Should run pytest
            assert "pytest" in content, "MIA workflow should run pytest"
            # Should use coverage
            assert "coverage" in content, "MIA workflow should use coverage"

        # MCP-specific features
        mcp_workflow = TEMPLATES_DIR / "mcp" / ".github" / "workflows" / "ci.yml.template"
        if mcp_workflow.exists():
            with open(mcp_workflow, 'r') as f:
                content = f.read()

            # Should validate MCP protocol
            assert "mcp" in content.lower(), "MCP workflow should validate MCP protocol"
            # Should test Docker
            assert "docker" in content, "MCP workflow should test Docker"

        # Android-specific features
        android_workflow = TEMPLATES_DIR / "android" / ".github" / "workflows" / "ci.yml.template"
        if android_workflow.exists():
            with open(android_workflow, 'r') as f:
                content = f.read()

            # Should test Android builds
            assert "gradle" in content or "./gradlew" in content, "Android workflow should use Gradle"
            # Should test different API levels
            assert "api-level" in content, "Android workflow should test different API levels"


def test_workflow_yaml_formatting():
    """Test that workflow YAML is properly formatted."""
    import re

    workflow_files = []

    for template in ["mia", "mcp", "android"]:
        workflow_path = TEMPLATES_DIR / template / ".github" / "workflows" / "ci.yml.template"
        if workflow_path.exists():
            workflow_files.append(workflow_path)

    for workflow_path in workflow_files:
        with open(workflow_path, 'r') as f:
            lines = f.readlines()

        # Check for consistent indentation (should use spaces, not tabs)
        for i, line in enumerate(lines, 1):
            if line.startswith('\t'):
                pytest.fail(f"Workflow {workflow_path} uses tabs instead of spaces at line {i}")

        # Check for trailing whitespace
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line.rstrip(' \t\n'):
                pytest.fail(f"Workflow {workflow_path} has trailing whitespace at line {i}")


if __name__ == "__main__":
    pytest.main([__file__])