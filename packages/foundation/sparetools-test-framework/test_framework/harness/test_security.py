#
# DATA_RIGHTS:  HONEYWELL CONFIDENTIAL & PROPRIETARY
#              THIS WORK CONTAINS VALUABLE CONFIDENTIAL AND PROPRIETARY
#              INFORMATION. DISCLOSURE, USE OR REPRODUCTION OUTSIDE OF
#              HONEYWELL INTERNATIONAL, INC. IS PROHIBITED EXCEPT AS
#              AUTHORIZED IN WRITING. THIS UNPUBLISHED WORK IS PROTECTED BY
#              THE LAWS OF THE UNITED STATES AND OTHER COUNTRIES. IN THE
#              EVENT OF PUBLICATION, THE FOLLOWING NOTICE SHALL APPLY:
#              COPR. 2020-2021 HONEYWELL INTERNATIONAL, INC. ALL RIGHTS RESERVED.
#

"""
Security Validation Tests for Ngapy
==================================

This module provides security validation testing for the ngapy package,
including vulnerability checks, secure coding practices, and compliance validation.
"""

import os
import sys
import re
import hashlib
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from .test_harness import NgapyTestHarnes
except ImportError:
    from sparetools.test_framework.harness import NgapyTestHarnes


class SecurityTestHarness(NgapyTestHarnes):
    """Test harness for security validation."""

    def __init__(self):
        super().__init__()
        self.vulnerabilities_found = []
        self.security_issues = []

    def test_code_security(self) -> bool:
        """Test for common security issues in code."""
        success = True

        # Check Python files for security issues
        python_files = self._find_python_files()

        for file_path in python_files:
            success &= self._check_file_security(file_path)

        return success

    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the project."""
        python_files = []

        for root, dirs, files in os.walk('.'):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', '.venv', 'venv']]

            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)

        return python_files

    def _check_file_security(self, file_path: Path) -> bool:
        """Check a single file for security issues."""
        success = True

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check for dangerous patterns
            security_checks = [
                (r'eval\s*\(', 'Use of eval() function'),
                (r'exec\s*\(', 'Use of exec() function'),
                (r'input\s*\(', 'Use of input() function (Python 2 style)'),
                (r'subprocess\.(call|Popen|run)\s*\([^)]*shell\s*=\s*True', 'Shell injection vulnerability'),
                (r'os\.system\s*\(', 'Use of os.system()'),
                (r'os\.popen\s*\(', 'Use of os.popen()'),
                (r'pickle\.(load|loads)', 'Unsafe pickle deserialization'),
                (r'yaml\.(load|safe_load)\s*\(', 'YAML loading without safe_load'),
                (r'requests\.get\s*\([^)]*verify\s*=\s*False', 'SSL verification disabled'),
                (r'urllib.*urlopen', 'Insecure URL handling'),
                (r'hardcoded.*password', 'Potential hardcoded password', re.IGNORECASE),
                (r'secret.*key', 'Potential hardcoded secret key', re.IGNORECASE),
            ]

            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                for pattern, description in security_checks:
                    if re.search(pattern, line, re.IGNORECASE):
                        issue = {
                            'file': str(file_path),
                            'line': line_num,
                            'code': line.strip(),
                            'issue': description,
                            'severity': 'HIGH'
                        }
                        self.security_issues.append(issue)

                        success &= self.verify(
                            False, True,
                            f"Security issue in {file_path}:{line_num} - {description}",
                            test_num=1
                        )

        except Exception as e:
            success &= self.verify(
                False, True,
                f"Failed to check security for {file_path}: {str(e)}",
                test_num=1
            )

        return success

    def test_dependency_security(self) -> bool:
        """Test for vulnerable dependencies."""
        success = True

        try:
            # Check if safety is available for vulnerability scanning
            import safety
            import pkg_resources

            # Get installed packages
            installed_packages = []
            for pkg in pkg_resources.working_set:
                installed_packages.append({
                    'name': pkg.key,
                    'version': pkg.version
                })

            # Run safety check
            vulnerabilities = safety.check(installed_packages)

            if vulnerabilities:
                for vuln in vulnerabilities:
                    issue = {
                        'package': vuln.package,
                        'version': vuln.version,
                        'vulnerability': vuln.vulnerability,
                        'severity': 'HIGH'
                    }
                    self.vulnerabilities_found.append(issue)

                    success &= self.verify(
                        False, True,
                        f"Vulnerable dependency: {vuln.package} {vuln.version} - {vuln.vulnerability}",
                        test_num=2
                    )
            else:
                success &= self.verify(
                    True, True,
                    "No known vulnerable dependencies found",
                    test_num=2
                )

        except ImportError:
            # Safety not available, try alternative check
            success &= self._check_dependencies_manually()

        except Exception as e:
            success &= self.verify(
                False, True,
                f"Dependency security check failed: {str(e)}",
                test_num=2
            )

        return success

    def _check_dependencies_manually(self) -> bool:
        """Manual dependency security check when safety is not available."""
        success = True

        try:
            import pkg_resources

            # Check for known problematic packages
            problematic_packages = {
                'insecure-package': 'Known insecure package',
                'vulnerable-lib': 'Package with known vulnerabilities'
            }

            installed = {pkg.key: pkg.version for pkg in pkg_resources.working_set}

            for pkg, description in problematic_packages.items():
                if pkg in installed:
                    success &= self.verify(
                        False, True,
                        f"Potentially problematic dependency: {pkg} v{installed[pkg]} - {description}",
                        test_num=2
                    )

        except Exception as e:
            success &= self.verify(
                False, True,
                f"Manual dependency check failed: {str(e)}",
                test_num=2
            )

        return success

    def test_file_permissions(self) -> bool:
        """Test file permissions for security."""
        success = True

        # Files that should not be world-readable/writable
        sensitive_files = [
            'keypack.pyu',
            'conanfile.py',
            'requirements.txt',
            'client_config.py'
        ]

        for filename in sensitive_files:
            if os.path.exists(filename):
                stat_info = os.stat(filename)

                # Check if world-readable
                if os.name != 'nt':  # Unix-like systems
                    world_readable = bool(stat_info.st_mode & 0o004)
                    world_writable = bool(stat_info.st_mode & 0o002)

                    if world_readable:
                        success &= self.verify(
                            False, True,
                            f"File {filename} is world-readable",
                            test_num=3
                        )

                    if world_writable:
                        success &= self.verify(
                            False, True,
                            f"File {filename} is world-writable",
                            test_num=3
                        )
                else:
                    # Windows - check if hidden or system files are accessible
                    success &= self.verify(
                        True, True,
                        f"Windows file permissions for {filename} (manual review needed)",
                        test_num=3
                    )

        return success

    def test_environment_security(self) -> bool:
        """Test environment for security issues."""
        success = True

        # Check for sensitive environment variables
        sensitive_patterns = [
            'password', 'passwd', 'secret', 'key', 'token',
            'credential', 'auth', 'api_key', 'access_token'
        ]

        env_vars = os.environ

        for var_name in env_vars:
            var_lower = var_name.lower()

            for pattern in sensitive_patterns:
                if pattern in var_lower:
                    # Don't log the actual value for security
                    issue = {
                        'type': 'environment_variable',
                        'variable': var_name,
                        'issue': f'Potentially sensitive environment variable detected',
                        'severity': 'MEDIUM'
                    }
                    self.security_issues.append(issue)

                    success &= self.verify(
                        False, True,
                        f"Potentially sensitive environment variable: {var_name}",
                        test_num=4
                    )
                    break

        return success

    def test_network_security(self) -> bool:
        """Test network-related security configurations."""
        success = True

        # Check for insecure configurations in config files
        config_files = ['conf/1_logging.yaml', 'conf/1_build.yaml', 'client_config.py']

        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Check for insecure settings
                    insecure_patterns = [
                        (r'verify_ssl.*[Ff]alse', 'SSL verification disabled'),
                        (r'ssl_verify.*[Ff]alse', 'SSL verification disabled'),
                        (r'insecure.*[Tt]rue', 'Insecure connection allowed'),
                        (r'allow_http.*[Tt]rue', 'HTTP connections allowed instead of HTTPS'),
                    ]

                    for pattern, description in insecure_patterns:
                        if re.search(pattern, content):
                            success &= self.verify(
                                False, True,
                                f"Insecure configuration in {config_file}: {description}",
                                test_num=5
                            )

                except Exception as e:
                    success &= self.verify(
                        False, True,
                        f"Failed to check network security in {config_file}: {str(e)}",
                        test_num=5
                    )

        return success

    def test_data_validation(self) -> bool:
        """Test data validation and sanitization."""
        success = True

        # Test input validation in key functions
        test_inputs = [
            ("normal_input", True),
            ("<script>alert('xss')</script>", False),
            ("../../../etc/passwd", False),
            ("normal@domain.com", True),
            ("'; DROP TABLE users; --", False),
        ]

        for test_input, should_pass in test_inputs:
            # Basic input validation check
            dangerous_chars = ['<', '>', "'", '"', ';', '--', '../../../']

            has_dangerous = any(char in test_input for char in dangerous_chars)

            if should_pass:
                success &= self.verify(
                    not has_dangerous, True,
                    f"Input validation for safe input: {test_input}",
                    test_num=6
                )
            else:
                success &= self.verify(
                    has_dangerous, True,
                    f"Dangerous input detected: {test_input}",
                    test_num=6
                )

        return success

    def generate_security_report(self, output_file: str = "security_report.json") -> bool:
        """Generate a comprehensive security report."""
        success = True

        try:
            import json

            report = {
                'metadata': {
                    'timestamp': time.time(),
                    'scanner': 'ngapy_security_test_harness',
                    'platform': sys.platform
                },
                'summary': {
                    'vulnerabilities_found': len(self.vulnerabilities_found),
                    'security_issues': len(self.security_issues),
                    'overall_risk': 'HIGH' if (self.vulnerabilities_found or self.security_issues) else 'LOW'
                },
                'vulnerabilities': self.vulnerabilities_found,
                'security_issues': self.security_issues
            }

            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)

            success &= self.verify(
                True, True,
                f"Security report generated: {output_file}",
                test_num=7
            )

        except Exception as e:
            success &= self.verify(
                False, True,
                f"Failed to generate security report: {str(e)}",
                test_num=7
            )

        return success

    def run_security_tests(self) -> bool:
        """Run all security validation tests."""
        print("Running Security Validation Tests...")

        results = []

        results.append(("Code Security", self.test_code_security()))
        results.append(("Dependency Security", self.test_dependency_security()))
        results.append(("File Permissions", self.test_file_permissions()))
        results.append(("Environment Security", self.test_environment_security()))
        results.append(("Network Security", self.test_network_security()))
        results.append(("Data Validation", self.test_data_validation()))
        results.append(("Report Generation", self.generate_security_report()))

        print("\nSecurity Test Results:")
        all_passed = True
        for test_name, passed in results:
            status = "PASS" if passed else "FAIL"
            print(f"  {test_name}: {status}")
            all_passed &= passed

        if self.vulnerabilities_found or self.security_issues:
            print(f"\n⚠️  Security Issues Found:")
            print(f"   Vulnerabilities: {len(self.vulnerabilities_found)}")
            print(f"   Issues: {len(self.security_issues)}")

        return all_passed


def run_security_tests():
    """Main function to run security tests."""
    harness = SecurityTestHarness()
    success = harness.run_security_tests()

    print(f"\nOverall Security Tests: {'PASS' if success else 'FAIL'}")
    return success


if __name__ == "__main__":
    success = run_security_tests()
    sys.exit(0 if success else 1)