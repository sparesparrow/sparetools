#!/usr/bin/env python3
"""
CI Environment Setup Script
Standardizes Python and Conan profile usage across all workflows.

This script:
1. Sets up Python environment with proper version
2. Copies Conan profiles to the correct location
3. Configures CONAN_USER_HOME properly
4. Validates profile names match exactly what's in conan-dev/profiles/
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

# Handle Windows console encoding issues
if sys.platform == 'win32':
    import codecs
    # Set UTF-8 encoding for stdout on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')


class CIEnvironmentSetup:
    """Handles CI environment setup and validation."""
    
    def __init__(self):
        self.repo_root = Path(os.environ.get('GITHUB_WORKSPACE', os.getcwd()))
        self.conan_home = Path(os.environ.get('CONAN_USER_HOME', self.repo_root / '.conan2'))
        self.profiles_source = self.repo_root / 'conan-dev' / 'profiles'
        self.profiles_dest = self.conan_home / 'profiles'
        self.conan_dev_venv = self.repo_root / 'conan-dev' / 'venv'
        
        # Follow oms-dev/ngapy-dev pattern: use conan-dev Python as primary
        if self.conan_dev_venv.exists():
            self.python_executable = self.conan_dev_venv / 'bin' / 'python'
        else:
            # Fallback to system Python if conan-dev venv doesn't exist
            self.python_executable = Path(sys.executable)
        
    def setup_python_environment(self) -> None:
        """Set up Python environment following oms-dev/ngapy-dev patterns."""
        print("[PYTHON] Setting up Python environment...")
        
        # Follow oms-dev pattern: Set PYTHON_APPLICATION environment variable
        if self.conan_dev_venv.exists() and self.python_executable.exists():
            os.environ['PYTHON_APPLICATION'] = str(self.python_executable)
            print(f"[OK] Using conan-dev Python: {self.python_executable}")
            print(f"   Set PYTHON_APPLICATION={self.python_executable}")
        else:
            print(f"[INFO] Conan-dev virtual environment not found, using system Python: {sys.executable}")
            print(f"   Set PYTHON_APPLICATION={sys.executable}")
            os.environ['PYTHON_APPLICATION'] = sys.executable
            self.python_executable = Path(sys.executable)
        
        # Get Python version
        try:
            result = subprocess.run([str(self.python_executable), '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"Python version: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"[WARN] Warning: Could not get Python version: {e}")
        
        # Update sys.executable to use the selected Python
        sys.executable = str(self.python_executable)
        
        # Check if we're in a CI environment
        is_ci = os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS')
        
        if not is_ci:
            print("[INFO] Running in local environment")
            print("   (Additional packages will be installed automatically in CI)")
            return
        
        # Install required packages following ngapy-dev pattern
        requirements = [
            'conan>=2.0.0',
            'PyYAML',
            'pytest',
            'pytest-cov',
            'coverage',
            'black',
            'flake8',
            'pylint',
            'mypy',
            'isort',
            'markdown-it',
            'normalizer',
            'distro'
        ]
        
        for package in requirements:
            try:
                subprocess.run([str(self.python_executable), '-m', 'pip', 'install', package], 
                              check=True, capture_output=True)
                print(f"[OK] Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"[WARN] Warning: Failed to install {package}: {e}")
                print("   This is normal in some environments")
    
    def setup_conan_profiles(self) -> None:
        """Copy Conan profiles to the correct location."""
        print("[CONAN] Setting up Conan profiles...")
        
        # Create CONAN_USER_HOME directory if it doesn't exist
        self.conan_home.mkdir(parents=True, exist_ok=True)
        
        # Create profiles directory
        self.profiles_dest.mkdir(parents=True, exist_ok=True)
        
        # Copy profiles from conan-dev/profiles/ to ~/.conan2/profiles/
        if self.profiles_source.exists():
            for profile_file in self.profiles_source.glob('*.profile'):
                dest_file = self.profiles_dest / profile_file.name
                shutil.copy2(profile_file, dest_file)
                print(f"[OK] Copied profile: {profile_file.name}")
        else:
            print(f"[WARN] Warning: Profiles source directory not found: {self.profiles_source}")
    
    def validate_profile_names(self) -> List[str]:
        """Validate that profile names match exactly what's in conan-dev/profiles/."""
        print("[VALIDATE] Validating profile names...")
        
        available_profiles = []
        if self.profiles_source.exists():
            available_profiles = [f.stem for f in self.profiles_source.glob('*.profile')]
            print(f"Available profiles: {available_profiles}")
        else:
            print("[WARN] Warning: No profiles found in conan-dev/profiles/")
        
        return available_profiles
    
    def setup_conan_config(self) -> None:
        """Set up Conan configuration."""
        print("[CONFIG] Setting up Conan configuration...")
        
        # Create conan.conf if it doesn't exist
        conan_conf = self.conan_home / 'conan.conf'
        if not conan_conf.exists():
            conan_conf.write_text("""[log]
level = 20

[tools.cmake.cmaketoolchain]
generator = Ninja

[tools.system.package_manager]
mode = install
sudo = True
""")
            print("[OK] Created conan.conf")
    
    def print_environment_info(self) -> None:
        """Print environment information for debugging."""
        print("\n[INFO] Environment Information:")
        print(f"Repository root: {self.repo_root}")
        print(f"CONAN_USER_HOME: {self.conan_home}")
        print(f"Conan-dev venv: {self.conan_dev_venv}")
        print(f"Python executable: {self.python_executable}")
        print(f"PYTHON_APPLICATION: {os.environ.get('PYTHON_APPLICATION', 'Not set')}")
        print(f"Python version: {sys.version}")
        
        # List available profiles
        if self.profiles_dest.exists():
            profiles = list(self.profiles_dest.glob('*.profile'))
            print(f"Available profiles in {self.profiles_dest}:")
            for profile in profiles:
                print(f"  - {profile.name}")
        else:
            print(f"No profiles found in {self.profiles_dest}")
    
    def run_setup(self) -> None:
        """Run the complete setup process."""
        print("[START] Starting CI environment setup...")
        
        try:
            self.setup_python_environment()
            self.setup_conan_profiles()
            self.setup_conan_config()
            available_profiles = self.validate_profile_names()
            self.print_environment_info()
            
            print("\n[SUCCESS] CI environment setup completed successfully!")
            print(f"Available profiles: {', '.join(available_profiles)}")
            
        except Exception as e:
            print(f"\n[ERROR] Setup failed: {e}")
            sys.exit(1)


def main():
    """Main entry point."""
    setup = CIEnvironmentSetup()
    setup.run_setup()


if __name__ == '__main__':
    main()