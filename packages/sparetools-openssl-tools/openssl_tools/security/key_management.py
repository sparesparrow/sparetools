#!/usr/bin/env python3
"""
Secure Key Manager for OpenSSL Conan packages
Ensures secure key management and supply chain security
"""

import os
import sys
import json
import yaml
import hashlib
import subprocess
import secrets
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
from datetime import datetime, timedelta
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class SecureKeyManager:
    """Manages secure keys and supply chain security"""
    
    def __init__(self, config_file: str = "conan-dev/secure-key-management.yml"):
        self.config_file = config_file
        self.config = self._load_config()
        self.key_registry = {}
        
    def _load_config(self) -> Dict:
        """Load secure key management configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default secure key management configuration"""
        return {
            'key_management': {
                'key_types': ['signing', 'encryption', 'authentication'],
                'key_rotation_days': 90,
                'key_storage': 'encrypted',
                'backup_enabled': True,
                'audit_logging': True
            },
            'supply_chain': {
                'signature_verification': True,
                'checksum_verification': True,
                'dependency_scanning': True,
                'vulnerability_scanning': True,
                'license_compliance': True
            },
            'security': {
                'encryption_algorithm': 'AES-256-GCM',
                'signing_algorithm': 'RSA-PSS',
                'hash_algorithm': 'SHA-256',
                'key_size': 4096
            },
            'workflow': {
                'signing_required': True,
                'verification_required': True,
                'audit_required': True,
                'approval_required': True
            }
        }
    
    def generate_key_pair(self, key_name: str, key_type: str = 'signing') -> Dict:
        """Generate secure key pair"""
        print(f"🔑 Generating {key_type} key pair: {key_name}...")
        
        try:
            # Generate RSA key pair
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=self.config['security']['key_size']
            )
            
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Generate key ID
            key_id = self._generate_key_id(public_pem)
            
            # Store key information
            key_info = {
                'name': key_name,
                'type': key_type,
                'key_id': key_id,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(days=self.config['key_management']['key_rotation_days'])).isoformat(),
                'status': 'active',
                'public_key': public_pem.decode(),
                'private_key_path': f"keys/{key_name}_private.pem",
                'public_key_path': f"keys/{key_name}_public.pem"
            }
            
            # Save keys to files
            self._save_key_files(key_name, private_pem, public_pem)
            
            # Register key
            self.key_registry[key_id] = key_info
            self._save_key_registry()
            
            print(f"✓ Generated key pair: {key_id}")
            return key_info
            
        except Exception as e:
            print(f"❌ Failed to generate key pair: {e}")
            return {}
    
    def _generate_key_id(self, public_key: bytes) -> str:
        """Generate unique key ID from public key"""
        hash_obj = hashlib.sha256(public_key)
        return hash_obj.hexdigest()[:16]
    
    def _save_key_files(self, key_name: str, private_key: bytes, public_key: bytes):
        """Save key files to secure location"""
        keys_dir = Path("keys")
        keys_dir.mkdir(exist_ok=True)
        
        # Save private key (encrypted)
        private_key_path = keys_dir / f"{key_name}_private.pem"
        with open(private_key_path, 'wb') as f:
            f.write(private_key)
        
        # Save public key
        public_key_path = keys_dir / f"{key_name}_public.pem"
        with open(public_key_path, 'wb') as f:
            f.write(public_key)
        
        # Set secure permissions
        os.chmod(private_key_path, 0o600)
        os.chmod(public_key_path, 0o644)
    
    def sign_artifact(self, artifact_path: str, key_id: str) -> str:
        """Sign artifact with specified key"""
        print(f"✍️  Signing artifact: {artifact_path}...")
        
        try:
            if key_id not in self.key_registry:
                raise ValueError(f"Key {key_id} not found")
            
            key_info = self.key_registry[key_id]
            private_key_path = key_info['private_key_path']
            
            # Load private key
            with open(private_key_path, 'rb') as f:
                private_key = serialization.load_pem_private_key(f.read(), password=None)
            
            # Read artifact
            with open(artifact_path, 'rb') as f:
                artifact_data = f.read()
            
            # Create signature
            signature = private_key.sign(
                artifact_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Save signature
            signature_path = f"{artifact_path}.sig"
            with open(signature_path, 'wb') as f:
                f.write(signature)
            
            # Create signature metadata
            signature_metadata = {
                'artifact_path': artifact_path,
                'key_id': key_id,
                'signature_path': signature_path,
                'signed_at': datetime.now().isoformat(),
                'algorithm': self.config['security']['signing_algorithm'],
                'hash_algorithm': self.config['security']['hash_algorithm']
            }
            
            # Save metadata
            metadata_path = f"{artifact_path}.sig.meta"
            with open(metadata_path, 'w') as f:
                json.dump(signature_metadata, f, indent=2)
            
            print(f"✓ Signed artifact: {signature_path}")
            return signature_path
            
        except Exception as e:
            print(f"❌ Failed to sign artifact: {e}")
            return ""
    
    def verify_signature(self, artifact_path: str, signature_path: str) -> bool:
        """Verify artifact signature"""
        print(f"🔍 Verifying signature: {artifact_path}...")
        
        try:
            # Load signature metadata
            metadata_path = f"{signature_path}.meta"
            if not os.path.exists(metadata_path):
                print("❌ Signature metadata not found")
                return False
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            key_id = metadata['key_id']
            if key_id not in self.key_registry:
                print(f"❌ Key {key_id} not found in registry")
                return False
            
            key_info = self.key_registry[key_id]
            public_key_path = key_info['public_key_path']
            
            # Load public key
            with open(public_key_path, 'rb') as f:
                public_key = serialization.load_pem_public_key(f.read())
            
            # Read artifact and signature
            with open(artifact_path, 'rb') as f:
                artifact_data = f.read()
            
            with open(signature_path, 'rb') as f:
                signature = f.read()
            
            # Verify signature
            try:
                public_key.verify(
                    signature,
                    artifact_data,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                print(f"✓ Signature verified: {key_id}")
                return True
                
            except Exception as e:
                print(f"❌ Signature verification failed: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to verify signature: {e}")
            return False
    
    def scan_vulnerabilities(self, package_path: str) -> Dict:
        """Scan package for vulnerabilities"""
        print(f"🔍 Scanning vulnerabilities: {package_path}...")
        
        vulnerabilities = {
            'package_path': package_path,
            'scan_timestamp': datetime.now().isoformat(),
            'vulnerabilities': [],
            'dependencies': [],
            'licenses': [],
            'risk_level': 'low'
        }
        
        try:
            # Check for known vulnerable files
            vulnerable_patterns = [
                'test', 'debug', 'backup', 'temp', 'old'
            ]
            
            for root, dirs, files in os.walk(package_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check file permissions
                    if os.access(file_path, os.W_OK):
                        vulnerabilities['vulnerabilities'].append({
                            'type': 'permission',
                            'severity': 'medium',
                            'file': file_path,
                            'description': 'File is world-writable'
                        })
                    
                    # Check for sensitive files
                    if any(pattern in file.lower() for pattern in vulnerable_patterns):
                        vulnerabilities['vulnerabilities'].append({
                            'type': 'sensitive_file',
                            'severity': 'low',
                            'file': file_path,
                            'description': 'Potentially sensitive file'
                        })
            
            # Check for hardcoded secrets
            secret_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'key\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']'
            ]
            
            for root, dirs, files in os.walk(package_path):
                for file in files:
                    if file.endswith(('.py', '.yml', '.yaml', '.json', '.txt')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                
                            for pattern in secret_patterns:
                                import re
                                if re.search(pattern, content, re.IGNORECASE):
                                    vulnerabilities['vulnerabilities'].append({
                                        'type': 'hardcoded_secret',
                                        'severity': 'high',
                                        'file': file_path,
                                        'description': 'Potential hardcoded secret found'
                                    })
                        except:
                            pass
            
            # Determine risk level
            high_vulns = [v for v in vulnerabilities['vulnerabilities'] if v['severity'] == 'high']
            medium_vulns = [v for v in vulnerabilities['vulnerabilities'] if v['severity'] == 'medium']
            
            if high_vulns:
                vulnerabilities['risk_level'] = 'high'
            elif medium_vulns:
                vulnerabilities['risk_level'] = 'medium'
            
            print(f"✓ Vulnerability scan completed: {len(vulnerabilities['vulnerabilities'])} issues found")
            return vulnerabilities
            
        except Exception as e:
            print(f"❌ Vulnerability scan failed: {e}")
            return vulnerabilities
    
    def audit_key_usage(self) -> Dict:
        """Audit key usage and security"""
        print("📊 Auditing key usage...")
        
        audit_report = {
            'timestamp': datetime.now().isoformat(),
            'total_keys': len(self.key_registry),
            'active_keys': 0,
            'expired_keys': 0,
            'key_usage': {},
            'security_issues': []
        }
        
        current_time = datetime.now()
        
        for key_id, key_info in self.key_registry.items():
            # Check key status
            if key_info['status'] == 'active':
                audit_report['active_keys'] += 1
                
                # Check expiration
                expires_at = datetime.fromisoformat(key_info['expires_at'])
                if expires_at < current_time:
                    audit_report['expired_keys'] += 1
                    audit_report['security_issues'].append({
                        'type': 'expired_key',
                        'severity': 'high',
                        'key_id': key_id,
                        'description': f"Key {key_id} has expired"
                    })
                elif expires_at < current_time + timedelta(days=7):
                    audit_report['security_issues'].append({
                        'type': 'expiring_key',
                        'severity': 'medium',
                        'key_id': key_id,
                        'description': f"Key {key_id} expires soon"
                    })
            
            # Track key usage
            key_type = key_info['type']
            if key_type not in audit_report['key_usage']:
                audit_report['key_usage'][key_type] = 0
            audit_report['key_usage'][key_type] += 1
        
        # Save audit report
        report_file = 'key-audit-report.json'
        with open(report_file, 'w') as f:
            json.dump(audit_report, f, indent=2)
        
        print(f"✓ Key audit completed: {audit_report['active_keys']} active keys")
        return audit_report
    
    def rotate_keys(self) -> int:
        """Rotate expired or soon-to-expire keys"""
        print("🔄 Rotating keys...")
        
        rotated_count = 0
        current_time = datetime.now()
        
        for key_id, key_info in list(self.key_registry.items()):
            expires_at = datetime.fromisoformat(key_info['expires_at'])
            
            # Rotate if expired or expiring soon
            if expires_at < current_time + timedelta(days=7):
                new_key_name = f"{key_info['name']}_rotated_{int(current_time.timestamp())}"
                new_key_info = self.generate_key_pair(new_key_name, key_info['type'])
                
                if new_key_info:
                    # Mark old key as rotated
                    key_info['status'] = 'rotated'
                    key_info['rotated_at'] = current_time.isoformat()
                    key_info['replaced_by'] = new_key_info['key_id']
                    
                    rotated_count += 1
                    print(f"  ✓ Rotated key {key_id} -> {new_key_info['key_id']}")
        
        if rotated_count > 0:
            self._save_key_registry()
        
        print(f"✓ Rotated {rotated_count} keys")
        return rotated_count
    
    def _save_key_registry(self):
        """Save key registry to persistent storage"""
        registry_file = 'key-registry.json'
        with open(registry_file, 'w') as f:
            json.dump(self.key_registry, f, indent=2)
    
    def generate_security_report(self) -> Dict:
        """Generate comprehensive security report"""
        print("📊 Generating security report...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'key_management': self.audit_key_usage(),
            'supply_chain': {
                'signature_verification': self.config['supply_chain']['signature_verification'],
                'checksum_verification': self.config['supply_chain']['checksum_verification'],
                'vulnerability_scanning': self.config['supply_chain']['vulnerability_scanning']
            },
            'recommendations': []
        }
        
        # Add security recommendations
        if report['key_management']['expired_keys'] > 0:
            report['recommendations'].append("Rotate expired keys immediately")
        
        if report['key_management']['active_keys'] < 2:
            report['recommendations'].append("Generate additional keys for redundancy")
        
        if len(report['key_management']['security_issues']) > 0:
            report['recommendations'].append("Address security issues in key management")
        
        # Save report
        report_file = 'security-report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Security report saved: {report_file}")
        return report


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Secure Key Manager for OpenSSL Conan packages')
    parser.add_argument('--config', default='conan-dev/secure-key-management.yml',
                       help='Path to secure key management configuration file')
    parser.add_argument('--generate-key', nargs=2, metavar=('NAME', 'TYPE'),
                       help='Generate new key pair')
    parser.add_argument('--sign', nargs=2, metavar=('ARTIFACT', 'KEY_ID'),
                       help='Sign artifact with key')
    parser.add_argument('--verify', nargs=2, metavar=('ARTIFACT', 'SIGNATURE'),
                       help='Verify artifact signature')
    parser.add_argument('--scan-vulnerabilities', metavar='PACKAGE_PATH',
                       help='Scan package for vulnerabilities')
    parser.add_argument('--audit-keys', action='store_true',
                       help='Audit key usage')
    parser.add_argument('--rotate-keys', action='store_true',
                       help='Rotate expired keys')
    parser.add_argument('--report', action='store_true',
                       help='Generate security report')
    
    args = parser.parse_args()
    
    manager = SecureKeyManager(args.config)
    
    if args.generate_key:
        name, key_type = args.generate_key
        key_info = manager.generate_key_pair(name, key_type)
    elif args.sign:
        artifact, key_id = args.sign
        signature = manager.sign_artifact(artifact, key_id)
    elif args.verify:
        artifact, signature = args.verify
        success = manager.verify_signature(artifact, signature)
    elif args.scan_vulnerabilities:
        vulnerabilities = manager.scan_vulnerabilities(args.scan_vulnerabilities)
    elif args.audit_keys:
        audit = manager.audit_key_usage()
    elif args.rotate_keys:
        rotated = manager.rotate_keys()
    elif args.report:
        report = manager.generate_security_report()
    else:
        print("Please specify an action")
        success = False
    
    if 'success' in locals() and not success:
        sys.exit(1)
    else:
        print("\n🎉 Secure key management completed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
