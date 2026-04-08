"""
Utility functions for repo-duplicate-detector.
"""

import hashlib
import json
import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def parse_repo_url(repo_url: str) -> Dict[str, str]:
    """
    Parse a GitHub repository URL.

    Args:
        repo_url: Repository URL or owner/repo format

    Returns:
        Dictionary with 'owner' and 'repo' keys

    Raises:
        InvalidRepositoryError: If URL format is invalid
    """
    from .exceptions import InvalidRepositoryError

    # Handle owner/repo format
    if "/" in repo_url and not repo_url.startswith("http"):
        parts = repo_url.strip().split("/")
        if len(parts) == 2:
            return {"owner": parts[0], "repo": parts[1]}

    # Handle full GitHub URL
    try:
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) >= 2 and parsed.hostname == "github.com":
            return {"owner": path_parts[0], "repo": path_parts[1]}
    except Exception as e:
        logger.error(f"Failed to parse repository URL: {repo_url}", exc_info=e)

    raise InvalidRepositoryError(f"Invalid repository URL format: {repo_url}")


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison.

    Args:
        text: Text to normalize

    Returns:
        Normalized text
    """
    if not text:
        return ""

    return (
        text.lower()
        .strip()
        .replace("-", " ")
        .replace("_", " ")
        .replace(".", " ")
    )


def calculate_hash(data: str) -> str:
    """
    Calculate SHA256 hash of data.

    Args:
        data: Data to hash

    Returns:
        Hex digest of SHA256 hash
    """
    return hashlib.sha256(data.encode()).hexdigest()


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks.

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def safe_get(data: Dict, key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary.

    Args:
        data: Dictionary to query
        key: Key to retrieve (supports dot notation)
        default: Default value if key not found

    Returns:
        Value from dictionary or default
    """
    if "." in key:
        keys = key.split(".")
        value = data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    return data.get(key, default)


def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes as human-readable string.

    Args:
        bytes_value: Number of bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def is_valid_github_owner(owner: str) -> bool:
    """
    Validate GitHub username/organization.

    Args:
        owner: GitHub username or organization name

    Returns:
        True if valid, False otherwise
    """
    if not owner or len(owner) > 39:
        return False

    # GitHub usernames can contain alphanumeric characters and hyphens
    # but cannot start or end with hyphens
    pattern = r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$"
    return bool(re.match(pattern, owner))


def is_valid_repo_name(repo: str) -> bool:
    """
    Validate GitHub repository name.

    Args:
        repo: Repository name

    Returns:
        True if valid, False otherwise
    """
    if not repo or len(repo) > 100:
        return False

    # Repository names can contain alphanumeric characters, hyphens, and underscores
    pattern = r"^[a-zA-Z0-9._-]+$"
    return bool(re.match(pattern, repo))