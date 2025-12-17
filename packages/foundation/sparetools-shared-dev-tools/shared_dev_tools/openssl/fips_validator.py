#!/usr/bin/env python3
"""
FIPS Compliance Validator for OpenSSL

This module provides automated FIPS 140-2/140-3 compliance validation
for OpenSSL builds and configurations.
"""

import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, NamedTuple
from dataclasses import dataclass
from enum import Enum


class FIPSLevel(Enum):
    """FIPS compliance levels."""
    FIPS_140_2 = "140-2"
    FIPS_140_3 = "140-3"


class ValidationStatus(Enum):
    """Validation result status."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"


class ValidationResult(NamedTuple):
    """Result of a validation check."""
    check_name: str
    status: ValidationStatus
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class FIPSValidationReport:
    """Comprehensive FIPS validation report."""
    openssl_version: str
    fips_level: FIPSLevel
    timestamp: str
    overall_status: ValidationStatus
    results: List[ValidationResult]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "openssl_version": self.openssl_version,
            "fips_level": self.fips_level.value,
            "timestamp": self.timestamp,
            "overall_status": self.overall_status.value,
            "results": [
                {
                    "check_name": r.check_name,
                    "status": r.status.value,
                    "message": r.message,
                    "details": r.details
                } for r in self.results
            ],
            "recommendations": self.recommendations
        }


class FIPSValidator:
    """
    Automated FIPS compliance validator for OpenSSL.

    This class performs comprehensive validation of OpenSSL builds
    against FIPS 140-2 and 140-3 requirements.
    """

    # FIPS-required algorithms and their minimum strengths
    FIPS_ALGORITHMS = {
        "AES": {"min_key_size": 128, "modes": ["CBC", "GCM", "ECB"]},
        "RSA": {"min_key_size": 2048, "max_key_size": 4096},
        "ECDSA": {"curves": ["P-256", "P-384", "P-521"]},
        "SHA": {"variants": ["SHA-256", "SHA-384", "SHA-512"]},
        "HMAC": {"variants": ["HMAC-SHA-256", "HMAC-SHA-384", "HMAC-SHA-512"]},
        "DRBG": {"mechanisms": ["CTR_DRBG", "HMAC_DRBG", "HASH_DRBG"]}
    }

    def __init__(self, openssl_path: Optional[str] = None, fips_level: FIPSLevel = FIPSLevel.FIPS_140_3):
        """
        Initialize the FIPS validator.

        Args:
            openssl_path: Path to OpenSSL executable
            fips_level: FIPS compliance level to validate against
        """
        self.openssl_path = openssl_path or self._find_openssl()
        self.fips_level = fips_level
        self.validation_cache: Dict[str, ValidationResult] = {}

    def _find_openssl(self) -> str:
        """Find OpenSSL executable in PATH."""
        common_paths = [
            "/usr/bin/openssl",
            "/usr/local/bin/openssl",
            "/opt/openssl/bin/openssl",
            "openssl"
        ]

        for path in common_paths:
            if os.path.exists(path) or self._is_command_available(path):
                return path

        raise FileNotFoundError("OpenSSL executable not found")

    def _is_command_available(self, command: str) -> bool:
        """Check if a command is available in PATH."""
        try:
            subprocess.run([command, "version"],
                         capture_output=True,
                         check=True,
                         timeout=10)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def validate_build(self, build_path: Optional[str] = None) -> FIPSValidationReport:
        """
        Perform comprehensive FIPS validation of an OpenSSL build.

        Args:
            build_path: Path to OpenSSL build directory (optional)

        Returns:
            Comprehensive validation report
        """
        import datetime
        timestamp = datetime.datetime.now().isoformat()

        # Get OpenSSL version
        version = self._get_openssl_version()

        # Perform all validation checks
        results = []
        results.extend(self._validate_fips_mode())
        results.extend(self._validate_algorithms())
        results.extend(self._validate_configuration())
        results.extend(self._validate_self_tests())
        results.extend(self._validate_module_integrity())

        if build_path:
            results.extend(self._validate_build_artifacts(build_path))

        # Determine overall status
        overall_status = self._calculate_overall_status(results)

        # Generate recommendations
        recommendations = self._generate_recommendations(results)

        return FIPSValidationReport(
            openssl_version=version,
            fips_level=self.fips_level,
            timestamp=timestamp,
            overall_status=overall_status,
            results=results,
            recommendations=recommendations
        )

    def _get_openssl_version(self) -> str:
        """Get OpenSSL version string."""
        try:
            result = subprocess.run([self.openssl_path, "version"],
                                  capture_output=True,
                                  text=True,
                                  timeout=10)
            return result.stdout.strip().split()[1] if result.returncode == 0 else "unknown"
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return "unknown"

    def _validate_fips_mode(self) -> List[ValidationResult]:
        """Validate FIPS mode configuration."""
        results = []

        try:
            # Check if FIPS is available
            result = subprocess.run([self.openssl_path, "list", "-providers"],
                                  capture_output=True,
                                  text=True,
                                  timeout=10)

            if result.returncode == 0:
                if "fips" in result.stdout.lower():
                    results.append(ValidationResult(
                        "fips_provider_available",
                        ValidationStatus.PASS,
                        "FIPS provider is available"
                    ))
                else:
                    results.append(ValidationResult(
                        "fips_provider_available",
                        ValidationStatus.FAIL,
                        "FIPS provider not found in available providers"
                    ))
            else:
                results.append(ValidationResult(
                    "fips_provider_available",
                    ValidationStatus.FAIL,
                    "Failed to query providers"
                ))

        except subprocess.TimeoutExpired:
            results.append(ValidationResult(
                "fips_provider_available",
                ValidationStatus.FAIL,
                "Timeout querying FIPS provider"
            ))

        # Check FIPS configuration file
        fips_config_paths = [
            "/etc/ssl/fipsmodule.cnf",
            "/usr/local/ssl/fipsmodule.cnf",
            "/opt/openssl/ssl/fipsmodule.cnf"
        ]

        fips_config_found = any(os.path.exists(path) for path in fips_config_paths)
        if fips_config_found:
            results.append(ValidationResult(
                "fips_configuration_file",
                ValidationStatus.PASS,
                "FIPS configuration file found"
            ))
        else:
            results.append(ValidationResult(
                "fips_configuration_file",
                ValidationStatus.WARNING,
                "FIPS configuration file not found in standard locations"
            ))

        return results

    def _validate_algorithms(self) -> List[ValidationResult]:
        """Validate FIPS-required algorithms."""
        results = []

        try:
            # Get list of supported ciphers
            result = subprocess.run([self.openssl_path, "ciphers"],
                                  capture_output=True,
                                  text=True,
                                  timeout=10)

            if result.returncode == 0:
                ciphers = result.stdout.upper()

                # Check AES requirements
                aes_required = ["AES128", "AES256"]
                aes_found = [cipher for cipher in aes_required if cipher in ciphers]

                if len(aes_found) == len(aes_required):
                    results.append(ValidationResult(
                        "aes_algorithms",
                        ValidationStatus.PASS,
                        f"AES algorithms available: {', '.join(aes_found)}"
                    ))
                else:
                    results.append(ValidationResult(
                        "aes_algorithms",
                        ValidationStatus.FAIL,
                        f"Missing AES algorithms: {', '.join(set(aes_required) - set(aes_found))}"
                    ))
            else:
                results.append(ValidationResult(
                    "cipher_list",
                    ValidationStatus.FAIL,
                    "Failed to get cipher list"
                ))

        except subprocess.TimeoutExpired:
            results.append(ValidationResult(
                "cipher_list",
                ValidationStatus.FAIL,
                "Timeout getting cipher list"
            ))

        # Check digest algorithms
        try:
            result = subprocess.run([self.openssl_path, "dgst", "-list"],
                                  capture_output=True,
                                  text=True,
                                  timeout=10)

            if result.returncode == 0:
                digests = result.stdout.upper()

                required_digests = ["SHA256", "SHA384", "SHA512"]
                digests_found = [d for d in required_digests if d in digests]

                if len(digests_found) == len(required_digests):
                    results.append(ValidationResult(
                        "digest_algorithms",
                        ValidationStatus.PASS,
                        f"Required digest algorithms available: {', '.join(digests_found)}"
                    ))
                else:
                    missing = set(required_digests) - set(digests_found)
                    results.append(ValidationResult(
                        "digest_algorithms",
                        ValidationStatus.FAIL,
                        f"Missing digest algorithms: {', '.join(missing)}"
                    ))
            else:
                results.append(ValidationResult(
                    "digest_algorithms",
                    ValidationStatus.FAIL,
                    "Failed to get digest list"
                ))

        except subprocess.TimeoutExpired:
            results.append(ValidationResult(
                "digest_algorithms",
                ValidationStatus.FAIL,
                "Timeout getting digest list"
            ))

        return results

    def _validate_configuration(self) -> List[ValidationResult]:
        """Validate OpenSSL configuration for FIPS compliance."""
        results = []

        # Check for secure configuration options
        config_checks = [
            ("no_ssl2", "SSLv2 disabled"),
            ("no_ssl3", "SSLv3 disabled"),
            ("no_tls1", "TLSv1.0 disabled"),
            ("no_tls1_1", "TLSv1.1 disabled"),
            ("no_weak_ssl_ciphers", "Weak SSL ciphers disabled"),
            ("no_md5", "MD5 disabled"),
            ("no_rc4", "RC4 disabled")
        ]

        for check, description in config_checks:
            # This is a simplified check - in practice, you'd parse openssl.cnf
            results.append(ValidationResult(
                f"config_{check}",
                ValidationStatus.WARNING,
                f"{description} - manual verification required"
            ))

        return results

    def _validate_self_tests(self) -> List[ValidationResult]:
        """Validate that FIPS self-tests are working."""
        results = []

        # Run basic self-test
        try:
            result = subprocess.run([self.openssl_path, "fipsinstall", "-verify"],
                                  capture_output=True,
                                  text=True,
                                  timeout=30)

            if result.returncode == 0:
                results.append(ValidationResult(
                    "fips_self_test",
                    ValidationStatus.PASS,
                    "FIPS self-test passed"
                ))
            else:
                results.append(ValidationResult(
                    "fips_self_test",
                    ValidationStatus.FAIL,
                    f"FIPS self-test failed: {result.stderr.strip()}"
                ))

        except subprocess.TimeoutExpired:
            results.append(ValidationResult(
                "fips_self_test",
                ValidationStatus.FAIL,
                "FIPS self-test timed out"
            ))
        except FileNotFoundError:
            results.append(ValidationResult(
                "fips_self_test",
                ValidationStatus.SKIP,
                "fipsinstall command not available"
            ))

        return results

    def _validate_module_integrity(self) -> List[ValidationResult]:
        """Validate FIPS module integrity."""
        results = []

        # Check for FIPS module file
        fips_module_paths = [
            "/usr/lib64/ossl-modules/fips.so",
            "/usr/lib/ossl-modules/fips.so",
            "/usr/local/lib64/ossl-modules/fips.so",
            "/usr/local/lib/ossl-modules/fips.so"
        ]

        fips_module_found = any(os.path.exists(path) for path in fips_module_paths)

        if fips_module_found:
            results.append(ValidationResult(
                "fips_module_integrity",
                ValidationStatus.PASS,
                "FIPS module found"
            ))
        else:
            results.append(ValidationResult(
                "fips_module_integrity",
                ValidationStatus.WARNING,
                "FIPS module not found in standard locations"
            ))

        return results

    def _validate_build_artifacts(self, build_path: str) -> List[ValidationResult]:
        """Validate build artifacts for FIPS compliance."""
        results = []

        build_path = Path(build_path)

        # Check for required build artifacts
        required_files = [
            "libcrypto.so",
            "libssl.so",
            "fips.so"
        ]

        for file in required_files:
            file_path = build_path / file
            if file_path.exists():
                results.append(ValidationResult(
                    f"build_artifact_{file}",
                    ValidationStatus.PASS,
                    f"Build artifact {file} found"
                ))
            else:
                results.append(ValidationResult(
                    f"build_artifact_{file}",
                    ValidationStatus.FAIL,
                    f"Required build artifact {file} not found"
                ))

        return results

    def _calculate_overall_status(self, results: List[ValidationResult]) -> ValidationStatus:
        """Calculate overall validation status."""
        if any(r.status == ValidationStatus.FAIL for r in results):
            return ValidationStatus.FAIL
        elif any(r.status == ValidationStatus.WARNING for r in results):
            return ValidationStatus.WARNING
        elif all(r.status == ValidationStatus.PASS for r in results):
            return ValidationStatus.PASS
        else:
            return ValidationStatus.SKIP

    def _generate_recommendations(self, results: List[ValidationResult]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        failed_checks = [r for r in results if r.status == ValidationStatus.FAIL]
        warning_checks = [r for r in results if r.status == ValidationStatus.WARNING]

        if failed_checks:
            recommendations.append("Address all FAILED validation checks before deploying in production")

        if warning_checks:
            recommendations.append("Review WARNING checks and consider remediation where appropriate")

        # Specific recommendations
        check_names = {r.check_name for r in results}

        if "fips_provider_available" in check_names:
            provider_result = next(r for r in results if r.check_name == "fips_provider_available")
            if provider_result.status == ValidationStatus.FAIL:
                recommendations.append("Install FIPS provider or rebuild OpenSSL with FIPS support")

        if any("aes_algorithms" in r.check_name and r.status == ValidationStatus.FAIL for r in results):
            recommendations.append("Ensure AES-128 and AES-256 algorithms are enabled in the build")

        if any("digest_algorithms" in r.check_name and r.status == ValidationStatus.FAIL for r in results):
            recommendations.append("Enable SHA-256, SHA-384, and SHA-512 digest algorithms")

        return recommendations

    def validate_algorithm_strength(self, algorithm: str, key_size: int) -> ValidationResult:
        """
        Validate algorithm key strength against FIPS requirements.

        Args:
            algorithm: Algorithm name (e.g., 'RSA', 'AES')
            key_size: Key size in bits

        Returns:
            Validation result
        """
        if algorithm not in self.FIPS_ALGORITHMS:
            return ValidationResult(
                f"algorithm_{algorithm}_strength",
                ValidationStatus.SKIP,
                f"Algorithm {algorithm} not in FIPS requirements"
            )

        requirements = self.FIPS_ALGORITHMS[algorithm]
        min_size = requirements.get("min_key_size", 0)

        if key_size >= min_size:
            return ValidationResult(
                f"algorithm_{algorithm}_strength",
                ValidationStatus.PASS,
                f"{algorithm}-{key_size} meets FIPS minimum key strength ({min_size} bits)"
            )
        else:
            return ValidationResult(
                f"algorithm_{algorithm}_strength",
                ValidationStatus.FAIL,
                f"{algorithm}-{key_size} does not meet FIPS minimum key strength ({min_size} bits)"
            )

    def save_report(self, report: FIPSValidationReport, output_path: str) -> None:
        """
        Save validation report to file.

        Args:
            report: Validation report to save
            output_path: Path to save the report
        """
        with open(output_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)

        print(f"FIPS validation report saved to: {output_path}")

    def print_report(self, report: FIPSValidationReport) -> None:
        """
        Print validation report to console.

        Args:
            report: Validation report to print
        """
        print(f"\n{'='*60}")
        print(f"FIPS {report.fips_level.value} Validation Report")
        print(f"{'='*60}")
        print(f"OpenSSL Version: {report.openssl_version}")
        print(f"Timestamp: {report.timestamp}")
        print(f"Overall Status: {report.overall_status.value.upper()}")
        print(f"{'='*60}\n")

        print("Validation Results:")
        for result in report.results:
            status_symbol = {
                ValidationStatus.PASS: "✓",
                ValidationStatus.FAIL: "✗",
                ValidationStatus.WARNING: "⚠",
                ValidationStatus.SKIP: "-"
            }[result.status]

            print(f"{status_symbol} {result.check_name}: {result.message}")

        if report.recommendations:
            print(f"\n{'='*60}")
            print("Recommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"{i}. {rec}")

        print(f"{'='*60}\n")