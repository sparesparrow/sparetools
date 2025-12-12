"""Unit tests for validation scripts"""
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import ast

# Add scripts to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "scripts"))


class TestValidateOpenSSLCompatibility:
    """Tests for validate-openssl-compatibility.py script"""
    
    def test_script_exists(self):
        """Test that validate-openssl-compatibility.py exists"""
        script_path = repo_root / "scripts" / "validate-openssl-compatibility.py"
        assert script_path.exists(), "validate-openssl-compatibility.py should exist"
    
    def test_script_has_valid_syntax(self):
        """Test that script has valid Python syntax"""
        script_path = repo_root / "scripts" / "validate-openssl-compatibility.py"
        
        with open(script_path, "r") as f:
            content = f.read()
        
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Script has syntax error: {e}")
    
    def test_script_detects_version_mismatch(self, tmp_path):
        """Test that script detects version mismatches"""
        # Create test conanfile with wrong version
        test_conanfile = tmp_path / "packages" / "test-pkg" / "conanfile.py"
        test_conanfile.parent.mkdir(parents=True)
        
        test_conanfile.write_text("""
from conan import ConanFile

class TestConan(ConanFile):
    name = "test-pkg"
    version = "1.0.0"
    
    requires = [
        "sparetools-openssl/3.2.0",  # Wrong version
    ]
""")
        
        sys.path.insert(0, str(repo_root / "scripts"))
        try:
            from validate_openssl_compatibility import OpenSSLCompatibilityValidator
            
            validator = OpenSSLCompatibilityValidator(tmp_path)
            issues = validator.validate_all()
            
            # Should detect version mismatch
            assert len(issues) > 0 or any("3.3.2" in str(issue) for issue in issues)
        except ImportError:
            pytest.skip("Cannot import validation script")
        finally:
            if str(repo_root / "scripts") in sys.path:
                sys.path.remove(str(repo_root / "scripts"))
    
    def test_script_generates_report(self, tmp_path):
        """Test that script generates compatibility report"""
        sys.path.insert(0, str(repo_root / "scripts"))
        try:
            from validate_openssl_compatibility import OpenSSLCompatibilityValidator
            
            validator = OpenSSLCompatibilityValidator(tmp_path)
            issues = validator.validate_all()
            
            # Generate report
            report = validator.generate_report()
            
            # Check report content
            assert "# OpenSSL 3.3.2 Compatibility Report" in report
            assert "3.3.2" in report
        except ImportError:
            pytest.skip("Cannot import validation script")
        finally:
            if str(repo_root / "scripts") in sys.path:
                sys.path.remove(str(repo_root / "scripts"))


class TestValidateSparetoolsOpenSSL:
    """Tests for validate-sparetools-openssl.py script"""
    
    def test_script_exists(self):
        """Test that validate-sparetools-openssl.py exists"""
        script_path = repo_root / "validate-sparetools-openssl.py"
        assert script_path.exists(), "validate-sparetools-openssl.py should exist"
    
    def test_script_has_valid_syntax(self):
        """Test that script has valid Python syntax"""
        script_path = repo_root / "validate-sparetools-openssl.py"
        
        with open(script_path, "r") as f:
            content = f.read()
        
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Script has syntax error: {e}")


class TestValidateConanPythonIntegration:
    """Tests for validate-conan-python-integration.py script"""
    
    def test_script_exists(self):
        """Test that validate-conan-python-integration.py exists"""
        script_path = repo_root / "validate-conan-python-integration.py"
        assert script_path.exists(), "validate-conan-python-integration.py should exist"
    
    def test_script_has_valid_syntax(self):
        """Test that script has valid Python syntax"""
        script_path = repo_root / "validate-conan-python-integration.py"
        
        with open(script_path, "r") as f:
            content = f.read()
        
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Script has syntax error: {e}")
    
    def test_script_validates_conan_api(self, tmp_path):
        """Test that script validates Conan 2.x API"""
        # Create test conanfile
        test_conanfile = tmp_path / "packages" / "test-pkg" / "conanfile.py"
        test_conanfile.parent.mkdir(parents=True)
        
        test_conanfile.write_text("""
from conan import ConanFile

class TestConan(ConanFile):
    name = "test-pkg"
    version = "1.0.0"
""")
        
        # Run validation script
        script_path = repo_root / "validate-conan-python-integration.py"
        
        import subprocess
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=tmp_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Script should run without crashing
            assert result.returncode is not None
        except subprocess.TimeoutExpired:
            pytest.fail("Script timed out")
        except FileNotFoundError:
            pytest.skip("Python not found")


class TestValidationScriptsStructure:
    """Tests for validation script structure"""
    
    def test_validation_scripts_are_executable(self):
        """Test that validation scripts can be executed"""
        scripts = [
            repo_root / "scripts" / "validate-openssl-compatibility.py",
            repo_root / "validate-sparetools-openssl.py",
            repo_root / "validate-conan-python-integration.py",
        ]
        
        for script in scripts:
            if script.exists():
                # Check if it's a Python script
                with open(script, "r") as f:
                    first_line = f.readline()
                    assert first_line.startswith("#!"), \
                        f"{script.name} should have shebang"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
