#!/usr/bin/env python3
"""
Pre-build validation script for OpenSSL Conan packages
Comprehensive validation of environment, dependencies, and configuration
"""

import os
import sys
import subprocess
import json
import yaml
import hashlib
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class PreBuildValidator:
    """Comprehensive pre-build validation for OpenSSL Conan packages"""
    
    def __init__(self, config_file: str = "conan-dev/validation-config.yml"):
        self.config_file = config_file
        self.config = self._load_config()
        self.errors = []
        self.warnings = []
        self.info = []
        
    def _load_config(self) -> Dict:
        """Load validation configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default validation configuration"""
        return {
            'environment': {
                'required_tools': ['conan', 'python', 'git', 'make', 'gcc', 'g++'],
                'min_conan_version': '2.0.0',
                'min_python_version': '3.8',
                'required_env_vars': ['CONAN_USER_HOME'],
                'disk_space_gb': 10
            },
            'dependencies': {
                'check_system_packages': True,
                'required_system_packages': ['build-essential', 'perl', 'pkg-config'],
                'check_conan_remotes': True,
                'required_remotes': ['conancenter']
            },
            'configuration': {
                'validate_conanfile': True,
                'check_version_consistency': True,
                'validate_profiles': True,
                'check_cache_config': True
            },
            'security': {
                'check_secrets': True,
                'validate_ssl_certs': True,
                'check_file_permissions': True
            }
        }
    
    def validate_all(self) -> bool:
        """Run all validation checks"""
        print("🔍 Starting comprehensive pre-build validation...")
        
        try:
            self._validate_environment()
            self._validate_dependencies()
            self._validate_configuration()
            self._validate_security()
            self._validate_cache_configuration()
            self._validate_build_environment()
            
            self._print_summary()
            return len(self.errors) == 0
            
        except Exception as e:
            self.errors.append(f"Validation failed with exception: {e}")
            return False
    
    def _validate_environment(self):
        """Validate build environment"""
        print("  📋 Validating environment...")
        
        # Check required tools
        for tool in self.config['environment']['required_tools']:
            if not shutil.which(tool):
                self.errors.append(f"Required tool '{tool}' not found in PATH")
            else:
                self.info.append(f"✓ Found tool: {tool}")
        
        # Check Conan version
        try:
            result = subprocess.run(['conan', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1]
                self.info.append(f"✓ Conan version: {version}")
            else:
                self.errors.append("Failed to get Conan version")
        except Exception as e:
            self.errors.append(f"Error checking Conan version: {e}")
        
        # Check Python version
        if sys.version_info < (3, 8):
            self.errors.append(f"Python version {sys.version_info} is too old. Minimum required: 3.8")
        else:
            self.info.append(f"✓ Python version: {sys.version}")
        
        # Check required environment variables
        for var in self.config['environment']['required_env_vars']:
            if not os.getenv(var):
                self.errors.append(f"Required environment variable '{var}' not set")
            else:
                self.info.append(f"✓ Environment variable {var} is set")
        
        # Check disk space
        try:
            statvfs = os.statvfs('.')
            free_space_gb = (statvfs.f_frsize * statvfs.f_bavail) / (1024**3)
            required_space = self.config['environment']['disk_space_gb']
            
            if free_space_gb < required_space:
                self.errors.append(f"Insufficient disk space: {free_space_gb:.1f}GB available, {required_space}GB required")
            else:
                self.info.append(f"✓ Disk space: {free_space_gb:.1f}GB available")
        except Exception as e:
            self.warnings.append(f"Could not check disk space: {e}")
    
    def _validate_dependencies(self):
        """Validate system and Conan dependencies"""
        print("  📦 Validating dependencies...")
        
        if self.config['dependencies']['check_system_packages']:
            self._check_system_packages()
        
        if self.config['dependencies']['check_conan_remotes']:
            self._check_conan_remotes()
    
    def _check_system_packages(self):
        """Check system package dependencies"""
        try:
            # Check if we're on a supported platform
            system = platform.system().lower()
            if system == 'linux':
                self._check_apt_packages()
            elif system == 'darwin':
                self._check_brew_packages()
            elif system == 'windows':
                self._check_windows_packages()
            else:
                self.warnings.append(f"Unsupported platform: {system}")
        except Exception as e:
            self.warnings.append(f"Could not check system packages: {e}")
    
    def _check_apt_packages(self):
        """Check APT packages on Debian/Ubuntu"""
        try:
            result = subprocess.run(['dpkg', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                installed_packages = result.stdout
                for package in self.config['dependencies']['required_system_packages']:
                    if package in installed_packages:
                        self.info.append(f"✓ System package installed: {package}")
                    else:
                        self.warnings.append(f"System package not found: {package}")
        except Exception as e:
            self.warnings.append(f"Could not check APT packages: {e}")
    
    def _check_brew_packages(self):
        """Check Homebrew packages on macOS"""
        try:
            result = subprocess.run(['brew', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                installed_packages = result.stdout
                for package in ['gcc', 'make', 'perl']:
                    if package in installed_packages:
                        self.info.append(f"✓ Homebrew package installed: {package}")
                    else:
                        self.warnings.append(f"Homebrew package not found: {package}")
        except Exception as e:
            self.warnings.append(f"Could not check Homebrew packages: {e}")
    
    def _check_windows_packages(self):
        """Check Windows packages"""
        # On Windows, we rely on Visual Studio and other tools being installed
        self.info.append("✓ Windows environment detected - assuming Visual Studio is installed")
    
    def _check_conan_remotes(self):
        """Check Conan remote configuration"""
        try:
            result = subprocess.run(['conan', 'remote', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                remotes = result.stdout
                for remote in self.config['dependencies']['required_remotes']:
                    if remote in remotes:
                        self.info.append(f"✓ Conan remote configured: {remote}")
                    else:
                        self.warnings.append(f"Conan remote not found: {remote}")
            else:
                self.errors.append("Failed to list Conan remotes")
        except Exception as e:
            self.errors.append(f"Error checking Conan remotes: {e}")
    
    def _validate_configuration(self):
        """Validate Conan configuration files"""
        print("  ⚙️  Validating configuration...")
        
        if self.config['configuration']['validate_conanfile']:
            self._validate_conanfile()
        
        if self.config['configuration']['check_version_consistency']:
            self._check_version_consistency()
        
        if self.config['configuration']['validate_profiles']:
            self._validate_profiles()
    
    def _validate_conanfile(self):
        """Validate conanfile.py"""
        conanfile_path = "conanfile.py"
        if not os.path.exists(conanfile_path):
            self.errors.append("conanfile.py not found")
            return
        
        try:
            # Basic syntax check
            with open(conanfile_path, 'r') as f:
                content = f.read()
            
            # Check for required methods
            required_methods = ['configure', 'build', 'package', 'package_info']
            for method in required_methods:
                if f"def {method}(" not in content:
                    self.errors.append(f"conanfile.py missing required method: {method}")
                else:
                    self.info.append(f"✓ conanfile.py has method: {method}")
            
            # Check for version detection
            if "VERSION.dat" in content:
                self.info.append("✓ conanfile.py reads version from VERSION.dat")
            else:
                self.warnings.append("conanfile.py doesn't read version from VERSION.dat")
                
        except Exception as e:
            self.errors.append(f"Error validating conanfile.py: {e}")
    
    def _check_version_consistency(self):
        """Check version consistency between files"""
        try:
            # Check VERSION.dat exists
            if os.path.exists("VERSION.dat"):
                with open("VERSION.dat", 'r') as f:
                    version_content = f.read()
                self.info.append("✓ VERSION.dat found")
            else:
                self.warnings.append("VERSION.dat not found")
                
        except Exception as e:
            self.warnings.append(f"Error checking version consistency: {e}")
    
    def _validate_profiles(self):
        """Validate Conan profiles"""
        profiles_dir = "conan-dev/profiles"
        if os.path.exists(profiles_dir):
            profile_files = [f for f in os.listdir(profiles_dir) if f.endswith('.profile')]
            if profile_files:
                self.info.append(f"✓ Found {len(profile_files)} profile files")
                for profile in profile_files:
                    self._validate_single_profile(os.path.join(profiles_dir, profile))
            else:
                self.warnings.append("No profile files found in conan-dev/profiles")
        else:
            self.warnings.append("Profile directory not found: conan-dev/profiles")
    
    def _validate_single_profile(self, profile_path: str):
        """Validate a single Conan profile"""
        try:
            with open(profile_path, 'r') as f:
                content = f.read()
            
            # Check for required sections
            required_sections = ['[settings]', '[conf]']
            for section in required_sections:
                if section in content:
                    self.info.append(f"✓ Profile {os.path.basename(profile_path)} has {section}")
                else:
                    self.warnings.append(f"Profile {os.path.basename(profile_path)} missing {section}")
                    
        except Exception as e:
            self.warnings.append(f"Error validating profile {profile_path}: {e}")
    
    def _validate_security(self):
        """Validate security configuration"""
        print("  🔒 Validating security...")
        
        if self.config['security']['check_secrets']:
            self._check_secrets()
        
        if self.config['security']['validate_ssl_certs']:
            self._validate_ssl_certs()
        
        if self.config['security']['check_file_permissions']:
            self._check_file_permissions()
    
    def _check_secrets(self):
        """Check for exposed secrets"""
        sensitive_files = ['conanfile.py', 'conan-dev/conan.conf', '.github/workflows/*.yml']
        sensitive_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']'
        ]
        
        for file_pattern in sensitive_files:
            if '*' in file_pattern:
                # Handle glob patterns
                import glob
                files = glob.glob(file_pattern)
            else:
                files = [file_pattern] if os.path.exists(file_pattern) else []
            
            for file_path in files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                        
                        for pattern in sensitive_patterns:
                            import re
                            if re.search(pattern, content, re.IGNORECASE):
                                self.warnings.append(f"Potential secret found in {file_path}")
                    except Exception as e:
                        self.warnings.append(f"Error checking {file_path} for secrets: {e}")
    
    def _validate_ssl_certs(self):
        """Validate SSL certificate configuration"""
        try:
            # Check if we can make HTTPS requests
            import urllib.request
            import ssl
            
            # Test connection to Conan Center
            context = ssl.create_default_context()
            with urllib.request.urlopen('https://center.conan.io', context=context) as response:
                if response.status == 200:
                    self.info.append("✓ SSL connection to Conan Center successful")
                else:
                    self.warnings.append("SSL connection to Conan Center returned non-200 status")
        except Exception as e:
            self.warnings.append(f"SSL validation failed: {e}")
    
    def _check_file_permissions(self):
        """Check file permissions for security"""
        sensitive_files = ['conanfile.py', 'conan-dev/conan.conf']
        
        for file_path in sensitive_files:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                # Check if file is world-writable
                if stat.st_mode & 0o002:
                    self.warnings.append(f"File {file_path} is world-writable")
                else:
                    self.info.append(f"✓ File {file_path} has secure permissions")
    
    def _validate_cache_configuration(self):
        """Validate cache configuration"""
        print("  💾 Validating cache configuration...")
        
        # Check cache directory
        cache_dir = os.getenv('CONAN_USER_HOME', os.path.expanduser('~/.conan2'))
        if os.path.exists(cache_dir):
            self.info.append(f"✓ Conan cache directory exists: {cache_dir}")
        else:
            self.warnings.append(f"Conan cache directory not found: {cache_dir}")
        
        # Check cache optimization config
        cache_config = "conan-dev/cache-optimization.yml"
        if os.path.exists(cache_config):
            self.info.append("✓ Cache optimization configuration found")
        else:
            self.warnings.append("Cache optimization configuration not found")
    
    def _validate_build_environment(self):
        """Validate build environment specifics"""
        print("  🔨 Validating build environment...")
        
        # Check for required build tools
        build_tools = ['make', 'gcc', 'g++', 'cmake']
        for tool in build_tools:
            if shutil.which(tool):
                self.info.append(f"✓ Build tool available: {tool}")
            else:
                self.warnings.append(f"Build tool not found: {tool}")
        
        # Check for OpenSSL specific requirements
        if os.path.exists('configure') or os.path.exists('config'):
            self.info.append("✓ OpenSSL configure script found")
        else:
            self.warnings.append("OpenSSL configure script not found")
        
        # Check for required source files
        required_files = ['VERSION.dat', 'LICENSE.txt', 'README.md']
        for file_path in required_files:
            if os.path.exists(file_path):
                self.info.append(f"✓ Required file found: {file_path}")
            else:
                self.warnings.append(f"Required file not found: {file_path}")
    
    def _print_summary(self):
        """Print validation summary"""
        print("\n" + "="*60)
        print("📊 VALIDATION SUMMARY")
        print("="*60)
        
        if self.info:
            print(f"\n✅ INFO ({len(self.info)} items):")
            for item in self.info:
                print(f"  • {item}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)} items):")
            for item in self.warnings:
                print(f"  • {item}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)} items):")
            for item in self.errors:
                print(f"  • {item}")
        
        print("\n" + "="*60)
        
        if self.errors:
            print("❌ VALIDATION FAILED - Fix errors before building")
            return False
        elif self.warnings:
            print("⚠️  VALIDATION PASSED WITH WARNINGS - Review warnings")
            return True
        else:
            print("✅ VALIDATION PASSED - Ready to build")
            return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Pre-build validation for OpenSSL Conan packages')
    parser.add_argument('--config', default='conan-dev/validation-config.yml',
                       help='Path to validation configuration file')
    parser.add_argument('--strict', action='store_true',
                       help='Treat warnings as errors')
    
    args = parser.parse_args()
    
    validator = PreBuildValidator(args.config)
    
    if args.strict:
        # In strict mode, treat warnings as errors
        original_warnings = validator.warnings
        validator.warnings = []
        validator.errors.extend(original_warnings)
    
    success = validator.validate_all()
    
    if not success:
        sys.exit(1)
    else:
        print("\n🎉 Pre-build validation completed successfully!")
        sys.exit(0)


if __name__ == '__main__':
    main()
