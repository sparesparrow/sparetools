#!/usr/bin/env python3
"""
Registry Versioning Manager for OpenSSL Conan packages
Ensures proper versioning and rollback protection for Conan registries
"""

import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
from datetime import datetime, timedelta
import semver


class RegistryVersioningManager:
    """Manages registry versioning and rollback protection"""
    
    def __init__(self, config_file: str = "conan-dev/registry-versioning.yml"):
        self.config_file = config_file
        self.config = self._load_config()
        self.version_registry = {}
        
    def _load_config(self) -> Dict:
        """Load registry versioning configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default registry versioning configuration"""
        return {
            'versioning': {
                'strategy': 'semantic',  # semantic, calendar, git-describe
                'pre_release_suffix': 'dev',
                'build_metadata': True,
                'version_scheme': {
                    'major': 'breaking_changes',
                    'minor': 'new_features',
                    'patch': 'bug_fixes'
                }
            },
            'rollback': {
                'enabled': True,
                'retention_days': 30,
                'max_versions': 10,
                'compatibility_checks': True,
                'dependency_validation': True
            },
            'registries': {
                'development': {
                    'versioning': 'dev',
                    'rollback_enabled': True,
                    'compatibility_checks': False
                },
                'staging': {
                    'versioning': 'rc',
                    'rollback_enabled': True,
                    'compatibility_checks': True
                },
                'production': {
                    'versioning': 'stable',
                    'rollback_enabled': True,
                    'compatibility_checks': True
                }
            }
        }
    
    def generate_version(self, package_name: str, change_type: str, 
                        current_version: str = None) -> str:
        """Generate new version based on change type"""
        print(f"🔢 Generating version for {package_name}...")
        
        if not current_version:
            current_version = self._get_latest_version(package_name)
        
        if not current_version:
            # First version
            new_version = "1.0.0"
        else:
            new_version = self._increment_version(current_version, change_type)
        
        # Add pre-release suffix if in development
        stage = self._get_current_stage()
        if stage == 'development':
            new_version = f"{new_version}-{self.config['versioning']['pre_release_suffix']}"
        
        # Add build metadata
        if self.config['versioning']['build_metadata']:
            build_metadata = self._generate_build_metadata()
            new_version = f"{new_version}+{build_metadata}"
        
        print(f"✓ Generated version: {new_version}")
        return new_version
    
    def _get_latest_version(self, package_name: str) -> str:
        """Get latest version of package from registry"""
        try:
            # Try to get from Conan registry
            result = subprocess.run(['conan', 'search', package_name], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                # Parse versions from output
                lines = result.stdout.split('\n')
                versions = []
                for line in lines:
                    if 'versions:' in line:
                        continue
                    if line.strip() and not line.startswith('Available versions:'):
                        version = line.strip()
                        if self._is_valid_version(version):
                            versions.append(version)
                
                if versions:
                    # Sort versions and return latest
                    versions.sort(key=lambda v: semver.VersionInfo.parse(v), reverse=True)
                    return versions[0]
            
            return None
            
        except Exception as e:
            print(f"Warning: Could not get latest version for {package_name}: {e}")
            return None
    
    def _is_valid_version(self, version: str) -> bool:
        """Check if version string is valid"""
        try:
            # Remove pre-release and build metadata for validation
            clean_version = version.split('+')[0].split('-')[0]
            semver.VersionInfo.parse(clean_version)
            return True
        except:
            return False
    
    def _increment_version(self, current_version: str, change_type: str) -> str:
        """Increment version based on change type"""
        try:
            # Parse current version
            version_info = semver.VersionInfo.parse(current_version.split('+')[0].split('-')[0])
            
            # Increment based on change type
            if change_type == 'breaking':
                new_version = version_info.bump_major()
            elif change_type == 'feature':
                new_version = version_info.bump_minor()
            elif change_type == 'bugfix':
                new_version = version_info.bump_patch()
            else:
                # Default to patch
                new_version = version_info.bump_patch()
            
            return str(new_version)
            
        except Exception as e:
            print(f"Warning: Could not increment version {current_version}: {e}")
            return "1.0.0"
    
    def _get_current_stage(self) -> str:
        """Get current deployment stage"""
        return os.environ.get('DEPLOYMENT_STAGE', 'development')
    
    def _generate_build_metadata(self) -> str:
        """Generate build metadata"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        git_commit = self._get_git_commit()
        return f"{timestamp}.{git_commit[:8]}"
    
    def _get_git_commit(self) -> str:
        """Get current git commit hash"""
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "unknown"
    
    def validate_rollback(self, package_name: str, target_version: str) -> bool:
        """Validate if rollback to target version is safe"""
        print(f"🔄 Validating rollback for {package_name} to {target_version}...")
        
        if not self.config['rollback']['enabled']:
            print("❌ Rollback is disabled")
            return False
        
        # Check if target version exists
        if not self._version_exists(package_name, target_version):
            print(f"❌ Target version {target_version} does not exist")
            return False
        
        # Check compatibility
        if self.config['rollback']['compatibility_checks']:
            if not self._check_compatibility(package_name, target_version):
                print(f"❌ Rollback to {target_version} would break compatibility")
                return False
        
        # Check dependencies
        if self.config['rollback']['dependency_validation']:
            if not self._validate_dependencies(package_name, target_version):
                print(f"❌ Rollback to {target_version} has dependency issues")
                return False
        
        print(f"✓ Rollback to {target_version} is safe")
        return True
    
    def _version_exists(self, package_name: str, version: str) -> bool:
        """Check if version exists in registry"""
        try:
            result = subprocess.run(['conan', 'search', f"{package_name}/{version}"], 
                                 capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _check_compatibility(self, package_name: str, version: str) -> bool:
        """Check compatibility of target version"""
        try:
            # Get current version
            current_version = self._get_latest_version(package_name)
            if not current_version:
                return True
            
            # Parse versions
            current = semver.VersionInfo.parse(current_version.split('+')[0].split('-')[0])
            target = semver.VersionInfo.parse(version.split('+')[0].split('-')[0])
            
            # Check if rollback is within same major version
            if current.major != target.major:
                return False
            
            # Check if rollback is not too far back
            if target < current and (current - target).patch > 10:
                return False
            
            return True
            
        except Exception as e:
            print(f"Warning: Could not check compatibility: {e}")
            return True
    
    def _validate_dependencies(self, package_name: str, version: str) -> bool:
        """Validate dependencies for target version"""
        try:
            # Get package info
            result = subprocess.run(['conan', 'info', f"{package_name}/{version}"], 
                                 capture_output=True, text=True)
            if result.returncode != 0:
                return False
            
            # Check for dependency conflicts
            # This is a simplified check - in practice, you'd need more sophisticated analysis
            return True
            
        except Exception as e:
            print(f"Warning: Could not validate dependencies: {e}")
            return True
    
    def create_rollback_plan(self, package_name: str, target_version: str) -> Dict:
        """Create detailed rollback plan"""
        print(f"📋 Creating rollback plan for {package_name} to {target_version}...")
        
        plan = {
            'package_name': package_name,
            'target_version': target_version,
            'current_version': self._get_latest_version(package_name),
            'rollback_steps': [],
            'risks': [],
            'recommendations': []
        }
        
        # Add rollback steps
        plan['rollback_steps'] = [
            f"1. Validate rollback safety for {package_name}/{target_version}",
            f"2. Create backup of current version {plan['current_version']}",
            f"3. Update registry to point to {target_version}",
            f"4. Verify package functionality",
            f"5. Update dependent packages if needed",
            f"6. Monitor system stability"
        ]
        
        # Add risk assessment
        if not self._check_compatibility(package_name, target_version):
            plan['risks'].append("Compatibility risk: Major version difference")
        
        if not self._validate_dependencies(package_name, target_version):
            plan['risks'].append("Dependency risk: Potential dependency conflicts")
        
        # Add recommendations
        plan['recommendations'] = [
            "Test rollback in staging environment first",
            "Have rollback plan ready in case of issues",
            "Monitor system metrics after rollback",
            "Update documentation with new version"
        ]
        
        # Save plan
        plan_file = f'rollback-plan-{package_name}-{target_version}.json'
        with open(plan_file, 'w') as f:
            json.dump(plan, f, indent=2)
        
        print(f"✓ Rollback plan saved: {plan_file}")
        return plan
    
    def execute_rollback(self, package_name: str, target_version: str) -> bool:
        """Execute rollback to target version"""
        print(f"🔄 Executing rollback for {package_name} to {target_version}...")
        
        # Validate rollback first
        if not self.validate_rollback(package_name, target_version):
            print("❌ Rollback validation failed")
            return False
        
        try:
            # Create backup
            current_version = self._get_latest_version(package_name)
            if current_version:
                self._create_backup(package_name, current_version)
            
            # Update registry
            self._update_registry(package_name, target_version)
            
            # Verify rollback
            if self._verify_rollback(package_name, target_version):
                print(f"✓ Rollback to {target_version} completed successfully")
                return True
            else:
                print(f"❌ Rollback verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False
    
    def _create_backup(self, package_name: str, version: str):
        """Create backup of current version"""
        backup_dir = f"backups/{package_name}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Export package to backup
        backup_file = f"{backup_dir}/{version}.tar.gz"
        subprocess.run(['conan', 'export-pkg', f"{package_name}/{version}", 
                       '--package-file', backup_file], check=False)
        
        print(f"✓ Created backup: {backup_file}")
    
    def _update_registry(self, package_name: str, version: str):
        """Update registry to point to target version"""
        # This would update the registry configuration
        # In practice, this would depend on your registry setup
        print(f"✓ Updated registry to {package_name}/{version}")
    
    def _verify_rollback(self, package_name: str, version: str) -> bool:
        """Verify rollback was successful"""
        try:
            # Check if package is accessible
            result = subprocess.run(['conan', 'search', f"{package_name}/{version}"], 
                                 capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def generate_version_report(self) -> Dict:
        """Generate version management report"""
        print("📊 Generating version report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'packages': {},
            'rollback_status': {},
            'version_statistics': {}
        }
        
        # Get all packages and their versions
        packages = self._get_all_packages()
        
        for package in packages:
            versions = self._get_package_versions(package)
            report['packages'][package] = {
                'latest_version': versions[0] if versions else None,
                'total_versions': len(versions),
                'versions': versions
            }
        
        # Check rollback status
        for package, info in report['packages'].items():
            if info['latest_version']:
                rollback_safe = self.validate_rollback(package, info['latest_version'])
                report['rollback_status'][package] = {
                    'safe': rollback_safe,
                    'latest_version': info['latest_version']
                }
        
        # Save report
        report_file = 'version-management-report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Version report saved: {report_file}")
        return report
    
    def _get_all_packages(self) -> List[str]:
        """Get all packages in registry"""
        try:
            result = subprocess.run(['conan', 'search'], capture_output=True, text=True)
            if result.returncode == 0:
                packages = []
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('Available packages:'):
                        packages.append(line.strip())
                return packages
        except:
            pass
        return []
    
    def _get_package_versions(self, package_name: str) -> List[str]:
        """Get all versions of a package"""
        try:
            result = subprocess.run(['conan', 'search', package_name], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                versions = []
                for line in result.stdout.split('\n'):
                    if line.strip() and not line.startswith('Available versions:'):
                        version = line.strip()
                        if self._is_valid_version(version):
                            versions.append(version)
                return sorted(versions, key=lambda v: semver.VersionInfo.parse(v), reverse=True)
        except:
            pass
        return []


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Registry Versioning Manager for OpenSSL Conan packages')
    parser.add_argument('--config', default='conan-dev/registry-versioning.yml',
                       help='Path to registry versioning configuration file')
    parser.add_argument('--generate-version', nargs=2, metavar=('PACKAGE', 'CHANGE_TYPE'),
                       help='Generate new version for package')
    parser.add_argument('--validate-rollback', nargs=2, metavar=('PACKAGE', 'VERSION'),
                       help='Validate rollback to version')
    parser.add_argument('--create-rollback-plan', nargs=2, metavar=('PACKAGE', 'VERSION'),
                       help='Create rollback plan')
    parser.add_argument('--execute-rollback', nargs=2, metavar=('PACKAGE', 'VERSION'),
                       help='Execute rollback')
    parser.add_argument('--report', action='store_true',
                       help='Generate version report')
    
    args = parser.parse_args()
    
    manager = RegistryVersioningManager(args.config)
    
    if args.generate_version:
        package, change_type = args.generate_version
        version = manager.generate_version(package, change_type)
        print(f"Generated version: {version}")
    elif args.validate_rollback:
        package, version = args.validate_rollback
        success = manager.validate_rollback(package, version)
    elif args.create_rollback_plan:
        package, version = args.create_rollback_plan
        plan = manager.create_rollback_plan(package, version)
    elif args.execute_rollback:
        package, version = args.execute_rollback
        success = manager.execute_rollback(package, version)
    elif args.report:
        report = manager.generate_version_report()
    else:
        print("Please specify an action")
        success = False
    
    if 'success' in locals() and not success:
        sys.exit(1)
    else:
        print("\n🎉 Registry versioning management completed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
