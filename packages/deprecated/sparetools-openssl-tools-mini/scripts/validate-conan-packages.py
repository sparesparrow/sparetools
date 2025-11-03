#!/usr/bin/env python3
"""
Validate Conan package contents in local cache and remote repository
"""

import subprocess
import json
import os
from pathlib import Path

def validate_package(package_ref):
    """Validate a single package"""
    checks = {
        "exists": False,
        "has_files": False,
        "has_conaninfo": False,
        "file_count": 0,
        "issues": []
    }
    
    # Get package path
    try:
        result = subprocess.run(
            ["conan", "cache", "path", package_ref],
            capture_output=True, text=True, check=True
        )
        package_path = Path(result.stdout.strip())
        checks["exists"] = True
    except:
        checks["issues"].append("Package not found in cache")
        return checks
    
    # Check for files
    files = list(package_path.rglob("*"))
    checks["file_count"] = len([f for f in files if f.is_file()])
    checks["has_files"] = checks["file_count"] > 2  # More than just conanfile.py
    
    if not checks["has_files"]:
        checks["issues"].append(f"Only {checks['file_count']} files found")
    
    return checks

def validate_openssl_base():
    """Validate openssl-base package"""
    print("\n=== Validating openssl-base/1.0.0 ===")
    checks = validate_package("openssl-base/1.0.0")
    
    if checks["exists"]:
        # Check for Python package
        # Check for profiles
        pass
    
    return checks

def validate_openssl_fips_data():
    """Validate openssl-fips-data package"""
    print("\n=== Validating openssl-fips-data/140-3.1 ===")
    return validate_package("openssl-fips-data/140-3.1")

def validate_openssl_tools():
    """Validate openssl-tools package"""
    print("\n=== Validating openssl-tools/1.2.0 ===")
    return validate_package("openssl-tools/1.2.0")

def validate_openssl():
    """Validate openssl package"""
    print("\n=== Validating openssl/3.6.0 ===")
    checks = validate_package("openssl/3.6.0")
    
    # Check for libraries
    # Check for headers
    # Check for binaries
    
    return checks

if __name__ == "__main__":
    results = {
        "openssl-base": validate_openssl_base(),
        "openssl-fips-data": validate_openssl_fips_data(),
        "openssl-tools": validate_openssl_tools(),
        "openssl": validate_openssl()
    }
    
    # Print summary
    print("\n=== VALIDATION SUMMARY ===")
    for pkg, checks in results.items():
        status = "✅ PASS" if checks["exists"] and checks["has_files"] else "❌ FAIL"
        print(f"{status} {pkg}: {checks['file_count']} files")
        if checks["issues"]:
            for issue in checks["issues"]:
                print(f"  ⚠️  {issue}")



