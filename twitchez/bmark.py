#!/usr/bin/env python3
# coding=utf-8

from ast import literal_eval
from pathlib import Path
from twitchez import conf
from twitchez import fs
from twitchez.iselect import iselect
from twitchez.tabs import find_tab, cpname_set, tab_add_new

bmsf = Path(fs.get_data_dir("data"), "bookmarks").resolve().as_posix()
SECT = "BMARKS"


def bmark_list() -> list:
    """Return list of bookmark (name, dict) tuples."""
    return conf.dta_list(SECT, bmsf)


def bmark_names() -> list:
    """Return list of bookmark names."""
    return [bname for bname, _ in bmark_list()]


def bmark_save(page_name: str, page_dict: dict):
    """Save bookmark."""
    conf.dta_set(page_name, page_dict, SECT, bmsf)


def bmark_add():
    """Find tab and save as bookmark."""
    page_dict = find_tab({})
    # handle cancel of the command
    if not page_dict:
        return
    page_name = page_dict.get("page_name")
    bmark_save(page_name, page_dict)


def bmark_find() -> tuple[str, dict]:
    """Find and return (name, dict) tuple of the selected bookmark."""
    bnames = bmark_names()
    mulstr = "\n".join(bnames)
    bname = iselect(mulstr, 130)
    # handle cancel of the command
    if (bname == 130):
        return "", {}
    # get dict by the key
    bdict = {}
    for key, val in bmark_list():
        if (key == bname):
            bdict = dict(literal_eval(val))
            break
    return bname, bdict


def bmark_del():
    """Delete bookmark by the name."""
    bname, _ = bmark_find()
    if (not bname):
        return
    conf.dta_rmo(bname, SECT, bmsf)


def bmark_open(fallback: dict) -> dict:
    """Open bookmark by the name."""
    bname, bdict = bmark_find()
    if (not bname or not bdict):
        return fallback
    tab_add_new(bname)
    cpname_set(bname)
    return bdict
