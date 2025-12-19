"""
GitHub API Client with Resilience Layer

Production-grade GitHub API client that handles rate limits, authentication errors,
timeouts, network issues, and pagination using tenacity for retries.

This module addresses common GitHub API failure modes:
- Rate limits (primary and secondary)
- Authentication errors (expired/invalid tokens)
- Timeouts and network issues
- Pagination limits (30-item default)
- Error classification (transient vs permanent)

Usage:
    from sparetools.scm.github import GitHubClient

    client = GitHubClient()  # Uses GITHUB_TOKEN env var
    try:
        issues = list(client.get_all_items("https://api.github.com/repos/owner/repo/issues"))
        print(f"Found {len(issues)} issues")
    except GitHubAPIError as e:
        print(f"GitHub API error: {e}")
"""

import os
import time
import logging
import requests
from typing import Dict, List, Any, Optional, Iterator
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

# Optional dependencies with graceful fallbacks
try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_random_exponential,
        retry_if_exception_type,
        before_sleep_log
    )
    HAS_TENACITY = True
except ImportError:
    HAS_TENACITY = False
    logger.warning("tenacity not available, retry functionality will be limited")


class GitHubAPIError(Exception):
    """Base class for all GitHub API errors."""
    pass


class RateLimitExceeded(GitHubAPIError):
    """Raised when primary or secondary rate limits are hit."""
    pass


class ResourceNotFoundError(GitHubAPIError):
    """Raised on 404 errors (distinct from auth issues)."""
    pass


class AuthenticationError(GitHubAPIError):
    """Raised on 401 errors (invalid/expired tokens)."""
    pass


class GitHubClient:
    """
    Robust GitHub API client with automatic retry logic and rate limit handling.

    Features:
    - Automatic rate limit detection and handling
    - Exponential backoff for transient errors
    - Pagination support
    - Authentication error detection
    - Configurable timeouts
    """

    def __init__(self, token: Optional[str] = None, timeout: int = 10):
        """
        Initialize GitHub API client.

        Args:
            token: GitHub personal access token. If None, uses GITHUB_TOKEN env var.
            timeout: Request timeout in seconds (default: 10)
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            logger.warning("No GitHub token provided. Some requests may fail due to rate limits.")

        self.timeout = timeout
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self):
        """Configure the requests session with proper headers."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "sparetools/1.0 (sparetools-github-client)"
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        self.session.headers.update(headers)

    def _handle_rate_limits(self, response: requests.Response):
        """
        Analyze response headers for rate limit information and handle accordingly.

        Args:
            response: The response object to analyze

        Raises:
            RateLimitExceeded: If rate limits are hit
        """
        if response.status_code in (403, 429):
            msg = response.json().get("message", "").lower() if response.headers.get('content-type', '').startswith('application/json') else ""

            # Secondary Rate Limit (most common cause of "always failing")
            if "secondary rate limit" in msg or "retry-after" in response.headers:
                wait_seconds = int(response.headers.get("Retry-After", 60))
                logger.warning(f"Hit Secondary Rate Limit. Waiting {wait_seconds}s before retry.")
                time.sleep(wait_seconds)
                raise RateLimitExceeded("Secondary rate limit hit - automatic retry initiated")

            # Primary Rate Limit
            remaining = int(response.headers.get("x-ratelimit-remaining", 1))
            if remaining == 0:
                reset_time = int(response.headers.get("x-ratelimit-reset", time.time() + 60))
                sleep_time = max(0, reset_time - time.time())
                logger.warning(f"Hit Primary Rate Limit. Reset in {sleep_time}s.")
                time.sleep(sleep_time + 1)  # +1s buffer
                raise RateLimitExceeded("Primary rate limit hit - waited for reset")

    def _is_transient_error(self, exception: Exception) -> bool:
        """
        Determine if an error is transient and should be retried.

        Args:
            exception: The exception to analyze

        Returns:
            True if the error is transient (network, 5xx, rate limit)
        """
        if isinstance(exception, RateLimitExceeded):
            return True

        if isinstance(exception, requests.RequestException):
            response = getattr(exception, 'response', None)
            if response is None:
                # Network error (no response) - retryable
                return True
            # 5xx server errors are retryable
            return 500 <= response.status_code < 600

        return False

    def fetch(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform a robust HTTP GET request to the GitHub API.

        Automatically handles:
        - Rate limits (primary and secondary)
        - Network errors and timeouts
        - 5xx server errors
        - Exponential backoff retries

        Args:
            url: GitHub API URL to fetch
            params: Optional query parameters

        Returns:
            Parsed JSON response

        Raises:
            AuthenticationError: For 401 errors (invalid/expired token)
            ResourceNotFoundError: For 404 errors
            GitHubAPIError: For other API errors
        """
        try:
            # Use tenacity for retry logic if available
            if HAS_TENACITY:
                return self._fetch_with_tenacity(url, params)
            else:
                return self._fetch_basic(url, params)

        except requests.HTTPError as e:
            response = e.response

            # Classify HTTP errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired GitHub token") from e
            elif response.status_code == 404:
                raise ResourceNotFoundError(f"Resource not found: {url}") from e
            else:
                raise GitHubAPIError(f"GitHub API error {response.status_code}: {response.text}") from e

        except requests.RequestException as e:
            raise GitHubAPIError(f"Network error: {e}") from e

    def _fetch_basic(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Basic fetch implementation without tenacity."""
        response = self.session.get(url, params=params, timeout=self.timeout)

        # Check for rate limits first
        self._handle_rate_limits(response)

        response.raise_for_status()
        return response.json()

    def _fetch_with_tenacity(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetch implementation with tenacity retry logic."""

        @retry(
            retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout, RateLimitExceeded, requests.HTTPError)),
            wait=wait_random_exponential(multiplier=1, max=60),
            stop=stop_after_attempt(5),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            retry_error_callback=lambda retry_state: retry_state.outcome.result()
        )
        def _do_request():
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)

                # Check for rate limits before raising HTTP errors
                self._handle_rate_limits(response)

                response.raise_for_status()
                return response.json()

            except requests.HTTPError as e:
                # Re-raise HTTP errors to let the main fetch method handle them
                # But first check if it's a 5xx error (retryable)
                if 500 <= e.response.status_code < 600:
                    logger.warning(f"Server error {e.response.status_code}, will retry")
                    raise
                # Other HTTP errors are not retryable
                raise

        return _do_request()

    def get_all_items(self, url: str, params: Optional[Dict[str, Any]] = None) -> Iterator[Dict[str, Any]]:
        """
        Fetch all items from a paginated GitHub API endpoint.

        Automatically handles pagination by following Link headers.
        Uses per_page=100 to maximize efficiency (vs default 30).

        Args:
            url: GitHub API URL to fetch
            params: Optional query parameters

        Yields:
            Individual items from all pages

        Raises:
            Same exceptions as fetch()
        """
        params = params or {}
        params.setdefault("per_page", 100)  # Maximize page size

        while url:
            data = self.fetch(url, params)

            # Yield items from this page
            if isinstance(data, list):
                yield from data
            else:
                # Some endpoints return objects with item arrays
                # For now, assume it's a list or has an 'items' key
                if 'items' in data:
                    yield from data['items']
                else:
                    yield data

            # Check for next page in Link header
            url = self._get_next_page_url()
            params = {}  # Params are usually encoded in the next URL

    def _get_next_page_url(self) -> Optional[str]:
        """
        Parse the Link header to find the next page URL.

        Returns:
            Next page URL if available, None otherwise
        """
        link_header = self.session.headers.get("Link", "")
        if not link_header:
            return None

        # Parse Link header (format: <url>; rel="next", <url>; rel="prev")
        links = requests.utils.parse_header_links(link_header)
        for link in links:
            if link.get("rel") == "next":
                return link.get("url")

        return None

    def check_token_scopes(self) -> Dict[str, Any]:
        """
        Debug utility to check token authentication and scopes.

        Returns:
            Dictionary with token information

        Raises:
            GitHubAPIError: If token validation fails
        """
        try:
            # Get user information
            user_data = self.fetch("https://api.github.com/user")

            # Check rate limit status
            rate_data = self.fetch("https://api.github.com/rate_limit")

            # Get scopes from response headers (if available)
            scopes = self.session.headers.get("x-oauth-scopes", "Not available")

            return {
                "authenticated": True,
                "user": user_data.get("login", "Unknown"),
                "scopes": scopes,
                "rate_limit": rate_data.get("rate", {}),
                "token_type": "oauth" if "Bearer" in str(self.session.headers.get("Authorization", "")) else "unknown"
            }

        except AuthenticationError:
            return {
                "authenticated": False,
                "error": "Invalid or expired token",
                "user": None,
                "scopes": None,
                "rate_limit": None
            }

        except GitHubAPIError as e:
            return {
                "authenticated": False,
                "error": str(e),
                "user": None,
                "scopes": None,
                "rate_limit": None
            }
