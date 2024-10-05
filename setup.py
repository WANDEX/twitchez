#!/usr/bin/env python3
# coding=utf-8

import twitchez

from setuptools import find_packages, setup

import re


def remove_gif(text: str) -> str:
    return re.sub(r"\n^<img src=.*>$\n\n", "", text, flags=re.DOTALL | re.MULTILINE)


def remove_video(text: str) -> str:
    return re.sub(r"http.*\.mp4\n\n", "", text)


def replace_gh_video_via_mdlink(text: str) -> str:
    return re.sub(r"(http.*\.mp4)\n\n", r"### [CLICK TO WATCH DEMO VIDEO](\1)\n\n", text)


def clean_md(text: str) -> str:
    """Clean the markdown text for pypi.org.
    directly embedded github videos are not supported by pypi.org.
    """
    #  text = remove_gif(text)
    text = replace_gh_video_via_mdlink(text)
    return text


with open("README.md", "r") as f:
    long_description = f.read()
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f]

long_description = clean_md(long_description)

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
        "thumbnails": ["ueberzugpp", "ueberzug"],
    },
    package_data={
        "twitchez": ["config/*.conf", "config/blank.jpg"],
    },
    entry_points={
        "console_scripts": ["twitchez=twitchez.__main__:main"]
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Environment :: Console :: Curses",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Development Status :: 4 - Beta",
    ],
    keywords="twitch TUI terminal curses ui client thumbnail image twitch.tv",
    project_urls={
        "Bug Reports": twitchez.__url_bug_reports__,
        "Source": twitchez.__url_repository__,
    },
)
