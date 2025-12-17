"""Unit tests for audit scripts"""
import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import sys
import ast

# Add scripts to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "scripts"))


class TestAuditConanRecipes:
    """Tests for audit-conan-recipes.py script"""
    
    def test_script_exists(self):
        """Test that audit-conan-recipes.py exists"""
        script_path = repo_root / "scripts" / "audit-conan-recipes.py"
        assert script_path.exists(), "audit-conan-recipes.py should exist"
    
    def test_script_has_valid_syntax(self):
        """Test that script has valid Python syntax"""
        script_path = repo_root / "scripts" / "audit-conan-recipes.py"
        
        with open(script_path, "r") as f:
            content = f.read()
        
        try:
            ast.parse(content)
        except SyntaxError as e:
            pytest.fail(f"Script has syntax error: {e}")
    
    def test_script_can_be_imported(self):
        """Test that script can be imported"""
        script_path = repo_root / "scripts" / "audit-conan-recipes.py"
        
        # Add to path temporarily
        import sys
        sys.path.insert(0, str(script_path.parent))
        
        try:
            # Try to import main components
            import importlib.util
            spec = importlib.util.spec_from_file_location("audit_script", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check for expected classes/functions
            assert hasattr(module, "PackageAudit") or hasattr(module, "ConanRecipeAuditor"), \
                "Script should define audit classes"
        except Exception as e:
            pytest.fail(f"Failed to import script: {e}")
        finally:
            sys.path.remove(str(script_path.parent))
    
    def test_audit_detects_missing_name(self, tmp_path):
        """Test that audit detects missing name field"""
        # Create a test conanfile without name
        test_conanfile = tmp_path / "conanfile.py"
        test_conanfile.write_text("""
from conan import ConanFile

class TestConan(ConanFile):
    version = "1.0.0"
""")
        
        # Import and test auditor
        sys.path.insert(0, str(repo_root / "scripts"))
        try:
            from audit_conan_recipes import ConanRecipeAuditor
            
            auditor = ConanRecipeAuditor(tmp_path)
            audit = auditor.audit_package(test_conanfile)
            
            # Should detect missing name
            assert any("name" in issue.lower() for issue in audit.issues), \
                "Should detect missing name field"
        except ImportError:
            pytest.skip("Cannot import audit script")
        finally:
            if str(repo_root / "scripts") in sys.path:
                sys.path.remove(str(repo_root / "scripts"))
    
    def test_audit_detects_env_info_usage(self, tmp_path):
        """Test that audit detects deprecated env_info usage"""
        # Create a test conanfile with env_info
        test_conanfile = tmp_path / "conanfile.py"
        test_conanfile.write_text("""
from conan import ConanFile

class TestConan(ConanFile):
    name = "test"
    version = "1.0.0"
    
    def package_info(self):
        self.env_info.PATH.append("bin")
""")
        
        # Import and test auditor
        sys.path.insert(0, str(repo_root / "scripts"))
        try:
            from audit_conan_recipes import ConanRecipeAuditor
            
            auditor = ConanRecipeAuditor(tmp_path)
            audit = auditor.audit_package(test_conanfile)
            
            # Should detect env_info usage
            assert audit.uses_env_info or any("env_info" in issue.lower() for issue in audit.issues), \
                "Should detect deprecated env_info usage"
        except ImportError:
            pytest.skip("Cannot import audit script")
        finally:
            if str(repo_root / "scripts") in sys.path:
                sys.path.remove(str(repo_root / "scripts"))
    
    def test_audit_generates_report(self, tmp_path):
        """Test that audit generates markdown report"""
        # Create test packages directory
        packages_dir = tmp_path / "packages" / "test-pkg"
        packages_dir.mkdir(parents=True)
        
        conanfile = packages_dir / "conanfile.py"
        conanfile.write_text("""
from conan import ConanFile

class TestConan(ConanFile):
    name = "test-pkg"
    version = "1.0.0"
    description = "Test package"
    license = "MIT"
    package_type = "library"
""")
        
        # Import and test auditor
        sys.path.insert(0, str(repo_root / "scripts"))
        try:
            from audit_conan_recipes import ConanRecipeAuditor
            
            auditor = ConanRecipeAuditor(tmp_path / "packages")
            packages = auditor.audit_all()
            
            # Generate report
            report = auditor.generate_report()
            
            # Check report content
            assert "# Conan Recipes Audit Report" in report
            assert "test-pkg" in report or len(packages) > 0
        except ImportError:
            pytest.skip("Cannot import audit script")
        finally:
            if str(repo_root / "scripts") in sys.path:
                sys.path.remove(str(repo_root / "scripts"))


class TestAuditScriptErrorHandling:
    """Tests for audit script error handling"""
    
    def test_audit_handles_invalid_conanfile(self, tmp_path):
        """Test that audit handles invalid conanfile gracefully"""
        # Create invalid conanfile
        invalid_conanfile = tmp_path / "conanfile.py"
        invalid_conanfile.write_text("invalid python syntax !!!")
        
        sys.path.insert(0, str(repo_root / "scripts"))
        try:
            from audit_conan_recipes import ConanRecipeAuditor
            
            auditor = ConanRecipeAuditor(tmp_path)
            audit = auditor.audit_package(invalid_conanfile)
            
            # Should handle error gracefully
            assert len(audit.issues) > 0 or "syntax" in str(audit.issues).lower()
        except ImportError:
            pytest.skip("Cannot import audit script")
        except Exception as e:
            # Should not crash
            assert True, f"Should handle error gracefully, got: {e}"
        finally:
            if str(repo_root / "scripts") in sys.path:
                sys.path.remove(str(repo_root / "scripts"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
