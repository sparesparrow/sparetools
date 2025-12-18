"""
Source Control Management Module

Provides utilities for SCM operations (git, etc.)
"""

from .git import (
    GitHandler,
    get_repository_sha,
    clone_repository,
    update_submodules,
    get_remote_branches,
    create_and_push_branch,
    get_uncommitted_changes,
    stash_changes,
    apply_stash,
)

__all__ = [
    "GitHandler",
    "get_repository_sha",
    "clone_repository",
    "update_submodules",
    "get_remote_branches",
    "create_and_push_branch",
    "get_uncommitted_changes",
    "stash_changes",
    "apply_stash",
]
