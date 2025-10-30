#!/usr/bin/env python3
"""
Upload Conan package to GitHub as a release asset
Since GitHub Packages doesn't support Conan directly, we'll create a GitHub release
with the Conan package as an asset.
"""

import argparse
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
import json
import requests
from datetime import datetime

def get_package_info():
    """Get package information from Conan cache"""
    try:
        # Get package info from Conan
        result = subprocess.run([
            "conan", "list", "*", "--format=json"
        ], capture_output=True, text=True, check=True)
        
        data = json.loads(result.stdout)
        
        # Handle Conan 2.x JSON structure
        if "Local Cache" in data:
            packages = data["Local Cache"]
        else:
            packages = data
            
        if not packages:
            print("❌ No packages found in Conan cache")
            return None
            
        # Find openssl-tools package
        for package_name, package_info in packages.items():
            if package_name.startswith("openssl-tools/"):
                # Extract version from package name
                version = package_name.split("/")[1]
                return {
                    "name": "openssl-tools",
                    "version": version,
                    "package_folder": package_info.get("package_folder", ""),
                    "full_name": package_name
                }
                
        print("❌ openssl-tools package not found in cache")
        return None
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get package info: {e}")
        return None

def create_package_archive(package_info, output_dir):
    """Create a zip archive of the Conan package"""
    try:
        # Get package folder path
        package_folder = Path(package_info["package_folder"])
        
        # Create zip file
        zip_path = output_dir / f"openssl-tools-{package_info['version']}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in package_folder.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(package_folder)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Created package archive: {zip_path}")
        return zip_path
        
    except Exception as e:
        print(f"❌ Failed to create package archive: {e}")
        return None

def create_github_release(owner, repo, version, token, zip_path):
    """Create a GitHub release with the package as an asset"""
    try:
        # GitHub API URL
        url = f"https://api.github.com/repos/{owner}/{repo}/releases"
        
        # Release data
        release_data = {
            "tag_name": f"v{version}",
            "name": f"OpenSSL Tools {version}",
            "body": f"Conan package for OpenSSL Tools {version}\n\n"
                   f"## Installation\n"
                   f"```bash\n"
                   f"conan install openssl-tools/{version}@\n"
                   f"```\n\n"
                   f"## Package Contents\n"
                   f"- Python tools for OpenSSL development\n"
                   f"- Review and release management tools\n"
                   f"- Statistics and analysis tools\n"
                   f"- GitHub integration tools\n\n"
                   f"Generated on: {datetime.now().isoformat()}",
            "draft": False,
            "prerelease": version.endswith(('dev', 'alpha', 'beta', 'rc'))
        }
        
        # Headers
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Create release
        print(f"🚀 Creating GitHub release: {release_data['tag_name']}")
        response = requests.post(url, json=release_data, headers=headers)
        
        if response.status_code == 201:
            release_info = response.json()
            print(f"✅ Created release: {release_info['html_url']}")
            
            # Upload package as asset
            upload_url = release_info['upload_url'].replace('{?name,label}', '')
            
            with open(zip_path, 'rb') as f:
                asset_data = f.read()
            
            asset_headers = {
                "Authorization": f"token {token}",
                "Content-Type": "application/zip"
            }
            
            asset_response = requests.post(
                f"{upload_url}?name={zip_path.name}",
                data=asset_data,
                headers=asset_headers
            )
            
            if asset_response.status_code == 201:
                print(f"✅ Uploaded package asset: {zip_path.name}")
                return True
            else:
                print(f"❌ Failed to upload asset: {asset_response.status_code} - {asset_response.text}")
                return False
                
        else:
            print(f"❌ Failed to create release: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create GitHub release: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Upload Conan package to GitHub")
    parser.add_argument("--github-owner", required=True, help="GitHub owner/username")
    parser.add_argument("--github-repo", required=True, help="GitHub repository name")
    parser.add_argument("--github-token", help="GitHub Personal Access Token")
    parser.add_argument("--version", help="Package version (auto-detected if not provided)")
    
    args = parser.parse_args()
    
    print("🚀 Uploading Conan package to GitHub...")
    
    # Get package info
    package_info = get_package_info()
    if not package_info:
        return 1
    
    version = args.version or package_info.get("version", "unknown")
    print(f"📦 Package: {package_info['name']} {version}")
    
    # Get GitHub token
    if not args.github_token:
        import getpass
        args.github_token = getpass.getpass("Enter GitHub Personal Access Token: ")
    
    if not args.github_token:
        print("❌ GitHub token is required")
        return 1
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create package archive
        zip_path = create_package_archive(package_info, temp_path)
        if not zip_path:
            return 1
        
        # Create GitHub release
        success = create_github_release(
            args.github_owner, 
            args.github_repo, 
            version, 
            args.github_token, 
            zip_path
        )
        
        if success:
            print("🎉 Package uploaded successfully!")
            print(f"📦 Release: https://github.com/{args.github_owner}/{args.github_repo}/releases")
            return 0
        else:
            return 1

if __name__ == "__main__":
    sys.exit(main())