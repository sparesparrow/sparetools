#!/usr/bin/env python3
"""
Flipper Zero Repository Cloner
Clones the Flipper Zero DIY repository for WiFi sensing integration
"""

import os
import subprocess
import json
import time
from pathlib import Path
import argparse

class FlipperZeroCloner:
    def __init__(self, output_dir="research/repositories"):
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.repo_name = "flipper_zero"
        self.repo_url = "https://github.com/GthiN89/FuckingCheapFlipperZero-DIY-Flipper-zero-The-real-on"
        self.repo_path = (self.output_dir / self.repo_name).resolve()

        # Load existing clone log
        self.load_clone_log()

    def load_clone_log(self):
        """Load log of Flipper Zero clone status"""
        log_file = self.output_dir / "flipper_clone_log.json"
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    self.clone_data = json.load(f)
            except json.JSONDecodeError:
                self.clone_data = {}
        else:
            self.clone_data = {}

    def save_clone_log(self):
        """Save log of Flipper Zero clone status"""
        log_file = self.output_dir / "flipper_clone_log.json"
        self.clone_data['last_updated'] = time.time()
        with open(log_file, 'w') as f:
            json.dump(self.clone_data, f, indent=2)

    def clone_repository(self):
        """Clone the Flipper Zero repository with branch analysis"""
        print("🔄 Starting Flipper Zero repository clone...")
        print(f"📂 Target directory: {self.repo_path}")
        print(f"🔗 Repository URL: {self.repo_url}")
        print("=" * 60)

        # Check if already cloned
        if self.repo_path.exists() and (self.repo_path / '.git').exists():
            print("⏭️  Repository already exists, checking for updates...")
            return self.update_existing_repository()

        try:
            # Clone the repository
            print("📥 Cloning Flipper Zero repository...")
            cmd = ['git', 'clone', self.repo_url, str(self.repo_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                print("✅ Repository cloned successfully")
                self.clone_data['status'] = 'cloned'
                self.clone_data['clone_time'] = time.time()
                self.analyze_branches()
                return True
            else:
                print(f"❌ Clone failed: {result.stderr}")
                self.clone_data['status'] = 'failed'
                self.clone_data['error'] = result.stderr
                return False

        except subprocess.TimeoutExpired:
            print("⏰ Clone timeout - repository may be large")
            self.clone_data['status'] = 'timeout'
            return False
        except Exception as e:
            print(f"❌ Clone error: {str(e)}")
            self.clone_data['status'] = 'error'
            self.clone_data['error'] = str(e)
            return False

    def update_existing_repository(self):
        """Update existing repository and analyze branches"""
        try:
            print("🔄 Updating existing repository...")

            # Ensure we're in the correct directory
            original_cwd = os.getcwd()
            os.chdir(self.repo_path)

            try:
                # Fetch latest changes
                subprocess.run(['git', 'fetch', '--all'], check=True, capture_output=True)

                # Get current branch
                result = subprocess.run(['git', 'branch', '--show-current'],
                                      capture_output=True, text=True, check=True)
                current_branch = result.stdout.strip()

                print(f"📍 Current branch: {current_branch}")

                self.analyze_branches()
                self.clone_data['status'] = 'updated'
                self.clone_data['last_update'] = time.time()
                return True
            finally:
                os.chdir(original_cwd)

        except Exception as e:
            print(f"❌ Update failed: {str(e)}")
            return False

    def analyze_branches(self):
        """Analyze available branches in the repository"""
        try:
            # Ensure we're in the correct directory
            original_cwd = os.getcwd()
            os.chdir(self.repo_path)

            try:
                # Get all branches
                result = subprocess.run(['git', 'branch', '-a'],
                                      capture_output=True, text=True, check=True)
                branches = result.stdout.strip().split('\n')

                # Parse branches
                local_branches = []
                remote_branches = []
                current_branch = None

                for branch in branches:
                    branch = branch.strip()
                    if branch.startswith('* '):
                        branch = branch[2:]
                        current_branch = branch
                    if branch.startswith('remotes/origin/'):
                        remote_branches.append(branch.replace('remotes/origin/', ''))
                    elif branch and not branch.startswith('remotes/'):
                        local_branches.append(branch)

                print("📊 Branch Analysis:")
                print(f"  Current branch: {current_branch}")
                print(f"  Local branches: {', '.join(local_branches)}")
                print(f"  Remote branches: {', '.join(remote_branches)}")

                # Check for specific branches mentioned in requirements
                target_branches = ['main', 'master', 'ext_first_pinout']
                available_targets = []

                for target in target_branches:
                    if target in local_branches or target in remote_branches:
                        available_targets.append(target)

                if available_targets:
                    print(f"✅ Target branches available: {', '.join(available_targets)}")
                else:
                    print("⚠️  No target branches found")

                # Store branch information
                self.clone_data['branches'] = {
                    'current': current_branch,
                    'local': local_branches,
                    'remote': remote_branches,
                    'available_targets': available_targets
                }

                # Analyze repository structure
                self.analyze_structure()
            finally:
                os.chdir(original_cwd)

        except Exception as e:
            print(f"❌ Branch analysis failed: {str(e)}")

    def analyze_structure(self):
        """Analyze the repository structure and key files"""
        try:
            structure = {}

            # Check for common Flipper Zero files/directories
            key_paths = [
                'README.md',
                'firmware',
                'hardware',
                'software',
                'docs',
                'src',
                'Arduino',
                'ESP32',
                'PCB',
                'schematics',
                '.git'
            ]

            for path in key_paths:
                full_path = self.repo_path / path
                if full_path.exists():
                    if full_path.is_dir():
                        # Count items in directory
                        try:
                            item_count = len(list(full_path.iterdir()))
                            structure[path] = f"directory ({item_count} items)"
                        except:
                            structure[path] = "directory"
                    else:
                        # Get file size
                        try:
                            size = full_path.stat().st_size
                            structure[path] = f"file ({size} bytes)"
                        except:
                            structure[path] = "file"
                else:
                    structure[path] = "not found"

            print("🏗️  Repository Structure:")
            for path, status in structure.items():
                print(f"  {path}: {status}")

            self.clone_data['structure'] = structure

            # Check for build files
            build_files = ['Makefile', 'CMakeLists.txt', 'platformio.ini', 'setup.py']
            found_build = []

            for build_file in build_files:
                if (self.repo_path / build_file).exists():
                    found_build.append(build_file)

            if found_build:
                print(f"🔨 Build files found: {', '.join(found_build)}")
                self.clone_data['build_files'] = found_build
            else:
                print("⚠️  No standard build files found")

        except Exception as e:
            print(f"❌ Structure analysis failed: {str(e)}")

    def checkout_branch(self, branch_name):
        """Checkout a specific branch"""
        try:
            # Ensure we're in the correct directory
            original_cwd = os.getcwd()
            os.chdir(self.repo_path)

            try:
                # Check if branch exists
                result = subprocess.run(['git', 'branch', '-a'],
                                      capture_output=True, text=True, check=True)
                branches = result.stdout

                target_branch = f"origin/{branch_name}" if f"remotes/origin/{branch_name}" in branches else branch_name

                print(f"🔄 Checking out branch: {branch_name}")
                subprocess.run(['git', 'checkout', target_branch], check=True, capture_output=True)

                # Update analysis
                self.analyze_branches()

                return True
            finally:
                os.chdir(original_cwd)

        except Exception as e:
            print(f"❌ Branch checkout failed: {str(e)}")
            return False

    def create_summary(self):
        """Create a summary of the Flipper Zero repository"""
        summary_file = self.output_dir / "flipper_zero_summary.md"

        with open(summary_file, 'w') as f:
            f.write("# Flipper Zero Repository Summary\n\n")
            f.write(f"**Repository URL:** {self.repo_url}\n\n")
            f.write(f"**Local Path:** {self.repo_path}\n\n")
            f.write(f"**Clone Status:** {self.clone_data.get('status', 'unknown')}\n\n")
            f.write(f"**Last Updated:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.clone_data.get('last_updated', time.time())))}\n\n")

            if 'branches' in self.clone_data:
                f.write("## Branch Information\n\n")
                branches = self.clone_data['branches']
                f.write(f"- **Current Branch:** {branches.get('current', 'unknown')}\n")
                f.write(f"- **Local Branches:** {', '.join(branches.get('local', []))}\n")
                f.write(f"- **Remote Branches:** {', '.join(branches.get('remote', []))}\n")
                f.write(f"- **Target Branches Available:** {', '.join(branches.get('available_targets', []))}\n\n")

            if 'structure' in self.clone_data:
                f.write("## Repository Structure\n\n")
                for path, status in self.clone_data['structure'].items():
                    f.write(f"- **{path}:** {status}\n")
                f.write("\n")

            if 'build_files' in self.clone_data:
                f.write("## Build Files\n\n")
                for build_file in self.clone_data['build_files']:
                    f.write(f"- {build_file}\n")
                f.write("\n")

            f.write("## Integration Notes\n\n")
            f.write("This Flipper Zero repository has been cloned for integration with the WiFi sensing workspace.\n\n")
            f.write("### Next Steps:\n")
            f.write("1. Analyze branch differences (main/master vs ext_first_pinout)\n")
            f.write("2. Set up build environment for firmware compilation\n")
            f.write("3. Integrate with existing WiFi sensing tools\n")
            f.write("4. Test hardware connectivity and CSI data collection\n\n")

        print(f"📝 Summary created: {summary_file}")

def main():
    parser = argparse.ArgumentParser(description='Clone Flipper Zero Repository for WiFi Sensing Integration')
    parser.add_argument('-o', '--output', default='research/repositories',
                       help='Output directory for cloned repository')
    parser.add_argument('-b', '--branch', help='Specific branch to checkout after cloning')
    parser.add_argument('--force', action='store_true',
                       help='Force re-clone even if repository exists')

    args = parser.parse_args()

    cloner = FlipperZeroCloner(args.output)

    if args.force and cloner.repo_path.exists():
        print("🗑️  Removing existing repository...")
        import shutil
        shutil.rmtree(cloner.repo_path)

    success = cloner.clone_repository()

    if success and args.branch:
        cloner.checkout_branch(args.branch)

    cloner.save_clone_log()
    cloner.create_summary()

    if success:
        print("\n✅ Flipper Zero repository setup complete!")
        print("📂 Location:", cloner.repo_path)
        if 'branches' in cloner.clone_data:
            branches = cloner.clone_data['branches']
            if branches.get('available_targets'):
                print("🎯 Available target branches:", ', '.join(branches['available_targets']))
    else:
        print("\n❌ Flipper Zero repository setup failed!")
        exit(1)

if __name__ == "__main__":
    main()