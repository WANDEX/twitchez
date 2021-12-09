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
    """Take iso date str and return shorten date str."""
    # remove Z character from default twitch date (2021-12-08T11:43:43Z)
    idate = isodate.replace("Z", "")
    vdate = datetime.fromisoformat(idate).isoformat(' ', 'minutes')
    today = datetime.today().isoformat(' ', 'minutes')
    current_year = today[:4]
    if current_year not in vdate:
        pattern = vdate[-6:]  # cut off only time
    else:
        sm = SequenceMatcher(None, vdate, today)
        match = sm.find_longest_match(0, len(vdate), 0, len(today))
        # longest common string between two
        pattern = vdate[match.a: match.a + match.size - 1]
    # remove pattern, cut leading '-' and strip whitespaces
    sdate = str(vdate).replace(pattern, "").strip("-").strip()
    return sdate


def duration(duration: str, simple=False, noprocessing=False) -> str:
    """Take twitch duration str and return duration with : as separators.
    Can optionally return a str without processing or with simple str processing.
    """
    if noprocessing:
        return duration
    if simple:
        # downside is very variable length of str and subjective ugliness of result.
        return duration.replace("h", ":").replace("m", ":").replace("s", ":").strip(":")
    # Don't see any real benefit of the following code over a silly simple one-liner :)
    # Result of the following algorithm are prettier, but also produces longer str.
    if "h" in duration:
        # extract hours from string
        H, _, _ = duration.partition("h")
        H = int(H.strip())
        # fix: if hours > 23 => put hours as simple str into format
        if H > 23:
            ifmt = f"{H}h%Mm%Ss"
            ofmt = f"{H}:%M:%S"
        else:
            ifmt = "%Hh%Mm%Ss"
            ofmt = "%H:%M:%S"
    elif "m" in duration:
        ifmt = "%Mm%Ss"
        ofmt = "%M:%S"
    else:
        return duration
    idur = datetime.strptime(duration, ifmt)
    odur = str(idur.strftime(ofmt))
    return odur
