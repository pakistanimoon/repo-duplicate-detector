"""
Pytest configuration and fixtures for repo-duplicate-detector tests.
"""

import pytest
from unittest.mock import Mock

from repo_duplicate_detector.config import Config
from repo_duplicate_detector.fetcher import GitHubFetcher
from repo_duplicate_detector.matcher import RepoMatcher
from repo_duplicate_detector.metrics import SimilarityMetrics


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    return Config(
        github_token="test_token",
        timeout=10,
        max_requests_per_minute=60,
        retry_attempts=1,
        use_cache=True,
        cache_ttl=3600,
        overall_similarity_threshold=0.7,
    )


@pytest.fixture
def mock_repo_data():
    """Sample repository data for testing."""
    return {
        "id": 12345,
        "name": "react",
        "full_name": "facebook/react",
        "description": "A JavaScript library for building user interfaces",
        "html_url": "https://github.com/facebook/react",
        "stargazers_count": 200000,
        "forks_count": 40000,
        "open_issues_count": 1200,
        "language": "JavaScript",
        "topics": ["javascript", "react", "ui", "library"],
        "updated_at": "2024-01-15T10:30:00Z",
        "created_at": "2013-05-24T16:35:32Z",
        "activity": {
            "stars": 200000,
            "forks": 40000,
            "issues": 1200,
        },
        "contributors": ["gaearon", "sebmarkbage", "acdlite"],
    }


@pytest.fixture
def mock_similar_repo_data():
    """Sample similar repository data for testing."""
    return {
        "id": 54321,
        "name": "preact",
        "full_name": "preactjs/preact",
        "description": "Fast 3kB alternative to React with the same modern API",
        "html_url": "https://github.com/preactjs/preact",
        "stargazers_count": 35000,
        "forks_count": 1900,
        "open_issues_count": 150,
        "language": "JavaScript",
        "topics": ["javascript", "react", "ui", "alternative"],
        "updated_at": "2024-01-14T15:45:00Z",
        "created_at": "2015-07-24T12:00:00Z",
        "activity": {
            "stars": 35000,
            "forks": 1900,
            "issues": 150,
        },
        "contributors": ["developit", "marvinhagemeister"],
    }


@pytest.fixture
def mock_fetcher(mock_config):
    """Create a mock fetcher."""
    fetcher = GitHubFetcher(config=mock_config)
    return fetcher


@pytest.fixture
def mock_matcher(mock_config):
    """Create a mock matcher."""
    matcher = RepoMatcher(config=mock_config)
    return matcher


@pytest.fixture
def similarity_metrics():
    """Create a similarity metrics calculator."""
    return SimilarityMetrics(use_semantic=False)


@pytest.fixture
def mock_api_response():
    """Mock GitHub API response."""
    return {
        "items": [
            {
                "id": 12345,
                "name": "repo1",
                "full_name": "owner/repo1",
                "description": "Test repository",
                "html_url": "https://github.com/owner/repo1",
                "stargazers_count": 100,
                "forks_count": 10,
                "language": "Python",
                "topics": ["test", "demo"],
            },
            {
                "id": 12346,
                "name": "repo2",
                "full_name": "owner/repo2",
                "description": "Test repository 2",
                "html_url": "https://github.com/owner/repo2",
                "stargazers_count": 50,
                "forks_count": 5,
                "language": "Python",
                "topics": ["test"],
            },
        ],
        "total_count": 2,
    }
