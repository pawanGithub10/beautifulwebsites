"""
Setup configuration for OpenAI Provider
"""

from setuptools import setup, find_packages

setup(
    name="ai-platform-openai",
    version="1.0.0",
    description="OpenAI provider for AI Platform",
    packages=find_packages(),
    install_requires=[
        "ai-platform-core>=1.0.0",
        "openai>=1.0.0",
        "tiktoken>=0.5.0",
    ],
    python_requires=">=3.9",
)
