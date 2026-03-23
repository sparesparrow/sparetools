"""GitHub API tools for the repository cleanup MCP server.

Requires GITHUB_TOKEN environment variable.
Uses the GitHub CLI (gh) as primary backend, with PyGitHub as optional fallback.
"""

import json
import logging
import os
import subprocess
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _gh(*args: str, check: bool = True) -> str:
    """Run a GitHub CLI command and return stdout."""
    token = os.environ.get("GITHUB_TOKEN", "")
    env = {**os.environ}
    if token:
        env["GH_TOKEN"] = token
    result = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        env=env,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


class GitHubManager:
    """GitHub API tools exposed as MCP tool methods."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._token = os.environ.get("GITHUB_TOKEN", "")

    def _require_gh(self) -> None:
        """Raise if gh CLI is not available."""
        result = subprocess.run(["gh", "--version"], capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(
                "GitHub CLI (gh) is not installed. "
                "Install from https://cli.github.com or set GITHUB_TOKEN and install gh."
            )

    def list_prs(
        self,
        repo: Optional[str] = None,
        state: str = "open",
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """List pull requests for a repository.

        Args:
            repo: Repository in OWNER/NAME format. Defaults to current repo.
            state: 'open', 'closed', or 'merged'.
            limit: Maximum number of PRs to return.

        Returns:
            List of PR dicts with number, title, author, state, url.
        """
        self._require_gh()
        args = ["pr", "list", "--state", state, "--limit", str(limit), "--json",
                "number,title,author,state,url,headRefName,createdAt"]
        if repo:
            args += ["--repo", repo]
        raw = _gh(*args)
        return json.loads(raw) if raw else []

    def get_workflow_status(
        self,
        repo: Optional[str] = None,
        workflow: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get recent GitHub Actions workflow run statuses.

        Args:
            repo: Repository in OWNER/NAME format. Defaults to current repo.
            workflow: Workflow file name or ID to filter by (e.g. 'ci.yml').
            limit: Number of recent runs to return.

        Returns:
            List of run dicts with status, conclusion, name, url.
        """
        self._require_gh()
        args = ["run", "list", "--limit", str(limit), "--json",
                "status,conclusion,name,workflowName,url,createdAt,headBranch"]
        if repo:
            args += ["--repo", repo]
        if workflow:
            args += ["--workflow", workflow]
        raw = _gh(*args)
        return json.loads(raw) if raw else []

    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        repo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a GitHub issue.

        Args:
            title: Issue title.
            body: Issue body (markdown supported).
            labels: Optional list of label names.
            repo: Repository in OWNER/NAME format. Defaults to current repo.

        Returns:
            Dict with 'number' and 'url' of the created issue.
        """
        self._require_gh()
        args = ["issue", "create", "--title", title, "--body", body]
        if labels:
            args += ["--label", ",".join(labels)]
        if repo:
            args += ["--repo", repo]
        raw = _gh(*args)
        # gh issue create returns the URL of the new issue
        return {"url": raw}

    def trigger_workflow(
        self,
        workflow: str,
        ref: str = "main",
        repo: Optional[str] = None,
        inputs: Optional[Dict[str, str]] = None,
    ) -> str:
        """Trigger a GitHub Actions workflow dispatch.

        Args:
            workflow: Workflow file name (e.g. 'ci.yml').
            ref: Branch or tag to run on.
            repo: Repository in OWNER/NAME format.
            inputs: Optional workflow_dispatch input values.

        Returns:
            Confirmation message.
        """
        self._require_gh()
        args = ["workflow", "run", workflow, "--ref", ref]
        if repo:
            args += ["--repo", repo]
        if inputs:
            for key, value in inputs.items():
                args += ["--field", f"{key}={value}"]
        _gh(*args)
        return f"Workflow '{workflow}' triggered on ref '{ref}'."

    def get_release_info(
        self,
        tag: Optional[str] = None,
        repo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get information about the latest or a specific release.

        Args:
            tag: Release tag (e.g. 'v2.0.4'). Omit for latest.
            repo: Repository in OWNER/NAME format.

        Returns:
            Release dict with tag, name, body, url, publishedAt.
        """
        self._require_gh()
        args = ["release", "view"]
        if tag:
            args.append(tag)
        args += ["--json", "tagName,name,body,url,publishedAt,isDraft,isPrerelease"]
        if repo:
            args += ["--repo", repo]
        raw = _gh(*args)
        return json.loads(raw) if raw else {}
