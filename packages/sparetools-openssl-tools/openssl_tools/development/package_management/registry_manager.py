#!/usr/bin/env python3
"""
Package Registry Manager
Manages package uploads to multiple registries (Artifactory, GitHub Packages, Conan Center).
"""

import argparse
import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PackageRegistryManager:
    """Manages package uploads to multiple registries."""
    
    def __init__(self, conan_home: Optional[Path] = None):
        self.conan_home = conan_home or Path(os.environ.get('CONAN_USER_HOME', Path.home() / '.conan2'))
        self.registries = {
            'artifactory': {
                'url': os.environ.get('ARTIFACTORY_URL'),
                'username': os.environ.get('ARTIFACTORY_USERNAME'),
                'password': os.environ.get('ARTIFACTORY_TOKEN'),
                'repo': os.environ.get('ARTIFACTORY_REPO', 'conan-local')
            },
            'github-packages': {
                'url': f"https://maven.pkg.github.com/{os.environ.get('GITHUB_REPOSITORY', '')}",
                'username': os.environ.get('GITHUB_ACTOR'),
                'password': os.environ.get('GITHUB_TOKEN'),
                'repo': 'conan'
            },
            'conan-center': {
                'url': 'https://center.conan.io',
                'username': os.environ.get('CONAN_CENTER_USERNAME'),
                'password': os.environ.get('CONAN_CENTER_PASSWORD'),
                'repo': 'conancenter'
            }
        }
    
    def configure_registry(self, registry_name: str) -> bool:
        """Configure a specific registry."""
        if registry_name not in self.registries:
            print(f"[ERROR] Unknown registry: {registry_name}")
            return False
        
        registry = self.registries[registry_name]
        
        if not all([registry['url'], registry['username'], registry['password']]):
            print(f"[WARN] Missing credentials for {registry_name}, skipping")
            return False
        
        try:
            # Add remote
            cmd = [
                'conan', 'remote', 'add', registry_name, 
                f"{registry['url']}/{registry['repo']}"
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Authenticate
            cmd = [
                'conan', 'user', '-p', registry['password'], 
                '-r', registry_name, registry['username']
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            
            print(f"[OK] Configured {registry_name} registry")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to configure {registry_name}: {e}")
            return False
    
    def upload_package(self, package_ref: str, registry_name: str, 
                      force: bool = False) -> bool:
        """Upload a package to a specific registry."""
        try:
            cmd = ['conan', 'upload', package_ref, '-r', registry_name, '--all']
            
            if force:
                cmd.append('--confirm')
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"[OK] Uploaded {package_ref} to {registry_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to upload {package_ref} to {registry_name}: {e}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
            return False
    
    def upload_to_all_registries(self, package_ref: str, 
                                registries: List[str] = None) -> Dict[str, bool]:
        """Upload a package to multiple registries."""
        if registries is None:
            registries = list(self.registries.keys())
        
        results = {}
        
        for registry_name in registries:
            print(f"[UPLOAD] Uploading to {registry_name}...")
            
            # Configure registry first
            if not self.configure_registry(registry_name):
                results[registry_name] = False
                continue
            
            # Upload package
            results[registry_name] = self.upload_package(package_ref, registry_name, force=True)
        
        return results
    
    def list_packages(self, registry_name: str = None) -> List[str]:
        """List packages in a registry."""
        try:
            if registry_name:
                cmd = ['conan', 'list', '*', '-r', registry_name]
            else:
                cmd = ['conan', 'list', '*']
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            packages = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('Local Cache'):
                    packages.append(line.strip())
            
            return packages
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to list packages: {e}")
            return []
    
    def generate_installation_instructions(self, package_ref: str, 
                                         registries: List[str] = None) -> str:
        """Generate installation instructions for a package."""
        if registries is None:
            registries = list(self.registries.keys())
        
        instructions = f"# Installation Instructions for {package_ref}\n\n"
        
        for registry_name in registries:
            registry = self.registries[registry_name]
            
            if not all([registry['url'], registry['username']]):
                continue
            
            instructions += f"## From {registry_name.title()}\n\n"
            instructions += "```bash\n"
            
            if registry_name != 'conan-center':
                instructions += f"conan remote add {registry_name} {registry['url']}/{registry['repo']}\n"
                instructions += f"conan user -p <password> -r {registry_name} <username>\n"
                instructions += f"conan install {package_ref} -r={registry_name}\n"
            else:
                instructions += f"conan install {package_ref}\n"
            
            instructions += "```\n\n"
        
        return instructions
    
    def cleanup_old_packages(self, registry_name: str, 
                           keep_days: int = 30) -> bool:
        """Clean up old packages from a registry."""
        try:
            # This would need to be implemented based on the specific registry API
            print(f"[INFO] Cleanup for {registry_name} not implemented yet")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to cleanup {registry_name}: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Manage package uploads to multiple registries")
    parser.add_argument("--conan-home", help="Conan home directory")
    parser.add_argument("--package-ref", required=True, help="Package reference (e.g., openssl/1.0.0@user/channel)")
    parser.add_argument("--registries", nargs='+', 
                       choices=['artifactory', 'github-packages', 'conan-center'],
                       default=['artifactory', 'github-packages'],
                       help="Registries to upload to")
    parser.add_argument("--configure-only", action="store_true", 
                       help="Only configure registries, don't upload")
    parser.add_argument("--list-packages", action="store_true",
                       help="List packages in registries")
    parser.add_argument("--generate-instructions", action="store_true",
                       help="Generate installation instructions")
    
    args = parser.parse_args()
    
    # Initialize manager
    conan_home = Path(args.conan_home) if args.conan_home else None
    manager = PackageRegistryManager(conan_home)
    
    if args.list_packages:
        print("[INFO] Listing packages in registries...")
        for registry_name in args.registries:
            print(f"\n{registry_name}:")
            packages = manager.list_packages(registry_name)
            for package in packages:
                print(f"  - {package}")
        return 0
    
    if args.generate_instructions:
        instructions = manager.generate_installation_instructions(
            args.package_ref, args.registries
        )
        print(instructions)
        return 0
    
    if args.configure_only:
        print("[INFO] Configuring registries...")
        success = True
        for registry_name in args.registries:
            if not manager.configure_registry(registry_name):
                success = False
        return 0 if success else 1
    
    # Upload packages
    print(f"[INFO] Uploading {args.package_ref} to registries: {', '.join(args.registries)}")
    
    results = manager.upload_to_all_registries(args.package_ref, args.registries)
    
    # Print results
    print("\n[RESULTS] Upload results:")
    for registry_name, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"  {registry_name}: {status}")
    
    # Generate instructions
    instructions = manager.generate_installation_instructions(
        args.package_ref, args.registries
    )
    
    # Save instructions to file
    instructions_file = Path("installation_instructions.md")
    instructions_file.write_text(instructions)
    print(f"\n[INFO] Installation instructions saved to {instructions_file}")
    
    # Return success if all uploads succeeded
    return 0 if all(results.values()) else 1


if __name__ == '__main__':
    sys.exit(main())