#!/usr/bin/env python3
"""
WiGLE.net Repository Cloner
Clones key repositories from wigle.net and wigle-related tools
"""

import os
import subprocess
import json
import time
from pathlib import Path
import argparse

class WigleRepositoryCloner:
    def __init__(self, output_dir="research/repositories/wigle"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cloned_repos = set()
        self.failed_clones = []

        # Load existing clones
        self.load_clone_log()

    def load_clone_log(self):
        """Load log of previously cloned repositories"""
        log_file = self.output_dir / "wigle_clone_log.json"
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
        log_file = self.output_dir / "wigle_clone_log.json"
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

    def clone_wigle_repositories(self):
        """Clone all key wigle repositories"""

        repositories = [
            # Official WiGLE Tools
            {
                'url': 'https://github.com/wiglenet/wigle-wifi-wardriving.git',
                'name': 'wigle-wifi-wardriving',
                'description': 'Official WiGLE Android wardriving client',
                'use_https': True
            },

            # WiGLE API Tools and Clients
            {
                'url': 'https://github.com/wytshadow/wigleQuery.git',
                'name': 'wigleQuery',
                'description': 'Command line tool for querying wigle.net and displaying results on Google Maps',
                'use_https': True
            },
            {
                'url': 'https://github.com/e-m3din4/wigle-wifi.git',
                'name': 'wigle-wifi',
                'description': 'Tool to get approximate location of Wi-Fi access points using wigle.net API',
                'use_https': True
            },
            {
                'url': 'https://github.com/e-m3din4/wigle-bt.git',
                'name': 'wigle-bt',
                'description': 'Tool to get approximate location of Bluetooth devices using wigle.net API',
                'use_https': True
            },
            {
                'url': 'https://github.com/takano32/wigle-tools.git',
                'name': 'wigle-tools-takano32',
                'description': 'WiGLE API tools collection',
                'use_https': True
            },
            {
                'url': 'https://github.com/DeathSec333/wigle-tools.git',
                'name': 'wigle-tools-deathsec',
                'description': 'WiGLE API tools for wardriving optimization',
                'use_https': True
            },
            {
                'url': 'https://github.com/gdaPythonProjects/ssidCliTool.git',
                'name': 'ssidCliTool',
                'description': 'CLI tool based on wigle.net API',
                'use_https': True
            },

            # Wardriving and Mapping Tools
            {
                'url': 'https://github.com/JosephHewitt/wardriver_rev3.git',
                'name': 'wardriver_rev3',
                'description': 'Portable ESP32-based WiFi/Bluetooth scanner for Wigle.net',
                'use_https': True
            },
            {
                'url': 'https://github.com/AlexLynd/ESP8266-Wardriving.git',
                'name': 'ESP8266-Wardriving',
                'description': 'ESP8266 wardriving scripts with Jupyter Notebook data visualization',
                'use_https': True
            },
            {
                'url': 'https://github.com/canaryradio/WigleToTAK.git',
                'name': 'WigleToTAK',
                'description': 'Convert wigle CSV data for use with TAK (Team Awareness Kit)',
                'use_https': True
            },

            # Integration Tools
            {
                'url': 'https://github.com/bbreukelen/geoprobe.git',
                'name': 'geoprobe',
                'description': 'Tool to sniff, collect and geolocate 802.11 ProbeRequests using WiGLE',
                'use_https': True
            },
            {
                'url': 'https://github.com/cyberartemio/wardriver-pwnagotchi-plugin.git',
                'name': 'wardriver-pwnagotchi-plugin',
                'description': 'Pwnagotchi plugin that uploads wardriving data to Wigle.net',
                'use_https': True
            },
            {
                'url': 'https://github.com/Znerox/wifimap.git',
                'name': 'wifimap',
                'description': 'WiFi and Bluetooth devices overlayed on Google Maps using WiGLE data',
                'use_https': True
            },

            # Analysis and Visualization
            {
                'url': 'https://github.com/digitalnivuk97-ctrl/wifi-map-viewer.git',
                'name': 'wifi-map-viewer',
                'description': 'Offline WiFi wardriving visualization tool - Like WiGLE but completely local',
                'use_https': True
            },
            {
                'url': 'https://github.com/jhodevstuff/kml-bluetooth-parser-wigle.git',
                'name': 'kml-bluetooth-parser-wigle',
                'description': 'Analyze and compare BT & BLE devices from kml files captured with WiGLE',
                'use_https': True
            }
        ]

        successful_clones = 0
        total_repos = len(repositories)

        print(f"🗺️  Starting clone of {total_repos} WiGLE repositories...")
        print("=" * 60)

        for repo in repositories:
            use_https = repo.get('use_https', True)  # Default to HTTPS
            if self.clone_repository(repo['url'], repo['name'], repo['description'], use_https):
                successful_clones += 1
            time.sleep(1)  # Be respectful to GitHub API

        # Save clone log
        self.save_clone_log()

        print(f"\n✅ WiGLE clone complete: {successful_clones}/{total_repos} repositories cloned successfully")

        # Create repository index
        self.create_wigle_repository_index(repositories)

    def create_wigle_repository_index(self, repositories):
        """Create an index file with all wigle repositories"""
        index_file = self.output_dir / "wigle_repositories.md"

        with open(index_file, 'w') as f:
            f.write("# WiGLE.net Research Repositories\n\n")
            f.write("Collection of GitHub repositories for WiGLE.net tools, API clients, and wardriving applications.\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
            f.write("## Repository Categories\\n\\n")

            categories = {
                'Official WiGLE Tools': [
                    'wigle-wifi-wardriving'
                ],
                'WiGLE API Tools': [
                    'wigleQuery', 'wigle-wifi', 'wigle-bt', 'wigle-tools-takano32',
                    'wigle-tools-deathsec', 'ssidCliTool'
                ],
                'Wardriving Hardware': [
                    'wardriver_rev3', 'ESP8266-Wardriving'
                ],
                'Integration Tools': [
                    'WigleToTAK', 'geoprobe', 'wardriver-pwnagotchi-plugin', 'wifimap'
                ],
                'Analysis & Visualization': [
                    'wifi-map-viewer', 'kml-bluetooth-parser-wigle'
                ]
            }

            for category, repo_names in categories.items():
                f.write(f"### {category}\\n\\n")
                for repo_name in repo_names:
                    repo_info = next((r for r in repositories if r['name'] == repo_name), None)
                    if repo_info:
                        status = "✅ Cloned" if repo_name in self.cloned_repos else "⏳ Pending"
                        f.write(f"- **{repo_info['description']}**\\n")
                        f.write(f"  - Repository: `{repo_name}`\\n")
                        f.write(f"  - URL: {repo_info['url']}\\n")
                        f.write(f"  - Status: {status}\\n\\n")

            f.write("## Quick Start Guide\\n\\n")
            f.write("### Setting up WiGLE API Access\\n\\n")
            f.write("Most WiGLE tools require an API key from wigle.net:\\n\\n")
            f.write("1. Create an account at [wigle.net](https://wigle.net)\\n")
            f.write("2. Get your API key from the account settings\\n")
            f.write("3. Set environment variable: `export WIGLE_API_KEY=your_key_here`\\n\\n")

            f.write("### Running WiGLE Tools\\n\\n")
            f.write("```bash\\n")
            f.write("# Query WiGLE for WiFi networks\\n")
            f.write("cd research/repositories/wigle/wigleQuery\\n")
            f.write("python3 wiglequery.py --ssid \"MyNetwork\"\\n")
            f.write("```\\n\\n")

            f.write("```bash\\n")
            f.write("# Use wigle-wifi tool\\n")
            f.write("cd research/repositories/wigle/wigle-wifi\\n")
            f.write("python3 wigle_wifi.py -b BSSID\\n")
            f.write("```\\n\\n")

            f.write("### ESP32 Wardriving\\n\\n")
            f.write("```bash\\n")
            f.write("# Setup wardriver_rev3\\n")
            f.write("cd research/repositories/wigle/wardriver_rev3\\n")
            f.write("# Follow README for ESP32 setup\\n")
            f.write("```\\n\\n")

            f.write("## WiGLE Wiki Download\\n\\n")
            f.write("WiGLE wiki content has been downloaded to: `research/repositories/wigle/wiki/`\\n\\n")

            f.write("## Integration with WiFi Sensing\\n\\n")
            f.write("These tools complement the existing WiFi sensing research by providing:\\n\\n")
            f.write("- Real-world WiFi mapping data from wigle.net\\n")
            f.write("- Wardriving hardware and software solutions\\n")
            f.write("- API access to global WiFi database\\n")
            f.write("- Data visualization and analysis tools\\n\\n")

            f.write("## Contributing\\n\\n")
            f.write("This collection focuses on WiGLE.net ecosystem tools. ")
            f.write("If you find additional WiGLE-related repositories, please submit a pull request.\\n\\n")

        print(f"📖 WiGLE repository index created: {index_file}")

def main():
    parser = argparse.ArgumentParser(description='Clone WiGLE.net Research Repositories')
    parser.add_argument('-o', '--output', default='research/repositories/wigle',
                       help='Output directory for cloned repositories')
    parser.add_argument('--retry-failed', action='store_true',
                       help='Retry previously failed clones')

    args = parser.parse_args()

    cloner = WigleRepositoryCloner(args.output)

    if args.retry_failed and cloner.failed_clones:
        print(f"🔄 Retrying {len(cloner.failed_clones)} failed clones...")
        # Implement retry logic here
        pass
    else:
        cloner.clone_wigle_repositories()

if __name__ == "__main__":
    main()