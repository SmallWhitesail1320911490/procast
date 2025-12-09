from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="procast",
    version="0.1.0",
    author="SmallWhitesail",
    description="使用 LLM 从播客中提取金句并生成分享卡片",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SmallWhitesail1320911490/procast",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai-whisper",
        "pydub",
        "ffmpeg-python",
        "openai>=1.0.0",
        "anthropic",
        "google-generativeai",
        "Pillow>=10.0.0",
        "pilmoji",
        "python-dotenv",
        "requests",
        "rich",
        "typer[all]",
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "procast=procast.cli:app",
        ],
    },
)
