# Contributing to Repo Duplicate Detector

Thank you for your interest in contributing! Here's how you can help.

## Code of Conduct

- Be respectful and inclusive
- No harassment or discrimination
- Report issues privately

## Development Setup

1. Fork the repository
2. Clone fork: `git clone https://github.com/pakistanimoon/repo-duplicate-detector.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate it: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
5. Install dev dependencies: `pip install -r requirements-dev.txt`
6. Install in editable mode: `pip install -e .`

## Running Tests

```bash
pytest tests/ -v --cov=src/repo_duplicate_detector