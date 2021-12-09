#!/usr/bin/env python3
# coding=utf-8

from datetime import datetime
from difflib import SequenceMatcher
from os import environ
from os.path import getmtime
from pathlib import Path
from tempfile import gettempdir
import time


def project_root(*args) -> Path:
    """ simply return project_root or compose path from args. """
    if not args:
        return Path(__file__).parent.parent
    else:
        return Path(Path(__file__).parent.parent, *args)


def get_cache_dir() -> Path:
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


def get_tmp_dir(*subdirs) -> Path:
    """Return path to tmp dir and create optional subdirs if they doesn't already exist."""
    dirname = "twitch-following-live"
    if not subdirs:
        tmp_dir_path = Path(gettempdir(), dirname)
    else:
        tmp_dir_path = Path(gettempdir(), dirname, *subdirs)
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


def secs_since_mtime(path):
    """time_now - target_mtime = int(secs)."""
    return int(time.time() - getmtime(path))


def replace_pattern_in_all(inputlist, oldstr, newstr) -> list:
    """Replace oldstr with newstr in all items from a list."""
    outputlist = []
    for e in inputlist:
        outputlist.append(str(e).replace(oldstr, newstr))
    return outputlist


def add_str_to_list(input_list, string) -> list:
    """Add string to the end of all elements in a list."""
    outputlist = [e + str(string) for e in input_list]
    return outputlist


def insert_to_all(list, string, opt_sep="") -> list:
    """ Insert the string at the beginning of all items in a list. """
    string = str(string)
    if opt_sep:
        string = f"{string}{opt_sep}"
    string += '% s'
    list = [string % i for i in list]
    return list


def strclean(str: str) -> str:
    """return slightly cleaner string."""
    # remove unneeded characters from string
    s = str.replace("\n", " ").replace("\t", " ")
    # replace repeating whitespaces by single whitespace
    s = ' '.join(s.split())
    s = s.strip()
    return s


def sdate(isodate: str) -> str:
    "Return shorten date."
    idate = isodate.replace("Z", "")  # remove Z character from date (2021-12-08T11:43:43Z)
    vdate = datetime.fromisoformat(idate).isoformat(' ', 'minutes')
    today = datetime.today().isoformat(' ', 'minutes')
    match = SequenceMatcher(None, vdate, today).find_longest_match(0, len(vdate), 0, len(today))
    longest_common_str = vdate[match.a: match.a + match.size]
    sdate = str(vdate).replace(longest_common_str, "")  # remove common between two str
    return sdate
