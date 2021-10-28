#!/usr/bin/env python3
# coding=utf-8

from pathlib import Path
from tempfile import gettempdir


def get_tmp_dir(subdir="") -> Path:
    """ Return path to tmp dir and create optional subdir if it doesn't already exist. """
    tmp_dir_name = "twitch_following_live"
    if not subdir:
        tmp_dir_path = Path(gettempdir(), tmp_dir_name)
    else:
        tmp_dir_path = Path(gettempdir(), tmp_dir_name, subdir)
    Path(tmp_dir_path).mkdir(parents=True, exist_ok=True)
    return tmp_dir_path
