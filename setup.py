from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="repo-duplicate-detector",
    version="0.1.0",
    author="pakistanimoon",
    author_email="rajaimranqamer@gmail.com",
    description="Detect duplicate and similar GitHub repositories using intelligent matching algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pakistanimoon/repo-duplicate-detector",
    project_urls={
        "Bug Tracker": "https://github.com/pakistanimoon/repo-duplicate-detector/issues",
        "Documentation": "https://github.com/pakistanimoon/repo-duplicate-detector/wiki",
        "Source Code": "https://github.com/pakistanimoon/repo-duplicate-detector",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "repo-detector=repo_duplicate_detector.cli:main",
        ],
    },
)
