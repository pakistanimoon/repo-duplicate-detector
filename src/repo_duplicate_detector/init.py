"""
Repo Duplicate Detector - Detect duplicate and similar GitHub repositories.

This package provides tools to:
- Find similar repositories on GitHub
- Analyze ecosystem fragmentation
- Detect abandoned forks
- Match developers to projects
"""

__version__ = "0.1.0"
__author__ = "pakistanimoon"
__license__ = "MIT"

from .matcher import RepoMatcher
from .fetcher import GitHubFetcher
from .metrics import SimilarityMetrics
from .exceptions import (
    RepoDetectorError,
    GitHubAPIError,
    InvalidRepositoryError,
    RateLimitError,
)

__all__ = [
    "RepoMatcher",
    "GitHubFetcher",
    "SimilarityMetrics",
    "RepoDetectorError",
    "GitHubAPIError",
    "InvalidRepositoryError",
    "RateLimitError",
]
