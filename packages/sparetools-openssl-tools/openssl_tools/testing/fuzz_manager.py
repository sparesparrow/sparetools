#!/usr/bin/env python3
"""
Fuzz Corpora Manager
Manages the OpenSSL fuzz corpora Conan package.
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional


class FuzzCorporaManager:
    """Manages fuzz corpora Conan package operations."""
    
    def __init__(self, conan_home: Optional[Path] = None):
        self.conan_home = conan_home or Path(os.environ.get('CONAN_USER_HOME', Path.home() / '.conan2'))
        self.recipe_path = Path(__file__).parent.parent.parent / 'conan-dev' / 'recipes' / 'fuzz-corpora'
        
    def build_package(self, profile: str = "default", build_type: str = "Release") -> bool:
        """Build the fuzz corpora package."""
        print(f"[BUILD] Building fuzz-corpora package with profile: {profile}")
        
        try:
            # Change to recipe directory
            os.chdir(self.recipe_path)
            
            # Build the package
            cmd = [
                "conan", "create", ".",
                f"--profile={profile}",
                f"--build=missing",
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"[OK] Package built successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Build failed: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return False
    
    def upload_package(self, remote: str = "openssl") -> bool:
        """Upload the fuzz corpora package to remote."""
        print(f"[UPLOAD] Uploading fuzz-corpora package to remote: {remote}")
        
        try:
            cmd = [
                "conan", "upload", "openssl-fuzz-corpora/*",
                f"--remote={remote}",
                "--confirm",
                "--all"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"[OK] Package uploaded successfully to {remote}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Upload failed: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return False
    
    def install_package(self, profile: str = "default", build_type: str = "Release") -> bool:
        """Install the fuzz corpora package."""
        print(f"[INSTALL] Installing fuzz-corpora package with profile: {profile}")
        
        try:
            # Create a temporary conanfile.txt
            conanfile_content = f"""[requires]
openssl-fuzz-corpora/1.0.0

[generators]
CMakeDeps
CMakeToolchain

[options]
openssl-fuzz-corpora:include_metadata=True
"""
            
            temp_dir = Path.cwd() / "temp_fuzz_corpora"
            temp_dir.mkdir(exist_ok=True)
            
            conanfile_path = temp_dir / "conanfile.txt"
            conanfile_path.write_text(conanfile_content)
            
            # Install the package
            cmd = [
                "conan", "install", str(conanfile_path),
                f"--profile={profile}",
                f"--build=missing",
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Get the corpora path
            corpora_path = self._get_corpora_path()
            if corpora_path and corpora_path.exists():
                print(f"[OK] Package installed successfully")
                print(f"[INFO] Corpora data available at: {corpora_path}")
                return True
            else:
                print(f"[ERROR] Corpora data not found after installation")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Installation failed: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            return False
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            return False
        finally:
            # Clean up temporary directory
            if 'temp_dir' in locals() and temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _get_corpora_path(self) -> Optional[Path]:
        """Get the path to the installed corpora data."""
        try:
            # Query for the package path
            cmd = ["conan", "list", "openssl-fuzz-corpora/1.0.0", "--format=json"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse the JSON output to find the package path
            import json
            data = json.loads(result.stdout)
            
            if 'local_cache' in data and data['local_cache']:
                for item in data['local_cache']:
                    if 'path' in item:
                        package_path = Path(item['path'])
                        corpora_path = package_path / 'corpora'
                        if corpora_path.exists():
                            return corpora_path
            
            return None
            
        except Exception as e:
            print(f"[WARN] Could not determine corpora path: {e}")
            return None
    
    def list_available_profiles(self) -> List[str]:
        """List available Conan profiles."""
        try:
            profiles_dir = self.conan_home / 'profiles'
            if profiles_dir.exists():
                profiles = [f.stem for f in profiles_dir.glob('*.profile')]
                return profiles
            return []
        except Exception as e:
            print(f"[WARN] Could not list profiles: {e}")
            return []
    
    def setup_corpora_for_fuzz_tests(self, target_dir: Path) -> bool:
        """Set up corpora data for fuzz tests in the target directory."""
        print(f"[SETUP] Setting up corpora data in: {target_dir}")
        
        try:
            # Install the package first
            if not self.install_package():
                return False
            
            # Get the corpora path
            corpora_path = self._get_corpora_path()
            if not corpora_path or not corpora_path.exists():
                print(f"[ERROR] Corpora data not found")
                return False
            
            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy corpora data to target directory
            import shutil
            if (target_dir / "corpora").exists():
                shutil.rmtree(target_dir / "corpora")
            
            shutil.copytree(corpora_path, target_dir / "corpora")
            
            print(f"[OK] Corpora data set up successfully in {target_dir / 'corpora'}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to set up corpora data: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Manage OpenSSL fuzz corpora Conan package")
    parser.add_argument("--profile", default="default", help="Conan profile to use")
    parser.add_argument("--build-type", default="Release", help="Build type")
    parser.add_argument("--remote", default="openssl", help="Conan remote for upload")
    parser.add_argument("--conan-home", help="Conan home directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Build command
    subparsers.add_parser("build", help="Build the fuzz corpora package")
    
    # Upload command
    subparsers.add_parser("upload", help="Upload the fuzz corpora package")
    
    # Install command
    subparsers.add_parser("install", help="Install the fuzz corpora package")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up corpora data for fuzz tests")
    setup_parser.add_argument("--target-dir", required=True, help="Target directory for corpora data")
    
    # List profiles command
    subparsers.add_parser("list-profiles", help="List available Conan profiles")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize manager
    conan_home = Path(args.conan_home) if args.conan_home else None
    manager = FuzzCorporaManager(conan_home)
    
    # Execute command
    if args.command == "build":
        success = manager.build_package(args.profile, args.build_type)
    elif args.command == "upload":
        success = manager.upload_package(args.remote)
    elif args.command == "install":
        success = manager.install_package(args.profile, args.build_type)
    elif args.command == "setup":
        success = manager.setup_corpora_for_fuzz_tests(Path(args.target_dir))
    elif args.command == "list-profiles":
        profiles = manager.list_available_profiles()
        print(f"[INFO] Available profiles: {', '.join(profiles)}")
        success = True
    else:
        print(f"[ERROR] Unknown command: {args.command}")
        success = False
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())