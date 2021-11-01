#!/usr/bin/env python3
# coding=utf-8

from pathlib import Path
from tempfile import gettempdir
from os import environ


def project_root(*args) -> Path:
    """ simply return project_root or compose path from args. """
    if not args:
        return Path(__file__).parent.parent
    else:
        return Path(Path(__file__).parent.parent, *args)


def get_cache_dir():
    """ check ENV variables, create cache dir and return it's path. """
    dirname = "twitch-following-live"
    if "TWITCH_FL_CACHE_DIR" in environ:
        cache_home = environ["TWITCH_FL_CACHE_DIR"]
    elif "XDG_CACHE_HOME" in environ:
        cache_home = environ["XDG_CACHE_HOME"]
    else:
        cache_home = Path(Path.home(), ".cache")
    cache_dir = Path(cache_home, dirname)
    # create cache_dir if not exist
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_tmp_dir(subdir="") -> Path:
    """ Return path to tmp dir and create optional subdir if it doesn't already exist. """
    tmp_dir_name = "twitch_following_live"
    if not subdir:
        tmp_dir_path = Path(gettempdir(), tmp_dir_name)
    else:
        tmp_dir_path = Path(gettempdir(), tmp_dir_name, subdir)
    Path(tmp_dir_path).mkdir(parents=True, exist_ok=True)
    return tmp_dir_path


def get_user_conf_dir() -> Path:
    """ check ENV variables, get user config dir and return it's path. """
    dirname = "twitch-following-live"
    if "XDG_CONFIG_HOME" in environ:
        config_home = environ["XDG_CONFIG_HOME"]
    else:
        config_home = Path(Path.home(), ".config")
    config_dir = Path(config_home, dirname)
    return config_dir
