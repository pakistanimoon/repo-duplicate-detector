"""
GitHub API fetcher with rate limiting and caching.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .config import Config
from .exceptions import (
    GitHubAPIError,
    InvalidRepositoryError,
    NetworkError,
    RateLimitError,
)
from .utils import parse_repo_url

logger = logging.getLogger(__name__)


class CacheEntry:
    """Simple cache entry with TTL."""

    def __init__(self, data: Any, ttl: int = 3600):
        self.data = data
        self.created_at = datetime.now()
        self.ttl = ttl

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)


class GitHubFetcher:
    """Fetch repository data from GitHub API."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize GitHub API fetcher.

        Args:
            config: Configuration object
        """
        self.config = config or Config.from_env()
        self.cache: Dict[str, CacheEntry] = {}
        self.session = self._create_session()
        self.rate_limit_remaining: Optional[int] = None
        self.rate_limit_reset: Optional[int] = None

    def _create_session(self) -> requests.Session:
        """Create and configure requests session."""
        session = requests.Session()

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "repo-duplicate-detector/0.1.0",
        }

        if self.config.github_token:
            headers["Authorization"] = f"token {self.config.github_token}"

        session.headers.update(headers)
        return session

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """Handle rate limit headers from response."""
        self.rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
        self.rate_limit_reset = int(response.headers.get("X-RateLimit-Reset", 0))

        if self.rate_limit_remaining == 0:
            wait_time = (self.rate_limit_reset or 0) - int(time.time())
            if wait_time > 0:
                logger.warning("Rate limit reached. Waiting %s seconds.", wait_time)
                raise RateLimitError(
                    f"GitHub API rate limit exceeded. Reset at {self.rate_limit_reset}"
                )

    def _get_cache_key(self, method: str, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key for request."""
        key_parts = [method, url]
        if params:
            key_parts.append(json.dumps(params, sort_keys=True))
        return "|".join(key_parts)

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get data from cache if not expired."""
        if not self.config.use_cache:
            return None

        entry = self.cache.get(key)
        if entry and not entry.is_expired():
            logger.debug("Cache hit for %s", key)
            return entry.data

        if entry:
            del self.cache[key]

        return None

    def _set_cache(self, key: str, data: Any) -> None:
        """Set data in cache."""
        if self.config.use_cache:
            self.cache[key] = CacheEntry(data, self.config.cache_ttl)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.RequestException, RateLimitError)),
        reraise=True,
    )
    def _make_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            params: Query parameters
            json_data: JSON body data

        Returns:
            Response data as dictionary

        Raises:
            GitHubAPIError: If API request fails
            RateLimitError: If rate limit is exceeded
            NetworkError: If network connection fails
        """
        cache_key = self._get_cache_key(method, url, params)
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=self.config.timeout,
            )

            self._handle_rate_limit(response)

            if response.status_code == 404:
                raise InvalidRepositoryError(f"Resource not found: {url}")

            if response.status_code == 403:
                raise RateLimitError("GitHub API rate limit exceeded or access forbidden")

            response.raise_for_status()

            data: Dict[str, Any] = response.json() if response.text else {}

            self._set_cache(cache_key, data)

            return data

        except requests.ConnectionError as exc:
            raise NetworkError(f"Network connection failed: {exc}") from exc
        except requests.Timeout as exc:
            raise NetworkError(f"Request timeout: {exc}") from exc
        except requests.HTTPError as exc:
            raise GitHubAPIError(f"HTTP error occurred: {exc}") from exc

    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get repository information.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Repository data dictionary
        """
        url = f"{self.config.api_base_url}/repos/{owner}/{repo}"
        return self._make_request("GET", url)

    def get_repository_topics(self, owner: str, repo: str) -> List[str]:
        """
        Get repository topics.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            List of topic names
        """
        url = f"{self.config.api_base_url}/repos/{owner}/{repo}/topics"
        headers = {"Accept": "application/vnd.github.mercy-preview+json"}

        try:
            response = self.session.request(
                "GET",
                url,
                headers=headers,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("names", [])
        except Exception as exc:
            logger.warning("Failed to get topics for %s/%s: %s", owner, repo, exc)
            return []

    def get_repository_contributors(self, owner: str, repo: str, per_page: int = 100) -> List[str]:
        """
        Get list of repository contributors.

        Args:
            owner: Repository owner
            repo: Repository name
            per_page: Results per page (max 100)

        Returns:
            List of contributor usernames
        """
        url = f"{self.config.api_base_url}/repos/{owner}/{repo}/contributors"

        contributors: List[str] = []
        page = 1

        while len(contributors) < per_page:
            try:
                data = self._make_request("GET", url, params={"page": page, "per_page": per_page})

                if isinstance(data, list):
                    for item in data:
                        if "login" in item:
                            contributors.append(item["login"])
                else:
                    break

                if len(data) < per_page:
                    break

                page += 1
            except Exception as exc:
                logger.warning("Failed to get page %s of contributors: %s", page, exc)
                break

        return contributors[:per_page]

    def search_repositories(
        self,
        query: str,
        sort: str = "stars",
        order: str = "desc",
        per_page: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Search repositories on GitHub.

        Args:
            query: Search query
            sort: Sort field (stars, forks, updated, etc.)
            order: Sort order (asc, desc)
            per_page: Results per page (max 100)

        Returns:
            List of repository data dictionaries
        """
        url = f"{self.config.api_base_url}/search/repositories"

        data = self._make_request(
            "GET",
            url,
            params={
                "q": query,
                "sort": sort,
                "order": order,
                "per_page": min(per_page, 100),
            },
        )

        return data.get("items", [])

    def search_users(
        self,
        query: str,
        sort: str = "followers",
        order: str = "desc",
        per_page: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Search users on GitHub.

        Args:
            query: Search query
            sort: Sort field (followers, repositories, joined, etc.)
            order: Sort order (asc, desc)
            per_page: Results per page (max 100)

        Returns:
            List of user data dictionaries
        """
        url = f"{self.config.api_base_url}/search/users"

        data = self._make_request(
            "GET",
            url,
            params={
                "q": query,
                "sort": sort,
                "order": order,
                "per_page": min(per_page, 100),
            },
        )

        return data.get("items", [])

    def get_user_repositories(self, username: str, per_page: int = 30) -> List[Dict[str, Any]]:
        """
        Get repositories for a user.

        Args:
            username: GitHub username
            per_page: Results per page (max 100)

        Returns:
            List of repository data dictionaries
        """
        url = f"{self.config.api_base_url}/users/{username}/repos"

        repos: List[Dict[str, Any]] = []
        page = 1

        while len(repos) < per_page:
            try:
                data = self._make_request(
                    "GET",
                    url,
                    params={"page": page, "per_page": per_page, "type": "all"},
                )

                if isinstance(data, list):
                    repos.extend(data)
                else:
                    break

                if len(data) < per_page:
                    break

                page += 1
            except Exception as exc:
                logger.warning("Failed to get page %s of user repos: %s", page, exc)
                break

        return repos[:per_page]

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current API rate limit status.

        Returns:
            Rate limit information dictionary
        """
        url = f"{self.config.api_base_url}/rate_limit"

        try:
            data = self._make_request("GET", url)
            return {
                "remaining": self.rate_limit_remaining,
                "reset": self.rate_limit_reset,
                "reset_datetime": (
                    datetime.fromtimestamp(self.rate_limit_reset) if self.rate_limit_reset else None
                ),
                "limit_data": data,
            }
        except Exception as exc:
            logger.warning("Failed to get rate limit status: %s", exc)
            return {}

    def close(self) -> None:
        """Close the requests session."""
        self.session.close()

    def __enter__(self) -> "GitHubFetcher":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
