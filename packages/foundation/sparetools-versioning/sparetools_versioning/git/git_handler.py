"""
Git Handler for Versioning

Repository operations for versioning workflows.
"""

import logging
import os
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

try:
    from git import Repo, Actor
    HAS_GITPYTHON = True
except ImportError:
    HAS_GITPYTHON = False
    log.warning("GitPython not available, git operations will be limited")

# Use sparetools-base utilities
try:
    from sparetools.util.execute_command import execute_command
    from sparetools.scm.git import GitHandler as BaseGitHandler
except ImportError:
    # Fallback if sparetools-base not available
    import subprocess
    BaseGitHandler = None


class GitHandler:
    """Handler for git repository operations."""

    def __init__(self):
        self.repository = None
        self.current_branch = None
        self.gitignore_path = ''

    def create_new_or_reuse_repo(self, git_path: str, git_remote: Optional[str] = None):
        """
        Create a new repository or reuse existing one.
        
        Args:
            git_path: Path to git repository
            git_remote: Remote URL (optional, for cloning)
        """
        self.gitignore_path = os.path.join(git_path, '.gitignore')
        if not os.path.exists(os.path.join(git_path, '.git')):
            if git_remote:
                if BaseGitHandler:
                    # Use sparetools-base if available
                    handler = BaseGitHandler()
                    handler.create_new_or_reuse_repo(git_path, git_remote)
                    self.repository = handler.repository
                else:
                    # Fallback to direct git command
                    execute_command(f'git clone {git_remote} {git_path}')
                    if HAS_GITPYTHON:
                        self.repository = Repo(git_path)
                    execute_command('git config --local core.autocrlf false', cwd=git_path)
            else:
                raise ValueError("git_remote required for new repository")
        else:
            if HAS_GITPYTHON:
                self.repository = Repo(git_path)
            else:
                log.warning("GitPython not available, limited functionality")
        
        if HAS_GITPYTHON and self.repository:
            self.repository.head.reset(index=True, working_tree=True)

    def open_repository(self, git_path: str):
        """
        Open an existing repository.
        
        Args:
            git_path: Path to git repository
        """
        if HAS_GITPYTHON:
            self.repository = Repo(git_path)
        else:
            log.warning("GitPython not available, cannot open repository")

    def add_to_git_ignore(self, path_list: list):
        """
        Add paths to .gitignore file.
        
        Args:
            path_list: List of paths to ignore
        """
        with open(self.gitignore_path, "w") as ignore:
            for ignore_element in path_list:
                ignore.write(ignore_element + '\n')

    def create_branch_and_switch(self, branch_name: str, branch_source: str = 'develop'):
        """
        Create a new branch and switch to it.
        
        Args:
            branch_name: Name of branch to create/switch to
            branch_source: Source branch for new branch
        """
        if not HAS_GITPYTHON or not self.repository:
            log.error("GitPython required for branch operations")
            return

        try:
            if self.repository.head.reference.name != branch_name:
                self.repository.git.checkout(branch_name)
                log.debug(f'Switching GIT branch {branch_name}')
            self.current_branch = self.repository.head.reference
        except Exception:
            self.current_branch = self.repository.create_head(branch_name, branch_source)
            log.debug(f'Creating GIT branch {branch_name}')

        if self.repository.head.reference != self.current_branch:
            self.repository.head.reference = self.current_branch
        self.repository.head.reset(index=True, working_tree=True)

    def commit_current_changes(self, message: str = '', date: str = '', author: str = '', email: str = ''):
        """
        Commit current changes.
        
        Args:
            message: Commit message
            date: Commit date (optional)
            author: Author name (optional)
            email: Author email (optional)
            
        Returns:
            Commit SHA if successful
        """
        if not HAS_GITPYTHON or not self.repository:
            log.error("GitPython required for commit operations")
            return None

        os.chdir(self.repository.working_dir)
        execute_command(f'git add -A {self.repository.working_dir}')
        
        if author and email:
            actor = Actor(author, email)
        else:
            actor = None
            
        commit_kwargs = {'skip_hooks': True}
        if date:
            commit_kwargs['author_date'] = date
            commit_kwargs['commit_date'] = date
        if actor:
            commit_kwargs['author'] = actor
            
        self.repository.index.commit(message, **commit_kwargs)
        return self.repository.head.commit.hexsha

    def diff_is_empty(self) -> bool:
        """
        Check if there are any uncommitted changes.
        
        Returns:
            True if no changes, False otherwise
        """
        if not self.repository:
            return True

        os.chdir(self.repository.working_dir)
        rc, _ = execute_command(f'git add -A')
        rc, _ = execute_command(f'git diff HEAD --exit-code --no-patch')
        return rc == 0

    def get_current_commit_sha(self) -> Optional[str]:
        """
        Get the current commit SHA.
        
        Returns:
            Commit SHA or None if not available
        """
        if not HAS_GITPYTHON or not self.repository:
            return None
        return self.repository.head.object.hexsha


def get_repository_sha(repository_path: str) -> Optional[str]:
    """
    Get the current commit SHA of a repository.
    
    Args:
        repository_path: Path to git repository

    Returns:
        Commit SHA or None if not available
    """
    git_handler = GitHandler()
    git_handler.open_repository(repository_path)
    return git_handler.get_current_commit_sha()
