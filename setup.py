from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="TgBee",
    version="1.0.5",
    author="Ahmed Negm",
    author_email="a7mednegm.x@gmail.com",
    description="An asynchronous Python Telegram Bot API wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/x7007x/TgBee",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiohttp>=3.7.4",
        "aiofiles"
    ],
)

