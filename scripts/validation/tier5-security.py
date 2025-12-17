#!/usr/bin/env python3
"""
Tier 5 Validation: Security and Compliance

Final validation tier focusing on security gates, compliance checks,
vulnerability assessments, and regulatory requirements.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from recipe_base import load_consumer_config, get_consumer_packages


class SecurityValidator:
    """Validates security and compliance requirements."""

    def __init__(self, verbose: bool = False, strict: bool = False):
        """Initialize security validator.

        Args:
            verbose: Enable verbose output
            strict: Enable strict validation (fail on warnings)
        """
        self.verbose = verbose
        self.strict = strict
        self.results = {
            "security_scans": {},
            "compliance_checks": {},
            "vulnerability_assessment": {},
            "regulatory_requirements": {},
            "risk_assessment": {},
            "critical_issues": [],
            "warnings": []
        }

    def log(self, message: str) -> None:
        """Log a message if verbose."""
        if self.verbose:
            print(f"[TIER5] {message}")

    def run_security_validation(self, consumers: List[str] = None) -> bool:
        """Run complete security and compliance validation.

        Args:
            consumers: Specific consumers to validate

        Returns:
            True if all security checks pass
        """
        print("🔍 Running Tier 5 Validation: Security and Compliance")

        consumers_to_check = consumers or ["openssl", "mia", "mcp", "android", "audio", "automotive"]

        # Run security scans
        self._run_security_scans(consumers_to_check)

        # Check compliance requirements
        self._check_compliance_requirements(consumers_to_check)

        # Assess vulnerabilities
        self._assess_vulnerabilities(consumers_to_check)

        # Validate regulatory requirements
        self._validate_regulatory_requirements(consumers_to_check)

        # Perform risk assessment
        self._perform_risk_assessment(consumers_to_check)

        # Report results
        self._report_results()

        # Return success based on critical issues
        critical_count = len(self.results["critical_issues"])
        warning_count = len(self.results["warnings"])

        if critical_count > 0:
            success = False
        elif self.strict and warning_count > 0:
            success = False
        else:
            success = True

        status = "✅ PASSED" if success else "❌ FAILED"
        severity = "CRITICAL" if critical_count > 0 else "WARNING" if warning_count > 0 else "NONE"
        print(f"\n{status} - {critical_count} critical, {warning_count} warnings ({severity})")

        return success

    def _run_security_scans(self, consumers: List[str]) -> None:
        """Run security scans on all consumers."""
        self.log("Running security scans...")

        for consumer in consumers:
            self.log(f"Scanning consumer: {consumer}")

            # Run container image scanning (simulate)
            scan_result = self._simulate_security_scan(consumer)
            self.results["security_scans"][consumer] = scan_result

            # Check for critical issues
            if scan_result.get("critical_vulnerabilities", 0) > 0:
                self.results["critical_issues"].append({
                    "type": "security_scan",
                    "consumer": consumer,
                    "issue": f"Found {scan_result['critical_vulnerabilities']} critical vulnerabilities",
                    "severity": "CRITICAL"
                })

            # Check for high severity issues
            if scan_result.get("high_vulnerabilities", 0) > 10:
                self.results["warnings"].append({
                    "type": "security_scan",
                    "consumer": consumer,
                    "issue": f"Found {scan_result['high_vulnerabilities']} high-severity vulnerabilities",
                    "severity": "WARNING"
                })

    def _check_compliance_requirements(self, consumers: List[str]) -> None:
        """Check compliance requirements for each consumer."""
        self.log("Checking compliance requirements...")

        compliance_requirements = {
            "openssl": ["FIPS_140_3", "OPENSSL_LICENSE", "EXPORT_COMPLIANCE"],
            "mia": ["GDPR_COMPLIANCE", "DATA_ENCRYPTION", "AUDIT_LOGGING"],
            "mcp": ["API_SECURITY", "AUTHENTICATION", "DATA_PROTECTION"],
            "android": ["ANDROID_SECURITY", "JNI_SANITIZATION", "APP_PERMISSIONS"],
            "audio": ["DATA_PRIVACY", "NETWORK_SECURITY"],
            "automotive": ["ISO_26262", "AUTOMOTIVE_SECURITY", "SAFETY_CRITICAL"]
        }

        for consumer in consumers:
            requirements = compliance_requirements.get(consumer, ["BASIC_SECURITY"])
            compliance_result = self._check_consumer_compliance(consumer, requirements)
            self.results["compliance_checks"][consumer] = compliance_result

            # Check for compliance failures
            failed_reqs = [req for req, status in compliance_result.items() if not status]
            if failed_reqs:
                self.results["critical_issues"].append({
                    "type": "compliance_failure",
                    "consumer": consumer,
                    "issue": f"Failed compliance requirements: {', '.join(failed_reqs)}",
                    "severity": "CRITICAL"
                })

    def _assess_vulnerabilities(self, consumers: List[str]) -> None:
        """Assess vulnerabilities across the ecosystem."""
        self.log("Assessing vulnerabilities...")

        # Aggregate vulnerability data across consumers
        total_critical = 0
        total_high = 0
        total_medium = 0

        for consumer in consumers:
            scan_result = self.results["security_scans"].get(consumer, {})
            total_critical += scan_result.get("critical_vulnerabilities", 0)
            total_high += scan_result.get("high_vulnerabilities", 0)
            total_medium += scan_result.get("medium_vulnerabilities", 0)

        vulnerability_assessment = {
            "total_critical": total_critical,
            "total_high": total_high,
            "total_medium": total_medium,
            "risk_level": self._calculate_risk_level(total_critical, total_high),
            "recommendations": self._generate_security_recommendations(total_critical, total_high)
        }

        self.results["vulnerability_assessment"] = vulnerability_assessment

        # Flag high-risk situations
        if vulnerability_assessment["risk_level"] in ["CRITICAL", "HIGH"]:
            self.results["critical_issues"].append({
                "type": "vulnerability_assessment",
                "issue": f"Overall risk level: {vulnerability_assessment['risk_level']}",
                "severity": "CRITICAL"
            })

    def _validate_regulatory_requirements(self, consumers: List[str]) -> None:
        """Validate regulatory requirements."""
        self.log("Validating regulatory requirements...")

        regulatory_checks = {
            "openssl": ["OPENSSL_FIPS_CERTIFICATION", "EXPORT_CONTROL_COMPLIANCE"],
            "mia": ["GDPR_DATA_PROTECTION", "IoT_SECURITY_STANDARDS"],
            "mcp": ["API_REGULATORY_COMPLIANCE", "DATA_PRIVACY_LAWS"],
            "android": ["GOOGLE_PLAY_SECURITY", "ANDROID_ENTERPRISE_SECURITY"],
            "automotive": ["ISO_26262_SAFETY", "AUTOMOTIVE_CYBERSECURITY"]
        }

        for consumer in consumers:
            checks = regulatory_checks.get(consumer, [])
            regulatory_result = {}

            for check in checks:
                # Simulate regulatory validation
                regulatory_result[check] = self._simulate_regulatory_check(check)

            self.results["regulatory_requirements"][consumer] = regulatory_result

            # Check for regulatory failures
            failed_checks = [check for check, passed in regulatory_result.items() if not passed]
            if failed_checks:
                self.results["critical_issues"].append({
                    "type": "regulatory_failure",
                    "consumer": consumer,
                    "issue": f"Failed regulatory checks: {', '.join(failed_checks)}",
                    "severity": "CRITICAL"
                })

    def _perform_risk_assessment(self, consumers: List[str]) -> None:
        """Perform overall risk assessment."""
        self.log("Performing risk assessment...")

        risk_factors = {
            "vulnerability_count": len(self.results["critical_issues"]),
            "compliance_failures": sum(1 for issue in self.results["critical_issues"]
                                     if issue["type"] == "compliance_failure"),
            "regulatory_failures": sum(1 for issue in self.results["critical_issues"]
                                     if issue["type"] == "regulatory_failure"),
            "consumers_affected": len(set(issue["consumer"] for issue in self.results["critical_issues"]
                                        if "consumer" in issue))
        }

        # Calculate overall risk score
        risk_score = (
            risk_factors["vulnerability_count"] * 10 +
            risk_factors["compliance_failures"] * 15 +
            risk_factors["regulatory_failures"] * 20
        )

        if risk_score == 0:
            overall_risk = "LOW"
        elif risk_score < 50:
            overall_risk = "MEDIUM"
        elif risk_score < 100:
            overall_risk = "HIGH"
        else:
            overall_risk = "CRITICAL"

        risk_assessment = {
            "risk_score": risk_score,
            "overall_risk": overall_risk,
            "risk_factors": risk_factors,
            "mitigation_required": overall_risk in ["HIGH", "CRITICAL"],
            "audit_recommended": overall_risk == "CRITICAL"
        }

        self.results["risk_assessment"] = risk_assessment

    def _simulate_security_scan(self, consumer: str) -> Dict[str, Any]:
        """Simulate a security scan for a consumer."""
        # In real implementation, this would run actual security tools
        # For now, return simulated results based on consumer type

        base_results = {
            "scanned_files": 100,
            "scan_duration": "45s",
            "critical_vulnerabilities": 0,
            "high_vulnerabilities": 2,
            "medium_vulnerabilities": 5,
            "low_vulnerabilities": 12,
            "passed": True
        }

        # Adjust based on consumer (some consumers might have more/less issues)
        if consumer == "openssl":
            # OpenSSL might have more security scrutiny
            base_results["critical_vulnerabilities"] = 0
            base_results["high_vulnerabilities"] = 1
        elif consumer == "android":
            # Android might have more medium issues
            base_results["medium_vulnerabilities"] = 8

        return base_results

    def _check_consumer_compliance(self, consumer: str, requirements: List[str]) -> Dict[str, bool]:
        """Check compliance requirements for a consumer."""
        results = {}

        for requirement in requirements:
            # Simulate compliance checks
            if requirement in ["FIPS_140_3", "OPENSSL_LICENSE", "BASIC_SECURITY"]:
                results[requirement] = True  # Assume these pass
            elif requirement in ["GDPR_COMPLIANCE", "API_SECURITY"]:
                results[requirement] = True  # Assume these pass for now
            else:
                results[requirement] = False  # Simulate some failures

        return results

    def _calculate_risk_level(self, critical: int, high: int) -> str:
        """Calculate overall risk level."""
        if critical > 0:
            return "CRITICAL"
        elif high > 5:
            return "HIGH"
        elif high > 0:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_security_recommendations(self, critical: int, high: int) -> List[str]:
        """Generate security recommendations based on vulnerability counts."""
        recommendations = []

        if critical > 0:
            recommendations.append("Address all critical vulnerabilities immediately")
            recommendations.append("Consider delaying deployment until critical issues are resolved")

        if high > 0:
            recommendations.append("Plan to address high-severity vulnerabilities in next sprint")
            recommendations.append("Review security patching process")

        if critical == 0 and high == 0:
            recommendations.append("Maintain current security practices")
            recommendations.append("Continue regular security scanning")

        return recommendations

    def _simulate_regulatory_check(self, check: str) -> bool:
        """Simulate a regulatory compliance check."""
        # In real implementation, this would check actual regulatory compliance
        # For simulation, most checks pass
        passing_checks = [
            "OPENSSL_FIPS_CERTIFICATION",
            "GDPR_DATA_PROTECTION",
            "API_REGULATORY_COMPLIANCE",
            "ANDROID_SECURITY"
        ]

        return check in passing_checks

    def _report_results(self) -> None:
        """Report security validation results."""
        print("\nSecurity & Compliance Validation Results:")

        # Security scans summary
        if self.results["security_scans"]:
            print(f"Security Scans: {len(self.results['security_scans'])} consumers")
            for consumer, scan in self.results["security_scans"].items():
                critical = scan.get("critical_vulnerabilities", 0)
                high = scan.get("high_vulnerabilities", 0)
                print(f"  {consumer}: {critical} critical, {high} high vulnerabilities")

        # Compliance checks summary
        if self.results["compliance_checks"]:
            print(f"\nCompliance Checks: {len(self.results['compliance_checks'])} consumers")
            total_passed = 0
            total_checked = 0
            for consumer, checks in self.results["compliance_checks"].items():
                passed = sum(1 for status in checks.values() if status)
                total_passed += passed
                total_checked += len(checks)
                print(f"  {consumer}: {passed}/{len(checks)} requirements met")

            if total_checked > 0:
                compliance_rate = (total_passed / total_checked) * 100
                print(".1f")

        # Vulnerability assessment
        vuln = self.results.get("vulnerability_assessment", {})
        if vuln:
            print("
Vulnerability Assessment:"            print(f"  Risk Level: {vuln.get('risk_level', 'UNKNOWN')}")
            print(f"  Critical: {vuln.get('total_critical', 0)}")
            print(f"  High: {vuln.get('total_high', 0)}")
            print(f"  Medium: {vuln.get('total_medium', 0)}")

        # Risk assessment
        risk = self.results.get("risk_assessment", {})
        if risk:
            print("
Risk Assessment:"            print(f"  Overall Risk: {risk.get('overall_risk', 'UNKNOWN')}")
            print(f"  Risk Score: {risk.get('risk_score', 0)}")

        # Critical issues
        if self.results["critical_issues"]:
            print(f"\n❌ Critical Issues: {len(self.results['critical_issues'])}")
            for issue in self.results["critical_issues"]:
                print(f"  - {issue['consumer']}: {issue['issue']}")

        # Warnings
        if self.results["warnings"]:
            print(f"\n⚠️  Warnings: {len(self.results['warnings'])}")
            for warning in self.results["warnings"]:
                print(f"  - {warning.get('consumer', 'system')}: {warning['issue']}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Tier 5 Validation: Security and Compliance"
    )

    parser.add_argument(
        "--consumer",
        action="append",
        help="Specific consumer to validate"
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict validation (fail on warnings)"
    )

    parser.add_argument(
        "--skip-regulatory",
        action="store_true",
        help="Skip regulatory compliance checks"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    validator = SecurityValidator(verbose=args.verbose, strict=args.strict)
    success = validator.run_security_validation(consumers=args.consumer)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()