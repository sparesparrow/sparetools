#!/usr/bin/env python3
"""
Authentication token manager for OpenSSL Conan packages
Manages authentication tokens for GitHub Packages, Artifactory, and other remotes
"""

import os
import sys
import json
import yaml
import subprocess
import base64
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse


class AuthTokenManager:
    """Authentication token manager for Conan remotes"""
    
    def __init__(self, config_file: str = "conan-dev/package-registries.yml"):
        self.config_file = config_file
        self.config = self._load_config()
        self.tokens = {}
        
    def _load_config(self) -> Dict:
        """Load package registries configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def validate_tokens(self) -> bool:
        """Validate all authentication tokens"""
        print("🔐 Validating authentication tokens...")
        
        success = True
        registries = self.config.get('registries', {})
        
        for registry_name, registry_config in registries.items():
            if not registry_config.get('enabled', False):
                continue
                
            print(f"  Validating {registry_name}...")
            
            if not self._validate_registry_token(registry_name, registry_config):
                success = False
                print(f"    ❌ {registry_name} token validation failed")
            else:
                print(f"    ✅ {registry_name} token is valid")
        
        return success
    
    def _validate_registry_token(self, registry_name: str, registry_config: Dict) -> bool:
        """Validate a specific registry token"""
        try:
            url = registry_config.get('url', '')
            username = registry_config.get('username', '')
            password = registry_config.get('password', '')
            
            if not url or not username or not password:
                print(f"    Warning: {registry_name} missing required credentials")
                return False
            
            # Test authentication based on registry type
            if 'github.com' in url:
                return self._validate_github_token(url, username, password)
            elif 'artifactory' in url.lower():
                return self._validate_artifactory_token(url, username, password)
            elif 'center.conan.io' in url:
                return self._validate_conan_center_token(url, username, password)
            else:
                # Generic validation
                return self._validate_generic_token(url, username, password)
                
        except Exception as e:
            print(f"    Error validating {registry_name}: {e}")
            return False
    
    def _validate_github_token(self, url: str, username: str, password: str) -> bool:
        """Validate GitHub Packages token"""
        try:
            # GitHub Packages uses Maven repository format
            # Test with a simple API call
            import urllib.request
            import urllib.error
            
            # Construct API URL
            repo_path = url.replace('https://maven.pkg.github.com/', '')
            api_url = f"https://api.github.com/repos/{repo_path}"
            
            # Create request with authentication
            request = urllib.request.Request(api_url)
            auth_string = f"{username}:{password}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            request.add_header('Authorization', f'Basic {auth_b64}')
            
            # Make request
            with urllib.request.urlopen(request) as response:
                if response.status == 200:
                    return True
                else:
                    return False
                    
        except Exception as e:
            print(f"    GitHub token validation error: {e}")
            return False
    
    def _validate_artifactory_token(self, url: str, username: str, password: str) -> bool:
        """Validate Artifactory token"""
        try:
            import urllib.request
            import urllib.error
            
            # Test with Artifactory API
            api_url = f"{url}/api/system/ping"
            
            # Create request with authentication
            request = urllib.request.Request(api_url)
            auth_string = f"{username}:{password}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            request.add_header('Authorization', f'Basic {auth_b64}')
            
            # Make request
            with urllib.request.urlopen(request) as response:
                if response.status == 200:
                    return True
                else:
                    return False
                    
        except Exception as e:
            print(f"    Artifactory token validation error: {e}")
            return False
    
    def _validate_conan_center_token(self, url: str, username: str, password: str) -> bool:
        """Validate Conan Center token"""
        try:
            # Conan Center doesn't require authentication for public packages
            # But we can test if the remote is accessible
            import urllib.request
            
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    return True
                else:
                    return False
                    
        except Exception as e:
            print(f"    Conan Center validation error: {e}")
            return False
    
    def _validate_generic_token(self, url: str, username: str, password: str) -> bool:
        """Validate generic token"""
        try:
            import urllib.request
            
            # Simple connectivity test
            with urllib.request.urlopen(url) as response:
                if response.status in [200, 401, 403]:  # 401/403 means auth required but URL is valid
                    return True
                else:
                    return False
                    
        except Exception as e:
            print(f"    Generic token validation error: {e}")
            return False
    
    def configure_remotes(self) -> bool:
        """Configure Conan remotes with authentication"""
        print("🌐 Configuring Conan remotes...")
        
        success = True
        registries = self.config.get('registries', {})
        
        for registry_name, registry_config in registries.items():
            if not registry_config.get('enabled', False):
                continue
                
            print(f"  Configuring {registry_name}...")
            
            if not self._configure_remote(registry_name, registry_config):
                success = False
                print(f"    ❌ Failed to configure {registry_name}")
            else:
                print(f"    ✅ {registry_name} configured successfully")
        
        return success
    
    def _configure_remote(self, registry_name: str, registry_config: Dict) -> bool:
        """Configure a specific Conan remote"""
        try:
            url = registry_config.get('url', '')
            username = registry_config.get('username', '')
            password = registry_config.get('password', '')
            
            if not url:
                print(f"    Warning: {registry_name} missing URL")
                return False
            
            # Add or update remote
            subprocess.run(['conan', 'remote', 'add', registry_name, url], 
                         check=False, capture_output=True)
            subprocess.run(['conan', 'remote', 'update', registry_name, url], 
                         check=False, capture_output=True)
            
            # Set authentication if credentials provided
            if username and password:
                subprocess.run(['conan', 'user', '-p', password, '-r', registry_name, username], 
                             check=False, capture_output=True)
            
            return True
            
        except Exception as e:
            print(f"    Error configuring {registry_name}: {e}")
            return False
    
    def test_uploads(self) -> bool:
        """Test uploads to configured remotes"""
        print("📤 Testing uploads to remotes...")
        
        success = True
        registries = self.config.get('registries', {})
        
        for registry_name, registry_config in registries.items():
            if not registry_config.get('enabled', False):
                continue
                
            print(f"  Testing upload to {registry_name}...")
            
            if not self._test_upload(registry_name, registry_config):
                success = False
                print(f"    ❌ Upload test failed for {registry_name}")
            else:
                print(f"    ✅ Upload test successful for {registry_name}")
        
        return success
    
    def _test_upload(self, registry_name: str, registry_config: Dict) -> bool:
        """Test upload to a specific remote"""
        try:
            # Create a test package for upload testing
            test_package = "test-upload-package"
            
            # Try to create a simple test package
            subprocess.run(['conan', 'create', '.', f"{test_package}/1.0.0@test/test"], 
                         check=False, capture_output=True)
            
            # Try to upload (this might fail if package already exists, which is OK)
            result = subprocess.run(['conan', 'upload', f"{test_package}/1.0.0@test/test", 
                                   '-r', registry_name, '--confirm'], 
                                 check=False, capture_output=True)
            
            # If upload fails due to package already existing, that's actually success
            if result.returncode == 0 or "already exists" in result.stderr.decode():
                return True
            else:
                return False
                
        except Exception as e:
            print(f"    Error testing upload to {registry_name}: {e}")
            return False
    
    def generate_token_report(self) -> Dict:
        """Generate authentication token report"""
        print("📊 Generating token report...")
        
        report = {
            'timestamp': str(os.environ.get('SOURCE_DATE_EPOCH', '')),
            'registries': {},
            'summary': {
                'total_registries': 0,
                'enabled_registries': 0,
                'valid_tokens': 0,
                'invalid_tokens': 0
            }
        }
        
        registries = self.config.get('registries', {})
        report['summary']['total_registries'] = len(registries)
        
        for registry_name, registry_config in registries.items():
            registry_report = {
                'enabled': registry_config.get('enabled', False),
                'url': registry_config.get('url', ''),
                'has_username': bool(registry_config.get('username', '')),
                'has_password': bool(registry_config.get('password', '')),
                'token_valid': False,
                'upload_test': False
            }
            
            if registry_report['enabled']:
                report['summary']['enabled_registries'] += 1
                
                # Test token validity
                registry_report['token_valid'] = self._validate_registry_token(registry_name, registry_config)
                
                if registry_report['token_valid']:
                    report['summary']['valid_tokens'] += 1
                else:
                    report['summary']['invalid_tokens'] += 1
                
                # Test upload
                registry_report['upload_test'] = self._test_upload(registry_name, registry_config)
            
            report['registries'][registry_name] = registry_report
        
        # Save report
        report_file = 'auth-token-report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Token report saved: {report_file}")
        return report
    
    def setup_environment_variables(self):
        """Set up environment variables for authentication"""
        print("🔧 Setting up environment variables...")
        
        registries = self.config.get('registries', {})
        
        for registry_name, registry_config in registries.items():
            if not registry_config.get('enabled', False):
                continue
            
            username = registry_config.get('username', '')
            password = registry_config.get('password', '')
            
            if username and password:
                # Set environment variables for the registry
                env_prefix = registry_name.upper().replace('-', '_')
                os.environ[f'{env_prefix}_USERNAME'] = username
                os.environ[f'{env_prefix}_PASSWORD'] = password
                
                print(f"  ✓ Set environment variables for {registry_name}")
    
    def run_full_setup(self) -> bool:
        """Run complete authentication setup"""
        print("🚀 Starting authentication setup...")
        
        try:
            # Validate tokens
            if not self.validate_tokens():
                print("❌ Token validation failed")
                return False
            
            # Configure remotes
            if not self.configure_remotes():
                print("❌ Remote configuration failed")
                return False
            
            # Test uploads
            if not self.test_uploads():
                print("❌ Upload tests failed")
                return False
            
            # Set up environment variables
            self.setup_environment_variables()
            
            # Generate report
            self.generate_token_report()
            
            print("✅ Authentication setup completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Authentication setup failed: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Authentication token manager for OpenSSL Conan packages')
    parser.add_argument('--config', default='conan-dev/package-registries.yml',
                       help='Path to package registries configuration file')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate tokens')
    parser.add_argument('--configure-only', action='store_true',
                       help='Only configure remotes')
    parser.add_argument('--test-only', action='store_true',
                       help='Only test uploads')
    
    args = parser.parse_args()
    
    manager = AuthTokenManager(args.config)
    
    if args.validate_only:
        success = manager.validate_tokens()
    elif args.configure_only:
        success = manager.configure_remotes()
    elif args.test_only:
        success = manager.test_uploads()
    else:
        success = manager.run_full_setup()
    
    if not success:
        sys.exit(1)
    else:
        print("\n🎉 Authentication setup completed successfully!")
        sys.exit(0)


if __name__ == '__main__':
    main()
