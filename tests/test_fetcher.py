"""
Tests for GitHub API fetcher.
"""

from unittest.mock import Mock, patch

import pytest

from repo_duplicate_detector.exceptions import InvalidRepositoryError
from repo_duplicate_detector.fetcher import CacheEntry, GitHubFetcher


class TestCacheEntry:
    """Test CacheEntry class."""

    def test_cache_entry_not_expired(self):
        """Test cache entry that hasn't expired."""
        entry = CacheEntry({"data": "test"}, ttl=3600)
        assert not entry.is_expired()

    def test_cache_entry_expired(self):
        """Test expired cache entry."""
        from datetime import datetime, timedelta

        entry = CacheEntry({"data": "test"}, ttl=0)
        entry.created_at = datetime.now() - timedelta(seconds=10)
        assert entry.is_expired()


class TestGitHubFetcher:
    """Test GitHub API fetcher."""

    def test_initialization(self, mock_config):
        """Test fetcher initialization."""
        fetcher = GitHubFetcher(config=mock_config)
        assert fetcher.config == mock_config
        assert fetcher.session is not None

    def test_cache_key_generation(self, mock_config):
        """Test cache key generation."""
        fetcher = GitHubFetcher(config=mock_config)

        key1 = fetcher._get_cache_key("GET", "http://api.github.com/repos/owner/repo")
        key2 = fetcher._get_cache_key("GET", "http://api.github.com/repos/owner/repo")
        key3 = fetcher._get_cache_key("GET", "http://api.github.com/repos/other/repo")

        assert key1 == key2
        assert key1 != key3

    @patch("repo_duplicate_detector.fetcher.requests.Session.request")
    def test_make_request_success(self, mock_request, mock_config):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"test": "data"}'
        mock_response.json.return_value = {"test": "data"}
        mock_response.headers = {
            "X-RateLimit-Remaining": "60",
            "X-RateLimit-Reset": "1234567890",
        }
        mock_request.return_value = mock_response

        fetcher = GitHubFetcher(config=mock_config)
        result = fetcher._make_request("GET", "http://test.com/api")

        assert result == {"test": "data"}
        assert fetcher.rate_limit_remaining == 60
