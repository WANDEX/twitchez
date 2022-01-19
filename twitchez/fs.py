#!/usr/bin/env python3
# coding=utf-8

from os import environ
from pathlib import Path
from tempfile import gettempdir


def project_root(*args) -> Path:
    """Simply return project_root or compose path from args."""
    if not args:
        return Path(__file__).parent.parent
    else:
        return Path(Path(__file__).parent.parent, *args)


def get_cache_dir() -> Path:
    """Check ENV variables, create cache dir and return it's path."""
    dirname = "twitchez"
    if "TWITCHEZ_CACHE_DIR" in environ:
        cache_home = environ["TWITCHEZ_CACHE_DIR"]
    elif "XDG_CACHE_HOME" in environ:
        cache_home = environ["XDG_CACHE_HOME"]
    else:
        cache_home = Path(Path.home(), ".cache")
    cache_dir = Path(cache_home, dirname)
    # create cache_dir if not exist
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_tmp_dir(*subdirs) -> Path:
    """Return path to tmp dir and create optional subdirs if they doesn't already exist."""
    dirname = "twitchez"
    if not subdirs:
        tmp_dir_path = Path(gettempdir(), dirname)
    else:
        tmp_dir_path = Path(gettempdir(), dirname, *subdirs)
    Path(tmp_dir_path).mkdir(parents=True, exist_ok=True)
    return tmp_dir_path


def get_user_conf_dir() -> Path:
    """Check ENV variables, get user config dir and return it's path."""
    dirname = "twitchez"
    if "XDG_CONFIG_HOME" in environ:
        config_home = environ["XDG_CONFIG_HOME"]
    else:
        config_home = Path(Path.home(), ".config")
    config_dir = Path(config_home, dirname)
    return config_dir
