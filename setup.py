from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="minion-manus",
    version="0.1.0",
    author="FemtoZheng",
    author_email="your.email@example.com",
    description="A framework combining Minion with browser use capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/minion-manus",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies from Minion
        "loguru",
        "python-dotenv",
        "litellm",
        "tenacity",
        "jinja2",
        "aiofiles",
        
        # Browser use dependencies from OpenManus
        "browser-use>=0.1.40",
        "pydantic>=2.10.4",
        "pillow>=10.4.0",
        "playwright>=1.49.1",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "black",
        ],
    },
) 