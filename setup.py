#!/usr/bin/env python
"""
Setup script for PodcastGenerator.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Read the version from podcast_generator/__init__.py
about = {}
with open(os.path.join("podcast_generator", "__init__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)

setup(
    name="podcast-generator",
    version=about["__version__"],
    description="Generate podcasts from research articles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/PodcastGenerator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "transformers>=4.35.2",
        "torch>=2.1.1",
        "sentencepiece>=0.1.99",
        "openai>=1.3.7",
        "sentence-transformers>=2.2.2",
        "gTTS>=2.4.0",
        "boto3>=1.34.1",
        "pydub>=0.25.1",
        "numpy>=1.26.2",
        "tqdm>=4.66.1",
    ],
    entry_points={
        "console_scripts": [
            "podcast-generator=podcast_generator.main:main",
        ],
    },
) 