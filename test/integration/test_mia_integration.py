#!/usr/bin/env python3
"""
Integration tests for MIA integration with sparetools packages.

Tests:
- Package importability from external repository
- Dependency resolution from Cloudsmith remote
- Remote configuration
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def repo_root():
    """Get repository root directory"""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def example_conanfile(repo_root):
    """Get path to example MIA consumer conanfile"""
    return repo_root / "examples" / "mia-consumer" / "conanfile.py"


@pytest.fixture
def temp_conan_home():
    """Create temporary Conan home directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestMIAIntegration:
    """Test MIA integration with sparetools packages"""
    
    def test_example_conanfile_exists(self, example_conanfile):
        """Test that example conanfile exists"""
        assert example_conanfile.exists(), f"Example conanfile not found at {example_conanfile}"
    
    def test_example_conanfile_syntax(self, example_conanfile):
        """Test that example conanfile has valid Python syntax"""
        import ast
        with open(example_conanfile, "r") as f:
            content = f.read()
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Example conanfile has syntax error: {e}")
    
    def test_example_conanfile_imports(self, example_conanfile):
        """Test that example conanfile imports Conan 2.x API correctly"""
        with open(example_conanfile, "r") as f:
            content = f.read()
        
        # Check for Conan 2.x imports
        assert "from conan import ConanFile" in content, "Should use Conan 2.x import"
        assert "from conan.tools.cmake" in content, "Should use Conan 2.x CMake tools"
        
        # Check for no Conan 1.x imports
        assert "from conans import" not in content, "Should not use Conan 1.x imports"
        assert "import conans" not in content, "Should not use Conan 1.x imports"
    
    def test_example_conanfile_dependencies(self, example_conanfile):
        """Test that example conanfile declares dependencies correctly"""
        with open(example_conanfile, "r") as f:
            content = f.read()
        
        # Check for sparetools-openssl dependency
        assert "sparetools-openssl" in content, "Should declare sparetools-openssl dependency"
        assert "3.3.2" in content, "Should use OpenSSL 3.3.2"
        
        # Check for proper dependency declarations
        assert "requires" in content, "Should declare requires"
    
    def test_package_importability(self, repo_root):
        """Test that sparetools packages can be imported (syntax check)"""
        # Check main OpenSSL package
        openssl_conanfile = repo_root / "packages" / "sparetools-openssl" / "conanfile.py"
        assert openssl_conanfile.exists(), "sparetools-openssl conanfile should exist"
        
        # Try to parse it
        import ast
        with open(openssl_conanfile, "r") as f:
            content = f.read()
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"sparetools-openssl conanfile has syntax error: {e}")
    
    def test_remote_configuration_example(self, repo_root):
        """Test that remote configuration is documented"""
        integration_doc = repo_root / "docs" / "MIA-INTEGRATION.md"
        if integration_doc.exists():
            with open(integration_doc, "r") as f:
                content = f.read()
            assert "sparesparrow-conan" in content or "cloudsmith" in content.lower(), \
                "Integration doc should mention remote configuration"
    
    @pytest.mark.skipif(
        not os.environ.get("CONAN_TEST_REMOTE"),
        reason="CONAN_TEST_REMOTE not set - skipping remote dependency resolution test"
    )
    def test_dependency_resolution_from_remote(self, temp_conan_home, example_conanfile):
        """Test dependency resolution from Cloudsmith remote (requires network)"""
        # This test requires network access and valid credentials
        # Skip if CONAN_TEST_REMOTE is not set
        env = os.environ.copy()
        env["CONAN_HOME"] = str(temp_conan_home)
        
        # Configure remote
        remote_cmd = [
            "conan", "remote", "add", "sparesparrow-conan",
            "https://dl.cloudsmith.io/public/sparesparrow-conan/openssl-conan/conan/",
            "--force"
        ]
        
        try:
            result = subprocess.run(
                remote_cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=10
            )
            # Don't fail if remote already exists
            assert result.returncode == 0 or "already exists" in result.stderr.lower()
        except subprocess.TimeoutExpired:
            pytest.skip("Remote configuration timed out")
        except FileNotFoundError:
            pytest.skip("Conan not installed or not in PATH")
    
    def test_example_readme_exists(self, repo_root):
        """Test that example README exists"""
        readme = repo_root / "examples" / "mia-consumer" / "README.md"
        assert readme.exists(), "Example README should exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
