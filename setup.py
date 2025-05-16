from setuptools import setup, find_packages

setup(
    name="async-llms",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "tqdm",
        "aiohttp",
        "openai",
        "google-generativeai",
    ],
    entry_points={
        "console_scripts": [
            "async-llms=async_llms.cli:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python library for making asynchronous LLM calls",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/async-llms",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
) 