#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

# Filter out comments and empty lines
requirements = [r for r in requirements if r and not r.startswith("#")]

setup(
    name="minion-manus",
    version="0.1.0",
    author="FemtoZheng",
    author_email="femto@example.com",
    description="A toolkit for implementing and managing tools for LLM agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/femto/minion-manus",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "smolagents": ["smolagents>=0.0.5", "nest-asyncio>=1.5.6"],
        "database": ["sqlalchemy>=2.0.0", "aiosqlite>=0.17.0"],
        "dev": ["pytest>=7.0.0", "pytest-asyncio>=0.21.0", "black>=23.0.0"],
    },
) 