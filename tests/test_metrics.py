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


class TestLanguageSimilarity:
    """Test language similarity calculation."""
    
    def test_same_language(self, similarity_metrics):
        """Test repositories with same language."""
        score = similarity_metrics.calculate_language_similarity("Python", "python")
        assert score == 1.0
    
    def test_different_language(self, similarity_metrics):
        """Test repositories with different languages."""
        score = similarity_metrics.calculate_language_similarity("Python", "JavaScript")
        assert score == 0.0
    
    def test_none_languages(self, similarity_metrics):
        """Test with None languages."""
        score = similarity_metrics.calculate_language_similarity(None, None)
        assert score == 1.0
    
    def test_one_none_language(self, similarity_metrics):
        """Test with one None language."""
        score = similarity_metrics.calculate_language_similarity("Python", None)
        assert score == 0.0


class TestContributorOverlap:
    """Test contributor overlap calculation."""
    
    def test_exact_match(self, similarity_metrics):
        """Test exact contributor match."""
        contribs1 = ["user1", "user2", "user3"]
        contribs2 = ["user1", "user2", "user3"]
        score = similarity_metrics.calculate_contributor_overlap(contribs1, contribs2)
        assert score == 1.0
    
    def test_partial_overlap(self, similarity_metrics):
        """Test partial contributor overlap."""
        contribs1 = ["user1", "user2", "user3"]
        contribs2 = ["user1", "user4", "user5"]
        score = similarity_metrics.calculate_contributor_overlap(contribs1, contribs2)
        assert 0.3 <= score < 1.0
    
    def test_no_overlap(self, similarity_metrics):
        """Test no contributor overlap."""
        contribs1 = ["user1", "user2"]
        contribs2 = ["user3", "user4"]
        score = similarity_metrics.calculate_contributor_overlap(contribs1, contribs2)
        assert score == 0.0
    
    def test_case_insensitive(self, similarity_metrics):
        """Test case-insensitive contributor matching."""
        contribs1 = ["User1", "User2"]
        contribs2 = ["user1", "user2"]
        score = similarity_metrics.calculate_contributor_overlap(contribs1, contribs2)
        assert score == 1.0


class TestActivitySimilarity:
    """Test activity similarity calculation."""
    
    def test_identical_activity(self, similarity_metrics):
        """Test identical activity profiles."""
        activity1 = {"stars": 1000, "forks": 100, "issues": 50}
        activity2 = {"stars": 1000, "forks": 100, "issues": 50}
        score = similarity_metrics.calculate_activity_similarity(activity1, activity2)
        assert score > 0.95
    
    def test_similar_activity(self, similarity_metrics):
        """Test similar activity profiles."""
        activity1 = {"stars": 1000, "forks": 100, "issues": 50}
        activity2 = {"stars": 900, "forks": 90, "issues": 60}
        score = similarity_metrics.calculate_activity_similarity(activity1, activity2)
        assert 0.8 <= score <= 1.0
    
    def test_different_activity(self, similarity_metrics):
        """Test different activity profiles."""
        activity1 = {"stars": 1000, "forks": 100, "issues": 50}
        activity2 = {"stars": 10, "forks": 1, "issues": 5}
        score = similarity_metrics.calculate_activity_similarity(activity1, activity2)
        assert 0.0 <= score < 0.8


class TestOverallSimilarity:
    """Test overall similarity calculation."""
    
    def test_identical_repos(self, similarity_metrics, mock_repo_data):
        """Test similarity between identical repositories."""
        result = similarity_metrics.calculate_overall_similarity(
            mock_repo_data,
            mock_repo_data
        )
        assert result.overall_score > 0.95
        assert isinstance(result, SimilarityResult)
    
    def test_very_similar_repos(self, similarity_metrics, mock_repo_data, mock_similar_repo_data):
        """Test similarity between very similar repositories."""
        result = similarity_metrics.calculate_overall_similarity(
            mock_repo_data,
            mock_similar_repo_data
        )
        assert 0.5 <= result.overall_score <= 1.0
        assert result.name_similarity >= 0.0
        assert result.description_similarity >= 0.0
        assert result.topic_similarity >= 0.0
    
    def test_custom_weights(self, similarity_metrics, mock_repo_data):
        """Test overall similarity with custom weights."""
        custom_weights = {
            "name": 0.5,
            "description": 0.2,
            "topics": 0.2,
            "language": 0.1,
            "contributors": 0.0,
            "activity": 0.0,
        }
        result = similarity_metrics.calculate_overall_similarity(
            mock_repo_data,
            mock_repo_data,
            weights=custom_weights
        )
        assert result.overall_score > 0.9