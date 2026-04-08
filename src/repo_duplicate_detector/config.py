"""
Configuration management for repo-duplicate-detector.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration for RepoMatcher and related services."""

    # GitHub API
    github_token: Optional[str] = None
    api_base_url: str = "https://api.github.com"
    timeout: int = 30

    # Rate limiting
    max_requests_per_minute: int = 60
    retry_attempts: int = 3
    retry_delay: float = 1.0

    # Similarity matching
    name_similarity_threshold: float = 0.6
    overall_similarity_threshold: float = 0.7
    max_results: int = 50

    # Caching
    use_cache: bool = True
    cache_ttl: int = 3600  # 1 hour

    # Performance
    batch_size: int = 10
    concurrent_requests: int = 5

    # Semantic similarity
    use_semantic_matching: bool = True
    semantic_model: str = "all-MiniLM-L6-v2"

    # Logging
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            github_token=os.getenv("GITHUB_TOKEN"),
            timeout=int(os.getenv("API_TIMEOUT", "30")),
            max_requests_per_minute=int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60")),
            retry_attempts=int(os.getenv("RETRY_ATTEMPTS", "3")),
            name_similarity_threshold=float(os.getenv("NAME_SIMILARITY_THRESHOLD", "0.6")),
            overall_similarity_threshold=float(os.getenv("OVERALL_SIMILARITY_THRESHOLD", "0.7")),
            max_results=int(os.getenv("MAX_RESULTS", "50")),
            use_cache=os.getenv("USE_CACHE", "true").lower() == "true",
            cache_ttl=int(os.getenv("CACHE_TTL", "3600")),
            batch_size=int(os.getenv("BATCH_SIZE", "10")),
            concurrent_requests=int(os.getenv("CONCURRENT_REQUESTS", "5")),
            use_semantic_matching=os.getenv("USE_SEMANTIC_MATCHING", "true").lower() == "true",
            semantic_model=os.getenv("SEMANTIC_MODEL", "all-MiniLM-L6-v2"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )


def get_config() -> Config:
    """Get the current configuration."""
    return Config.from_env()
