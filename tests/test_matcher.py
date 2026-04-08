"""
Tests for repository matcher.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from repo_duplicate_detector.matcher import RepoMatcher, RepoMatch
from repo_duplicate_detector.exceptions import InvalidRepositoryError


class TestRepoMatch:
    """Test RepoMatch class."""
    
    def test_repo_match_creation(self, mock_repo_data, mock_similar_repo_data, similarity_metrics):
        """Test creating a RepoMatch."""
        from repo_duplicate_detector.metrics import SimilarityResult
        
        similarity = SimilarityResult(
            overall_score=0.85,
            name_similarity=0.8,
            description_similarity=0.85,
            topic_similarity=0.9,
            language_match=1.0,
            contributor_overlap=0.5,
            activity_similarity=0.8,
        )
        
        match = RepoMatch(
            mock_repo_data,
            mock_similar_repo_data,
            similarity,
            "similar"
        )
        
        assert match.repo1 == mock_repo_data
        assert match.repo2 == mock_similar_repo_data
        assert match.similarity == similarity
        assert match.match_type == "similar"
    
    def test_repo_match_to_dict(self, mock_repo_data, mock_similar_repo_data, similarity_metrics):
        """Test converting RepoMatch to dictionary."""
        from repo_duplicate_detector.metrics import SimilarityResult
        
        similarity = SimilarityResult(
            overall_score=0.85,
            name_similarity=0.8,
            description_similarity=0.85,
            topic_similarity=0.9,
            language_match=1.0,
            contributor_overlap=0.5,
            activity_similarity=0.8,
        )
        
        match = RepoMatch(
            mock_repo_data,
            mock_similar_repo_data,
            similarity,
            "similar"
        )
        
        match_dict = match.to_dict()
        
        assert "repo1" in match_dict
        assert "repo2" in match_dict
        assert "similarity" in match_dict
        assert "match_type" in match_dict
        assert match_dict["repo1"]["full_name"] == "facebook/react"
        assert match_dict["repo2"]["full_name"] == "preactjs/preact"


class TestRepoMatcher:
    """Test RepoMatcher class."""
    
    def test_initialization(self, mock_config):
        """Test RepoMatcher initialization."""
        matcher = RepoMatcher(config=mock_config)
        assert matcher.config == mock_config
        assert matcher.fetcher is not None
        assert matcher.metrics is not None
    
    def test_parse_repo_url_owner_slash_repo(self, mock_matcher):
        """Test parsing owner/repo format."""
        from repo_duplicate_detector.utils import parse_repo_url
        
        result = parse_repo_url("facebook/react")
        assert result["owner"] == "facebook"
        assert result["repo"] == "react"
    
    def test_parse_repo_url_full_url(self, mock_matcher):
        """Test parsing full GitHub URL."""
        from repo_duplicate_detector.utils import parse_repo_url
        
        result = parse_repo_url("https://github.com/facebook/react")
        assert result["owner"] == "facebook"
        assert result["repo"] == "react"
    
    def test_parse_repo_url_invalid(self, mock_matcher):
        """Test parsing invalid repository URL."""
        from repo_duplicate_detector.utils import parse_repo_url
        
        with pytest.raises(InvalidRepositoryError):
            parse_repo_url("invalid_repo_format")
    
    @patch('repo_duplicate_detector.matcher.RepoMatcher._get_repo_data')
    @patch('repo_duplicate_detector.matcher.GitHubFetcher.search_repositories')
    def test_find_similar_repos(self, mock_search, mock_get_data, mock_matcher, mock_repo_data, mock_similar_repo_data):
        """Test finding similar repositories."""
        mock_get_data.return_value = mock_repo_data
        mock_search.return_value = [mock_similar_repo_data]
        
        matches = mock_matcher.find_similar_repos("facebook/react", max_results=10)
        
        assert isinstance(matches, list)
    
    @patch('repo_duplicate_detector.matcher.RepoMatcher._get_repo_data')
    def test_find_duplicates_in_list(self, mock_get_data, mock_matcher, mock_repo_data):
        """Test finding duplicates in a repository list."""
        mock_get_data.return_value = mock_repo_data
        
        repos = ["facebook/react", "preactjs/preact"]
        duplicates = mock_matcher.find_duplicates_in_list(repos)
        
        assert isinstance(duplicates, list)
    
    @patch('repo_duplicate_detector.matcher.GitHubFetcher.search_repositories')
    def test_analyze_ecosystem(self, mock_search, mock_matcher, mock_repo_data, mock_similar_repo_data):
        """Test ecosystem analysis."""
        mock_search.return_value = [mock_repo_data, mock_similar_repo_data]
        
        analysis = mock_matcher.analyze_ecosystem("javascript", language="python")
        
        assert "topic" in analysis
        assert "total_repos" in analysis
        assert "num_clusters" in analysis
        assert "fragmentation_score" in analysis