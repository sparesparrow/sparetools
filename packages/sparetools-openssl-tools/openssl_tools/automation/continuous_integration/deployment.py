#!/usr/bin/env python3
"""
OpenSSL Deployment Automation Script
Based on ngapy-dev patterns for robust deployment automation
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml
import requests


class DeploymentManager:
    """Deployment manager for OpenSSL packages"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("scripts/ci/ci_config.yaml")
        self.config = self._load_config()
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Deployment state
        self.deployment_state = {
            "start_time": datetime.now().isoformat(),
            "environment": None,
            "packages": [],
            "status": "pending"
        }
        
    def _load_config(self) -> Dict:
        """Load deployment configuration"""
        if not self.config_path.exists():
            self.logger.warning(f"Config file {self.config_path} not found, using defaults")
            return self._get_default_config()
            
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        return config
        
    def _get_default_config(self) -> Dict:
        """Get default deployment configuration"""
        return {
            "deployment": {
                "environments": {
                    "staging": {
                        "conan_remote": "staging-remote",
                        "registry_url": "https://staging.conan.io",
                        "auto_approve": True
                    },
                    "production": {
                        "conan_remote": "production-remote", 
                        "registry_url": "https://production.conan.io",
                        "auto_approve": False
                    }
                }
            }
        }
        
    def validate_deployment_packages(self, packages_dir: Path) -> List[Path]:
        """Validate deployment packages"""
        self.logger.info(f"Validating packages in {packages_dir}")
        
        if not packages_dir.exists():
            raise ValueError(f"Packages directory not found: {packages_dir}")
            
        valid_packages = []
        
        # Look for Conan packages
        for package_path in packages_dir.rglob("*"):
            if package_path.is_dir() and (package_path / "conaninfo.txt").exists():
                # Validate package structure
                if self._validate_package_structure(package_path):
                    valid_packages.append(package_path)
                    self.logger.info(f"Valid package found: {package_path}")
                else:
                    self.logger.warning(f"Invalid package structure: {package_path}")
                    
        # Look for SBOM files
        sbom_files = list(packages_dir.rglob("sbom.json"))
        if sbom_files:
            self.logger.info(f"Found {len(sbom_files)} SBOM files")
            
        return valid_packages
        
    def _validate_package_structure(self, package_path: Path) -> bool:
        """Validate Conan package structure"""
        required_files = [
            "conaninfo.txt",
            "conanmanifest.txt"
        ]
        
        required_dirs = [
            "lib",
            "include"
        ]
        
        # Check required files
        for file_name in required_files:
            if not (package_path / file_name).exists():
                self.logger.warning(f"Missing required file: {file_name}")
                return False
                
        # Check required directories
        for dir_name in required_dirs:
            if not (package_path / dir_name).exists():
                self.logger.warning(f"Missing required directory: {dir_name}")
                return False
                
        return True
        
    def upload_packages(self, packages: List[Path], environment: str) -> bool:
        """Upload packages to registry"""
        self.logger.info(f"Uploading {len(packages)} packages to {environment}")
        
        env_config = self.config.get("deployment", {}).get("environments", {}).get(environment)
        if not env_config:
            raise ValueError(f"Environment configuration not found: {environment}")
            
        remote_name = env_config.get("conan_remote", f"{environment}-remote")
        registry_url = env_config.get("registry_url")
        
        # Set up Conan remote
        if not self._setup_conan_remote(remote_name, registry_url):
            return False
            
        # Upload packages
        success_count = 0
        for package_path in packages:
            if self._upload_single_package(package_path, remote_name):
                success_count += 1
                self.deployment_state["packages"].append({
                    "path": str(package_path),
                    "status": "uploaded",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                self.deployment_state["packages"].append({
                    "path": str(package_path),
                    "status": "failed",
                    "timestamp": datetime.now().isoformat()
                })
                
        self.logger.info(f"Successfully uploaded {success_count}/{len(packages)} packages")
        return success_count == len(packages)
        
    def _setup_conan_remote(self, remote_name: str, registry_url: str) -> bool:
        """Set up Conan remote"""
        try:
            # Remove existing remote if it exists
            subprocess.run(["conan", "remote", "remove", remote_name], 
                         capture_output=True, check=False)
            
            # Add new remote
            result = subprocess.run([
                "conan", "remote", "add", remote_name, registry_url
            ], capture_output=True, text=True, check=True)
            
            self.logger.info(f"Conan remote '{remote_name}' set up successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to set up Conan remote: {e.stderr}")
            return False
            
    def _upload_single_package(self, package_path: Path, remote_name: str) -> bool:
        """Upload a single package"""
        try:
            # Extract package reference from conaninfo.txt
            package_ref = self._extract_package_reference(package_path)
            if not package_ref:
                self.logger.error(f"Could not extract package reference from {package_path}")
                return False
                
            # Upload package
            result = subprocess.run([
                "conan", "upload", package_ref,
                "--remote", remote_name,
                "--confirm"
            ], capture_output=True, text=True, check=True)
            
            self.logger.info(f"Successfully uploaded {package_ref}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to upload package {package_path}: {e.stderr}")
            return False
            
    def _extract_package_reference(self, package_path: Path) -> Optional[str]:
        """Extract package reference from conaninfo.txt"""
        conaninfo_path = package_path / "conaninfo.txt"
        if not conaninfo_path.exists():
            return None
            
        try:
            with open(conaninfo_path, 'r') as f:
                content = f.read()
                
            # Parse conaninfo.txt to extract package reference
            # This is a simplified parser - in practice you'd use Conan's API
            for line in content.split('\n'):
                if line.startswith('name='):
                    name = line.split('=')[1].strip()
                elif line.startswith('version='):
                    version = line.split('=')[1].strip()
                elif line.startswith('user='):
                    user = line.split('=')[1].strip()
                elif line.startswith('channel='):
                    channel = line.split('=')[1].strip()
                    
            return f"{name}/{version}@{user}/{channel}"
            
        except Exception as e:
            self.logger.error(f"Failed to parse conaninfo.txt: {e}")
            return None
            
    def run_health_checks(self, environment: str) -> bool:
        """Run health checks after deployment"""
        self.logger.info(f"Running health checks for {environment}")
        
        env_config = self.config.get("deployment", {}).get("environments", {}).get(environment)
        if not env_config:
            self.logger.error(f"Environment configuration not found: {environment}")
            return False
            
        health_checks = env_config.get("health_checks", [])
        if not health_checks:
            self.logger.info("No health checks configured")
            return True
            
        all_passed = True
        for check in health_checks:
            if not self._run_single_health_check(check):
                all_passed = False
                
        return all_passed
        
    def _run_single_health_check(self, check_config: Dict) -> bool:
        """Run a single health check"""
        check_type = check_config.get("type")
        check_name = check_config.get("name", "unnamed")
        
        self.logger.info(f"Running health check: {check_name}")
        
        try:
            if check_type == "http":
                return self._run_http_health_check(check_config)
            elif check_type == "conan":
                return self._run_conan_health_check(check_config)
            elif check_type == "command":
                return self._run_command_health_check(check_config)
            else:
                self.logger.warning(f"Unknown health check type: {check_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Health check '{check_name}' failed: {e}")
            return False
            
    def _run_http_health_check(self, check_config: Dict) -> bool:
        """Run HTTP health check"""
        url = check_config.get("url")
        expected_status = check_config.get("expected_status", 200)
        timeout = check_config.get("timeout", 30)
        
        try:
            response = requests.get(url, timeout=timeout)
            success = response.status_code == expected_status
            
            if success:
                self.logger.info(f"HTTP health check passed: {url}")
            else:
                self.logger.error(f"HTTP health check failed: {url} (status: {response.status_code})")
                
            return success
            
        except Exception as e:
            self.logger.error(f"HTTP health check failed: {url} - {e}")
            return False
            
    def _run_conan_health_check(self, check_config: Dict) -> bool:
        """Run Conan health check"""
        package_ref = check_config.get("package_reference")
        remote = check_config.get("remote", "conancenter")
        
        try:
            result = subprocess.run([
                "conan", "search", package_ref,
                "--remote", remote
            ], capture_output=True, text=True, check=True)
            
            success = package_ref in result.stdout
            
            if success:
                self.logger.info(f"Conan health check passed: {package_ref}")
            else:
                self.logger.error(f"Conan health check failed: {package_ref} not found")
                
            return success
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Conan health check failed: {package_ref} - {e.stderr}")
            return False
            
    def _run_command_health_check(self, check_config: Dict) -> bool:
        """Run command health check"""
        command = check_config.get("command")
        expected_output = check_config.get("expected_output")
        timeout = check_config.get("timeout", 30)
        
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            if expected_output:
                success = success and expected_output in result.stdout
                
            if success:
                self.logger.info(f"Command health check passed: {command}")
            else:
                self.logger.error(f"Command health check failed: {command}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Command health check failed: {command} - {e}")
            return False
            
    def send_notifications(self, environment: str, success: bool):
        """Send deployment notifications"""
        self.logger.info(f"Sending notifications for {environment} deployment")
        
        notification_config = self.config.get("deployment", {}).get("notifications", {})
        if not notification_config:
            self.logger.info("No notification configuration found")
            return
            
        # Prepare notification message
        status = "SUCCESS" if success else "FAILED"
        message = {
            "environment": environment,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "packages": len(self.deployment_state["packages"]),
            "duration": self._calculate_duration()
        }
        
        # Send to configured channels
        for channel, config in notification_config.items():
            try:
                if channel == "slack":
                    self._send_slack_notification(config, message)
                elif channel == "email":
                    self._send_email_notification(config, message)
                elif channel == "webhook":
                    self._send_webhook_notification(config, message)
                else:
                    self.logger.warning(f"Unknown notification channel: {channel}")
                    
            except Exception as e:
                self.logger.error(f"Failed to send {channel} notification: {e}")
                
    def _send_slack_notification(self, config: Dict, message: Dict):
        """Send Slack notification"""
        webhook_url = config.get("webhook_url")
        if not webhook_url:
            return
            
        slack_message = {
            "text": f"OpenSSL Deployment {message['status']}",
            "attachments": [{
                "color": "good" if message["status"] == "SUCCESS" else "danger",
                "fields": [
                    {"title": "Environment", "value": message["environment"], "short": True},
                    {"title": "Status", "value": message["status"], "short": True},
                    {"title": "Packages", "value": str(message["packages"]), "short": True},
                    {"title": "Duration", "value": message["duration"], "short": True}
                ]
            }]
        }
        
        response = requests.post(webhook_url, json=slack_message)
        response.raise_for_status()
        
    def _send_email_notification(self, config: Dict, message: Dict):
        """Send email notification"""
        # This would integrate with your email service
        self.logger.info(f"Email notification: {message}")
        
    def _send_webhook_notification(self, config: Dict, message: Dict):
        """Send webhook notification"""
        webhook_url = config.get("url")
        if not webhook_url:
            return
            
        response = requests.post(webhook_url, json=message)
        response.raise_for_status()
        
    def _calculate_duration(self) -> str:
        """Calculate deployment duration"""
        start_time = datetime.fromisoformat(self.deployment_state["start_time"])
        duration = datetime.now() - start_time
        return str(duration)
        
    def save_deployment_log(self, log_path: Path):
        """Save deployment log"""
        self.deployment_state["end_time"] = datetime.now().isoformat()
        
        with open(log_path, 'w') as f:
            json.dump(self.deployment_state, f, indent=2)
            
        self.logger.info(f"Deployment log saved to {log_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='OpenSSL Deployment Automation')
    parser.add_argument('--config', type=Path, help='Configuration file path')
    parser.add_argument('--environment', required=True, 
                       choices=['staging', 'production'],
                       help='Deployment environment')
    parser.add_argument('--packages-dir', type=Path, required=True,
                       help='Directory containing packages to deploy')
    parser.add_argument('--dry-run', action='store_true',
                       help='Perform dry run without actual deployment')
    parser.add_argument('--skip-health-checks', action='store_true',
                       help='Skip health checks after deployment')
    
    args = parser.parse_args()
    
    # Initialize deployment manager
    deployer = DeploymentManager(args.config)
    deployer.deployment_state["environment"] = args.environment
    
    try:
        # Validate packages
        deployer.logger.info("Validating deployment packages")
        packages = deployer.validate_deployment_packages(args.packages_dir)
        
        if not packages:
            deployer.logger.error("No valid packages found for deployment")
            return 1
            
        deployer.logger.info(f"Found {len(packages)} valid packages")
        
        if args.dry_run:
            deployer.logger.info("Dry run mode - no actual deployment")
            return 0
            
        # Upload packages
        deployer.logger.info(f"Starting deployment to {args.environment}")
        upload_success = deployer.upload_packages(packages, args.environment)
        
        if not upload_success:
            deployer.logger.error("Package upload failed")
            deployer.deployment_state["status"] = "failed"
            deployer.send_notifications(args.environment, False)
            return 1
            
        # Run health checks
        if not args.skip_health_checks:
            health_check_success = deployer.run_health_checks(args.environment)
            if not health_check_success:
                deployer.logger.error("Health checks failed")
                deployer.deployment_state["status"] = "failed"
                deployer.send_notifications(args.environment, False)
                return 1
                
        # Deployment successful
        deployer.deployment_state["status"] = "success"
        deployer.logger.info(f"Deployment to {args.environment} completed successfully")
        
        # Send notifications
        deployer.send_notifications(args.environment, True)
        
        # Save deployment log
        log_path = Path(f"deployment_log_{args.environment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        deployer.save_deployment_log(log_path)
        
        return 0
        
    except Exception as e:
        deployer.logger.error(f"Deployment failed: {e}")
        deployer.deployment_state["status"] = "failed"
        deployer.send_notifications(args.environment, False)
        return 1


if __name__ == '__main__':
    sys.exit(main())
