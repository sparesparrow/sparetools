"""
Git Operations

Git utilities for repository management, cloning, branching, and commits.
Based on ngapy-dev/ngapy/miscellaneous/git_handler.py
Extended with additional git utilities.
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

try:
    from git import Repo, Actor
    HAS_GITPYTHON = True
except ImportError:
    HAS_GITPYTHON = False
    log.warning("GitPython not available, git operations will be limited")

from ..util.execute_command import execute_command


# Copied from ngapy/miscellaneous/git_handler.py
class GitHandler:
    """
    Handler for git repository operations.
    
    Based on ngapy/miscellaneous/git_handler.py GitHandler class.
    Extended with additional utilities for submodules, branch management, and stash operations.
    """

    def __init__(self):
        self.repository = None
        self.current_branch = None
        self.gitignore_path = ''

    def create_new_or_reuse_repo(self, git_path, git_remote=None):
        """
        Create a new repository or reuse existing one.
        
        Based on ngapy/miscellaneous/git_handler.py create_new_or_reuse_repo method.
        """
        self.gitignore_path = os.path.join(git_path, '.gitignore')
        if not os.path.exists(os.path.join(git_path, '.git')):
            shutil.rmtree(git_path, ignore_errors=True)
            os.makedirs(git_path, exist_ok=True)
            execute_command(f'git clone {git_remote} {git_path}', git_path)
            self.repository = Repo(git_path)
            execute_command('git config --local core.autocrlf false', self.repository.working_dir)
        else:
            self.repository = Repo(git_path)
        self.repository.head.reset(index=True, working_tree=True)

    def open_repository(self, git_path):
        """
        Open an existing repository.
        
        Based on ngapy/miscellaneous/git_handler.py open_repository method.
        """
        self.repository = Repo(git_path)

    def add_to_git_ignore(self, path_list):
        """
        Add paths to .gitignore file.
        
        Based on ngapy/miscellaneous/git_handler.py add_to_git_ignore method.
        """
        with open(self.gitignore_path, "w") as ignore:
            for ignore_element in path_list:
                ignore.write(ignore_element + '\n')

    def create_branch_and_switch(self, branch_name, branch_source='develop'):
        """
        Create a new branch and switch to it.
        
        Based on ngapy/miscellaneous/git_handler.py create_branch_and_switch method.
        """
        try:
            if self.repository.head.reference.name != branch_name:
                self.repository.git.checkout(branch_name)
                log.debug(f'Switching GIT branch {branch_name}')
            self.current_branch = self.repository.head.reference
        except:
            self.current_branch = self.repository.create_head(branch_name, branch_source)
            log.debug(f'Creating GIT branch {branch_name}')

        if self.repository.head.reference != self.current_branch:
            self.repository.head.reference = self.current_branch
        self.repository.head.reset(index=True, working_tree=True)

    def commit_current_changes(self, message='', date='', author='', email=''):
        """
        Commit current changes.
        
        Based on ngapy/miscellaneous/git_handler.py commit_current_changes method.

        Returns:
            Commit SHA if successful
        """
        os.chdir(self.repository.working_dir)
        execute_command(f'git add -A {self.repository.working_dir}')
        self.repository.index.commit(message, author=Actor(author, email), author_date=date, commit_date=date,
                                     skip_hooks=True)
        return self.repository.head.commit.hexsha

    def diff_is_empty(self):
        """
        Check if there are any uncommitted changes.
        
        Based on ngapy/miscellaneous/git_handler.py diff_is_empty method.
        """
        os.chdir(self.repository.working_dir)
        rc, result = execute_command(f'git add -A')
        rc, result = execute_command(f'git diff HEAD --exit-code --no-patch')
        return rc == 0

    def get_current_commit_sha(self):
        """
        Get the current commit SHA.
        
        Based on ngapy/miscellaneous/git_handler.py get_current_commit_sha method.
        """
        return self.repository.head.object.hexsha


# Copied from ngapy/miscellaneous/git_handler.py
def get_repository_sha(repository_path):
    """
    Get the current commit SHA of a repository.
    
    Based on ngapy/miscellaneous/git_handler.py get_repository_sha function.

    Args:
        repository_path: Path to git repository

    Returns:
        Commit SHA or None if not available
    """
    git_handler = GitHandler()
    git_handler.open_repository(repository_path)
    return git_handler.get_current_commit_sha()


# Extended functions beyond ngapy
def clone_repository(url: str, destination: str, branch: Optional[str] = None,
                    depth: Optional[int] = None) -> bool:
    """
    Clone a git repository.

    Args:
        url: Repository URL to clone
        destination: Destination directory
        branch: Branch to clone (optional)
        depth: Depth for shallow clone (optional)

    Returns:
        True if successful, False otherwise
    """
    cmd_parts = ['git', 'clone']

    if depth:
        cmd_parts.extend(['--depth', str(depth)])

    if branch:
        cmd_parts.extend(['--branch', branch])

    cmd_parts.extend([url, destination])

    try:
        rc, _ = execute_command(' '.join(cmd_parts))
        return rc == 0
    except Exception as e:
        log.error(f"Failed to clone repository {url}: {e}")
        return False


def update_submodules(repository_path: str, recursive: bool = True) -> bool:
    """
    Initialize and update git submodules.

    Args:
        repository_path: Path to git repository
        recursive: Whether to recursively update submodules

    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = 'git submodule update --init'
        if recursive:
            cmd += ' --recursive'
        rc, _ = execute_command(cmd, cwd=repository_path)
        return rc == 0
    except Exception as e:
        log.error(f"Failed to update submodules in {repository_path}: {e}")
        return False


def get_remote_branches(repository_path: str) -> list:
    """
    Get list of remote branches.

    Args:
        repository_path: Path to git repository

    Returns:
        List of remote branch names
    """
    try:
        rc, output = execute_command('git branch -r', cwd=repository_path)
        if rc != 0:
            return []
        branches = []
        for line in output:
            line = line.strip()
            if line and '->' not in line:  # Skip HEAD -> branch pointers
                # Remove 'origin/' prefix if present
                if '/' in line:
                    branches.append(line.split('/', 1)[1])
                else:
                    branches.append(line)
        return branches
    except Exception as e:
        log.error(f"Failed to get remote branches for {repository_path}: {e}")
        return []


def create_and_push_branch(repository_path: str, branch_name: str,
                          remote_name: str = 'origin') -> bool:
    """
    Create a new branch and push it to remote.

    Args:
        repository_path: Path to git repository
        branch_name: Name of new branch
        remote_name: Remote name to push to

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create and switch to new branch
        rc1, _ = execute_command(f'git checkout -b {branch_name}', cwd=repository_path)
        if rc1 != 0:
            return False

        # Push to remote
        rc2, _ = execute_command(f'git push -u {remote_name} {branch_name}', cwd=repository_path)
        return rc2 == 0
    except Exception as e:
        log.error(f"Failed to create and push branch {branch_name}: {e}")
        return False


def get_uncommitted_changes(repository_path: str) -> list:
    """
    Get list of files with uncommitted changes.

    Args:
        repository_path: Path to git repository

    Returns:
        List of changed file paths
    """
    try:
        rc, output = execute_command('git status --porcelain', cwd=repository_path)
        if rc != 0:
            return []

        files = []
        for line in output:
            if line.strip():
                # Extract filename from status output (skip status codes)
                parts = line.strip().split()
                if len(parts) >= 2:
                    files.append(parts[-1])  # Last part is the filename

        return files
    except Exception as e:
        log.error(f"Failed to get uncommitted changes for {repository_path}: {e}")
        return []


def stash_changes(repository_path: str, message: Optional[str] = None) -> Optional[str]:
    """
    Stash current changes.

    Args:
        repository_path: Path to git repository
        message: Optional stash message

    Returns:
        Stash reference if successful, None otherwise
    """
    try:
        cmd = 'git stash push'
        if message:
            cmd += f' -m "{message}"'

        rc, output = execute_command(cmd, cwd=repository_path)
        if rc == 0:
            # Try to extract stash reference from output
            for line in output:
                if 'Saved working directory' in line:
                    return "stash@{0}"  # Most recent stash
        return None
    except Exception as e:
        log.error(f"Failed to stash changes in {repository_path}: {e}")
        return None


def apply_stash(repository_path: str, stash_ref: str = "stash@{0}") -> bool:
    """
    Apply a stashed change.

    Args:
        repository_path: Path to git repository
        stash_ref: Stash reference to apply

    Returns:
        True if successful, False otherwise
    """
    try:
        rc, _ = execute_command(f'git stash apply {stash_ref}', cwd=repository_path)
        return rc == 0
    except Exception as e:
        log.error(f"Failed to apply stash {stash_ref} in {repository_path}: {e}")
        return False
