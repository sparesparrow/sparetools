#!/usr/bin/env python3
"""
SpareTools Conan Launcher

Command-line tool for Conan package management operations.
Supports Cloudsmith, GitHub Packages, and other repository types.
"""

import argparse
import glob
import logging
import multiprocessing
import os
import shlex
import sys
from pathlib import Path
from typing import List, Tuple

from .core import (
    download_python_interpreter,
    download_package_for_repository,
    ConanConfiguration,
    print_package_version,
    print_package_path,
    remove_conan_lock_files,
    install_packages_for_repository,
)
from .repositories import RepositoryManager, RepositoryConfig, RepositoryType

__version__ = '1.0.0'


def setup_logging():
    """Setup basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def check_conan_validity(folder_path: Path) -> None:
    """
    Check if a folder contains a valid Conan repository.

    Args:
        folder_path: Path to check

    Raises:
        RuntimeError: If folder is not valid
    """
    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        raise RuntimeError(f'{folder_path} is not a valid directory')

    conanfile = folder_path / 'conanfile.py'
    if not conanfile.is_file():
        raise RuntimeError(f'{folder_path} does not contain a valid conanfile.py')


def add_packages_paths_to_search_paths(packages: dict) -> None:
    """
    Add package paths to Python search paths.

    Args:
        packages: Dictionary of packages
    """
    package_paths = [str(package[2]) for package in packages.values()]
    package_paths_str = os.pathsep.join(package_paths)

    current_pythonpath = os.environ.get('PYTHONPATH', '')
    if current_pythonpath:
        package_paths_str = package_paths_str + os.pathsep + current_pythonpath

    os.environ['PYTHONPATH'] = package_paths_str
    sys.path = package_paths + sys.path


def prepare_package_script_arguments(repository_root: str, arguments: str) -> List[str]:
    """
    Prepare script arguments by resolving package names to paths.

    Args:
        repository_root: Repository root path
        arguments: Space-separated arguments

    Returns:
        List of processed arguments
    """
    packages = ConanConfiguration().get_configuration(repository_path=repository_root)
    add_packages_paths_to_search_paths(packages)

    new_arguments = []
    for argument in shlex.split(arguments, posix=False):
        for package_name, package_version, package_path in packages.values():
            if argument.startswith(package_name):
                download_package_for_repository(repository_root, package_name)
                argument = argument.replace(package_name, str(package_path), 1)
                break
        new_arguments.append(argument)

    return new_arguments


def run_package_python_script(repository_root: str, arguments: str,
                            wait_till_finish: bool = True,
                            extra_arguments: str = None) -> List[Tuple[int, List[str]]]:
    """
    Run a Python script with package resolution.

    Args:
        repository_root: Repository root path
        arguments: Script arguments
        wait_till_finish: Whether to wait for completion
        extra_arguments: Additional arguments

    Returns:
        List of (return_code, output_lines) tuples
    """
    os.environ['ENV_REPOSITORY_ROOT'] = repository_root
    converted_arguments = prepare_package_script_arguments(repository_root, arguments)

    if extra_arguments:
        converted_arguments.extend(shlex.split(extra_arguments))

    # Handle glob patterns
    script_paths = glob.glob(converted_arguments[0]) if converted_arguments else []

    full_conan, python_path = download_python_interpreter(repository_root)
    result_array = []

    for script_path in script_paths:
        cmd = [str(python_path), script_path] + converted_arguments[1:]
        # Note: execute_command equivalent would go here
        # For now, using subprocess directly
        import subprocess
        try:
            result = subprocess.run(
                cmd,
                capture_output=not wait_till_finish,
                text=True,
                cwd=repository_root
            )
            result_array.append((result.returncode, result.stdout.strip().split('\n') if result.stdout else []))
        except subprocess.CalledProcessError as e:
            result_array.append((e.returncode, str(e).split('\n')))

    return result_array


def setup_repository(args) -> None:
    """Setup a repository remote."""
    if not args.repo_type or not args.repo_url:
        print("Error: --repo-type and --repo-url are required for repository setup")
        sys.exit(1)

    # Parse credentials
    credentials = {}
    if args.username and args.password:
        credentials = {'username': args.username, 'password': args.password}
    elif args.token:
        credentials = {'token': args.token}

    repo_type = RepositoryType(args.repo_type.lower())

    config = RepositoryConfig(
        name=args.repo_name,
        url=args.repo_url,
        repo_type=repo_type,
        credentials=credentials
    )

    manager = RepositoryManager()
    if manager.setup_repository(config):
        print(f"Successfully set up repository '{args.repo_name}'")
    else:
        print(f"Failed to set up repository '{args.repo_name}'")
        sys.exit(1)


def main():
    """Main entry point."""
    multiprocessing.freeze_support()
    setup_logging()

    parser = argparse.ArgumentParser(
        description='SpareTools Conan Package Manager v' + __version__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup a Cloudsmith repository
  python -m sparetools.conan.launcher --setup-repo --repo-name myremote --repo-type cloudsmith --repo-url https://conan.cloudsmith.io/myorg --token <token>

  # Install packages for a repository
  python -m sparetools.conan.launcher --install /path/to/repo

  # Run a Conan command
  python -m sparetools.conan.launcher --conan-cmd /path/to/repo "install . --build=missing"

  # Print package version
  python -m sparetools.conan.launcher --package-version /path/to/repo mypackage

  # Run a Python script with package resolution
  python -m sparetools.conan.launcher --run-script /path/to/repo "mypackage/script.py arg1 arg2"
        """
    )

    # Repository setup
    parser.add_argument('--setup-repo', action='store_true',
                       help='Setup a repository remote')
    parser.add_argument('--repo-name', required=False,
                       help='Repository remote name')
    parser.add_argument('--repo-type', required=False,
                       choices=['conan', 'cloudsmith', 'github', 'pip', 'docker', 'generic'],
                       help='Repository type')
    parser.add_argument('--repo-url', required=False,
                       help='Repository URL')
    parser.add_argument('--username', required=False,
                       help='Username for authentication')
    parser.add_argument('--password', required=False,
                       help='Password for authentication')
    parser.add_argument('--token', required=False,
                       help='Token for authentication')

    # Package operations
    parser.add_argument('--install', nargs=1, metavar='REPO_PATH',
                       help='Install packages for repository')
    parser.add_argument('--conan-cmd', nargs=2, metavar=('REPO_PATH', 'CONAN_ARGS'),
                       help='Run conan command in repository')
    parser.add_argument('--run-script', nargs=2, metavar=('REPO_PATH', 'SCRIPT_ARGS'),
                       help='Run Python script with package resolution')
    parser.add_argument('--package-version', nargs=2, metavar=('REPO_PATH', 'PACKAGE'),
                       help='Print package version')
    parser.add_argument('--package-path', nargs=2, metavar=('REPO_PATH', 'PACKAGE'),
                       help='Print package path')

    # Options
    parser.add_argument('--no-wait', action='store_true',
                       help='Do not wait for script completion')

    args = parser.parse_args()

    # Clean up lock files
    try:
        remove_conan_lock_files()
    except Exception as e:
        logging.warning(f"Failed to clean lock files: {e}")

    # Handle repository setup
    if args.setup_repo:
        setup_repository(args)
        return

    # Handle install
    if args.install:
        repo_path = args.install[0]
        check_conan_validity(repo_path)
        try:
            packages = install_packages_for_repository(repo_path)
            print(f"Installed packages for {repo_path}")
            for name, (pkg_name, version, path) in packages.items():
                print(f"  {pkg_name}/{version} -> {path}")
        except Exception as e:
            print(f"Failed to install packages: {e}")
            sys.exit(1)
        return

    # Handle conan command
    if args.conan_cmd:
        repo_path, conan_args = args.conan_cmd
        check_conan_validity(repo_path)

        try:
            full_conan, python_path = download_python_interpreter(repo_path)
            import subprocess
            result = subprocess.run(
                f'{full_conan} {conan_args}',
                shell=True,
                cwd=repo_path
            )
            sys.exit(result.returncode)
        except Exception as e:
            print(f"Failed to run conan command: {e}")
            sys.exit(1)

    # Handle package version
    if args.package_version:
        repo_path, package_name = args.package_version
        check_conan_validity(repo_path)
        try:
            print_package_version(repo_path, package_name)
        except Exception as e:
            print(f"Failed to get package version: {e}")
            sys.exit(1)
        return

    # Handle package path
    if args.package_path:
        repo_path, package_name = args.package_path
        check_conan_validity(repo_path)
        try:
            print_package_path(repo_path, package_name)
        except Exception as e:
            print(f"Failed to get package path: {e}")
            sys.exit(1)
        return

    # Handle script execution
    if args.run_script:
        repo_path, script_args = args.run_script
        check_conan_validity(repo_path)

        try:
            wait = not args.no_wait
            results = run_package_python_script(repo_path, script_args, wait)

            # Check results
            all_success = all(rc == 0 for rc, _ in results)
            if not all_success:
                print("Some scripts failed")
                sys.exit(1)

        except Exception as e:
            print(f"Failed to run script: {e}")
            sys.exit(1)

    # Default: show help
    parser.print_help()


if __name__ == '__main__':
    main()