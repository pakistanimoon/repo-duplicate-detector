"""
Custom exceptions for repo-duplicate-detector.
"""


class RepoDetectorError(Exception):
    """Base exception for repo-duplicate-detector."""

    pass


class GitHubAPIError(RepoDetectorError):
    """Raised when GitHub API call fails."""

    pass


class InvalidRepositoryError(RepoDetectorError):
    """Raised when repository data is invalid."""

    pass


class RateLimitError(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded."""

    pass


class InvalidConfigError(RepoDetectorError):
    """Raised when configuration is invalid."""

    pass


class NetworkError(GitHubAPIError):
    """Raised when network connection fails."""

    pass