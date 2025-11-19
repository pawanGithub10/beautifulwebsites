"""
Setup configuration for Anthropic Claude Provider
"""

from setuptools import setup, find_packages

setup(
    name="ai-platform-anthropic",
    version="1.0.0",
    description="Anthropic Claude provider for AI Platform",
    packages=find_packages(),
    install_requires=[
        "ai-platform-core>=1.0.0",
        "anthropic>=0.18.0",
    ],
    python_requires=">=3.9",
)
