"""
Conan Management Core

Utilities for Conan package management, remote configuration,
profile validation, and cache operations.
"""

import json
import logging
import os
import re
import subprocess
import tempfile
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple

log = logging.getLogger(__name__)


def download_python_interpreter(repository_path: str, python_package_name: str = "sparetools-cpython") -> Tuple[str, Path]:
    """
    Download Python interpreter from Conan package.

    Args:
        repository_path: Path to repository
        python_package_name: Name of Python package in Conan

    Returns:
        Tuple of (full_conan_command, python_executable_path)
    """
    package_path = download_package_for_repository(repository_path, python_package_name)
    python_exe = "python.exe" if os.name == "nt" else "python"
    python_path = package_path / python_exe

    # Try different possible conan script locations
    conan_script_path = package_path / 'Scripts' / 'conan-script.py'
    conan_exe_path = package_path / 'Scripts' / 'conan.exe'

    full_conan = ''
    if conan_script_path.exists():
        full_conan = f'"{python_path}" "{conan_script_path}"'
    elif conan_exe_path.exists():
        full_conan = f'"{python_path}" "{conan_exe_path}"'
    else:
        # Fallback to system conan
        conan_path = get_default_conan()
        if conan_path:
            full_conan = f'"{python_path}" "{conan_path}"'

    if not full_conan:
        raise RuntimeError(f'Conan was not found in {package_path}')

    return full_conan, python_path


def print_package_version(repository_path: str, package: Optional[str] = None) -> None:
    """
    Print package version information.

    Args:
        repository_path: Path to repository
        package: Specific package name (optional)
    """
    packages = get_configuration_safe(repository_path)
    if package and package in packages:
        name, version, _ = packages[package]
        print(f'{name}/{version}')
    else:
        # Print root package
        repo_path = Path(repository_path)
        for name, (pkg_name, version, path) in packages.items():
            if path == repo_path:
                print(f'{pkg_name}/{version}')
                break


def print_package_path(repository_path: str, package: Optional[str] = None) -> None:
    """
    Print package path information.

    Args:
        repository_path: Path to repository
        package: Specific package name (optional)
    """
    packages = get_configuration_safe(repository_path)
    if package and package in packages:
        _, _, path = packages[package]
        print(path)
    else:
        # Print root package path
        repo_path = Path(repository_path)
        for name, (pkg_name, version, path) in packages.items():
            if path == repo_path:
                print(path)
                break


def install_packages_for_repository(repository_path: str) -> Dict[str, Tuple[str, str, Path]]:
    """
    Install all packages for a repository.

    Args:
        repository_path: Path to repository

    Returns:
        Dictionary of package configurations
    """
    conan_path = get_default_conan()
    if not conan_path:
        log.error("Conan executable not found")
        return {}

    try:
        result = subprocess.run(
            [conan_path, "install", repository_path],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=300
        )

        # Get configuration after install
        return get_configuration_safe(repository_path)
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to install packages for {repository_path}: {e}")
        return {}


def download_package_for_repository(repository_path: str, package_name: str) -> Path:
    """
    Download a specific package for a repository.

    Args:
        repository_path: Path to repository
        package_name: Name of package to download

    Returns:
        Path to downloaded package
    """
    packages = get_configuration_safe(repository_path)
    if package_name in packages:
        name, version, package_path = packages[package_name]
        if not package_path.exists():
            download_package_version(name, version)
        return package_path
    else:
        raise RuntimeError(f'Requested package {package_name} information was not found in {repository_path}.')


def get_info_about_package(package_name: str, repository_path: str) -> Tuple[int, List[str]]:
    """
    Get information about a specific package.

    Args:
        package_name: Name of package
        repository_path: Path to repository

    Returns:
        Tuple of (return_code, output_lines)
    """
    conan_path = get_default_conan()
    if not conan_path:
        return 1, ["Conan executable not found"]

    try:
        result = subprocess.run(
            [conan_path, "info", repository_path, "--package-filter", f"{package_name}*"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        return e.returncode, str(e).split('\n')


def create_package_graph(repository_path: str) -> Path:
    """
    Create a dependency graph HTML file for a repository.

    Args:
        repository_path: Path to repository

    Returns:
        Path to generated HTML file
    """
    conan_path = get_default_conan()
    if not conan_path:
        raise RuntimeError("Conan executable not found")

    repo_path = Path(repository_path)

    # Install packages first
    try:
        subprocess.run(
            [conan_path, "install", str(repo_path)],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            check=True,
            timeout=300
        )
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to install packages for graph: {e}")
        raise

    # Generate graph
    output_file = repo_path / 'graph.html'
    try:
        subprocess.run(
            [conan_path, "info", "-g", str(output_file), str(repo_path)],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            check=True,
            timeout=120
        )
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to create package graph: {e}")
        raise

    return output_file


def install_package_version(package: str, version: str, options: str = "") -> Tuple[int, List[str]]:
    """
    Install a specific package version.

    Args:
        package: Package name
        version: Package version
        options: Additional options

    Returns:
        Tuple of (return_code, output_lines)
    """
    conan_path = get_default_conan()
    if not conan_path:
        return 1, ["Conan executable not found"]

    if version and package:
        command = [conan_path, "install", f"{package}/{version}@", options]
    else:
        command = [conan_path, "install", ".", options]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode, result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        return e.returncode, str(e).split('\n')


def download_package_version(package: str, version: str, remote: Optional[str] = None, options: str = "") -> Path:
    """
    Download a specific package version.

    Args:
        package: Package name
        version: Package version
        remote: Remote repository name (optional)
        options: Additional options

    Returns:
        Path to downloaded package
    """
    conan_path = get_default_conan()
    if not conan_path:
        raise RuntimeError("Conan executable not found")

    # Check if package is already in cache
    info_cmd = [conan_path, "info", f"{package}/{version}@", "--paths", "-n", "package_folder"]
    if options:
        info_cmd.extend(options.split())

    try:
        result = subprocess.run(
            info_cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )

        # Extract package folder from output
        for line in result.stdout.split('\n'):
            if line.startswith('package_folder:'):
                package_path_str = line.split(':', 1)[1].strip()
                package_path = Path(package_path_str)
                if package_path.is_dir():
                    return package_path
                break

        # Package not in cache, download it
        download_cmd = [conan_path, "download", f"{package}/{version}@"]
        if remote:
            download_cmd.extend(["-r", remote])
        if options:
            download_cmd.extend(options.split())

        subprocess.run(
            download_cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=300
        )

        # Get path again after download
        result = subprocess.run(
            info_cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )

        for line in result.stdout.split('\n'):
            if line.startswith('package_folder:'):
                package_path_str = line.split(':', 1)[1].strip()
                package_path = Path(package_path_str)
                if package_path.is_dir():
                    return package_path

        raise RuntimeError(f'Could not find package folder after download: {package}/{version}')

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Failed to download package {package}/{version}: {e}')


def reinitialize_conan_cache() -> None:
    """
    Reinitialize the Conan cache by removing and recreating it.
    """
    from sparetools.fs.core import remove_directory_tree

    conan_home = get_conan_home()
    if not conan_home:
        raise RuntimeError("Could not determine Conan home directory")

    # Remove existing cache
    conan_home_path = Path(conan_home)
    if conan_home_path.exists():
        remove_directory_tree(str(conan_home_path))

    # Remove short home if it exists (Windows)
    short_home = os.environ.get("CONAN_USER_HOME_SHORT")
    if short_home:
        short_home_path = Path(short_home)
        if short_home_path.exists():
            remove_directory_tree(str(short_home_path))


def remove_conan_lock_files(conan_home: Optional[str] = None) -> None:
    """
    Remove Conan lock files from cache.

    Args:
        conan_home: Conan home directory (auto-detected if None)
    """
    if not conan_home:
        conan_home = get_conan_home()

    if not conan_home:
        log.warning("Could not determine Conan home directory")
        return

    conan_home_path = Path(conan_home)

    # Remove lock files
    lock_patterns = ["**/_.*.lock", "**/LCK*"]
    for pattern in lock_patterns:
        for lock_file in conan_home_path.glob(pattern):
            try:
                lock_file.unlink(missing_ok=True)
                log.debug(f"Removed lock file: {lock_file}")
            except OSError as e:
                log.warning(f"Failed to remove lock file {lock_file}: {e}")


def get_all_package_config_folders(repository_path: str) -> List[Path]:
    """
    Get all configuration folders from packages in a repository.

    Args:
        repository_path: Path to repository

    Returns:
        List of configuration folder paths
    """
    packages = get_configuration_safe(repository_path)
    config_paths = []

    for name, version, package_path in packages.values():
        # Check common config folder locations
        config_candidates = [
            package_path / 'Conf',
            package_path / '_Build' / 'SOURCE' / 'Conf',
            package_path / 'config',
            package_path / 'etc'
        ]

        for config_path in config_candidates:
            if config_path.exists() and config_path.is_dir() and not config_path.is_symlink():
                config_paths.append(config_path)

    return config_paths


def get_configuration_safe(repository_path: str) -> Dict[str, Tuple[str, str, Path]]:
    """
    Safely get package configuration, with fallback on failure.

    Args:
        repository_path: Path to repository

    Returns:
        Dictionary of package configurations
    """
    try:
        # Use ConanJsonLoader to get configuration
        loader = ConanJsonLoader(repository_path)
        packages = {}

        # Get root package info
        root_package = loader._get_root_node()
        if root_package:
            name, version = loader.get_package_name_version(root_package)
            packages[name] = (name, version, Path(repository_path))

        # Get dependency packages
        for dep in loader.get_dependencies():
            if dep.get('reference') != root_package.get('reference'):
                name, version = loader.get_package_name_version(dep)
                package_folder = dep.get('package_folder')
                if package_folder:
                    packages[name] = (name, version, Path(package_folder))

        return packages

    except Exception as e:
        log.warning(f"Failed to get configuration for {repository_path}: {e}")
        # Fallback: return basic info
        return {'root': ('unknown', 'unknown', Path(repository_path))}


def setup_parallel_download(download_threads: int = -1) -> None:
    """
    Configure parallel download settings.

    Args:
        download_threads: Number of threads (-1 for CPU count)
    """
    import psutil

    conan_path = get_default_conan()
    if not conan_path:
        log.error("Conan executable not found")
        return

    threads = psutil.cpu_count() if download_threads == -1 else download_threads

    try:
        subprocess.run(
            [conan_path, "config", "set", "general.parallel_download", str(threads)],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        log.info(f"Set parallel download threads to {threads}")
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to set parallel download: {e}")


def get_default_conan() -> Optional[str]:
    """
    Get the path to the default Conan executable.

    Returns:
        Path to Conan executable or None if not found
    """
    # Try common locations
    possible_paths = [
        "conan",  # In PATH
        "/usr/local/bin/conan",
        "/usr/bin/conan",
        os.path.expanduser("~/.local/bin/conan"),
    ]

    for path in possible_paths:
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            if "Conan version" in result.stdout:
                return path
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            continue

    return None


def get_conan_home() -> Optional[str]:
    """
    Get the Conan home directory.

    Returns:
        Path to Conan home directory or None if not found
    """
    # Check environment variable first
    conan_home = os.environ.get("CONAN_HOME")
    if conan_home:
        return conan_home

    # Default location
    default_home = os.path.expanduser("~/.conan")
    if os.path.exists(default_home):
        return default_home

    # Try to get from Conan itself
    conan_path = get_default_conan()
    if conan_path:
        try:
            result = subprocess.run(
                [conan_path, "config", "home"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            pass

    return None


def get_all_packages_in_cache() -> List[Dict[str, Any]]:
    """
    Get information about all packages in the Conan cache.

    Returns:
        List of dictionaries with package information
    """
    conan_path = get_default_conan()
    if not conan_path:
        log.warning("Conan executable not found")
        return []

    try:
        result = subprocess.run(
            [conan_path, "cache", "path", "--all"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )

        packages = []
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('Conan Cache'):
                # Parse package reference from path
                # Format: package/version@user/channel -> /path/to/cache
                if ' -> ' in line:
                    ref, path = line.split(' -> ', 1)
                    ref = ref.strip()
                    path = path.strip()
                    packages.append({
                        "reference": ref,
                        "path": path,
                        "exists": os.path.exists(path)
                    })

        return packages
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to get Conan cache packages: {e}")
        return []


def remove_conan_package_in_cache(package_ref: str) -> bool:
    """
    Remove a specific package from the Conan cache.

    Args:
        package_ref: Package reference (e.g., "pkg/1.0@user/channel")

    Returns:
        True if successful, False otherwise
    """
    conan_path = get_default_conan()
    if not conan_path:
        log.warning("Conan executable not found")
        return False

    try:
        result = subprocess.run(
            [conan_path, "remove", package_ref, "-f"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        return True
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to remove package {package_ref}: {e}")
        return False


class ConanConfiguration:
    """Manages Conan configuration files and settings."""

    def __init__(self, conan_home: Optional[str] = None):
        """
        Initialize Conan configuration manager.

        Args:
            conan_home: Conan home directory (auto-detected if None)
        """
        self.conan_home = conan_home or get_conan_home()
        self.conan_path = get_default_conan()

    def get_config_value(self, key: str) -> Optional[str]:
        """
        Get a Conan configuration value.

        Args:
            key: Configuration key

        Returns:
            Configuration value or None
        """
        if not self.conan_path:
            return None

        try:
            result = subprocess.run(
                [self.conan_path, "config", "get", key],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def set_config_value(self, key: str, value: str) -> bool:
        """
        Set a Conan configuration value.

        Args:
            key: Configuration key
            value: Configuration value

        Returns:
            True if successful, False otherwise
        """
        if not self.conan_path:
            return False

        try:
            result = subprocess.run(
                [self.conan_path, "config", "set", key, value],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            return True
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to set config {key}={value}: {e}")
            return False

    def add_remote(self, name: str, url: str) -> bool:
        """
        Add a Conan remote.

        Args:
            name: Remote name
            url: Remote URL

        Returns:
            True if successful, False otherwise
        """
        if not self.conan_path:
            return False

        try:
            result = subprocess.run(
                [self.conan_path, "remote", "add", name, url],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            return True
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to add remote {name}={url}: {e}")
            return False

    def remove_remote(self, name: str) -> bool:
        """
        Remove a Conan remote.

        Args:
            name: Remote name

        Returns:
            True if successful, False otherwise
        """
        if not self.conan_path:
            return False

        try:
            result = subprocess.run(
                [self.conan_path, "remote", "remove", name],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            return True
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to remove remote {name}: {e}")
            return False

    def list_remotes(self) -> List[Dict[str, str]]:
        """
        List all Conan remotes.

        Returns:
            List of remote dictionaries with name and url
        """
        if not self.conan_path:
            return []

        try:
            result = subprocess.run(
                [self.conan_path, "remote", "list"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )

            remotes = []
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if line and ': ' in line:
                    name, url = line.split(': ', 1)
                    remotes.append({"name": name.strip(), "url": url.strip()})

            return remotes
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to list remotes: {e}")
            return []


class ConanJsonLoader:
    """Loads and parses Conan-generated JSON files."""

    def __init__(self, repository_path: str):
        """
        Initialize JSON loader for a repository.

        Args:
            repository_path: Path to repository
        """
        import munch

        self.repository_path = Path(repository_path)

        # Generate JSON info
        conan_path = get_default_conan()
        if not conan_path:
            raise RuntimeError("Conan executable not found")

        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_out:
            temp_json_file = temp_out.name

        try:
            result = subprocess.run(
                [conan_path, "info", str(self.repository_path), "--paths", "-j", temp_json_file],
                cwd=str(self.repository_path),
                capture_output=True,
                text=True,
                check=True,
                timeout=60
            )

            with open(temp_json_file, 'r') as f:
                result_json = json.load(f)

            self.result_munch = munch.munchify(result_json)
            self._get_root_node().package_folder = str(self.repository_path)

        except subprocess.CalledProcessError as e:
            log.error(f"Conan info failed: {e}")
            # Try fallback without remote
            try:
                result = subprocess.run(
                    [conan_path, "info", str(self.repository_path), "--paths", "-if", "C:", "-j", temp_json_file],
                    cwd=str(self.repository_path),
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                with open(temp_json_file, 'r') as f:
                    result_json = json.load(f)

                self.result_munch = munch.munchify(result_json)
                self._get_root_node().package_folder = str(self.repository_path)

            except subprocess.CalledProcessError as e2:
                log.error(f"Conan info fallback also failed: {e2}")
                raise RuntimeError(f"Failed to load Conan info for {repository_path}")

        finally:
            # Clean up temp file
            try:
                os.unlink(temp_json_file)
            except OSError:
                pass

    def _get_root_node(self):
        """Get the root node (conanfile.py)."""
        for dependency_node in self.result_munch:
            if dependency_node.display_name.startswith('conanfile.py'):
                return dependency_node
        return None

    def _get_node_with_reference(self, reference: str):
        """Get node with specific reference."""
        for dependency_node in self.result_munch:
            if dependency_node.reference == reference:
                return dependency_node
        return None

    @staticmethod
    def get_package_name_version(package) -> Tuple[str, str]:
        """
        Extract name and version from package.

        Args:
            package: Package object

        Returns:
            Tuple of (name, version)
        """
        _, version = package.display_name.split('/', maxsplit=1)
        version = version.split(')', maxsplit=1)[0]
        name = package.provides[0] if package.provides else "unknown"
        return name, version

    def filter_skipped(self) -> Dict[str, Any]:
        """
        Filter out skipped packages and handle conflicts.

        Returns:
            Dictionary of packages
        """
        package_dict = {}
        for dependency_node in self.result_munch:
            name, version = self.get_package_name_version(dependency_node)
            if name in package_dict:
                # Handle conflicts - prefer non-skipped packages
                existing_node = package_dict[name]
                if dependency_node.get('binary', None) == 'Skip':
                    continue  # Skip this one, keep existing
                elif existing_node.get('binary', None) != 'Skip':
                    log.info(f'Conan package conflict: {name}/{version} and existing')
                    continue  # Keep existing non-skipped
            package_dict[name] = dependency_node
        return package_dict

    def get_dependencies(self) -> List[Dict[str, Any]]:
        """
        Get dependency information.

        Returns:
            List of dependency dictionaries
        """
        return [dict(dep) for dep in self.result_munch if not dep.display_name.startswith('conanfile.py')]

    def load(self) -> bool:
        """Legacy method for compatibility."""
        return True

    def get_settings(self) -> Dict[str, Any]:
        """Get settings from root node."""
        root = self._get_root_node()
        return dict(root.settings) if root and hasattr(root, 'settings') else {}

    def get_options(self) -> Dict[str, Any]:
        """Get options from root node."""
        root = self._get_root_node()
        return dict(root.options) if root and hasattr(root, 'options') else {}


class ConanConfigurationTracker:
    """Tracks Conan package usage and manages cache cleanup."""

    def __init__(self, conan_home: Optional[str] = None):
        """
        Initialize configuration tracker.

        Args:
            conan_home: Conan home directory
        """
        import yaml

        self.conan_home = conan_home or get_conan_home()
        self.expected_version = 1.0
        self._data = {
            'version': self.expected_version,
            'conan_usage': {},
        }
        self.load_config()

    @property
    def config_path(self) -> Path:
        """Get path to tracker configuration file."""
        return Path(self.conan_home or "~/.conan") / 'conan_tracker.yaml'

    @property
    def packages(self) -> Dict[str, Any]:
        """Get package usage data."""
        return self._data['conan_usage']

    @packages.setter
    def packages(self, value: Dict[str, Any]) -> None:
        """Set package usage data."""
        self._data['conan_usage'] = value

    def load_config(self) -> None:
        """Load tracker configuration from file."""
        import yaml

        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as stream:
                    temp_data = yaml.safe_load(stream)
                    if temp_data and str(temp_data.get('version', 0)) == str(self.expected_version):
                        self._data = temp_data
                    else:
                        self.save_config()
            except (yaml.YAMLError, IOError):
                log.warning("Failed to load conan tracker config, using defaults")

    def save_config(self) -> None:
        """Save tracker configuration to file."""
        import yaml

        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as stream:
                yaml.safe_dump(self._data, stream)
        except IOError as e:
            log.error(f"Failed to save conan tracker config: {e}")

    def remove_old_packages(self, time_delta: timedelta) -> None:
        """
        Remove packages that haven't been used recently.

        Args:
            time_delta: How old packages must be to be removed
        """
        from sparetools.fs.core import remove_directory_tree

        all_packages = self.packages.copy()
        cached_packages = get_all_packages_in_cache()

        removed_count = 0
        for cached_ref in cached_packages:
            if cached_ref not in all_packages:
                log.warning(f'Removing untracked package: {cached_ref}')
                if remove_conan_package_in_cache(cached_ref):
                    removed_count += 1
            elif all_packages[cached_ref]['last_used'] < datetime.now() - time_delta:
                log.warning(f'Removing old package: {cached_ref}. '
                           f'Last Used: {all_packages[cached_ref]["last_used"]}')
                if remove_conan_package_in_cache(cached_ref):
                    removed_count += 1
                    del all_packages[cached_ref]
            else:
                log.debug(f'Keeping active package: {cached_ref}')

        self.save_config()
        log.info(f'Conan package cleanup finished. Removed {removed_count} packages')

    def snapshot_initial_config(self) -> bool:
        """Legacy method - kept for compatibility."""
        return True

    def snapshot_current_config(self) -> bool:
        """Legacy method - kept for compatibility."""
        return True

    def get_changed_configs(self) -> Dict[str, Tuple[str, str]]:
        """Legacy method - kept for compatibility."""
        return {}

    def restore_initial_config(self) -> bool:
        """Legacy method - kept for compatibility."""
        return True


def download_python_interpreter(repository_path: str) -> Tuple[str, Path]:
    """
    Download Python interpreter from Conan package.

    Args:
        repository_path: Path to the repository

    Returns:
        Tuple of (conan_command, python_path)
    """
    package_path = download_package_for_repository(repository_path, 'sparetools-cpython')
    python_path = package_path / 'python.exe' if os.name == 'nt' else package_path / 'bin' / 'python'
    conan_script_path = package_path / 'Scripts' / 'conan-script.py'
    conan_exe_path = package_path / 'Scripts' / 'conan.exe' if os.name == 'nt' else package_path / 'bin' / 'conan'

    full_conan = ''
    if conan_script_path.exists():
        full_conan = f'{python_path} {conan_script_path}'
    elif conan_exe_path.exists():
        full_conan = str(conan_exe_path)
    else:
        raise RuntimeError(f'Conan was not found in {package_path}')

    # Add to PATH if needed
    if package_path / 'bin' not in os.environ.get('PATH', '').split(os.pathsep):
        os.environ['PATH'] = str(package_path / 'bin') + os.pathsep + os.environ.get('PATH', '')

    return full_conan, python_path


def print_package_version(repository_path: str, package: Optional[str] = None) -> None:
    """
    Print package version to stdout.

    Args:
        repository_path: Path to the repository
        package: Specific package name (optional)
    """
    packages = get_configuration_safe(repository_path)
    if package and package in packages:
        name, version, _ = packages[package]
        print(f'{name}/{version}')
    else:
        # Find the root package
        repo_path = Path(repository_path)
        for name, (pkg_name, version, pkg_path) in packages.items():
            if pkg_path == repo_path:
                print(f'{pkg_name}/{version}')
                return


def print_package_path(repository_path: str, package: Optional[str] = None) -> None:
    """
    Print package path to stdout.

    Args:
        repository_path: Path to the repository
        package: Specific package name (optional)
    """
    packages = get_configuration_safe(repository_path)
    if package and package in packages:
        _, _, pkg_path = packages[package]
        print(pkg_path)
    else:
        # Find the root package
        repo_path = Path(repository_path)
        for name, (pkg_name, version, pkg_path) in packages.items():
            if pkg_path == repo_path:
                print(pkg_path)
                return


def install_packages_for_repository(repository_path: str) -> Dict[str, Tuple[str, str, Path]]:
    """
    Install all packages for a repository.

    Args:
        repository_path: Path to the repository

    Returns:
        Dictionary of package configurations
    """
    conan_path = get_default_conan()
    if not conan_path:
        log.warning("Conan executable not found")
        return {}

    try:
        result = subprocess.run(
            [conan_path, "install", repository_path],
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=300
        )
        return get_configuration_safe(repository_path)
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to install packages for {repository_path}: {e}")
        return {}


def download_package_for_repository(repository_path: str, package_name: str) -> Path:
    """
    Download a specific package for a repository.

    Args:
        repository_path: Path to the repository
        package_name: Name of the package to download

    Returns:
        Path to the downloaded package

    Raises:
        RuntimeError: If package information is not found
    """
    packages = get_configuration_safe(repository_path)
    if package_name in packages:
        name, version, package_path = packages[package_name]
        if not package_path.exists():
            download_package_version(package_name, version)
        return package_path
    else:
        raise RuntimeError(f'Requested package {package_name} information was not found in {repository_path}.')


def get_info_about_package(package_name: str, repository_path: str) -> Tuple[int, List[str]]:
    """
    Get detailed information about a package.

    Args:
        package_name: Name of the package
        repository_path: Path to the repository

    Returns:
        Tuple of (return_code, output_lines)
    """
    conan_path = get_default_conan()
    if not conan_path:
        return -1, []

    try:
        result = subprocess.run(
            [conan_path, "info", repository_path, "--package-filter", f"{package_name}*"],
            cwd=repository_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        return e.returncode, str(e).split('\n')


def create_package_graph(repository_path: str) -> Path:
    """
    Create a dependency graph HTML file for a repository.

    Args:
        repository_path: Path to the repository

    Returns:
        Path to the generated HTML file
    """
    conan_path = get_default_conan()
    if not conan_path:
        raise RuntimeError("Conan executable not found")

    repo_path = Path(repository_path)

    # Install packages first
    subprocess.run([conan_path, "install", str(repo_path)], cwd=str(repo_path), check=True, timeout=300)

    output_file = repo_path / 'graph.html'
    subprocess.run(
        [conan_path, "info", "-g", str(output_file), str(repo_path)],
        cwd=str(repo_path),
        check=True,
        timeout=120
    )

    return output_file


def install_package_version(package: str, version: str, opts: str = '') -> Tuple[int, List[str]]:
    """
    Install a specific package version.

    Args:
        package: Package name
        version: Package version
        opts: Additional options

    Returns:
        Tuple of (return_code, output_lines)
    """
    conan_path = get_default_conan()
    if not conan_path:
        return -1, []

    if version and package:
        command = [conan_path, "install", f"{package}/{version}@", opts]
    else:
        command = [conan_path, "install", ".", opts]

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
        return result.returncode, result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        return e.returncode, str(e).split('\n')


def download_package_version(package: str, version: str, remote: str = "cloudsmith", opts: str = '') -> Path:
    """
    Download a specific package version.

    Args:
        package: Package name
        version: Package version
        remote: Remote name (default: cloudsmith)
        opts: Additional options

    Returns:
        Path to the downloaded package

    Raises:
        RuntimeError: If package download fails
    """
    conan_path = get_default_conan()
    if not conan_path:
        raise RuntimeError("Conan executable not found")

    # Check if package is already in local cache
    try:
        result = subprocess.run(
            [conan_path, "info", f"{package}/{version}@", "--paths", "-n", "package_folder", opts],
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )

        import re
        m = re.search(r'package_folder: (.*)', result.stdout)
        if m and m.group(1) and Path(m.group(1)).is_dir():
            return Path(m.group(1))

        # Download if not in cache
        subprocess.run(
            [conan_path, "download", f"{package}/{version}@", "-r", remote, opts],
            check=True,
            timeout=300
        )

        # Get path again
        result = subprocess.run(
            [conan_path, "info", f"{package}/{version}@", "--paths", "-n", "package_folder", opts],
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )

        m = re.search(r'package_folder: (.*)', result.stdout)
        if m and m.group(1):
            package_path = Path(m.group(1))
            if package_path.is_dir():
                return package_path

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Failed to download package {package}/{version}: {e}')

    raise RuntimeError(f'Package {package}/{version} not found after download')


def reinitialize_conan_cache() -> None:
    """
    Clear and reinitialize the Conan cache.
    """
    from ..fs.core import remove_directory_tree

    conan_home = get_conan_home()
    if conan_home:
        remove_directory_tree(conan_home)

    # Reinitialize remotes
    setup_cloudsmith_remote()
    setup_github_packages_remote()


def remove_conan_lock_files(conan_home: Optional[str] = None) -> None:
    """
    Remove Conan lock files.

    Args:
        conan_home: Conan home directory (auto-detected if None)
    """
    if not conan_home:
        conan_home = get_conan_home()

    if conan_home:
        conan_home_path = Path(conan_home)
        for pattern in ['**/_.count', '**/_.count.lock']:
            for path in conan_home_path.glob(pattern):
                try:
                    path.unlink()
                except OSError:
                    pass


def get_all_package_config_folders(repository_path: str) -> List[Path]:
    """
    Get all package configuration folders.

    Args:
        repository_path: Path to the repository

    Returns:
        List of configuration folder paths
    """
    packages = get_configuration_safe(repository_path)
    config_paths = []

    for name, version, package_path in packages.values():
        # Check common config locations
        for config_dir in ['Conf', '_Build/SOURCE/Conf']:
            config_path = package_path / config_dir
            if config_path.exists() and not config_path.is_symlink():
                config_paths.append(config_path)

    return config_paths


def get_configuration_safe(repository_path: str) -> Dict[str, Tuple[str, str, Path]]:
    """
    Safely get package configuration.

    Args:
        repository_path: Path to the repository

    Returns:
        Dictionary of package configurations
    """
    try:
        # This would need a ConanConfiguration class adapted from ngapy
        # For now, return a basic structure
        return _get_basic_package_config(repository_path)
    except Exception:
        # Fallback configuration
        return {'root': ('root', '1.0', Path(repository_path))}


def _get_basic_package_config(repository_path: str) -> Dict[str, Tuple[str, str, Path]]:
    """
    Get basic package configuration from conanfile.py.

    Args:
        repository_path: Path to the repository

    Returns:
        Dictionary of package configurations
    """
    # This is a simplified version - would need full ConanConfiguration implementation
    repo_path = Path(repository_path)
    conanfile = repo_path / 'conanfile.py'

    if conanfile.exists():
        # Try to extract package name from conanfile
        try:
            with open(conanfile, 'r') as f:
                content = f.read()
                # Simple regex to find name = "package_name"
                import re
                match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    package_name = match.group(1)
                    return {package_name: (package_name, '1.0', repo_path)}
        except Exception:
            pass

    return {'unknown': ('unknown', '1.0', repo_path)}


def setup_parallel_download(download_threads: int = -1) -> None:
    """
    Configure parallel download settings.

    Args:
        download_threads: Number of threads (-1 for CPU count)
    """
    import psutil

    conan_path = get_default_conan()
    if not conan_path:
        return

    threads = psutil.cpu_count() if download_threads == -1 else download_threads

    try:
        subprocess.run(
            [conan_path, "config", "set", "general.parallel_download", str(threads)],
            check=True,
            timeout=30
        )
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to set parallel download: {e}")


def setup_cloudsmith_remote(name: str = "cloudsmith", url: str = "", token: str = "") -> bool:
    """
    Set up Cloudsmith remote.

    Args:
        name: Remote name
        url: Remote URL
        token: Authentication token

    Returns:
        True if successful, False otherwise
    """
    config = ConanConfiguration()

    # Clean existing remotes if needed
    # config.remove_remote(name)  # Optional: remove if exists

    if config.add_remote(name, url):
        if token:
            # For Cloudsmith, authentication might be different
            # This would need to be adapted based on actual Cloudsmith auth method
            pass
        return True

    return False


def setup_github_packages_remote(name: str = "github", url: str = "", token: str = "") -> bool:
    """
    Set up GitHub Packages remote.

    Args:
        name: Remote name
        url: Remote URL
        token: GitHub token

    Returns:
        True if successful, False otherwise
    """
    config = ConanConfiguration()

    if config.add_remote(name, url):
        if token:
            # GitHub Packages uses token authentication
            # This would need to be implemented based on GitHub auth
            pass
        return True

    return False


def enable_conan_remote(name: str) -> bool:
    """
    Enable a Conan remote.

    Args:
        name: Remote name

    Returns:
        True if successful, False otherwise
    """
    conan_path = get_default_conan()
    if not conan_path:
        return False

    try:
        subprocess.run([conan_path, "remote", "enable", name], check=True, timeout=30)
        return True
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to enable remote {name}: {e}")
        return False


def disable_conan_remote(name: str) -> bool:
    """
    Disable a Conan remote.

    Args:
        name: Remote name

    Returns:
        True if successful, False otherwise
    """
    conan_path = get_default_conan()
    if not conan_path:
        return False

    try:
        subprocess.run([conan_path, "remote", "disable", name], check=True, timeout=30)
        return True
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to disable remote {name}: {e}")
        return False


def clean_conan_remotes() -> bool:
    """
    Clean all Conan remotes.

    Returns:
        True if successful, False otherwise
    """
    conan_path = get_default_conan()
    if not conan_path:
        return False

    try:
        subprocess.run([conan_path, "remote", "clean"], check=True, timeout=30)
        return True
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to clean remotes: {e}")
        return False