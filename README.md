# 🔍 Repo Duplicate Detector

A powerful Python package to detect duplicate and similar repositories on GitHub. Analyze ecosystem fragmentation, find abandoned forks, and identify alternative implementations.

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-repo--duplicate--detector-black.svg)](https://github.com/pakistanimoon/repo-duplicate-detector)

---

## 🎯 Features

✅ **Find Similar Repositories** - Detect repositories solving similar problems
✅ **Duplicate Detection** - Identify nearly identical repositories
✅ **Ecosystem Analysis** - Analyze topic fragmentation across GitHub
✅ **Fork Detection** - Find abandoned or active forks
✅ **Intelligent Matching** - Multi-factor similarity algorithm
✅ **Rate Limit Handling** - Built-in rate limit management
✅ **Semantic Analysis** - Optional deep learning-based description matching
✅ **Caching** - Efficient caching to reduce API calls
✅ **High Performance** - Concurrent API requests with retry logic
✅ **Security** - Input validation and secure token handling

---

## 🚀 Quick Start

### Installation

```bash
pip install repo-duplicate-detector
```

### Basic Usage

```python
from repo_duplicate_detector import RepoMatcher

# Initialize
matcher = RepoMatcher(github_token="your_github_token")

# Find similar repositories
similar_repos = matcher.find_similar_repos("facebook/react")

for match in similar_repos:
    print(f"{match.repo2['full_name']}: {match.similarity.overall_score:.2%}")
```

### Using GitHub Token

Set your GitHub token as environment variable:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

Or pass it directly:

```python
from repo_duplicate_detector import RepoMatcher
from repo_duplicate_detector.config import Config

config = Config(github_token="ghp_your_token")
matcher = RepoMatcher(config=config)
```

---

## 📚 Documentation

### RepoMatcher

Main class for finding duplicates and analyzing repositories.

#### Methods

**`find_similar_repos(repo, language=None, threshold=None, max_results=None)`**

Find repositories similar to a given repository.

```python
matches = matcher.find_similar_repos(
    repo="facebook/react",
    language="javascript",
    threshold=0.7,
    max_results=20
)

for match in matches:
    print(match)
    print(match.to_dict())
```

**`find_duplicates_in_list(repos, threshold=None)`**

Find duplicates within a list of repositories.

```python
duplicates = matcher.find_duplicates_in_list
```

##### Digital Helpers

- Github
- CoPilot
- ChatGPT
- Visual Studio
- Github Dev
- Claude