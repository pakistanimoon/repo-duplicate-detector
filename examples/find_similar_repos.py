"""
Example: Find repositories similar to a given repository.
"""

from repo_duplicate_detector import RepoMatcher
from repo_duplicate_detector.config import Config
import os


def main():
    """Find similar repositories."""
    # Initialize with GitHub token from environment
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable not set")
    
    config = Config(github_token=github_token)
    
    # Create matcher
    with RepoMatcher(config=config) as matcher:
        # Find repositories similar to React
        print("🔍 Finding repositories similar to facebook/react...\n")
        
        matches = matcher.find_similar_repos(
            repo="facebook/react",
            language="javascript",
            threshold=0.65,
            max_results=10
        )
        
        if not matches:
            print("No similar repositories found.")
            return
        
        print(f"Found {len(matches)} similar repositories:\n")
        print("-" * 80)
        
        for i, match in enumerate(matches, 1):
            print(f"\n{i}. {match.repo2['full_name']}")
            print(f"   URL: {match.repo2['html_url']}")
            print(f"   Description: {match.repo2.get('description', 'N/A')}")
            print(f"   Stars: ⭐ {match.repo2.get('stargazers_count', 0):,}")
            print(f"   Language: {match.repo2.get('language', 'Unknown')}")
            print(f"\n   📊 Similarity Scores:")
            print(f"      Overall: {match.similarity.overall_score:.2%}")
            print(f"      Name: {match.similarity.name_similarity:.2%}")
            print(f"      Description: {match.similarity.description_similarity:.2%}")
            print(f"      Topics: {match.similarity.topic_similarity:.2%}")
            print(f"      Language: {match.similarity.language_match:.2%}")
            print(f"      Contributors: {match.similarity.contributor_overlap:.2%}")
            print(f"      Activity: {match.similarity.activity_similarity:.2%}")
            print(f"\n   Match Type: {match.match_type}")
            print("-" * 80)


if __name__ == "__main__":
    main()