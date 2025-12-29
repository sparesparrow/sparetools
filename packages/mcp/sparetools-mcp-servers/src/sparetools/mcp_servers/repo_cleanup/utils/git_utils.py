"""Git utility functions."""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

import git


class GitUtils:
    """Utility class for Git operations."""

    @staticmethod
    def is_git_repository(path: Path) -> bool:
        """Check if path is a Git repository.

        Args:
            path: Path to check

        Returns:
            True if path is a Git repository
        """
        try:
            git.Repo(path)
            return True
        except git.InvalidGitRepositoryError:
            return False

    @staticmethod
    def get_repo_status(repo_path: Path) -> dict:
        """Get comprehensive repository status.

        Args:
            repo_path: Path to Git repository

        Returns:
            Dictionary with repository status information
        """
        try:
            repo = git.Repo(repo_path)

            # Get status
            status = repo.git.status(porcelain=True)
            staged_files = []
            unstaged_files = []
            untracked_files = []

            for line in status.split('\n'):
                if line.strip():
                    status_code = line[:2]
                    filename = line[3:]

                    if status_code[0] in ['A', 'M', 'D']:
                        staged_files.append(filename)
                    if status_code[1] in ['M', 'D', '?']:
                        if status_code[1] == '?':
                            untracked_files.append(filename)
                        else:
                            unstaged_files.append(filename)

            # Get branch info
            try:
                current_branch = repo.active_branch.name
            except TypeError:
                current_branch = "detached HEAD"

            # Get remote info
            remotes = [remote.name for remote in repo.remotes]

            return {
                "is_clean": len(staged_files) == 0 and len(unstaged_files) == 0 and len(untracked_files) == 0,
                "current_branch": current_branch,
                "remotes": remotes,
                "staged_files": staged_files,
                "unstaged_files": unstaged_files,
                "untracked_files": untracked_files,
                "has_uncommitted_changes": bool(staged_files or unstaged_files or untracked_files)
            }

        except Exception as e:
            return {"error": str(e), "is_valid_repo": False}

    @staticmethod
    def get_file_size_in_repo(repo_path: Path, file_path: str) -> Optional[int]:
        """Get the size of a file as known to Git.

        Args:
            repo_path: Path to Git repository
            file_path: Relative path to file in repository

        Returns:
            File size in bytes, or None if not found
        """
        try:
            repo = git.Repo(repo_path)
            # Get file size from Git
            size_output = repo.git.cat_file("-s", f"HEAD:{file_path}")
            return int(size_output.strip())
        except (git.GitCommandError, ValueError):
            return None

    @staticmethod
    def add_files_to_index(repo_path: Path, files: List[str]) -> bool:
        """Add files to Git index.

        Args:
            repo_path: Path to Git repository
            files: List of file paths to add

        Returns:
            True if successful
        """
        try:
            repo = git.Repo(repo_path)
            repo.index.add(files)
            return True
        except Exception:
            return False

    @staticmethod
    def commit_changes(repo_path: Path, message: str, author_name: str = "Repo Cleanup",
                      author_email: str = "cleanup@automated.ai") -> Optional[str]:
        """Commit changes to repository.

        Args:
            repo_path: Path to Git repository
            message: Commit message
            author_name: Author name
            author_email: Author email

        Returns:
            Commit SHA if successful, None otherwise
        """
        try:
            repo = git.Repo(repo_path)

            # Create commit
            commit = repo.index.commit(
                message,
                author=git.Actor(author_name, author_email)
            )

            return str(commit.hexsha)
        except Exception:
            return None

    @staticmethod
    def push_changes(repo_path: Path, remote: str = "origin", branch: str = None) -> bool:
        """Push changes to remote repository.

        Args:
            repo_path: Path to Git repository
            remote: Remote name
            branch: Branch name (defaults to current branch)

        Returns:
            True if successful
        """
        try:
            repo = git.Repo(repo_path)

            if branch is None:
                try:
                    branch = repo.active_branch.name
                except TypeError:
                    return False  # Detached HEAD

            repo.remote(remote).push(branch)
            return True
        except Exception:
            return False

    @staticmethod
    def get_gitignore_content(repo_path: Path) -> Optional[str]:
        """Get content of .gitignore file.

        Args:
            repo_path: Path to Git repository

        Returns:
            Content of .gitignore file, or None if not found
        """
        gitignore_path = repo_path / ".gitignore"
        if gitignore_path.exists():
            return gitignore_path.read_text(encoding='utf-8')
        return None

    @staticmethod
    def update_gitignore(repo_path: Path, patterns: List[str],
                        comment: str = "# Added by repo-cleanup") -> bool:
        """Update .gitignore file with new patterns.

        Args:
            repo_path: Path to Git repository
            patterns: List of patterns to add
            comment: Comment to add before patterns

        Returns:
            True if successful
        """
        try:
            gitignore_path = repo_path / ".gitignore"

            # Read existing content
            existing_content = ""
            if gitignore_path.exists():
                existing_content = gitignore_path.read_text(encoding='utf-8')

            # Check if patterns already exist
            existing_lines = set(existing_content.strip().split('\n'))
            new_patterns = [p for p in patterns if p not in existing_lines]

            if not new_patterns:
                return True  # Nothing to add

            # Add new patterns
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                if existing_content and not existing_content.endswith('\n'):
                    f.write('\n')
                f.write(f"\n{comment}\n")
                for pattern in new_patterns:
                    f.write(f"{pattern}\n")

            return True
        except Exception:
            return False


# Global git utilities instance
git_utils = GitUtils()