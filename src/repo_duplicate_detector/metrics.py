"""
Similarity metrics for comparing repositories.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .utils import normalize_text

try:
    import Levenshtein

    HAS_LEVENSHTEIN = True
except ImportError:
    HAS_LEVENSHTEIN = False

try:
    from sentence_transformers import SentenceTransformer

    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

logger = logging.getLogger(__name__)


@dataclass
class SimilarityResult:
    """Result of similarity comparison between two repositories."""

    overall_score: float
    name_similarity: float
    description_similarity: float
    topic_similarity: float
    language_match: float
    contributor_overlap: float
    activity_similarity: float
    details: Dict = field(default_factory=dict)

    def __str__(self) -> str:
        return (
            f"SimilarityResult(overall={self.overall_score:.2%}, "
            f"name={self.name_similarity:.2%}, "
            f"description={self.description_similarity:.2%}, "
            f"topics={self.topic_similarity:.2%})"
        )


class SimilarityMetrics:
    """Calculate similarity metrics between repositories."""

    def __init__(self, use_semantic: bool = True, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize similarity metrics calculator.

        Args:
            use_semantic: Whether to use semantic similarity for descriptions
            model_name: Name of the sentence transformer model to use
        """
        self.use_semantic = use_semantic and HAS_SENTENCE_TRANSFORMERS
        self.model = None

        if self.use_semantic:
            try:
                self.model = SentenceTransformer(model_name)
                logger.info(f"Loaded sentence transformer model: {model_name}")
            except Exception as e:
                logger.warning(
                    f"Failed to load semantic model: {e}. Falling back to text matching."
                )
                self.use_semantic = False

    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two repository names.

        Args:
            name1: First repository name
            name2: Second repository name

        Returns:
            Similarity score between 0 and 1
        """
        if not name1 or not name2:
            return 0.0

        norm1 = normalize_text(name1)
        norm2 = normalize_text(name2)

        # Exact match
        if norm1 == norm2:
            return 1.0

        # Check for substring matches
        if norm1 in norm2 or norm2 in norm1:
            return 0.9

        # Use Levenshtein distance if available
        if HAS_LEVENSHTEIN:
            try:
                max_len = max(len(norm1), len(norm2))
                distance = Levenshtein.distance(norm1, norm2)
                similarity = 1.0 - (distance / max_len)
                return max(0.0, similarity)
            except Exception as e:
                logger.warning(f"Levenshtein distance calculation failed: {e}")

        # Fallback: simple character overlap
        set1 = set(norm1.split())
        set2 = set(norm2.split())
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def calculate_description_similarity(self, desc1: str, desc2: str) -> float:
        """
        Calculate similarity between two descriptions.

        Args:
            desc1: First description
            desc2: Second description

        Returns:
            Similarity score between 0 and 1
        """
        if not desc1 or not desc2:
            return 0.0

        # Use semantic similarity if available
        if self.use_semantic and self.model:
            try:
                embeddings = self.model.encode([desc1, desc2])
                from sklearn.metrics.pairwise import cosine_similarity

                similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
                return float(similarity)
            except Exception as e:
                logger.warning(f"Semantic similarity calculation failed: {e}")

        # Fallback: simple word overlap
        words1 = set(normalize_text(desc1).split())
        words2 = set(normalize_text(desc2).split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0

    def calculate_topic_similarity(self, topics1: List[str], topics2: List[str]) -> float:
        """
        Calculate Jaccard similarity between topic sets.

        Args:
            topics1: First list of topics
            topics2: Second list of topics

        Returns:
            Jaccard similarity score between 0 and 1
        """
        if not topics1 and not topics2:
            return 1.0

        if not topics1 or not topics2:
            return 0.0

        set1 = set(t.lower() for t in topics1)
        set2 = set(t.lower() for t in topics2)

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def calculate_language_similarity(self, lang1: Optional[str], lang2: Optional[str]) -> float:
        """
        Calculate language match score.

        Args:
            lang1: First language
            lang2: Second language

        Returns:
            1.0 if languages match, 0.0 otherwise
        """
        if not lang1 and not lang2:
            return 1.0

        if not lang1 or not lang2:
            return 0.0

        return 1.0 if lang1.lower() == lang2.lower() else 0.0

    def calculate_contributor_overlap(
        self, contributors1: List[str], contributors2: List[str]
    ) -> float:
        """
        Calculate overlap in contributors.

        Args:
            contributors1: First list of contributors
            contributors2: Second list of contributors

        Returns:
            Overlap score between 0 and 1
        """
        if not contributors1 and not contributors2:
            return 1.0

        if not contributors1 or not contributors2:
            return 0.0

        set1 = set(c.lower() for c in contributors1)
        set2 = set(c.lower() for c in contributors2)

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def calculate_activity_similarity(self, activity1: Dict, activity2: Dict) -> float:
        """
        Calculate similarity based on activity patterns.

        Args:
            activity1: First activity data
            activity2: Second activity data

        Returns:
            Activity similarity score between 0 and 1
        """
        try:
            # Extract metrics
            stars1 = activity1.get("stars", 0)
            forks1 = activity1.get("forks", 0)
            issues1 = activity1.get("issues", 0)

            stars2 = activity2.get("stars", 0)
            forks2 = activity2.get("forks", 0)
            issues2 = activity2.get("issues", 0)

            # Calculate ratios for comparison
            total1 = max(1, stars1 + forks1 + issues1)
            total2 = max(1, stars2 + forks2 + issues2)

            # Normalize by total activity
            profile1 = (stars1 / total1, forks1 / total1, issues1 / total1)
            profile2 = (stars2 / total2, forks2 / total2, issues2 / total2)

            # Calculate cosine similarity
            dot_product = sum(a * b for a, b in zip(profile1, profile2))
            magnitude1 = sum(x**2 for x in profile1) ** 0.5
            magnitude2 = sum(x**2 for x in profile2) ** 0.5

            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0

            return dot_product / (magnitude1 * magnitude2)

        except Exception as e:
            logger.warning(f"Activity similarity calculation failed: {e}")
            return 0.5

    def calculate_overall_similarity(
        self,
        repo1: Dict,
        repo2: Dict,
        weights: Optional[Dict[str, float]] = None,
    ) -> SimilarityResult:
        """
        Calculate overall similarity between two repositories.

        Args:
            repo1: First repository data
            repo2: Second repository data
            weights: Custom weight dictionary for metrics

        Returns:
            SimilarityResult object with detailed metrics
        """
        # Default weights
        default_weights = {
            "name": 0.20,
            "description": 0.25,
            "topics": 0.20,
            "language": 0.15,
            "contributors": 0.10,
            "activity": 0.10,
        }

        weights = weights or default_weights

        # Calculate individual metrics
        name_sim = self.calculate_name_similarity(repo1.get("name", ""), repo2.get("name", ""))

        desc_sim = self.calculate_description_similarity(
            repo1.get("description", ""), repo2.get("description", "")
        )

        topic_sim = self.calculate_topic_similarity(
            repo1.get("topics", []), repo2.get("topics", [])
        )

        lang_sim = self.calculate_language_similarity(repo1.get("language"), repo2.get("language"))

        contrib_sim = self.calculate_contributor_overlap(
            repo1.get("contributors", []), repo2.get("contributors", [])
        )

        activity_sim = self.calculate_activity_similarity(
            repo1.get("activity", {}), repo2.get("activity", {})
        )

        # Calculate weighted overall score
        overall = (
            name_sim * weights.get("name", 0.2)
            + desc_sim * weights.get("description", 0.25)
            + topic_sim * weights.get("topics", 0.2)
            + lang_sim * weights.get("language", 0.15)
            + contrib_sim * weights.get("contributors", 0.1)
            + activity_sim * weights.get("activity", 0.1)
        )

        return SimilarityResult(
            overall_score=overall,
            name_similarity=name_sim,
            description_similarity=desc_sim,
            topic_similarity=topic_sim,
            language_match=lang_sim,
            contributor_overlap=contrib_sim,
            activity_similarity=activity_sim,
            details={
                "weights": weights,
                "repo1_name": repo1.get("name"),
                "repo2_name": repo2.get("name"),
            },
        )
