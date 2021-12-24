#!/usr/bin/env python3
# coding=utf-8

from datetime import datetime
from difflib import SequenceMatcher
from os.path import getmtime
from threading import Thread
import time


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


def strws(str: str) -> str:
    """Return a str with whitespace characters replaced by '_'."""
    return str.strip().replace(" ", "_")


def strclean(str: str) -> str:
    """return slightly cleaner string."""
    # remove unneeded characters from string
    s = str.replace("\n", " ").replace("\t", " ")
    # replace repeating whitespaces by single whitespace
    s = ' '.join(s.split())
    s = s.strip()
    return s


def strtoolong(str: str, width: int, indicator="..") -> str:
    """Return str slice of width with indicator at the end.
    (to show that the string cannot fit completely in width)
    """
    if len(str) > width:
        return str[:width - len(indicator)] + indicator
    else:
        return str


def word_wrap(str: str, width: int, sep="\n") -> str:
    """Basic word wrap."""
    if len(str) < width or " " not in str:
        return str
    # length of longest non-space str in list
    lls = len(max(str.split(" "), key=len))
    if lls > width:  # fix: too long => do not do anything
        return str
    out_str = ""
    while len(str) > width:
        index = width - 1
        # find nearest whitespace to the left of width
        while not str[index].isspace():
            index = index - 1
        chunk = str[:index] + sep  # separate on chunks
        out_str = out_str + chunk
        str = str[index + 1:]  # remaining words
    return out_str + str


def word_wrap_for_box(str: str, width: int) -> str:
    """Word wrap with trailing whitespaces till width
    (use only to fit in width like boxes).
    """
    if len(str) < width:
        return str
    out_str = ""
    text = word_wrap(str, width, "\n")
    lines = text.splitlines(keepends=True)
    for line in lines:
        num_ws = width - len(line) + 1
        out_str += line.replace("\n", " " * num_ws)
    # with additional spaces to mask/differentiate from underlying text
    return out_str + "  "


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


def background(func):
    """use @background decorator above the function to run in the background."""
    def background_func(*args, **kwargs):
        Thread(target=func, args=args, kwargs=kwargs).start()
    return background_func
