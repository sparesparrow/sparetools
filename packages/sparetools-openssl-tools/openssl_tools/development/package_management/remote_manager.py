#!/usr/bin/env python3
"""
OpenSSL Tools - Conan Remote Manager
Manages Conan remotes and package uploads to GitHub Packages.
"""

import json
import subprocess
import logging
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import requests
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConanRemoteManager:
    """Manages Conan remotes and package operations."""
    
    def __init__(self, github_token: Optional[str] = None, username: Optional[str] = None):
        self.github_packages_url = "https://maven.pkg.github.com/sparesparrow/openssl"
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.username = username or os.getenv("GITHUB_USERNAME", "sparesparrow")
        self.remote_name = "github-packages"
        self.config_file = Path.home() / ".conan" / "conan.conf"
        
    def setup_github_packages_remote(self, force: bool = False) -> bool:
        """
        Set up GitHub Packages as a Conan remote.
        
        Args:
            force: If True, overwrite existing remote
            
        Returns:
            bool: True if setup was successful
        """
        if not self.github_token:
            logger.error("GitHub token not provided. Set GITHUB_TOKEN environment variable.")
            return False
            
        try:
            # Check if remote already exists
            existing_remotes = self.list_remotes()
            if self.remote_name in existing_remotes:
                if force:
                    logger.info(f"Removing existing remote: {self.remote_name}")
                    subprocess.run([
                        "conan", "remote", "remove", self.remote_name
                    ], check=True)
                else:
                    logger.info(f"Remote {self.remote_name} already exists")
                    return True
                    
            # Add GitHub Packages remote
            logger.info(f"Adding GitHub Packages remote: {self.remote_name}")
            subprocess.run([
                "conan", "remote", "add", self.remote_name, 
                self.github_packages_url, "--force"
            ], check=True)
            
            # Login to GitHub Packages using SSH
            logger.info("Logging in to GitHub Packages using SSH")
            # For Maven registry, we use the username and a personal access token
            # The token should have packages:write permissions
            if not self.github_token:
                logger.error("GitHub token required for Maven registry authentication")
                return False
                
            subprocess.run([
                "conan", "remote", "login", self.remote_name, 
                self.username, self.github_token
            ], check=True)
            
            # Verify connection
            if self._verify_remote_connection():
                logger.info("Successfully set up GitHub Packages remote")
                return True
            else:
                logger.error("Failed to verify remote connection")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to set up GitHub Packages remote: {e}")
            return False
            
    def list_remotes(self) -> Dict[str, str]:
        """List all configured Conan remotes."""
        try:
            result = subprocess.run([
                "conan", "remote", "list"
            ], capture_output=True, text=True, check=True)
            
            remotes = {}
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        name = parts[0].strip()
                        url = parts[1].strip()
                        remotes[name] = url
                        
            return remotes
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list remotes: {e}")
            return {}
            
    def _verify_remote_connection(self) -> bool:
        """Verify that the remote connection is working."""
        try:
            # Try to search for a package (this will test the connection)
            result = subprocess.run([
                "conan", "search", "*", "-r", self.remote_name
            ], capture_output=True, text=True, timeout=30)
            
            # Even if no packages are found, a successful connection should return 0
            return result.returncode == 0
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False
            
    def upload_packages(self, patterns: List[str] = None, 
                       remote: str = None, 
                       confirm: bool = True) -> bool:
        """
        Upload packages to the specified remote.
        
        Args:
            patterns: List of package patterns to upload (default: ["*"])
            remote: Remote name to upload to (default: github-packages)
            confirm: If True, skip confirmation prompts
            
        Returns:
            bool: True if upload was successful
        """
        if patterns is None:
            patterns = ["*"]
            
        if remote is None:
            remote = self.remote_name
            
        try:
            for pattern in patterns:
                logger.info(f"Uploading packages matching pattern: {pattern}")
                
                cmd = [
                    "conan", "upload", pattern,
                    "-r", remote
                ]
                
                if confirm:
                    cmd.append("--confirm")
                    
                subprocess.run(cmd, check=True)
                
            logger.info("Package upload completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to upload packages: {e}")
            return False
            
    def download_packages(self, patterns: List[str], 
                         remote: str = None) -> bool:
        """
        Download packages from the specified remote.
        
        Args:
            patterns: List of package patterns to download
            remote: Remote name to download from (default: github-packages)
            
        Returns:
            bool: True if download was successful
        """
        if remote is None:
            remote = self.remote_name
            
        try:
            for pattern in patterns:
                logger.info(f"Downloading packages matching pattern: {pattern}")
                
                subprocess.run([
                    "conan", "download", pattern,
                    "-r", remote
                ], check=True)
                
            logger.info("Package download completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download packages: {e}")
            return False
            
    def search_packages(self, query: str, remote: str = None) -> List[Dict]:
        """
        Search for packages in the specified remote.
        
        Args:
            query: Search query
            remote: Remote name to search in (default: github-packages)
            
        Returns:
            List of package information dictionaries
        """
        if remote is None:
            remote = self.remote_name
            
        try:
            result = subprocess.run([
                "conan", "search", query, "-r", remote
            ], capture_output=True, text=True, check=True)
            
            packages = []
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if line.strip() and not line.startswith('Existing'):
                    # Parse package information
                    parts = line.split('/')
                    if len(parts) >= 2:
                        packages.append({
                            'name': parts[0],
                            'version': parts[1] if len(parts) > 1 else None,
                            'user': parts[2] if len(parts) > 2 else None,
                            'channel': parts[3] if len(parts) > 3 else None
                        })
                        
            return packages
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to search packages: {e}")
            return []
            
    def create_package(self, recipe_path: Path, 
                      name: str, version: str, 
                      user: str = None, channel: str = None) -> bool:
        """
        Create a Conan package from a recipe.
        
        Args:
            recipe_path: Path to the Conan recipe
            name: Package name
            version: Package version
            user: Package user (default: sparesparrow)
            channel: Package channel (default: stable)
            
        Returns:
            bool: True if package creation was successful
        """
        if user is None:
            user = self.username
        if channel is None:
            channel = "stable"
            
        try:
            # Export the recipe
            logger.info(f"Exporting recipe: {recipe_path}")
            subprocess.run([
                "conan", "export", str(recipe_path), 
                f"{name}/{version}@{user}/{channel}"
            ], check=True)
            
            # Create the package
            logger.info(f"Creating package: {name}/{version}")
            subprocess.run([
                "conan", "create", str(recipe_path),
                f"{name}/{version}@{user}/{channel}"
            ], check=True)
            
            logger.info(f"Successfully created package: {name}/{version}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create package: {e}")
            return False
            
    def install_package(self, package_ref: str, 
                       remote: str = None) -> bool:
        """
        Install a package from the specified remote.
        
        Args:
            package_ref: Package reference (e.g., "openssl/1.1.1@sparesparrow/stable")
            remote: Remote name to install from (default: github-packages)
            
        Returns:
            bool: True if installation was successful
        """
        if remote is None:
            remote = self.remote_name
            
        try:
            logger.info(f"Installing package: {package_ref}")
            subprocess.run([
                "conan", "install", package_ref,
                "-r", remote
            ], check=True)
            
            logger.info(f"Successfully installed package: {package_ref}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install package: {e}")
            return False
            
    def get_package_info(self, package_ref: str) -> Optional[Dict]:
        """
        Get information about a package.
        
        Args:
            package_ref: Package reference
            
        Returns:
            Dictionary with package information or None if not found
        """
        try:
            result = subprocess.run([
                "conan", "inspect", package_ref
            ], capture_output=True, text=True, check=True)
            
            # Parse the output to extract package information
            info = {}
            for line in result.stdout.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
                    
            return info
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get package info: {e}")
            return None
            
    def setup_ssh_authentication(self) -> bool:
        """Set up SSH-based authentication for GitHub Packages."""
        logger.info("Setting up SSH authentication for GitHub Packages...")
        
        try:
            # Check if SSH key exists
            ssh_key_path = Path.home() / ".ssh" / "id_rsa"
            if not ssh_key_path.exists():
                logger.warning("SSH key not found. Please generate one with: ssh-keygen -t rsa -b 4096")
                return False
                
            # Test SSH connection to GitHub
            result = subprocess.run([
                "ssh", "-T", "git@github.com"
            ], capture_output=True, text=True, timeout=10)
            
            if "successfully authenticated" in result.stderr.lower():
                logger.info("SSH authentication to GitHub successful")
                return True
            else:
                logger.error(f"SSH authentication failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("SSH connection timeout")
            return False
        except Exception as e:
            logger.error(f"SSH setup failed: {e}")
            return False
            
    def test_connection(self) -> bool:
        """Test the connection to GitHub Packages."""
        logger.info("Testing connection to GitHub Packages...")
        
        # First try SSH authentication
        if self.setup_ssh_authentication():
            return True
            
        # Fallback to token-based authentication
        if not self.github_token:
            logger.error("Neither SSH nor GitHub token configured")
            return False
            
        # Test GitHub API access
        try:
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(
                'https://api.github.com/user',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_info = response.json()
                logger.info(f"Successfully connected as: {user_info.get('login')}")
                return True
            else:
                logger.error(f"GitHub API error: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Failed to connect to GitHub API: {e}")
            return False


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenSSL Conan Remote Manager")
    parser.add_argument("--token", help="GitHub token")
    parser.add_argument("--username", help="GitHub username")
    parser.add_argument("--setup", action="store_true", help="Set up GitHub Packages remote")
    parser.add_argument("--list", action="store_true", help="List remotes")
    parser.add_argument("--upload", nargs="+", help="Upload packages (patterns)")
    parser.add_argument("--download", nargs="+", help="Download packages (patterns)")
    parser.add_argument("--search", help="Search for packages")
    parser.add_argument("--test", action="store_true", help="Test connection")
    parser.add_argument("--setup-ssh", action="store_true", help="Set up SSH authentication")
    parser.add_argument("--remote", default="github-packages", help="Remote name")
    
    args = parser.parse_args()
    
    manager = ConanRemoteManager(
        github_token=args.token,
        username=args.username
    )
    
    if args.setup:
        success = manager.setup_github_packages_remote()
        if not success:
            sys.exit(1)
            
    if args.list:
        remotes = manager.list_remotes()
        if remotes:
            print("Configured remotes:")
            for name, url in remotes.items():
                print(f"  {name}: {url}")
        else:
            print("No remotes configured")
            
    if args.upload:
        success = manager.upload_packages(args.upload, args.remote)
        if not success:
            sys.exit(1)
            
    if args.download:
        success = manager.download_packages(args.download, args.remote)
        if not success:
            sys.exit(1)
            
    if args.search:
        packages = manager.search_packages(args.search, args.remote)
        if packages:
            print(f"Found {len(packages)} packages:")
            for pkg in packages:
                print(f"  {pkg['name']}/{pkg['version']}")
        else:
            print("No packages found")
            
    if args.setup_ssh:
        success = manager.setup_ssh_authentication()
        if not success:
            sys.exit(1)
            
    if args.test:
        success = manager.test_connection()
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    import sys
    main()