"""
Security Module Core

Security scanning and validation utilities for artifacts, including
vulnerability scanning, SBOM generation, and compliance checking.
"""

import hashlib
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

log = logging.getLogger(__name__)


def run_trivy_scan(target_path: str, severity: str = "CRITICAL,HIGH",
                   fail_on_findings: bool = True) -> Dict[str, Any]:
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


def generate_sbom(target_path: str, output_format: str = "cyclonedx-json",
                  output_file: Optional[str] = None) -> str:
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


def validate_package(target_path: str, run_trivy: bool = True,
                     generate_sbom_file: bool = True) -> Dict[str, Any]:
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


def check_fips_compliance(openssl_path: str) -> Dict[str, Any]:
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


def calculate_file_hash(file_path: str, algorithm: str = "sha256") -> Optional[str]:
    """
    Calculate hash of a file.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm (sha256, sha512, md5)

    Returns:
        Hexadecimal hash string or None if failed
    """
    if not os.path.exists(file_path):
        return None

    hash_func = getattr(hashlib, algorithm, None)
    if not hash_func:
        log.error(f"Unsupported hash algorithm: {algorithm}")
        return None

    try:
        with open(file_path, "rb") as f:
            h = hash_func()
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
            return h.hexdigest()
    except Exception as e:
        log.error(f"Failed to calculate {algorithm} hash for {file_path}: {e}")
        return None


def verify_file_integrity(file_path: str, expected_hash: str,
                         algorithm: str = "sha256") -> bool:
    """
    Verify file integrity against expected hash.

    Args:
        file_path: Path to file
        expected_hash: Expected hash value
        algorithm: Hash algorithm used

    Returns:
        True if hashes match, False otherwise
    """
    actual_hash = calculate_file_hash(file_path, algorithm)
    if actual_hash is None:
        return False

    return actual_hash.lower() == expected_hash.lower()


def scan_for_malware(target_path: str, use_clamav: bool = True) -> Dict[str, Any]:
    """
    Scan for malware using ClamAV.

    Args:
        target_path: Path to scan
        use_clamav: Whether to use ClamAV

    Returns:
        dict with scan results
    """
    if not use_clamav:
        return {"scanned": False, "message": "Malware scanning disabled"}

    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Target path not found: {target_path}")

    try:
        cmd = ["clamscan", "--recursive", "--infected", target_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        infected_count = 0
        if result.stdout:
            # Count infected files
            for line in result.stdout.split('\n'):
                if 'Infected files:' in line:
                    try:
                        infected_count = int(line.split(':')[1].strip())
                    except ValueError:
                        pass

        return {
            "scanned": True,
            "infected_count": infected_count,
            "passed": infected_count == 0,
            "clamav_output": result.stdout,
            "target": target_path
        }
    except FileNotFoundError:
        raise FileNotFoundError("ClamAV not installed. Install with: apt install clamav")
    except Exception as e:
        log.error(f"Malware scan failed: {e}")
        return {"scanned": False, "error": str(e)}


def check_file_permissions(file_path: str) -> Dict[str, Any]:
    """
    Check file permissions and ownership.

    Args:
        file_path: Path to file or directory

    Returns:
        dict with permission information
    """
    if not os.path.exists(file_path):
        return {"exists": False, "path": file_path}

    stat_info = os.stat(file_path)
    mode = stat_info.st_mode

    results = {
        "path": file_path,
        "exists": True,
        "is_file": os.path.isfile(file_path),
        "is_directory": os.path.isdir(file_path),
        "owner_readable": bool(mode & 0o400),
        "owner_writable": bool(mode & 0o200),
        "owner_executable": bool(mode & 0o100),
        "group_readable": bool(mode & 0o040),
        "group_writable": bool(mode & 0o020),
        "group_executable": bool(mode & 0o010),
        "other_readable": bool(mode & 0o004),
        "other_writable": bool(mode & 0o002),
        "other_executable": bool(mode & 0o001),
        "octal_mode": oct(mode)[-3:],  # Last 3 digits
        "uid": stat_info.st_uid,
        "gid": stat_info.st_gid,
    }

    # Check for security issues
    issues = []
    if results["other_writable"]:
        issues.append("World-writable file/directory")
    if results["other_executable"] and results["is_file"]:
        issues.append("World-executable file")

    results["issues"] = issues
    results["secure"] = len(issues) == 0

    return results


def validate_certificate(cert_path: str, ca_cert_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate X.509 certificate.

    Args:
        cert_path: Path to certificate file
        ca_cert_path: Path to CA certificate for chain validation

    Returns:
        dict with certificate validation results
    """
    if not os.path.exists(cert_path):
        return {"valid": False, "error": "Certificate file not found"}

    try:
        import ssl
        import OpenSSL.crypto as crypto

        # Load certificate
        with open(cert_path, 'rb') as f:
            cert_data = f.read()

        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)

        results = {
            "valid": True,
            "subject": str(cert.get_subject()),
            "issuer": str(cert.get_issuer()),
            "version": cert.get_version(),
            "serial": str(cert.get_serial_number()),
            "not_before": cert.get_notBefore().decode(),
            "not_after": cert.get_notAfter().decode(),
            "signature_algorithm": cert.get_signature_algorithm().decode(),
            "has_expired": False,
            "is_self_signed": False,
            "chain_valid": True,
        }

        # Check expiration
        try:
            results["has_expired"] = cert.has_expired()
        except Exception:
            # Some certificates might not have proper dates
            pass

        # Check if self-signed
        subject = cert.get_subject()
        issuer = cert.get_issuer()
        results["is_self_signed"] = str(subject) == str(issuer)

        # Validate chain if CA cert provided
        if ca_cert_path and os.path.exists(ca_cert_path):
            try:
                with open(ca_cert_path, 'rb') as f:
                    ca_data = f.read()
                ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, ca_data)

                # Create store and validate
                store = crypto.X509Store()
                store.add_cert(ca_cert)

                store_ctx = crypto.X509StoreContext(store, cert)
                store_ctx.verify_certificate()

            except Exception as e:
                results["chain_valid"] = False
                results["chain_error"] = str(e)

        return results

    except ImportError:
        return {"valid": False, "error": "pyOpenSSL not installed"}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def security_audit_path(target_path: str, recursive: bool = True) -> Dict[str, Any]:
    """
    Perform comprehensive security audit on a path.

    Args:
        target_path: Path to audit
        recursive: Whether to audit recursively

    Returns:
        dict with audit results
    """
    if not os.path.exists(target_path):
        return {"error": "Path not found", "path": target_path}

    audit_results = {
        "path": target_path,
        "total_files": 0,
        "total_directories": 0,
        "issues": [],
        "file_permissions": [],
        "suspicious_files": [],
        "audit_completed": False
    }

    try:
        for root, dirs, files in os.walk(target_path):
            audit_results["total_directories"] += len(dirs)
            audit_results["total_files"] += len(files)

            # Check directory permissions
            dir_perm = check_file_permissions(root)
            if not dir_perm.get("secure", True):
                audit_results["issues"].extend(dir_perm.get("issues", []))
                audit_results["file_permissions"].append(dir_perm)

            # Check file permissions
            for file in files:
                file_path = os.path.join(root, file)
                file_perm = check_file_permissions(file_path)
                if not file_perm.get("secure", True):
                    audit_results["issues"].extend(file_perm.get("issues", []))
                    audit_results["file_permissions"].append(file_perm)

                # Check for suspicious file extensions
                _, ext = os.path.splitext(file.lower())
                suspicious_exts = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com']
                if ext in suspicious_exts:
                    audit_results["suspicious_files"].append(file_path)

            if not recursive:
                break

        audit_results["audit_completed"] = True
        audit_results["issues_count"] = len(audit_results["issues"])

    except Exception as e:
        audit_results["error"] = str(e)

    return audit_results