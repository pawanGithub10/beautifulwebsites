"""
Setup configuration for AI Core package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-platform-core",
    version="1.0.0",
    author="Beautiful Websites Team",
    description="Universal, framework-agnostic AI engine for Python applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        # Minimal dependencies - just what's needed for core functionality
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
        "openai": [
            "openai>=1.0.0",
            "tiktoken>=0.5.0",
        ],
        "anthropic": [
            "anthropic>=0.18.0",
        ],
        "redis": [
            "redis>=5.0.0",
        ],
        "postgres": [
            "asyncpg>=0.29.0",
            "sqlalchemy>=2.0.0",
        ],
        "all": [
            "openai>=1.0.0",
            "tiktoken>=0.5.0",
            "anthropic>=0.18.0",
            "redis>=5.0.0",
            "asyncpg>=0.29.0",
            "sqlalchemy>=2.0.0",
        ]
    },
)
