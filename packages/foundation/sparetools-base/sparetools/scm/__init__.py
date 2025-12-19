"""
Source Control Management Module

Provides utilities for SCM operations (git, GitHub API, etc.)
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

from .github import (
    GitHubClient,
    GitHubAPIError,
    RateLimitExceeded,
    ResourceNotFoundError,
    AuthenticationError,
)

__all__ = [
    # Git utilities
    "GitHandler",
    "get_repository_sha",
    "clone_repository",
    "update_submodules",
    "get_remote_branches",
    "create_and_push_branch",
    "get_uncommitted_changes",
    "stash_changes",
    "apply_stash",

    # GitHub API client
    "GitHubClient",
    "GitHubAPIError",
    "RateLimitExceeded",
    "ResourceNotFoundError",
    "AuthenticationError",
]
