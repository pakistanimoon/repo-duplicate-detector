"""
Tests for similarity metrics calculation.
"""

import pytest

from repo_duplicate_detector.metrics import SimilarityMetrics, SimilarityResult


class TestNameSimilarity:
    """Test name similarity calculation."""

    def test_exact_match(self, similarity_metrics):
        """Test exact name match."""
        score = similarity_metrics.calculate_name_similarity("react", "react")
        assert score == 1.0

    def test_case_insensitive(self, similarity_metrics):
        """Test case-insensitive matching."""
        score = similarity_metrics.calculate_name_similarity("React", "REACT")
        assert score == 1.0

    def test_normalized_match(self, similarity_metrics):
        """Test matching with normalization."""
        score = similarity_metrics.calculate_name_similarity("React-JS", "react_js")
        assert score >= 0.9

    def test_substring_match(self, similarity_metrics):
        """Test substring matching."""
        score = similarity_metrics.calculate_name_similarity("react", "preact")
        assert score > 0.5

    def test_no_match(self, similarity_metrics):
        """Test completely different names."""
        score = similarity_metrics.calculate_name_similarity("react", "django")
        assert score < 0.5

    def test_empty_string(self, similarity_metrics):
        """Test with empty strings."""
        score = similarity_metrics.calculate_name_similarity("", "react")
        assert score == 0.0


class TestTopicSimilarity:
    """Test topic similarity calculation."""

    def test_exact_match(self, similarity_metrics):
        """Test exact topic match."""
        topics1 = ["javascript", "react", "ui"]
        topics2 = ["javascript", "react", "ui"]
        score = similarity_metrics.calculate_topic_similarity(topics1, topics2)
        assert score == 1.0

    def test_partial_match(self, similarity_metrics):
        """Test partial topic overlap."""
        topics1 = ["javascript", "react", "ui"]
        topics2 = ["javascript", "react", "framework"]
        score = similarity_metrics.calculate_topic_similarity(topics1, topics2)
        assert 0.5 <= score < 1.0

    def test_no_match(self, similarity_metrics):
        """Test no topic overlap."""
        topics1 = ["javascript", "react"]
        topics2 = ["python", "django"]
        score = similarity_metrics.calculate_topic_similarity(topics1, topics2)
        assert score == 0.0

    def test_empty_lists(self, similarity_metrics):
        """Test with empty topic lists."""
        score = similarity_metrics.calculate_topic_similarity([], [])
        assert score == 1.0

    def test_case_insensitive(self, similarity_metrics):
        """Test case-insensitive topic matching."""
        topics1 = ["JavaScript", "React"]
        topics2 = ["javascript", "react"]
        score = similarity_metrics.calculate_topic_similarity(topics1, topics2)
        assert score == 1.0