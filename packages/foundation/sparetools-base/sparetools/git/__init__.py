"""
Git Operations Module

Provides utilities for git operations including clone, pull, submodule handling,
and tag/branch resolution.
"""

# Backward compatibility: import from scm/git.py
from ..scm.git import (
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