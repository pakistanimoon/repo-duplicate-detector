"""
Tests for repository matcher.
"""

import pytest
from unittest.mock import Mock, patch

from repo_duplicate_detector.matcher import RepoMatch, RepoMatcher
from repo_duplicate_detector.metrics import SimilarityResult
from repo_duplicate_detector.exceptions import InvalidRepositoryError


class TestRepoMatch:
    """Test RepoMatch class."""

    def test_repo_match_creation(self, mock_repo_data, mock_similar_repo_data):
        """Test creating a RepoMatch."""
        similarity = SimilarityResult(
            overall_score=0.85,
            name_similarity=0.8,
            description_similarity=0.85,
            topic_similarity=0.9,
            language_match=1.0,
            contributor_overlap=0.5,
            activity_similarity=0.8,
        )

        match = RepoMatch(mock_repo_data, mock_similar_repo_data, similarity, "similar")

        assert match.repo1 == mock_repo_data
        assert match.repo2 == mock_similar_repo_data
        assert match.similarity == similarity
        assert match.match_type == "similar"

    def test_repo_match_to_dict(self, mock_repo_data, mock_similar_repo_data):
        """Test converting RepoMatch to dictionary."""
        similarity = SimilarityResult(
            overall_score=0.85,
            name_similarity=0.8,
            description_similarity=0.85,
            topic_similarity=0.9,
            language_match=1.0,
            contributor_overlap=0.5,
            activity_similarity=0.8,
        )

        match = RepoMatch(mock_repo_data, mock_similar_repo_data, similarity, "similar")
        match_dict = match.to_dict()

        assert "repo1" in match_dict
        assert "repo2" in match_dict
        assert "similarity" in match_dict
        assert "match_type" in match_dict


class TestRepoMatcher:
    """Test RepoMatcher class."""

    def test_initialization(self, mock_config):
        """Test RepoMatcher initialization."""
        matcher = RepoMatcher(config=mock_config)
        assert matcher.config == mock_config
        assert matcher.fetcher is not None
        assert matcher.metrics is not None