from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sparetools-py",
    version="1.0.0",
    author="SpareSparrow",
    author_email="dev@sparesparrow.com",
    description="Python utilities for SpareTools embedded development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sparesparrow/sparetools",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flatbuffers>=24.3.25",
        "dataclasses>=0.6; python_version < '3.7'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sparetools-test=sparetools.test_harness:main",
            "sparetools-conan=sparetools.conan_helpers:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)