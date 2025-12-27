#!/usr/bin/env python3
"""
WiFi Sensing Repository Cloner
Clones key GitHub repositories for CSI tools, WiFi sensing frameworks, and research code
"""

import os
import subprocess
import json
import time
from pathlib import Path
import argparse

class RepositoryCloner:
    def __init__(self, output_dir="research/repositories"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cloned_repos = set()
        self.failed_clones = []

        # Load existing clones
        self.load_clone_log()

    def load_clone_log(self):
        """Load log of previously cloned repositories"""
        log_file = self.output_dir / "clone_log.json"
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    data = json.load(f)
                    self.cloned_repos = set(data.get('cloned', []))
                    self.failed_clones = data.get('failed', [])
            except json.JSONDecodeError:
                pass

    def save_clone_log(self):
        """Save log of cloned repositories"""
        log_file = self.output_dir / "clone_log.json"
        data = {
            'cloned': list(self.cloned_repos),
            'failed': self.failed_clones,
            'last_updated': time.time()
        }
        with open(log_file, 'w') as f:
            json.dump(data, f, indent=2)

    def clone_repository(self, url, name, description="", use_https=False):
        """Clone a single repository"""
        repo_path = self.output_dir / name

        if repo_path.exists() and (repo_path / '.git').exists():
            print(f"⏭️  Already cloned: {name}")
            self.cloned_repos.add(name)
            return True

        try:
            print(f"📥 Cloning: {description or name}")

            # Try git clone first
            clone_url = url
            if use_https and 'github.com' in url:
                # Ensure HTTPS URL
                clone_url = url.replace('git@github.com:', 'https://github.com/')

            cmd = ['git', 'clone', '--depth', '1', clone_url, str(repo_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                self.cloned_repos.add(name)
                print(f"✅ Cloned: {name}")
                return True
            else:
                # Try downloading as zip archive
                print(f"⚠️  Git clone failed, trying zip download...")
                if self.download_as_zip(url, name):
                    self.cloned_repos.add(name)
                    print(f"✅ Downloaded as zip: {name}")
                    return True
                else:
                    error_msg = f"Failed to clone/download {name}: {result.stderr}"
                    print(f"❌ {error_msg}")
                    self.failed_clones.append({
                        'name': name,
                        'url': url,
                        'error': result.stderr,
                        'timestamp': time.time()
                    })
                    return False

        except subprocess.TimeoutExpired:
            error_msg = f"Timeout cloning {name}"
            print(f"⏰ {error_msg}")
            self.failed_clones.append({
                'name': name,
                'url': url,
                'error': 'timeout',
                'timestamp': time.time()
            })
            return False
        except Exception as e:
            error_msg = f"Error cloning {name}: {str(e)}"
            print(f"❌ {error_msg}")
            self.failed_clones.append({
                'name': name,
                'url': url,
                'error': str(e),
                'timestamp': time.time()
            })
            return False

    def download_as_zip(self, url, name):
        """Download repository as zip archive"""
        try:
            # Convert GitHub URL to zip download URL
            if 'github.com' in url:
                zip_url = url.replace('.git', '/archive/refs/heads/main.zip')
                if 'main' not in zip_url:
                    zip_url = url.replace('.git', '/archive/refs/heads/master.zip')
            else:
                return False

            zip_path = self.output_dir / f"{name}.zip"
            repo_path = self.output_dir / name

            # Download zip file
            import urllib.request
            with urllib.request.urlopen(zip_url) as response:
                with open(zip_path, 'wb') as f:
                    f.write(response.read())

            # Extract zip file
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract to a temporary directory first
                temp_dir = self.output_dir / f"{name}_temp"
                zip_ref.extractall(temp_dir)

                # Move contents to final location
                extracted_dirs = list(temp_dir.iterdir())
                if extracted_dirs:
                    source_dir = extracted_dirs[0]
                    if source_dir.is_dir():
                        # Rename to target name
                        target_dir = self.output_dir / name
                        source_dir.rename(target_dir)
                        temp_dir.rmdir()
                    else:
                        return False
                else:
                    return False

            # Clean up zip file
            zip_path.unlink()

            return True

        except Exception as e:
            print(f"❌ Zip download failed: {e}")
            return False

    def clone_repositories(self):
        """Clone all key repositories"""

        repositories = [
            # CSI Tools and Drivers
            {
                'url': 'https://github.com/dhalperi/linux-80211n-csitool.git',
                'name': 'linux-80211n-csitool',
                'description': 'Intel 5300 CSI extraction tool',
                'use_https': True
            },
            {
                'url': 'https://github.com/xieyaxiongfly/Atheros-CSI-Tool.git',
                'name': 'Atheros-CSI-Tool',
                'description': 'Atheros chipset CSI extraction tool',
                'use_https': True
            },
            {
                'url': 'https://github.com/seemoo-lab/nexmon_csi.git',
                'name': 'nexmon_csi',
                'description': 'Nexmon CSI extraction for Broadcom chipsets',
                'use_https': True
            },

            # WiFi Sensing Frameworks
            {
                'url': 'https://github.com/ucsdwcsng/WiFi-CSI-Sensing.git',
                'name': 'WiFi-CSI-Sensing',
                'description': 'Comprehensive WiFi CSI sensing toolkit'
            },
            {
                'url': 'https://github.com/ermongroup/Wifi_Activity_Recognition.git',
                'name': 'Wifi_Activity_Recognition',
                'description': 'WiFi-based activity recognition'
            },
            {
                'url': 'https://github.com/koutilya-pnvr/WiFi_Sensing.git',
                'name': 'WiFi_Sensing',
                'description': 'WiFi sensing research framework'
            },

            # Research Implementations
            {
                'url': 'https://github.com/geekfeiw/WiFi-Sensing.git',
                'name': 'WiFi-Sensing-geekfeiw',
                'description': 'WiFi sensing algorithms and implementations'
            },
            {
                'url': 'https://github.com/leewi9/WiFi-CSI-Sensing.git',
                'name': 'WiFi-CSI-Sensing-leewi9',
                'description': 'CSI-based sensing research code'
            },

            # Datasets and Benchmarks
            {
                'url': 'https://github.com/ermongroup/WiAR.git',
                'name': 'WiAR',
                'description': 'WiFi Activity Recognition dataset and code'
            },
            {
                'url': 'https://github.com/geekfeiw/WiSign.git',
                'name': 'WiSign',
                'description': 'WiFi sensing dataset collection'
            },

            # Advanced Applications
            {
                'url': 'https://github.com/mengxiuyu/WiKey.git',
                'name': 'WiKey',
                'description': 'Keystroke recognition using WiFi signals'
            },
            {
                'url': 'https://github.com/mengxiuyu/SignFi.git',
                'name': 'SignFi',
                'description': 'Sign language recognition with WiFi'
            },
            {
                'url': 'https://github.com/mengxiuyu/WiHear.git',
                'name': 'WiHear',
                'description': 'Speech recognition through walls'
            },

            # Tools and Utilities
            {
                'url': 'https://github.com/StevenHsuYL/WiFi-CSI-Tool.git',
                'name': 'WiFi-CSI-Tool',
                'description': 'WiFi CSI processing tools'
            },
            {
                'url': 'https://github.com/jonathanmuller/WiFi-CSI-Tool.git',
                'name': 'WiFi-CSI-Tool-jonathanmuller',
                'description': 'Alternative WiFi CSI processing toolkit'
            },

            # Machine Learning for CSI
            {
                'url': 'https://github.com/jianlincheng/CsiGAN.git',
                'name': 'CsiGAN',
                'description': 'GAN-based CSI data augmentation'
            },
            {
                'url': 'https://github.com/geekfeiw/CsiNet.git',
                'name': 'CsiNet',
                'description': 'Deep learning for CSI compression'
            },

            # Simulation and Testing
            {
                'url': 'https://github.com/lizonghang/wifi-sensing-simulation.git',
                'name': 'wifi-sensing-simulation',
                'description': 'WiFi sensing simulation framework'
            },
        ]

        successful_clones = 0
        total_repos = len(repositories)

        print(f"📦 Starting clone of {total_repos} repositories...")
        print("=" * 60)

        for repo in repositories:
            use_https = repo.get('use_https', True)  # Default to HTTPS
            if self.clone_repository(repo['url'], repo['name'], repo['description'], use_https):
                successful_clones += 1
            time.sleep(1)  # Be respectful to GitHub API

        # Save clone log
        self.save_clone_log()

        print(f"\n✅ Clone complete: {successful_clones}/{total_repos} repositories cloned successfully")

        # Create repository index
        self.create_repository_index(repositories)

    def create_repository_index(self, repositories):
        """Create an index file with all repositories"""
        index_file = self.output_dir / "repositories.md"

        with open(index_file, 'w') as f:
            f.write("# WiFi Sensing Research Repositories\n\n")
            f.write("Collection of GitHub repositories for WiFi sensing, CSI processing, and research.\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Repository Categories\n\n")

            categories = {
                'CSI Tools and Drivers': [
                    'linux-80211n-csitool', 'Atheros-CSI-Tool', 'nexmon_csi'
                ],
                'WiFi Sensing Frameworks': [
                    'WiFi-CSI-Sensing', 'Wifi_Activity_Recognition', 'WiFi_Sensing'
                ],
                'Research Implementations': [
                    'WiFi-Sensing-geekfeiw', 'WiFi-CSI-Sensing-leewi9'
                ],
                'Datasets and Benchmarks': [
                    'WiAR', 'WiSign'
                ],
                'Advanced Applications': [
                    'WiKey', 'SignFi', 'WiHear'
                ],
                'Tools and Utilities': [
                    'WiFi-CSI-Tool', 'WiFi-CSI-Tool-jonathanmuller'
                ],
                'Machine Learning for CSI': [
                    'CsiGAN', 'CsiNet'
                ],
                'Simulation and Testing': [
                    'wifi-sensing-simulation'
                ]
            }

            for category, repo_names in categories.items():
                f.write(f"### {category}\n\n")
                for repo_name in repo_names:
                    repo_info = next((r for r in repositories if r['name'] == repo_name), None)
                    if repo_info:
                        status = "✅ Cloned" if repo_name in self.cloned_repos else "⏳ Pending"
                        f.write(f"- **{repo_info['description']}**\n")
                        f.write(f"  - Repository: `{repo_name}`\n")
                        f.write(f"  - URL: {repo_info['url']}\n")
                        f.write(f"  - Status: {status}\n\n")

            f.write("## Quick Start Guide\n\n")
            f.write("### Building CSI Tools\n\n")
            f.write("```bash\n")
            f.write("# Intel 5300 CSI Tool\n")
            f.write("cd research/repositories/linux-80211n-csitool\n")
            f.write("make\n")
            f.write("sudo make install\n")
            f.write("```\n\n")
            f.write("```bash\n")
            f.write("# Atheros CSI Tool\n")
            f.write("cd research/repositories/Atheros-CSI-Tool\n")
            f.write("chmod +x setup.sh\n")
            f.write("./setup.sh\n")
            f.write("```\n\n")
            f.write("### Running Examples\n\n")
            f.write("```bash\n")
            f.write("# WiFi CSI Sensing Framework\n")
            f.write("cd research/repositories/WiFi-CSI-Sensing\n")
            f.write("python3 main.py --interface wlan0\n")
            f.write("```\n\n")
            f.write("## Contributing\n\n")
            f.write("This collection focuses on open-source WiFi sensing research. ")
            f.write("If you find additional repositories that should be included, ")
            f.write("please submit a pull request.\n\n")

        print(f"📖 Repository index created: {index_file}")

def main():
    parser = argparse.ArgumentParser(description='Clone WiFi Sensing Research Repositories')
    parser.add_argument('-o', '--output', default='research/repositories',
                       help='Output directory for cloned repositories')
    parser.add_argument('--retry-failed', action='store_true',
                       help='Retry previously failed clones')

    args = parser.parse_args()

    cloner = RepositoryCloner(args.output)

    if args.retry_failed and cloner.failed_clones:
        print(f"🔄 Retrying {len(cloner.failed_clones)} failed clones...")
        # Implement retry logic here
        pass
    else:
        cloner.clone_repositories()

if __name__ == "__main__":
    main()