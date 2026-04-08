"""
Repository matcher for finding duplicates and similar repositories.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .config import Config
from .fetcher import GitHubFetcher
from .metrics import SimilarityMetrics, SimilarityResult
from .utils import parse_repo_url

logger = logging.getLogger(__name__)


class RepoMatch:
    """Result of repository matching."""

    def __init__(
        self,
        repo1: Dict[str, Any],
        repo2: Dict[str, Any],
        similarity: SimilarityResult,
        match_type: str = "similar",
    ):
        self.repo1 = repo1
        self.repo2 = repo2
        self.similarity = similarity
        self.match_type = match_type

    def __repr__(self) -> str:
        return (
            f"RepoMatch({self.repo1['full_name']} <-> {self.repo2['full_name']}, "
            f"similarity={self.similarity.overall_score:.2%})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "repo1": {
                "full_name": self.repo1.get("full_name"),
                "url": self.repo1.get("html_url"),
                "stars": self.repo1.get("stargazers_count", 0),
                "forks": self.repo1.get("forks_count", 0),
            },
            "repo2": {
                "full_name": self.repo2.get("full_name"),
                "url": self.repo2.get("html_url"),
                "stars": self.repo2.get("stargazers_count", 0),
                "forks": self.repo2.get("forks_count", 0),
            },
            "similarity": {
                "overall": self.similarity.overall_score,
                "name": self.similarity.name_similarity,
                "description": self.similarity.description_similarity,
                "topics": self.similarity.topic_similarity,
                "language": self.similarity.language_match,
                "contributors": self.similarity.contributor_overlap,
                "activity": self.similarity.activity_similarity,
            },
            "match_type": self.match_type,
        }


class RepoMatcher:
    """Main class for finding duplicate and similar repositories."""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize repository matcher.

        Args:
            config: Configuration object
        """
        self.config = config or Config.from_env()
        self.fetcher = GitHubFetcher(self.config)
        self.metrics = SimilarityMetrics(
            use_semantic=self.config.use_semantic_matching,
            model_name=self.config.semantic_model,
        )
        self._repo_cache: Dict[str, Dict[str, Any]] = {}

    def _get_repo_data(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get repository data with caching.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Repository data dictionary
        """
        cache_key = f"{owner}/{repo}"

        if cache_key in self._repo_cache:
            return self._repo_cache[cache_key]

        try:
            repo_data = self.fetcher.get_repository(owner, repo)

            repo_data["topics"] = self.fetcher.get_repository_topics(owner, repo)
            repo_data["contributors"] = self.fetcher.get_repository_contributors(
                owner, repo, per_page=20
            )
            repo_data["activity"] = {
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "issues": repo_data.get("open_issues_count", 0),
            }

            self._repo_cache[cache_key] = repo_data
            return repo_data

        except Exception as exc:
            logger.error("Failed to get repository data for %s/%s: %s", owner, repo, exc)
            raise

    def find_similar_repos(
        self,
        repo: str,
        language: Optional[str] = None,
        threshold: Optional[float] = None,
        max_results: Optional[int] = None,
    ) -> List[RepoMatch]:
        """
        Find repositories similar to the given repository.

        Args:
            repo: Repository in format "owner/repo" or full URL
            language: Filter by programming language
            threshold: Similarity threshold (0-1)
            max_results: Maximum number of results

        Returns:
            List of RepoMatch objects sorted by similarity

        Raises:
            InvalidRepositoryError: If repository format is invalid
            GitHubAPIError: If GitHub API call fails
        """
        parsed = parse_repo_url(repo)
        owner, repo_name = parsed["owner"], parsed["repo"]

        threshold = threshold or self.config.overall_similarity_threshold
        max_results = max_results or self.config.max_results

        logger.info("Finding similar repos to %s/%s", owner, repo_name)

        source_repo = self._get_repo_data(owner, repo_name)

        query_parts: List[str] = []

        if source_repo.get("language"):
            query_parts.append(f"language:{source_repo['language']}")
        elif language:
            query_parts.append(f"language:{language}")

        if source_repo.get("topics"):
            topic = source_repo["topics"][0]
            query_parts.append(f"topic:{topic}")

        stars = source_repo.get("stargazers_count", 0)
        stars_min = max(0, stars - 100)
        stars_max = stars + 100
        query_parts.append(f"stars:{stars_min}..{stars_max}")

        search_query = " ".join(query_parts) if query_parts else f"language:{language or 'python'}"

        try:
            results = self.fetcher.search_repositories(
                search_query, per_page=min(max_results * 2, 100)
            )
        except Exception as exc:
            logger.warning("Search failed with query '%s': %s", search_query, exc)
            return []

        matches: List[RepoMatch] = []

        for result in results:
            if result["full_name"] == source_repo["full_name"]:
                continue

            similarity = self.metrics.calculate_overall_similarity(source_repo, result)

            if similarity.overall_score >= threshold:
                match_type = self._determine_match_type(source_repo, result, similarity)
                match = RepoMatch(source_repo, result, similarity, match_type)
                matches.append(match)

        matches.sort(key=lambda m: m.similarity.overall_score, reverse=True)

        return matches[:max_results]

    def find_duplicates_in_list(
        self,
        repos: List[str],
        threshold: Optional[float] = None,
    ) -> List[Tuple[str, str, RepoMatch]]:
        """
        Find duplicate repositories in a list.

        Args:
            repos: List of repositories in format "owner/repo"
            threshold: Similarity threshold

        Returns:
            List of duplicate repo tuples (repo1_name, repo2_name, match)
        """
        threshold = threshold or self.config.overall_similarity_threshold

        logger.info("Analyzing %s repositories for duplicates", len(repos))

        repo_data: Dict[str, Dict[str, Any]] = {}
        for repo in repos:
            try:
                parsed = parse_repo_url(repo)
                owner, repo_name = parsed["owner"], parsed["repo"]
                repo_data[repo] = self._get_repo_data(owner, repo_name)
            except Exception as exc:
                logger.warning("Failed to get data for %s: %s", repo, exc)

        duplicates: List[Tuple[str, str, RepoMatch]] = []
        repo_list = list(repo_data.items())

        for i, (repo1_name, repo1_data) in enumerate(repo_list):
            for repo2_name, repo2_data in repo_list[i + 1 :]:
                similarity = self.metrics.calculate_overall_similarity(repo1_data, repo2_data)

                if similarity.overall_score >= threshold:
                    match = RepoMatch(repo1_data, repo2_data, similarity, "duplicate")
                    duplicates.append((repo1_name, repo2_name, match))

        return duplicates

    def analyze_ecosystem(
        self,
        topic: str,
        language: Optional[str] = None,
        max_repos: int = 100,
    ) -> Dict[str, Any]:
        """
        Analyze ecosystem fragmentation for a topic.

        Args:
            topic: GitHub topic to analyze
            language: Filter by programming language
            max_repos: Maximum repositories to analyze

        Returns:
            Ecosystem analysis dictionary
        """
        logger.info("Analyzing ecosystem for topic: %s", topic)

        query_parts = [f"topic:{topic}"]
        if language:
            query_parts.append(f"language:{language}")

        search_query = " ".join(query_parts)

        try:
            results = self.fetcher.search_repositories(
                search_query, sort="stars", per_page=max_repos
            )
        except Exception as exc:
            logger.error("Failed to search ecosystem: %s", exc)
            return {}

        clusters = self._cluster_repositories(results)

        analysis: Dict[str, Any] = {
            "topic": topic,
            "language": language,
            "total_repos": len(results),
            "num_clusters": len(clusters),
            "fragmentation_score": len(clusters) / max(len(results), 1),
            "clusters": [
                {
                    "size": len(cluster),
                    "repos": [r["full_name"] for r in cluster],
                    "top_repo": max(cluster, key=lambda r: r.get("stargazers_count", 0))[
                        "full_name"
                    ],
                }
                for cluster in clusters
            ],
        }

        return analysis

    def find_orphaned_forks(
        self,
        original_repo: str,
        threshold: float = 0.95,
    ) -> List[Dict[str, Any]]:
        """
        Find potentially abandoned forks of a repository.

        Args:
            original_repo: Original repository in format "owner/repo"
            threshold: Similarity threshold for fork detection

        Returns:
            List of orphaned fork data dictionaries
        """
        logger.info("Finding orphaned forks of %s", original_repo)

        parsed = parse_repo_url(original_repo)
        owner, repo_name = parsed["owner"], parsed["repo"]

        source_repo = self._get_repo_data(owner, repo_name)

        query = f"fork:true {source_repo['name']}"

        try:
            results = self.fetcher.search_repositories(query, per_page=50)
        except Exception as exc:
            logger.warning("Failed to search for forks: %s", exc)
            return []

        orphaned: List[Dict[str, Any]] = []

        for result in results:
            if result["full_name"] == source_repo["full_name"]:
                continue

            similarity = self.metrics.calculate_overall_similarity(source_repo, result)

            if similarity.overall_score >= threshold:
                is_orphaned = self._is_fork_orphaned(result)

                if is_orphaned:
                    orphaned.append(
                        {
                            "full_name": result["full_name"],
                            "url": result["html_url"],
                            "updated_at": result.get("updated_at"),
                            "stargazers_count": result.get("stargazers_count", 0),
                            "forks_count": result.get("forks_count", 0),
                            "similarity_score": similarity.overall_score,
                        }
                    )

        return sorted(orphaned, key=lambda x: x["similarity_score"], reverse=True)

    def _determine_match_type(
        self, repo1: Dict[str, Any], repo2: Dict[str, Any], similarity: SimilarityResult
    ) -> str:
        """Determine the type of match between two repositories."""
        if similarity.overall_score >= 0.95:
            return "duplicate"
        if similarity.name_similarity >= 0.8 and similarity.topic_similarity >= 0.7:
            return "fork"
        return "similar"

    def _cluster_repositories(
        self, repos: List[Dict[str, Any]], threshold: float = 0.7
    ) -> List[List[Dict[str, Any]]]:
        """
        Cluster similar repositories.

        Args:
            repos: List of repository data
            threshold: Similarity threshold for clustering

        Returns:
            List of clusters (each cluster is a list of repos)
        """
        if not repos:
            return []

        clusters: List[List[Dict[str, Any]]] = []
        assigned: set = set()

        for i, repo1 in enumerate(repos):
            if i in assigned:
                continue

            cluster: List[Dict[str, Any]] = [repo1]
            assigned.add(i)

            for j, repo2 in enumerate(repos[i + 1 :], start=i + 1):
                if j in assigned:
                    continue

                similarity = self.metrics.calculate_overall_similarity(repo1, repo2)

                if similarity.overall_score >= threshold:
                    cluster.append(repo2)
                    assigned.add(j)

            clusters.append(cluster)

        return clusters

    def _is_fork_orphaned(self, repo: Dict[str, Any], days: int = 365) -> bool:
        """
        Check if a fork appears to be orphaned.

        Args:
            repo: Repository data
            days: Number of days to consider as orphaned

        Returns:
            True if fork appears orphaned
        """
        updated_at = repo.get("updated_at")
        if not updated_at:
            return True

        try:
            last_update = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            days_since_update = (datetime.now(last_update.tzinfo) - last_update).days
            return days_since_update > days
        except Exception as exc:
            logger.warning("Failed to parse updated_at: %s", exc)
            return False

    def close(self) -> None:
        """Close connections and cleanup."""
        self.fetcher.close()

    def __enter__(self) -> "RepoMatcher":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
