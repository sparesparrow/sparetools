"""
Git to Conan Collector

Builds Conan packages from git tags/branches.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional

log = logging.getLogger(__name__)

# Use sparetools-base utilities
try:
    from sparetools.conan.core import download_python_interpreter
    from sparetools.util.execute_command import execute_command
    from sparetools.fs.core import copy_file
except ImportError:
    log.warning("sparetools-base not available, using fallback implementations")
    download_python_interpreter = None
    execute_command = None
    copy_file = None

# Use local modules
try:
    from ..git.git_handler import GitHandler
    from ..conan.conan_versioning import ConanVersionManager
except ImportError:
    from sparetools_versioning.git.git_handler import GitHandler
    from sparetools_versioning.conan.conan_versioning import ConanVersionManager

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    log.warning("PyYAML not available, YAML features disabled")


class Options:
    """Options for git-to-conan collector."""
    git_path = ''
    skipped_names_yaml_file = ''
    conanfile_path = ''
    package_name = ''
    parse_tags = False
    parse_branches = False
    parse_branches_remote = False
    remote_name = 'cloudsmith'  # Default remote for SpareTools


def prepare_arguments(args: List[str]) -> argparse.Namespace:
    """
    Prepare command-line arguments.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Parsed arguments
    """
    new_args = []
    for arg in args:
        new_args.extend(arg.split(' '))
    
    parser = argparse.ArgumentParser(
        description='Git Collector to Conan - Build packages from git tags/branches'
    )
    parser.add_argument(
        '-g',
        '--gitPath',
        dest='git_path',
        help='Path to GIT repository',
        required=True
    )
    parser.add_argument(
        '-s',
        '--skippedNamesYaml',
        dest='skipped_names_yaml_file',
        help='Path to YAML file with list of skipped items',
        required=True
    )
    parser.add_argument(
        '-c',
        '--conanfilePath',
        dest='conanfile_path',
        help='Path to conanfile',
        required=True
    )
    parser.add_argument(
        '-p',
        '--packageName',
        dest='package_name',
        help='Package name',
        required=True
    )
    parser.add_argument(
        '-t',
        '--Tags',
        dest='parse_tags',
        default=False,
        action='store_true',
        help='Parse git tags'
    )
    parser.add_argument(
        '-b',
        '--branches',
        dest='parse_branches',
        default=False,
        action='store_true',
        help='Parse local branches'
    )
    parser.add_argument(
        '-br',
        '--branchesRemote',
        dest='parse_branches_remote',
        default=False,
        action='store_true',
        help='Parse remote branches'
    )
    parser.add_argument(
        '-r',
        '--remote',
        dest='remote_name',
        default='cloudsmith',
        help='Conan remote name for upload (default: cloudsmith)'
    )

    return parser.parse_args(new_args)


class GitToConanCollector:
    """Collects git tags/branches and creates Conan packages."""

    def __init__(self, options: Optional[Options] = None):
        """
        Initialize collector.
        
        Args:
            options: Options object or None
        """
        self.options = options
        self.version_manager = ConanVersionManager()

    def run(self, options: Optional[Options] = None) -> int:
        """
        Run the git-to-conan collection process.
        
        Args:
            options: Options object (uses self.options if None)
            
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        if options is None:
            options = self.options
            
        if options is None:
            log.error("No options provided")
            return 1

        # Determine what to parse
        if options.parse_tags:
            rc, items = get_tags(options.git_path)
        elif options.parse_branches:
            rc, items = get_branches(options.git_path)
        elif options.parse_branches_remote:
            rc, items = get_branches_remote(options.git_path)
        else:
            log.error('You need to select one of the parsing type options!')
            return 1

        if rc != 0:
            message = '\n'.join(items) if isinstance(items, list) else str(items)
            log.error(f'Parsing command returned non-zero status: {rc}. Message: {message}')
            return 1

        # Load skipped items
        skipped_items = Path(options.skipped_names_yaml_file)
        if skipped_items.exists() and HAS_YAML:
            try:
                with open(skipped_items, 'r') as f:
                    gathered_builds = set(yaml.safe_load(f) or [])
            except Exception as e:
                log.warning(f"Failed to load skipped items: {e}")
                gathered_builds = set()
        else:
            gathered_builds = set()

        items_changed = False

        # Get Conan executable
        if download_python_interpreter:
            try:
                full_conan, python_path = download_python_interpreter(options.git_path)
            except Exception as e:
                log.error(f"Failed to get Python interpreter: {e}")
                # Fallback to system conan
                from sparetools.conan.core import get_default_conan
                conan_path = get_default_conan()
                if conan_path:
                    full_conan = conan_path
                else:
                    log.error("Conan executable not found")
                    return 1
        else:
            # Fallback
            from sparetools.conan.core import get_default_conan
            conan_path = get_default_conan()
            if conan_path:
                full_conan = conan_path
            else:
                log.error("Conan executable not found")
                return 1

        # Process each item
        items_set = set(items) if isinstance(items, list) else {items}
        for item in items_set - gathered_builds:
            item_str = str(item).strip()
            if not item_str:
                continue
                
            log.info(f'Processing {item_str}')
            
            # Checkout git reference
            rc, _ = execute_command(f'git reset --hard {item_str}', cwd=options.git_path)
            if rc != 0:
                log.warning(f'Git was not able to checkout {item_str}')
                continue

            # Set CONAN_BUILD_VERSION environment variable
            os.environ['CONAN_BUILD_VERSION'] = item_str

            # Copy conanfile if needed
            if copy_file:
                copy_file(options.conanfile_path, options.git_path)
            else:
                # Fallback
                import shutil
                shutil.copy2(options.conanfile_path, options.git_path)

            # Create Conan package
            rc, return_string = execute_command(
                f'{full_conan} create . --ignore-dirty',
                cwd=options.git_path
            )
            if rc != 0:
                message = '\n'.join(return_string) if isinstance(return_string, list) else str(return_string)
                log.warning(f'Conan was not able to create package. Result: {rc} Log:\n{message}')
                continue

            # Track package
            self.version_manager.track_package(options.package_name, item_str)
            items_changed = True

        # Upload if items changed
        if items_changed:
            rc, return_string = execute_command(
                f'{full_conan} upload {options.package_name}/* -r {options.remote_name} -c --parallel --all'
            )
            if rc != 0:
                log.warning(f'Failed to upload packages: {return_string}')

            # Save skipped items
            if HAS_YAML:
                try:
                    with open(skipped_items, 'w') as f:
                        yaml.safe_dump(list(items_set), f)
                except Exception as e:
                    log.warning(f"Failed to save skipped items: {e}")
        else:
            log.info(f'All items have been already processed')

        return 0


def get_tags(git_path: str) -> Tuple[int, List[str]]:
    """
    Get git tags.
    
    Args:
        git_path: Path to git repository
        
    Returns:
        Tuple of (return_code, list of tags)
    """
    if execute_command:
        return execute_command('git tag', cwd=git_path)
    else:
        # Fallback
        import subprocess
        result = subprocess.run(['git', 'tag'], cwd=git_path, capture_output=True, text=True)
        return result.returncode, result.stdout.strip().split('\n') if result.stdout else []


def get_branches(git_path: str) -> Tuple[int, List[str]]:
    """
    Get local git branches.
    
    Args:
        git_path: Path to git repository
        
    Returns:
        Tuple of (return_code, list of branches)
    """
    if execute_command:
        return execute_command('git branch', cwd=git_path)
    else:
        # Fallback
        import subprocess
        result = subprocess.run(['git', 'branch'], cwd=git_path, capture_output=True, text=True)
        branches = []
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('*'):
                    branches.append(line)
        return result.returncode, branches


def get_branches_remote(git_path: str) -> Tuple[int, List[str]]:
    """
    Get remote git branches.
    
    Args:
        git_path: Path to git repository
        
    Returns:
        Tuple of (return_code, list of remote branches)
    """
    if execute_command:
        return execute_command('git branch -r', cwd=git_path)
    else:
        # Fallback
        import subprocess
        result = subprocess.run(['git', 'branch', '-r'], cwd=git_path, capture_output=True, text=True)
        branches = []
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if line and '->' not in line:
                    # Remove 'origin/' prefix
                    if '/' in line:
                        branches.append(line.split('/', 1)[1])
                    else:
                        branches.append(line)
        return result.returncode, branches


def main():
    """Main entry point for command-line usage."""
    options = prepare_arguments(sys.argv[1:])
    collector = GitToConanCollector()
    sys.exit(collector.run(options))


if __name__ == '__main__':
    main()
