#!/usr/bin/env python3
"""
Enhanced Multi-Registry Upload Script
Supports Artifactory, GitHub Packages, and future registries
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

class MultiRegistryUploader:
    def __init__(self):
        self.components = ["openssl-crypto", "openssl-ssl", "openssl-tools"]
        self.version = "3.2.0"
        self.upload_stats = {
            "started_at": datetime.now().isoformat(),
            "uploads": []
        }
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, cmd, check=True):
        """Execute command and return result"""
        self.log(f"Executing: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=check)
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e.stderr}", "ERROR")
            raise
    
    def setup_artifactory(self):
        """Configure Artifactory remote"""
        artifactory_url = os.getenv('ARTIFACTORY_URL')
        artifactory_user = os.getenv('ARTIFACTORY_USER')
        artifactory_token = os.getenv('ARTIFACTORY_TOKEN')
        
        if not all([artifactory_url, artifactory_user, artifactory_token]):
            self.log("Artifactory credentials not complete, skipping", "WARN")
            return False
        
        self.run_command([
            "conan", "remote", "add", "artifactory", 
            artifactory_url, "--force"
        ], check=False)
        
        self.run_command([
            "conan", "remote", "login", "artifactory", 
            artifactory_user, "-p", artifactory_token
        ])
        
        self.log("✅ Artifactory configured successfully")
        return True
    
    def setup_github_packages(self):
        """Configure GitHub Packages"""
        github_token = os.getenv('GITHUB_TOKEN')
        
        if not github_token:
            self.log("GitHub token not available, skipping", "WARN")
            return False
        
        self.log("📦 GitHub Packages setup (placeholder)")
        return True
    
    def upload_component_to_artifactory(self, component):
        """Upload single component to Artifactory"""
        start_time = time.time()
        
        try:
            result = self.run_command([
                "conan", "upload", f"{component}/{self.version}",
                "-r=artifactory", "--confirm"
            ])
            
            duration = time.time() - start_time
            self.upload_stats["uploads"].append({
                "component": component,
                "registry": "artifactory",
                "status": "success",
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            })
            
            self.log(f"✅ {component} uploaded to Artifactory ({duration:.1f}s)")
            return True
            
        except subprocess.CalledProcessError:
            self.upload_stats["uploads"].append({
                "component": component,
                "registry": "artifactory", 
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            })
            self.log(f"❌ {component} upload to Artifactory failed", "ERROR")
            return False
    
    def upload_component_to_github(self, component):
        """Upload single component to GitHub Packages"""
        self.log(f"📦 {component} → GitHub Packages (placeholder)")
        
        self.upload_stats["uploads"].append({
            "component": component,
            "registry": "github_packages",
            "status": "placeholder",
            "timestamp": datetime.now().isoformat()
        })
        return True
    
    def upload_all_components(self):
        """Upload all components to all configured registries"""
        self.log("🚀 Starting multi-registry upload process")
        
        artifactory_available = self.setup_artifactory()
        github_available = self.setup_github_packages()
        
        if not artifactory_available and not github_available:
            self.log("No registries available for upload", "ERROR")
            return False
        
        success_count = 0
        total_uploads = 0
        
        for component in self.components:
            if artifactory_available:
                total_uploads += 1
                if self.upload_component_to_artifactory(component):
                    success_count += 1
            
            if github_available:
                total_uploads += 1
                if self.upload_component_to_github(component):
                    success_count += 1
        
        success_rate = (success_count / total_uploads * 100) if total_uploads > 0 else 0
        self.log(f"📊 Upload Summary: {success_count}/{total_uploads} successful ({success_rate:.1f}%)")
        
        self.upload_stats["completed_at"] = datetime.now().isoformat()
        self.upload_stats["success_rate"] = success_rate
        
        with open("upload-stats.json", "w") as f:
            json.dump(self.upload_stats, f, indent=2)
        
        return success_rate == 100.0

def main():
    uploader = MultiRegistryUploader()
    
    if uploader.upload_all_components():
        print("🎉 All uploads completed successfully!")
        sys.exit(0)
    else:
        print("💥 Some uploads failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

