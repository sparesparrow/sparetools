"""Security scanning and validation utilities for artifacts"""
import subprocess
import json
import os


def run_trivy_scan(target_path, severity="CRITICAL,HIGH", fail_on_findings=True):
    """
    Run Trivy security scan on filesystem.
    
    Args:
        target_path: Path to scan
        severity: Severity levels to report (comma-separated)
        fail_on_findings: Whether to raise exception on findings
    
    Returns:
        dict with scan results
    
    Raises:
        subprocess.CalledProcessError: If Trivy returns error
        Exception: If findings found and fail_on_findings=True
    """
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Target path not found: {target_path}")
    
    cmd = [
        "trivy", "fs",
        "--severity", severity,
        "--format", "json",
        "--exit-code", "0",  # Don't fail on findings, we handle it
        target_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        scan_data = json.loads(result.stdout) if result.stdout else {}
    except json.JSONDecodeError:
        raise Exception(f"Failed to parse Trivy output: {result.stdout}")
    
    findings = []
    for target in scan_data.get("Results", []):
        findings.extend(target.get("Vulnerabilities", []))
    
    if findings and fail_on_findings:
        critical_count = sum(1 for f in findings if f.get("Severity") == "CRITICAL")
        high_count = sum(1 for f in findings if f.get("Severity") == "HIGH")
        raise Exception(
            f"Found vulnerabilities in {target_path}: "
            f"{critical_count} CRITICAL, {high_count} HIGH"
        )
    
    return {
        "findings_count": len(findings),
        "findings": findings,
        "passed": len(findings) == 0,
        "target": target_path
    }


def generate_sbom(target_path, output_format="cyclonedx-json", output_file=None):
    """
    Generate SBOM using Syft.
    
    Args:
        target_path: Path to scan
        output_format: SBOM format (cyclonedx-json, spdx-json, table, etc.)
        output_file: Output file path (if None, uses default naming)
    
    Returns:
        Path to generated SBOM file
    
    Raises:
        subprocess.CalledProcessError: If Syft fails
        FileNotFoundError: If Syft not installed
    """
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Target path not found: {target_path}")
    
    if output_file is None:
        base_name = os.path.basename(target_path.rstrip("/"))
        ext = "json" if "json" in output_format else "txt"
        output_file = f"{base_name}.sbom.{ext}"
    
    cmd = [
        "syft",
        target_path,
        "-o", f"{output_format}={output_file}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ SBOM generated: {output_file}")
        return output_file
    except FileNotFoundError:
        raise FileNotFoundError("Syft not installed. Install with: pip install syft")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Syft failed: {e.stderr}")


def validate_package(target_path, run_trivy=True, generate_sbom_file=True):
    """
    Comprehensive package validation.
    
    Runs security scans and generates artifacts for compliance.
    
    Args:
        target_path: Path to package
        run_trivy: Whether to run Trivy scan
        generate_sbom_file: Whether to generate SBOM
    
    Returns:
        dict with validation results
    """
    results = {
        "target": target_path,
        "exists": os.path.exists(target_path),
        "is_directory": os.path.isdir(target_path) if os.path.exists(target_path) else False,
        "trivy": None,
        "sbom": None,
        "passed": True,
        "issues": []
    }
    
    if not results["exists"]:
        results["passed"] = False
        results["issues"].append(f"Target not found: {target_path}")
        return results
    
    if run_trivy:
        try:
            results["trivy"] = run_trivy_scan(target_path, fail_on_findings=False)
            if not results["trivy"]["passed"]:
                results["passed"] = False
        except Exception as e:
            results["issues"].append(f"Trivy scan failed: {e}")
    
    if generate_sbom_file:
        try:
            results["sbom"] = generate_sbom(target_path)
        except Exception as e:
            results["issues"].append(f"SBOM generation failed: {e}")
    
    return results


def check_fips_compliance(openssl_path):
    """
    Check if OpenSSL is FIPS-compliant.
    
    Args:
        openssl_path: Path to openssl executable or installation
    
    Returns:
        dict with FIPS compliance status
    """
    results = {
        "fips_enabled": False,
        "version": None,
        "provider_available": False,
        "issues": []
    }
    
    # Check version
    try:
        result = subprocess.run(
            [os.path.join(openssl_path, "bin", "openssl"), "version", "-a"],
            capture_output=True,
            text=True,
            check=True
        )
        results["version"] = result.stdout.strip()
        
        if "FIPS" in result.stdout:
            results["fips_enabled"] = True
    except Exception as e:
        results["issues"].append(f"Failed to check OpenSSL version: {e}")
    
    # Check FIPS provider
    try:
        env = os.environ.copy()
        openssl_conf = os.path.join(openssl_path, "openssl.cnf")
        if os.path.exists(openssl_conf):
            env["OPENSSL_CONF"] = openssl_conf
        
        result = subprocess.run(
            [os.path.join(openssl_path, "bin", "openssl"), "list", "-providers"],
            capture_output=True,
            text=True,
            check=True,
            env=env
        )
        
        if "fips" in result.stdout.lower():
            results["provider_available"] = True
    except Exception as e:
        results["issues"].append(f"Failed to check FIPS provider: {e}")
    
    return results
