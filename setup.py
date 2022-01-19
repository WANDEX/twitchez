#!/usr/bin/env python3
# coding=utf-8

from setuptools import find_packages, setup
import twitchez

with open("README.md", "r") as f:
    long_description = f.read()
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f]

setup(
    name="twitchez",
    version=twitchez.__version__,
    license=twitchez.__license__,
    url=twitchez.__url_project__,
    author=twitchez.__author__,
    description=twitchez.__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require={
        "thumbnails": ["ueberzug"],  # (X11 only)
    },
    package_data={
        "": ["config/*.conf", "config/blank.jpg"],
    },
    entry_points={
        "console_scripts": ["twitchez=twitchez.init:main"]
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Environment :: Console :: Curses",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Development Status :: 2 - Pre-Alpha",
    ],
    keywords="twitch TUI terminal ui curses client thumbnail image twitch.tv",
    project_urls={
        "Bug Reports": twitchez.__url_bug_reports__,
        "Source": twitchez.__url_repository__,
    },
)
