#!/usr/bin/env python3
"""
WiGLE Tools Installer
Installs dependencies for all cloned WiGLE tools and repositories
"""

import os
import subprocess
import sys
from pathlib import Path
import json

class WigleToolsInstaller:
    def __init__(self, wigle_dir="research/repositories/wigle"):
        self.wigle_dir = Path(wigle_dir)
        self.installed_tools = []
        self.failed_installs = []

    def run_command(self, cmd, cwd=None, description=""):
        """Run a shell command with error handling"""
        try:
            print(f"🔧 {description}")
            result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {description} - Success")
                return True
            else:
                print(f"❌ {description} - Failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ {description} - Error: {e}")
            return False

    def install_python_requirements(self):
        """Install Python requirements for all wigle tools"""
        requirements_files = [
            "wigleQuery/requirements.txt",
            "wigle-wifi/requirements.txt",
            "wigle-bt/requirements.txt",
            "WigleToTAK/requirements.txt",
            "ssidCliTool/requirements.txt",
            "wigle-tools-takano32/requirements.txt"
        ]

        print("🐍 Installing Python dependencies for WiGLE tools...")
        print("=" * 60)

        for req_file in requirements_files:
            req_path = self.wigle_dir / req_file
            if req_path.exists():
                tool_name = req_file.split('/')[0]
                tool_dir = self.wigle_dir / tool_name
                venv_dir = tool_dir / "venv"

                print(f"📦 Setting up virtual environment for {tool_name}")

                # Create virtual environment
                venv_success = self.run_command(
                    f"python3 -m venv {venv_dir}",
                    description=f"Create virtual environment for {tool_name}"
                )

                if venv_success:
                    # Install requirements in virtual environment
                    pip_path = venv_dir / "bin" / "pip"
                    install_success = self.run_command(
                        f"{pip_path} install -r {req_path}",
                        description=f"Install {tool_name} requirements in venv"
                    )

                    if install_success:
                        self.installed_tools.append(f"python-{tool_name}")
                        print(f"✅ Virtual environment created: {venv_dir}")
                    else:
                        self.failed_installs.append(f"python-{tool_name}")
                else:
                    # Fallback: try pipx
                    print(f"⚠️  Virtual environment failed, trying pipx for {tool_name}")
                    pipx_success = self.run_command(
                        f"pipx install --include-deps -r {req_path}",
                        description=f"Install {tool_name} with pipx"
                    )
                    if pipx_success:
                        self.installed_tools.append(f"pipx-{tool_name}")
                    else:
                        self.failed_installs.append(f"python-{tool_name}")
            else:
                print(f"⚠️  Requirements file not found: {req_file}")

    def install_arduino_esp32_tools(self):
        """Install ESP32/Arduino tools for wardriving hardware"""
        print("\\n🤖 Installing ESP32/Arduino tools...")

        # Check if wardriver_rev3 has specific installation instructions
        wardriver_dir = self.wigle_dir / "wardriver_rev3"
        if wardriver_dir.exists():
            readme_path = wardriver_dir / "README.md"
            if readme_path.exists():
                print("📖 Checking wardriver_rev3 README for installation instructions...")
                # Could parse README here, but for now just note it exists

        # ESP8266-Wardriving might need Jupyter
        esp8266_dir = self.wigle_dir / "ESP8266-Wardriving"
        if esp8266_dir.exists():
            venv_dir = esp8266_dir / "venv"
            venv_success = self.run_command(
                f"python3 -m venv {venv_dir}",
                description="Create virtual environment for ESP8266-Wardriving"
            )

            if venv_success:
                pip_path = venv_dir / "bin" / "pip"
                install_success = self.run_command(
                    f"{pip_path} install jupyter notebook pandas matplotlib",
                    description="Install Jupyter in ESP8266 venv"
                )
                if install_success:
                    self.installed_tools.append("jupyter-notebook")
                    print(f"✅ Jupyter venv created: {venv_dir}")
                else:
                    self.failed_installs.append("jupyter-notebook")

    def install_system_tools(self):
        """Install system-level tools if needed"""
        print("\\n🔨 Installing system tools...")

        # Check if any tools need system dependencies
        tools_to_check = [
            ("geoprobe", ["libpcap-dev", "python3-scapy"]),
            ("wifimap", ["python3-gi", "gir1.2-gtk-3.0"]),
        ]

        for tool_name, packages in tools_to_check:
            tool_dir = self.wigle_dir / tool_name
            if tool_dir.exists():
                print(f"🔍 Checking system dependencies for {tool_name}")
                for package in packages:
                    # Check if package is available (this is a simple check)
                    result = subprocess.run(f"dpkg -l | grep {package}",
                                          shell=True, capture_output=True)
                    if result.returncode != 0:
                        print(f"⚠️  System package {package} may need installation")
                        print(f"   Run: sudo apt install {package}")

    def setup_wigle_api_access(self):
        """Setup instructions for WiGLE API access"""
        print("\\n🔑 WiGLE API Setup Instructions:")
        print("-" * 40)
        print("Most WiGLE tools require an API key from wigle.net")
        print("1. Create an account at https://wigle.net")
        print("2. Get your API key from account settings")
        print("3. Set environment variable:")
        print("   export WIGLE_API_KEY='your_api_key_here'")
        print("4. Or create a .env file in each tool directory")

        # Create a sample .env file
        env_sample = self.wigle_dir / ".env.sample"
        with open(env_sample, 'w') as f:
            f.write("# WiGLE API Configuration\\n")
            f.write("# Get your API key from https://wigle.net\\n")
            f.write("WIGLE_API_KEY=your_api_key_here\\n")
            f.write("WIGLE_USERNAME=your_username\\n")

        print(f"📄 Sample .env file created: {env_sample}")

    def create_installation_report(self):
        """Create a report of installed tools"""
        report_file = self.wigle_dir / "installation_report.json"

        report = {
            'installed_tools': self.installed_tools,
            'failed_installs': self.failed_installs,
            'installation_date': subprocess.run(['date'], capture_output=True, text=True).stdout.strip(),
            'python_version': sys.version,
            'pip_version': subprocess.run(['pip3', '--version'], capture_output=True, text=True).stdout.strip()
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\\n📊 Installation report saved: {report_file}")

        if self.installed_tools:
            print(f"✅ Successfully installed: {', '.join(self.installed_tools)}")

        if self.failed_installs:
            print(f"❌ Failed to install: {', '.join(self.failed_installs)}")

    def install_all(self):
        """Run complete installation process"""
        print("🚀 Starting WiGLE Tools Installation")
        print("=" * 60)

        self.install_python_requirements()
        self.install_arduino_esp32_tools()
        self.install_system_tools()
        self.setup_wigle_api_access()
        self.create_installation_report()

        print("\\n🎉 WiGLE Tools Installation Complete!")
        print("\\n📚 Quick Start:")
        print("cd research/repositories/wigle/wigleQuery")
        print("python3 wiglequery.py --help")

def main():
    installer = WigleToolsInstaller()
    installer.install_all()

if __name__ == "__main__":
    main()