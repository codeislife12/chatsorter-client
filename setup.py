# setup.py
"""
Setup configuration for ChatSorter Python Client
"""

from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chatsorter-client",
    version="1.0.0",
    author="ChatSorter Team",
    author_email="theiogamer1st@gmail.com",
    description="Official Python client for ChatSorter Memory API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/codeislife12/chatsorter-client",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
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
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    keywords="chatbot memory api semantic-search ai llm",
    project_urls={
        "Bug Reports": "https://github.com/codeislife12/chatsorter-client/issues",
        "Source": "https://github.com/codeislife12/chatsorter-client",
    },
)