"""Unit tests for sparetools-base security-gates module"""
import os
import json
import subprocess
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the module we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "sparetools-base"))

from security_gates import (
    run_trivy_scan,
    generate_sbom,
    validate_package,
    check_fips_compliance
)


class TestRunTrivyScan:
    """Tests for run_trivy_scan function"""
    
    def test_raises_when_target_missing(self, tmp_path):
        """Test raises FileNotFoundError when target doesn't exist"""
        target = tmp_path / "nonexistent"
        
        with pytest.raises(FileNotFoundError):
            run_trivy_scan(str(target))
    
    @patch('subprocess.run')
    def test_parses_trivy_output_correctly(self, mock_run, tmp_path):
        """Test parsing of Trivy JSON output"""
        target = tmp_path / "target"
        target.mkdir()
        
        # Mock Trivy output
        mock_output = {
            "Results": [
                {
                    "Vulnerabilities": [
                        {"Severity": "CRITICAL", "VulnerabilityID": "CVE-2024-1234"},
                        {"Severity": "HIGH", "VulnerabilityID": "CVE-2024-5678"}
                    ]
                }
            ]
        }
        
        mock_result = Mock()
        mock_result.stdout = json.dumps(mock_output)
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        result = run_trivy_scan(str(target), fail_on_findings=False)
        
        assert result["findings_count"] == 2
        assert len(result["findings"]) == 2
        assert result["passed"] is False
    
    @patch('subprocess.run')
    def test_passes_when_no_findings(self, mock_run, tmp_path):
        """Test passes when no vulnerabilities found"""
        target = tmp_path / "target"
        target.mkdir()
        
        mock_output = {"Results": []}
        
        mock_result = Mock()
        mock_result.stdout = json.dumps(mock_output)
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        result = run_trivy_scan(str(target), fail_on_findings=False)
        
        assert result["findings_count"] == 0
        assert result["passed"] is True
    
    @patch('subprocess.run')
    def test_raises_on_critical_findings(self, mock_run, tmp_path):
        """Test raises exception on critical findings when fail_on_findings=True"""
        target = tmp_path / "target"
        target.mkdir()
        
        mock_output = {
            "Results": [
                {
                    "Vulnerabilities": [
                        {"Severity": "CRITICAL", "VulnerabilityID": "CVE-2024-1234"}
                    ]
                }
            ]
        }
        
        mock_result = Mock()
        mock_result.stdout = json.dumps(mock_output)
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        with pytest.raises(Exception, match="Found vulnerabilities"):
            run_trivy_scan(str(target), fail_on_findings=True)


class TestGenerateSbom:
    """Tests for generate_sbom function"""
    
    def test_raises_when_target_missing(self, tmp_path):
        """Test raises FileNotFoundError when target doesn't exist"""
        target = tmp_path / "nonexistent"
        
        with pytest.raises(FileNotFoundError):
            generate_sbom(str(target))
    
    @patch('subprocess.run')
    def test_generates_sbom_with_default_name(self, mock_run, tmp_path):
        """Test SBOM generation with default output filename"""
        target = tmp_path / "target"
        target.mkdir()
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        output_file = generate_sbom(str(target), output_format="cyclonedx-json")
        
        assert output_file == "target.sbom.json"
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_generates_sbom_with_custom_output(self, mock_run, tmp_path):
        """Test SBOM generation with custom output file"""
        target = tmp_path / "target"
        target.mkdir()
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        output_file = generate_sbom(
            str(target),
            output_format="cyclonedx-json",
            output_file="custom.sbom.json"
        )
        
        assert output_file == "custom.sbom.json"
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_raises_when_syft_not_found(self, mock_run, tmp_path):
        """Test raises FileNotFoundError when Syft not installed"""
        target = tmp_path / "target"
        target.mkdir()
        
        mock_run.side_effect = FileNotFoundError("syft: command not found")
        
        with pytest.raises(FileNotFoundError, match="Syft not installed"):
            generate_sbom(str(target))


class TestValidatePackage:
    """Tests for validate_package function"""
    
    def test_validates_existing_directory(self, tmp_path):
        """Test validation of existing directory"""
        target = tmp_path / "package"
        target.mkdir()
        (target / "file.txt").write_text("test")
        
        with patch('security_gates.run_trivy_scan') as mock_trivy, \
             patch('security_gates.generate_sbom') as mock_sbom:
            
            mock_trivy.return_value = {"passed": True, "findings_count": 0}
            mock_sbom.return_value = "package.sbom.json"
            
            results = validate_package(str(target))
        
        assert results["exists"] is True
        assert results["is_directory"] is True
        assert results["passed"] is True
    
    def test_detects_missing_target(self, tmp_path):
        """Test detection of missing target"""
        target = tmp_path / "nonexistent"
        
        results = validate_package(str(target))
        
        assert results["exists"] is False
        assert results["passed"] is False
        assert len(results["issues"]) > 0


class TestCheckFipsCompliance:
    """Tests for check_fips_compliance function"""
    
    @patch('subprocess.run')
    def test_detects_fips_enabled(self, mock_run, tmp_path):
        """Test detection of FIPS-enabled OpenSSL"""
        openssl_path = tmp_path / "openssl"
        openssl_path.mkdir()
        (openssl_path / "bin").mkdir()
        (openssl_path / "bin" / "openssl").write_text("#!/bin/sh\necho 'OpenSSL 3.3.2 FIPS'")
        
        # Mock version check
        mock_result = Mock()
        mock_result.stdout = "OpenSSL 3.3.2 FIPS enabled"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        results = check_fips_compliance(str(openssl_path))
        
        assert results["fips_enabled"] is True
        assert results["version"] is not None
    
    @patch('subprocess.run')
    def test_handles_missing_openssl(self, mock_run, tmp_path):
        """Test handling when OpenSSL executable is missing"""
        openssl_path = tmp_path / "openssl"
        openssl_path.mkdir()
        
        mock_run.side_effect = FileNotFoundError("openssl: command not found")
        
        results = check_fips_compliance(str(openssl_path))
        
        assert results["fips_enabled"] is False
        assert len(results["issues"]) > 0
