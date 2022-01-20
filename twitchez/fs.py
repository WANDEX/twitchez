#!/usr/bin/env python3
# coding=utf-8

from os import environ
from pathlib import Path
from tempfile import gettempdir


def set_owner_only_permissions(path: Path) -> Path:
    """Set owner only path permissions."""
    if path.is_dir():
        path.chmod(0o700, follow_symlinks=True)
    else:
        path.chmod(0o600, follow_symlinks=True)
    return path


def private_data_path() -> Path:
    """Check that the .private file exists, if not -> create empty file.
    Also set r+w dir & file permissions to owner only & return path to file.
    """
    private_dir = get_data_dir(".private")       # create dir if not exist
    file_path = Path(private_dir, ".private")
    if not file_path.exists():
        file_path.touch(exist_ok=True)           # create empty file
        set_owner_only_permissions(private_dir)  # set dir permissions
        set_owner_only_permissions(file_path)    # set file permissions
    return file_path


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


def get_data_dir(*subdirs) -> Path:
    """Return path to data dir and create optional subdirs if they doesn't already exist."""
    dirname = "twitchez"
    if "TWITCHEZ_DATA_DIR" in environ:
        data_home = environ["TWITCHEZ_DATA_DIR"]
    elif "XDG_DATA_HOME" in environ:
        data_home = environ["XDG_DATA_HOME"]
    else:
        data_home = Path(Path.home(), ".local", "share")
    if not subdirs:
        data_path = Path(data_home, dirname)
    else:
        data_path = Path(data_home, dirname, *subdirs)
    # create data_path dirs if not exist
    Path(data_path).mkdir(parents=True, exist_ok=True)
    return data_path


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
