#!/usr/bin/env python3
"""
Network Tools - A comprehensive Python networking utility package.
"""

from setuptools import setup, find_packages
import os
import re

# Read the version from __init__.py to avoid duplication
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), 'nettools', '__init__.py')
    with open(init_path) as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if version_match:
            return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# Read the long description from README.md
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="nettools",
    version=get_version(),
    author="Network Tools Team",
    author_email="nettools@example.com",
    description="A comprehensive toolkit for network operations and diagnostics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nettools/nettools",
    project_urls={
        "Bug Tracker": "https://github.com/nettools/nettools/issues",
        "Documentation": "https://nettools.readthedocs.io/",
        "Source Code": "https://github.com/nettools/nettools",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet",
        "Topic :: System :: Networking",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Utilities",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "rich>=10.0.0",
        "requests>=2.25.0",
        "dnspython>=2.1.0",
    ],
    entry_points={
        'console_scripts': [
            'nettools=nettools.cli:main',
        ],
    },
    keywords="network tools ip dns port scan web monitoring",
    zip_safe=False,
)