#!/usr/bin/env python3
"""
Advanced Dependency Management System
Inspired by ngaims-icd-dev and oms-dev patterns for automated dependency updates
"""

import os
import sys
import json
import yaml
import logging
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DependencyManager:
    """Advanced dependency management with automated updates and vulnerability scanning"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.conanfile_path = project_root / "conanfile.py"
        self.dependency_config_path = project_root / "conan-dev" / "dependency-config.yml"
        self.vulnerability_db_path = project_root / "conan-dev" / "vulnerability-db.json"
        self.update_log_path = project_root / "conan-dev" / "dependency-updates.log"
        
        # Create directories
        self.dependency_config_path.parent.mkdir(parents=True, exist_ok=True)
        
    def setup_dependency_config(self):
        """Set up dependency configuration based on oms-dev patterns"""
        config = {
            "dependency_management": {
                "auto_update": {
                    "enabled": True,
                    "schedule": "weekly",  # daily, weekly, monthly
                    "exclude_packages": [
                        "openssl",  # Don't auto-update OpenSSL itself
                        "titan-python-environment"  # Critical system packages
                    ],
                    "update_strategy": "patch",  # patch, minor, major
                    "test_after_update": True,
                    "rollback_on_failure": True
                },
                "vulnerability_scanning": {
                    "enabled": True,
                    "scan_schedule": "daily",
                    "severity_threshold": "medium",  # low, medium, high, critical
                    "auto_fix": False,  # Auto-apply security patches
                    "notification_channels": ["github_issues", "email"]
                },
                "license_compliance": {
                    "enabled": True,
                    "allowed_licenses": [
                        "Apache-2.0", "MIT", "BSD-3-Clause", "BSD-2-Clause",
                        "ISC", "Zlib", "OpenSSL", "LGPL-2.1", "LGPL-3.0"
                    ],
                    "blocked_licenses": [
                        "GPL-2.0", "GPL-3.0", "AGPL-3.0"
                    ],
                    "require_approval": [
                        "LGPL-2.1", "LGPL-3.0"
                    ]
                },
                "dependency_sources": {
                    "conan_center": {
                        "enabled": True,
                        "priority": 1
                    },
                    "artifactory": {
                        "enabled": True,
                        "priority": 2,
                        "url": os.getenv("ARTIFACTORY_URL", ""),
                        "username": os.getenv("ARTIFACTORY_USERNAME", ""),
                        "password": os.getenv("ARTIFACTORY_TOKEN", "")
                    },
                    "github_packages": {
                        "enabled": True,
                        "priority": 3
                    }
                }
            },
            "monitoring": {
                "metrics_collection": True,
                "update_history": True,
                "vulnerability_tracking": True,
                "license_tracking": True
            }
        }
        
        with open(self.dependency_config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"✅ Dependency configuration created: {self.dependency_config_path}")
    
    def scan_vulnerabilities(self) -> Dict:
        """Scan for known vulnerabilities in dependencies"""
        logger.info("🔍 Scanning for vulnerabilities...")
        
        vulnerabilities = {
            "scan_timestamp": datetime.now().isoformat(),
            "packages_scanned": 0,
            "vulnerabilities_found": [],
            "severity_summary": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }
        
        try:
            # Get current dependencies from conanfile.py
            dependencies = self._extract_dependencies()
            vulnerabilities["packages_scanned"] = len(dependencies)
            
            for dep_name, dep_version in dependencies.items():
                # Check against known vulnerability databases
                vulns = self._check_package_vulnerabilities(dep_name, dep_version)
                vulnerabilities["vulnerabilities_found"].extend(vulns)
                
                # Update severity summary
                for vuln in vulns:
                    severity = vuln.get("severity", "unknown").lower()
                    if severity in vulnerabilities["severity_summary"]:
                        vulnerabilities["severity_summary"][severity] += 1
            
            # Save vulnerability report
            self._save_vulnerability_report(vulnerabilities)
            
            # Generate alerts if needed
            self._generate_vulnerability_alerts(vulnerabilities)
            
            logger.info(f"✅ Vulnerability scan complete: {len(vulnerabilities['vulnerabilities_found'])} issues found")
            return vulnerabilities
            
        except Exception as e:
            logger.error(f"❌ Vulnerability scan failed: {e}")
            return vulnerabilities
    
    def check_for_updates(self) -> Dict:
        """Check for available dependency updates"""
        logger.info("🔄 Checking for dependency updates...")
        
        updates = {
            "check_timestamp": datetime.now().isoformat(),
            "packages_checked": 0,
            "updates_available": [],
            "update_summary": {
                "patch": 0,
                "minor": 0,
                "major": 0
            }
        }
        
        try:
            dependencies = self._extract_dependencies()
            updates["packages_checked"] = len(dependencies)
            
            for dep_name, current_version in dependencies.items():
                latest_version = self._get_latest_version(dep_name)
                if latest_version and latest_version != current_version:
                    update_type = self._determine_update_type(current_version, latest_version)
                    
                    update_info = {
                        "package": dep_name,
                        "current_version": current_version,
                        "latest_version": latest_version,
                        "update_type": update_type,
                        "changelog_url": self._get_changelog_url(dep_name, latest_version),
                        "security_relevant": self._is_security_update(dep_name, current_version, latest_version)
                    }
                    
                    updates["updates_available"].append(update_info)
                    updates["update_summary"][update_type] += 1
            
            # Save update report
            self._save_update_report(updates)
            
            logger.info(f"✅ Update check complete: {len(updates['updates_available'])} updates available")
            return updates
            
        except Exception as e:
            logger.error(f"❌ Update check failed: {e}")
            return updates
    
    def auto_update_dependencies(self, update_types: List[str] = ["patch"]) -> bool:
        """Automatically update dependencies based on configuration"""
        logger.info("🚀 Starting automatic dependency updates...")
        
        try:
            # Load configuration
            with open(self.dependency_config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            auto_update_config = config["dependency_management"]["auto_update"]
            
            if not auto_update_config["enabled"]:
                logger.info("⏸️ Auto-update is disabled in configuration")
                return False
            
            # Check for updates
            updates = self.check_for_updates()
            
            # Filter updates based on strategy
            eligible_updates = []
            for update in updates["updates_available"]:
                if (update["update_type"] in update_types and 
                    update["package"] not in auto_update_config["exclude_packages"]):
                    eligible_updates.append(update)
            
            if not eligible_updates:
                logger.info("✅ No eligible updates found")
                return True
            
            # Create backup of current conanfile.py
            backup_path = self.conanfile_path.with_suffix('.py.backup')
            self.conanfile_path.rename(backup_path)
            
            success_count = 0
            for update in eligible_updates:
                try:
                    if self._apply_dependency_update(update):
                        success_count += 1
                        self._log_update(update)
                        
                        # Test after update if configured
                        if auto_update_config["test_after_update"]:
                            if not self._test_after_update(update):
                                logger.warning(f"⚠️ Tests failed after updating {update['package']}")
                                if auto_update_config["rollback_on_failure"]:
                                    self._rollback_update(update)
                                    continue
                        
                except Exception as e:
                    logger.error(f"❌ Failed to update {update['package']}: {e}")
                    if auto_update_config["rollback_on_failure"]:
                        self._rollback_update(update)
            
            logger.info(f"✅ Auto-update complete: {success_count}/{len(eligible_updates)} packages updated")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Auto-update failed: {e}")
            return False
    
    def validate_licenses(self) -> Dict:
        """Validate dependency licenses for compliance"""
        logger.info("📋 Validating dependency licenses...")
        
        license_report = {
            "validation_timestamp": datetime.now().isoformat(),
            "packages_validated": 0,
            "license_summary": {
                "approved": [],
                "requires_approval": [],
                "blocked": [],
                "unknown": []
            },
            "compliance_status": "compliant"
        }
        
        try:
            # Load configuration
            with open(self.dependency_config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            license_config = config["dependency_management"]["license_compliance"]
            allowed_licenses = license_config["allowed_licenses"]
            blocked_licenses = license_config["blocked_licenses"]
            require_approval = license_config["require_approval"]
            
            dependencies = self._extract_dependencies()
            license_report["packages_validated"] = len(dependencies)
            
            for dep_name, dep_version in dependencies.items():
                license_info = self._get_package_license(dep_name, dep_version)
                
                if license_info["license"] in allowed_licenses:
                    license_report["license_summary"]["approved"].append({
                        "package": dep_name,
                        "version": dep_version,
                        "license": license_info["license"]
                    })
                elif license_info["license"] in blocked_licenses:
                    license_report["license_summary"]["blocked"].append({
                        "package": dep_name,
                        "version": dep_version,
                        "license": license_info["license"]
                    })
                    license_report["compliance_status"] = "non_compliant"
                elif license_info["license"] in require_approval:
                    license_report["license_summary"]["requires_approval"].append({
                        "package": dep_name,
                        "version": dep_version,
                        "license": license_info["license"]
                    })
                else:
                    license_report["license_summary"]["unknown"].append({
                        "package": dep_name,
                        "version": dep_version,
                        "license": license_info["license"]
                    })
            
            # Save license report
            self._save_license_report(license_report)
            
            logger.info(f"✅ License validation complete: {license_report['compliance_status']}")
            return license_report
            
        except Exception as e:
            logger.error(f"❌ License validation failed: {e}")
            return license_report
    
    def _extract_dependencies(self) -> Dict[str, str]:
        """Extract dependencies from conanfile.py"""
        dependencies = {}
        
        try:
            with open(self.conanfile_path, 'r') as f:
                content = f.read()
            
            # Extract build_requires
            build_requires_match = re.search(r'build_requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
            if build_requires_match:
                requires_text = build_requires_match.group(1)
                for line in requires_text.split('\n'):
                    line = line.strip().strip(',').strip("'\"")
                    if line and not line.startswith('#'):
                        if '/' in line:
                            name, version = line.split('/', 1)
                            dependencies[name.strip()] = version.strip()
            
            # Extract requires
            requires_match = re.search(r'requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
            if requires_match:
                requires_text = requires_match.group(1)
                for line in requires_text.split('\n'):
                    line = line.strip().strip(',').strip("'\"")
                    if line and not line.startswith('#'):
                        if '/' in line:
                            name, version = line.split('/', 1)
                            dependencies[name.strip()] = version.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract dependencies: {e}")
        
        return dependencies
    
    def _check_package_vulnerabilities(self, package_name: str, version: str) -> List[Dict]:
        """Check package against vulnerability databases"""
        vulnerabilities = []
        
        try:
            # Check against OSV (Open Source Vulnerabilities)
            osv_url = f"https://api.osv.dev/v1/query"
            payload = {
                "package": {
                    "name": package_name,
                    "ecosystem": "conan"
                },
                "version": version
            }
            
            response = requests.post(osv_url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for vuln in data.get("vulns", []):
                    vulnerabilities.append({
                        "id": vuln.get("id"),
                        "summary": vuln.get("summary"),
                        "severity": self._extract_severity(vuln),
                        "references": vuln.get("references", []),
                        "database": "OSV"
                    })
            
        except Exception as e:
            logger.debug(f"Failed to check vulnerabilities for {package_name}: {e}")
        
        return vulnerabilities
    
    def _get_latest_version(self, package_name: str) -> Optional[str]:
        """Get latest version of a package"""
        try:
            # Use Conan search to find latest version
            result = subprocess.run(
                ["conan", "search", package_name, "--remote", "conancenter"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if package_name in line and '/' in line:
                        version = line.split('/')[1].strip()
                        if version and version != "latest":
                            return version
            
        except Exception as e:
            logger.debug(f"Failed to get latest version for {package_name}: {e}")
        
        return None
    
    def _determine_update_type(self, current: str, latest: str) -> str:
        """Determine if update is patch, minor, or major"""
        try:
            current_parts = [int(x) for x in current.split('.')]
            latest_parts = [int(x) for x in latest.split('.')]
            
            if len(current_parts) >= 3 and len(latest_parts) >= 3:
                if latest_parts[0] > current_parts[0]:
                    return "major"
                elif latest_parts[1] > current_parts[1]:
                    return "minor"
                elif latest_parts[2] > current_parts[2]:
                    return "patch"
            
        except (ValueError, IndexError):
            pass
        
        return "patch"  # Default to patch for safety
    
    def _apply_dependency_update(self, update: Dict) -> bool:
        """Apply a dependency update to conanfile.py"""
        try:
            with open(self.conanfile_path, 'r') as f:
                content = f.read()
            
            # Replace the version in the file
            old_pattern = f"'{update['package']}/{update['current_version']}'"
            new_pattern = f"'{update['package']}/{update['latest_version']}'"
            
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                
                with open(self.conanfile_path, 'w') as f:
                    f.write(content)
                
                return True
            
        except Exception as e:
            logger.error(f"Failed to apply update for {update['package']}: {e}")
        
        return False
    
    def _test_after_update(self, update: Dict) -> bool:
        """Test the project after applying an update"""
        try:
            # Run basic Conan commands to test
            test_commands = [
                ["conan", "install", ".", "--build=missing"],
                ["conan", "build", ".", "--build=missing"]
            ]
            
            for cmd in test_commands:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    logger.error(f"Test command failed: {' '.join(cmd)}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Testing failed after update: {e}")
            return False
    
    def _rollback_update(self, update: Dict):
        """Rollback a failed update"""
        try:
            with open(self.conanfile_path, 'r') as f:
                content = f.read()
            
            # Restore the old version
            new_pattern = f"'{update['package']}/{update['latest_version']}'"
            old_pattern = f"'{update['package']}/{update['current_version']}'"
            
            if new_pattern in content:
                content = content.replace(new_pattern, old_pattern)
                
                with open(self.conanfile_path, 'w') as f:
                    f.write(content)
                
                logger.info(f"✅ Rolled back {update['package']} to {update['current_version']}")
            
        except Exception as e:
            logger.error(f"Failed to rollback {update['package']}: {e}")
    
    def _log_update(self, update: Dict):
        """Log successful update"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "package": update["package"],
            "from_version": update["current_version"],
            "to_version": update["latest_version"],
            "update_type": update["update_type"],
            "security_relevant": update.get("security_relevant", False)
        }
        
        with open(self.update_log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def _save_vulnerability_report(self, vulnerabilities: Dict):
        """Save vulnerability report"""
        report_path = self.project_root / "conan-dev" / f"vulnerability-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(vulnerabilities, f, indent=2)
    
    def _save_update_report(self, updates: Dict):
        """Save update report"""
        report_path = self.project_root / "conan-dev" / f"update-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(updates, f, indent=2)
    
    def _save_license_report(self, license_report: Dict):
        """Save license report"""
        report_path = self.project_root / "conan-dev" / f"license-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(license_report, f, indent=2)
    
    def _extract_severity(self, vuln: Dict) -> str:
        """Extract severity from vulnerability data"""
        severity = "unknown"
        
        if "severity" in vuln:
            for sev in vuln["severity"]:
                if sev.get("type") == "CVSS_V3":
                    score = sev.get("score", 0)
                    if score >= 9.0:
                        severity = "critical"
                    elif score >= 7.0:
                        severity = "high"
                    elif score >= 4.0:
                        severity = "medium"
                    else:
                        severity = "low"
                    break
        
        return severity
    
    def _get_changelog_url(self, package_name: str, version: str) -> str:
        """Get changelog URL for a package version"""
        # This would typically query package metadata
        return f"https://github.com/{package_name}/releases/tag/v{version}"
    
    def _is_security_update(self, package_name: str, current_version: str, latest_version: str) -> bool:
        """Check if update contains security fixes"""
        # This would check against security advisories
        return False  # Simplified for now
    
    def _get_package_license(self, package_name: str, version: str) -> Dict:
        """Get license information for a package"""
        # This would query package metadata
        return {
            "package": package_name,
            "version": version,
            "license": "Unknown"  # Would be populated from actual metadata
        }
    
    def _generate_vulnerability_alerts(self, vulnerabilities: Dict):
        """Generate alerts for high-severity vulnerabilities"""
        high_severity_count = vulnerabilities["severity_summary"]["high"] + vulnerabilities["severity_summary"]["critical"]
        
        if high_severity_count > 0:
            logger.warning(f"🚨 {high_severity_count} high/critical vulnerabilities found!")
            # In a real implementation, this would send notifications

def main():
    """Main entry point for dependency management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Dependency Management")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--action", choices=["setup", "scan", "check-updates", "auto-update", "validate-licenses"],
                       required=True, help="Action to perform")
    parser.add_argument("--update-types", nargs="+", default=["patch"],
                       choices=["patch", "minor", "major"],
                       help="Types of updates to apply (for auto-update)")
    
    args = parser.parse_args()
    
    dm = DependencyManager(args.project_root)
    
    if args.action == "setup":
        dm.setup_dependency_config()
    elif args.action == "scan":
        dm.scan_vulnerabilities()
    elif args.action == "check-updates":
        dm.check_for_updates()
    elif args.action == "auto-update":
        dm.auto_update_dependencies(args.update_types)
    elif args.action == "validate-licenses":
        dm.validate_licenses()

if __name__ == "__main__":
    main()
