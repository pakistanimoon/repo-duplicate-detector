"""
Example: Find potentially orphaned forks of a repository.
"""

from repo_duplicate_detector import RepoMatcher
from repo_duplicate_detector.config import Config
import os
from datetime import datetime


def main():
    """Find orphaned forks."""
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable not set")
    
    config = Config(github_token=github_token)
    
    with RepoMatcher(config=config) as matcher:
        print("🔍 Finding orphaned forks of torvalds/linux...\n")
        
        orphaned_forks = matcher.find_orphaned_forks(
            original_repo="torvalds/linux",
            threshold=0.95
        )
        
        if not orphaned_forks:
            print("No orphaned forks found.")
            return
        
        print(f"Found {len(orphaned_forks)} orphaned forks:\n")
        print("-" * 80)
        
        for i, fork in enumerate(orphaned_forks, 1):
            updated_at = fork.get('updated_at', 'Unknown')
            try:
                last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                days_ago = (datetime.now(last_update.tzinfo) - last_update).days
                update_str = f"{days_ago} days ago"
            except:
                update_str = updated_at
            
            print(f"\n{i}. {fork['full_name']}")
            print(f"   URL: {fork['url']}")
            print(f"   Stars: ⭐ {fork['stargazers_count']:,}")
            print(f"   Forks: 🍴 {fork['forks_count']:,}")
            print(f"   Last Updated: {update_str}")
            print(f"   Similarity Score: {fork['similarity_score']:.2%}")
            print("-" * 80)


if __name__ == "__main__":
    main()