"""
Example: Analyze ecosystem fragmentation for a topic.
"""

from repo_duplicate_detector import RepoMatcher
from repo_duplicate_detector.config import Config
import os
import json


def main():
    """Analyze ecosystem fragmentation."""
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable not set")
    
    config = Config(github_token=github_token)
    
    with RepoMatcher(config=config) as matcher:
        # Analyze JavaScript testing frameworks
        print("📊 Analyzing Python testing frameworks ecosystem...\n")
        
        analysis = matcher.analyze_ecosystem(
            topic="testing",
            language="python",
            max_repos=50
        )
        
        if not analysis:
            print("No analysis data available.")
            return
        
        print(f"Topic: {analysis.get('topic')}")
        print(f"Language: {analysis.get('language')}")
        print(f"Total Repositories: {analysis.get('total_repos')}")
        print(f"Number of Clusters: {analysis.get('num_clusters')}")
        print(f"Fragmentation Score: {analysis.get('fragmentation_score'):.2%}\n")
        
        print("Clusters:")
        print("-" * 80)
        
        for i, cluster in enumerate(analysis.get('clusters', []), 1):
            print(f"\nCluster {i}: ({cluster['size']} repositories)")
            print(f"   Top Repository: {cluster['top_repo']}")
            print(f"   Repositories:")
            for repo in cluster['repos'][:5]:  # Show first 5
                print(f"      - {repo}")
            if len(cluster['repos']) > 5:
                print(f"      ... and {len(cluster['repos']) - 5} more")


if __name__ == "__main__":
    main()