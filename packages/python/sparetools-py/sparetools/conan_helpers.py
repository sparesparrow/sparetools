"""
Conan Helper Utilities for SpareTools

This module provides utilities for working with Conan package manager
in the context of SpareTools projects.
"""

import subprocess
import os
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ConanPackage:
    name: str
    version: str
    user: Optional[str] = None
    channel: Optional[str] = None

    @property
    def reference(self) -> str:
        """Get the full Conan reference"""
        ref = f"{self.name}/{self.version}"
        if self.user and self.channel:
            ref += f"@{self.user}/{self.channel}"
        elif self.user:
            ref += f"@{self.user}"
        return ref

@dataclass
class ConanProfile:
    name: str
    settings: Dict[str, str]
    options: Dict[str, Any]
    env_vars: Dict[str, str]

class ConanHelper:
    """Helper class for Conan operations"""

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root or os.getcwd())

    def run_conan_command(self, command: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
        """
        Run a Conan command and return the result

        Args:
            command: Command arguments (without 'conan')
            cwd: Working directory

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        full_command = ["conan"] + command
        working_dir = cwd or self.workspace_root

        try:
            result = subprocess.run(
                full_command,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", f"Command execution failed: {e}"

    def create_package(self, conanfile_path: str, name: str, version: str,
                      profile: Optional[str] = None) -> bool:
        """
        Create a Conan package

        Args:
            conanfile_path: Path to conanfile.py
            name: Package name
            version: Package version
            profile: Conan profile to use

        Returns:
            True if successful
        """
        command = ["create", conanfile_path, f"{name}/{version}"]
        if profile:
            command.extend(["--profile", profile])

        exit_code, stdout, stderr = self.run_conan_command(command)
        if exit_code == 0:
            print(f"Successfully created package {name}/{version}")
            return True
        else:
            print(f"Failed to create package {name}/{version}")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return False

    def install_dependencies(self, conanfile_path: str, install_folder: Optional[str] = None,
                           profile: Optional[str] = None) -> bool:
        """
        Install dependencies from a conanfile

        Args:
            conanfile_path: Path to conanfile.txt or conanfile.py
            install_folder: Installation folder
            profile: Conan profile to use

        Returns:
            True if successful
        """
        command = ["install", conanfile_path]
        if install_folder:
            command.extend(["--install-folder", install_folder])
        if profile:
            command.extend(["--profile", profile])

        exit_code, stdout, stderr = self.run_conan_command(command)
        if exit_code == 0:
            print("Successfully installed dependencies")
            return True
        else:
            print("Failed to install dependencies")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return False

    def upload_package(self, reference: str, remote: str = "sparesparrow") -> bool:
        """
        Upload a package to a remote

        Args:
            reference: Package reference (name/version@user/channel)
            remote: Remote name

        Returns:
            True if successful
        """
        command = ["upload", reference, "--remote", remote]

        exit_code, stdout, stderr = self.run_conan_command(command)
        if exit_code == 0:
            print(f"Successfully uploaded {reference}")
            return True
        else:
            print(f"Failed to upload {reference}")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return False

    def list_remotes(self) -> List[Dict[str, str]]:
        """List configured Conan remotes"""
        exit_code, stdout, stderr = self.run_conan_command(["remote", "list", "--format", "json"])

        if exit_code == 0:
            try:
                data = json.loads(stdout)
                return data.get("remotes", [])
            except json.JSONDecodeError:
                return []
        return []

    def add_remote(self, name: str, url: str, verify_ssl: bool = True) -> bool:
        """
        Add a Conan remote

        Args:
            name: Remote name
            url: Remote URL
            verify_ssl: Whether to verify SSL

        Returns:
            True if successful
        """
        command = ["remote", "add", name, url]
        if not verify_ssl:
            command.append("--insecure")

        exit_code, stdout, stderr = self.run_conan_command(command)
        if exit_code == 0:
            print(f"Successfully added remote {name}")
            return True
        else:
            print(f"Failed to add remote {name}")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return False

    def authenticate_remote(self, remote: str, username: str, password: str) -> bool:
        """
        Authenticate with a remote

        Args:
            remote: Remote name
            username: Username
            password: Password

        Returns:
            True if successful
        """
        command = ["remote", "auth", remote, "--username", username, "--password", password]

        exit_code, stdout, stderr = self.run_conan_command(command)
        if exit_code == 0:
            print(f"Successfully authenticated with {remote}")
            return True
        else:
            print(f"Failed to authenticate with {remote}")
            return False

    def get_package_info(self, reference: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a package

        Args:
            reference: Package reference

        Returns:
            Package information dictionary or None if not found
        """
        command = ["inspect", reference, "--format", "json"]

        exit_code, stdout, stderr = self.run_conan_command(command)
        if exit_code == 0:
            try:
                return json.loads(stdout)
            except json.JSONDecodeError:
                return None
        return None

def create_conanfile_txt(requirements: List[ConanPackage],
                        generators: List[str] = ["CMakeDeps", "CMakeToolchain"]) -> str:
    """
    Create a conanfile.txt content from requirements

    Args:
        requirements: List of ConanPackage objects
        generators: List of generators to include

    Returns:
        conanfile.txt content as string
    """
    content = "[requires]\n"
    for req in requirements:
        content += f"{req.reference}\n"

    content += "\n[generators]\n"
    for gen in generators:
        content += f"{gen}\n"

    return content

def setup_cloudsmith_remote(organization: str = "sparesparrow",
                           token: Optional[str] = None) -> bool:
    """
    Setup Cloudsmith remote for SpareTools

    Args:
        organization: Cloudsmith organization
        token: API token (if not provided, will use environment variable)

    Returns:
        True if successful
    """
    url = f"https://conan.cloudsmith.io/{organization}/"
    token = token or os.environ.get("CLOUDSMITH_API_KEY")

    if not token:
        print("No Cloudsmith API token provided")
        return False

    helper = ConanHelper()

    # Add remote
    if not helper.add_remote(organization, url):
        return False

    # Authenticate
    if not helper.authenticate_remote(organization, organization, token):
        return False

    return True