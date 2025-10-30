#!/usr/bin/env python3
"""
GitHub Packages Conan Setup
Sets up Conan 2.x with GitHub Packages for artifact storage
Based on ngapy patterns for proper Python dev/testing environment
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import logging
import json
import base64

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitHubPackagesConanSetup:
    """GitHub Packages Conan setup following ngapy patterns"""
    
    def __init__(self, project_root: Path, github_owner: str, github_repo: str):
        self.project_root = project_root
        self.github_owner = github_owner
        self.github_repo = github_repo
        self.platform = platform.system().lower()
        self.conan_dir = project_root / "conan-dev"
        self.venv_dir = self.conan_dir / "venv"
        
    def setup_github_packages(self, github_token: str = None) -> bool:
        """Set up GitHub Packages with Conan 2.x"""
        try:
            logger.info("🚀 Setting up GitHub Packages with Conan 2.x...")
            
            # Get GitHub token
            if not github_token:
                github_token = self._get_github_token()
            
            if not github_token:
                logger.error("❌ GitHub token not found. Please set GITHUB_TOKEN environment variable or provide --token")
                return False
            
            # Set up Conan configuration
            self._setup_conan_config()
            
            # Add GitHub Packages remote
            self._add_github_packages_remote(github_token)
            
            # Create GitHub Actions workflow
            self._create_github_actions_workflow()
            
            # Create local development scripts
            self._create_dev_scripts()
            
            logger.info("✅ GitHub Packages setup complete!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False
    
    def _get_github_token(self) -> Optional[str]:
        """Get GitHub token from environment or prompt user"""
        # Try environment variable first
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            return token
        
        # Try GitHub CLI
        try:
            result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except:
            pass
        
        # Prompt user
        import getpass
        token = getpass.getpass("Enter GitHub Personal Access Token: ")
        return token if token else None
    
    def _setup_conan_config(self):
        """Set up Conan 2.x configuration"""
        logger.info("⚙️ Setting up Conan 2.x configuration...")
        
        # Create conan directory
        self.conan_dir.mkdir(parents=True, exist_ok=True)
        
        # Create global.conf
        global_conf = self.conan_dir / "global.conf"
        global_conf_content = f"""[log]
level = info

[storage]
path = {self.conan_dir / "cache"}

[proxies]
# http = http://user:pass@server:port
# https = http://user:pass@server:port

[remotes]
# GitHub Packages will be added here

[settings_defaults]
# Default settings for this environment
"""
        
        with open(global_conf, 'w') as f:
            f.write(global_conf_content)
        
        logger.info(f"✅ Created global.conf: {global_conf}")
    
    def _add_github_packages_remote(self, github_token: str):
        """Add GitHub Packages remote to Conan"""
        logger.info("🔗 Adding GitHub Packages remote...")
        
        # Get Conan executable
        conan_exe = self._get_conan_executable()
        
        # GitHub Packages remote URL
        remote_url = f"https://maven.pkg.github.com/{self.github_owner}/{self.github_repo}"
        remote_name = "github-packages"
        
        # Add remote
        try:
            # Try to add remote, ignore if it already exists
            try:
                subprocess.run([
                    str(conan_exe), "remote", "add", remote_name, remote_url
                ], check=True, cwd=self.project_root)
                logger.info(f"✅ Added GitHub Packages remote: {remote_name}")
            except subprocess.CalledProcessError as e:
                if "already exists" in str(e):
                    logger.info(f"ℹ️ Remote {remote_name} already exists, continuing...")
                else:
                    raise
            
            # Authenticate with GitHub Packages (Conan 2.x syntax)
            subprocess.run([
                str(conan_exe), "remote", "login", remote_name, 
                f"--username={self.github_owner}", f"--password={github_token}"
            ], check=True, cwd=self.project_root)
            
            logger.info(f"✅ Authenticated with GitHub Packages remote: {remote_name}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to setup GitHub Packages remote: {e}")
            raise
    
    def _get_conan_executable(self) -> Path:
        """Get Conan executable path"""
        # Try to find Conan in virtual environment first
        if self.platform == "windows":
            conan_exe = self.venv_dir / "Scripts" / "conan.exe"
        else:
            conan_exe = self.venv_dir / "bin" / "conan"
        
        if conan_exe.exists():
            return conan_exe
        
        # Fall back to system Conan
        return Path("conan")
    
    def _create_github_actions_workflow(self):
        """Create GitHub Actions workflow for Conan 2.x with GitHub Packages"""
        logger.info("🔄 Creating GitHub Actions workflow...")
        
        workflows_dir = self.project_root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_file = workflows_dir / "conan-github-packages.yml"
        workflow_content = f"""name: Conan Package with GitHub Packages

on:
  push:
    branches: [ main, develop ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build-and-publish:
    runs-on: ${{{{ matrix.os }}}}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        include:
          - os: ubuntu-latest
            conan_profile: linux-gcc11
          - os: windows-latest
            conan_profile: windows-msvc2022
          - os: macos-latest
            conan_profile: macos-clang14

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Full history for version detection

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install Conan 2.x
      run: |
        pip install conan>=2.0.0

    - name: Configure Conan
      run: |
        conan config init
        conan config set general.default_profile={{{{ matrix.conan_profile }}}}

    - name: Add GitHub Packages Remote
      run: |
        conan remote add github-packages https://maven.pkg.github.com/{self.github_owner}/{self.github_repo}
        conan remote login github-packages --username=${{{{ github.actor }}}} --password=${{{{ secrets.GITHUB_TOKEN }}}}

    - name: Create Conan Profile
      run: |
        conan profile detect --force
        conan profile show default

    - name: Install Dependencies
      run: |
        conan install . --profile={{{{ matrix.conan_profile }}}} --build=missing

    - name: Build Package
      run: |
        conan create . --profile={{{{ matrix.conan_profile }}}} --build=missing

    - name: Upload to GitHub Packages
      if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop' || startsWith(github.ref, 'refs/tags/'))
      run: |
        conan upload "*" --remote=github-packages --all --confirm

    - name: Run Tests
      run: |
        python scripts/test-openssl-tools-conan.py --test-type=all --profile={{{{ matrix.conan_profile }}}}

    - name: Generate SBOM
      run: |
        conan sbom . --format=json --output=sbom.json

    - name: Upload SBOM
      uses: actions/upload-artifact@v3
      with:
        name: sbom-${{{{ matrix.os }}}}
        path: sbom.json
"""
        
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
        
        logger.info(f"✅ Created GitHub Actions workflow: {workflow_file}")
    
    def _create_dev_scripts(self):
        """Create development scripts for GitHub Packages"""
        logger.info("📝 Creating development scripts...")
        
        scripts_dir = self.project_root / "scripts" / "conan"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # Create GitHub Packages upload script
        upload_script = scripts_dir / "upload-to-github-packages.py"
        upload_script_content = f'''#!/usr/bin/env python3
"""
Upload OpenSSL Tools to GitHub Packages
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Upload to GitHub Packages")
    parser.add_argument("--profile", "-p", required=True, help="Conan profile to use")
    parser.add_argument("--version", "-v", help="Package version")
    parser.add_argument("--dry-run", action="store_true", help="Dry run without uploading")
    
    args = parser.parse_args()
    
    # Get GitHub token
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    # Build package
    print(f"🔨 Building package with profile: {{args.profile}}")
    subprocess.run(["conan", "create", ".", f"--profile={{args.profile}}", "--build=missing"], check=True)
    
    if not args.dry_run:
        print("📤 Uploading to GitHub Packages...")
        subprocess.run([
            "conan", "upload", "*", "--remote=github-packages", "--all", "--confirm"
        ], check=True)
        print("✅ Upload complete!")
    else:
        print("🔍 Dry run - would upload to GitHub Packages")

if __name__ == "__main__":
    main()
'''
        
        with open(upload_script, 'w') as f:
            f.write(upload_script_content)
        
        # Make executable on Unix
        if self.platform != "windows":
            os.chmod(upload_script, 0o755)
        
        # Create install from GitHub Packages script
        install_script = scripts_dir / "install-from-github-packages.py"
        install_script_content = f'''#!/usr/bin/env python3
"""
Install OpenSSL Tools from GitHub Packages
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Install from GitHub Packages")
    parser.add_argument("--profile", "-p", required=True, help="Conan profile to use")
    parser.add_argument("--version", "-v", default="latest", help="Package version")
    
    args = parser.parse_args()
    
    # Get GitHub token
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    # Add remote if not exists
    print("🔗 Setting up GitHub Packages remote...")
    try:
        subprocess.run([
            "conan", "remote", "add", "github-packages", 
            f"https://maven.pkg.github.com/{self.github_owner}/{self.github_repo}"
        ], check=True)
    except subprocess.CalledProcessError:
        print("ℹ️ Remote already exists")
    
    # Authenticate
    print("🔐 Authenticating with GitHub Packages...")
    subprocess.run([
        "conan", "remote", "login", "github-packages",
        f"--username={self.github_owner}", f"--password={github_token}"
    ], check=True)
    
    # Install package
    print(f"📦 Installing openssl-tools/{{args.version}} from GitHub Packages...")
    subprocess.run([
        "conan", "install", f"openssl-tools/{{args.version}}@", 
        f"--profile={{args.profile}}", "--build=missing"
    ], check=True)
    
    print("✅ Installation complete!")

if __name__ == "__main__":
    main()
'''
        
        with open(install_script, 'w') as f:
            f.write(install_script_content)
        
        # Make executable on Unix
        if self.platform != "windows":
            os.chmod(install_script, 0o755)
        
        logger.info("✅ Created development scripts")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Set up GitHub Packages with Conan 2.x")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    parser.add_argument("--github-owner", required=True,
                       help="GitHub organization or username")
    parser.add_argument("--github-repo", required=True,
                       help="GitHub repository name")
    parser.add_argument("--token", 
                       help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set up GitHub Packages
    setup = GitHubPackagesConanSetup(args.project_root, args.github_owner, args.github_repo)
    success = setup.setup_github_packages(github_token=args.token)
    
    if success:
        print("\n🎉 GitHub Packages setup complete!")
        print("\n📋 Next steps:")
        print("1. Set GITHUB_TOKEN environment variable:")
        print("   export GITHUB_TOKEN=your_token_here")
        print("2. Build and upload package:")
        print("   python scripts/conan/upload-to-github-packages.py --profile=linux-gcc11")
        print("3. Install from GitHub Packages:")
        print("   python scripts/conan/install-from-github-packages.py --profile=linux-gcc11")
        print("\n🔄 GitHub Actions workflow created for automated builds!")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()