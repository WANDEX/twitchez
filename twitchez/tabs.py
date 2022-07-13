#!/usr/bin/env python3
# coding=utf-8

from ast import literal_eval
from twitchez import conf
from twitchez import paged
from twitchez.iselect import iselect

SECT = "TABS"


def tab_names() -> list:
    """Return list of tab names"""
    try:
        tabs = literal_eval(conf.tmp_get("tabs", [], SECT))
    except ValueError:  # handle literal_eval() error with empty list
        tabs = []
    return tabs


def tab_upd(page_name: str, page_dict: dict):
    """Update tabs, update current & add page as the new tab (if not exist)."""
    # set page tmp vars for reusing in next/prev tab movement etc.
    conf.tmp_set("page_dict", page_dict, page_name)
    # add/set current/new tab as page_name (if not already in tabs)
    add_tab(page_name)


def cpnset(page_name: str) -> str:
    """Set current page name."""
    conf.tmp_set("current_page_name", page_name, "CTAB")
    return page_name


def cpname() -> str:
    """Get current page name."""
    return conf.tmp_get("current_page_name", "", "CTAB")


def cpdict() -> dict:
    """Get current page dict."""
    return pdict(cpname())


def tabs_upd(tabs: list):
    """Update/set list of tabs."""
    conf.tmp_set("tabs", tabs, SECT)


def pdict(page_name="") -> dict:
    """Return page dict by the page name or (current tab/page by default)."""
    if not page_name:  # return page_dict of current tab/page
        pdict_str = conf.tmp_get("page_dict", "", cpname())
    else:
        pdict_str = conf.tmp_get("page_dict", cpname(), page_name)
    if not pdict_str or pdict_str == paged.FLPN or page_name == paged.FLPN:
        return paged.following_live()  # fallback to following live page
    try:
        page_dict = literal_eval(pdict_str)
    except Exception as e:
        raise ValueError(f"pdict_str: '{pdict_str}'\n{e}")
    return page_dict


def add_tab(page_name: str):
    """Add page to the tabs list, set/update current page."""
    tabs = tab_names()
    cpn = cpname()
    # set/update current page name
    if not cpn or cpn != page_name:
        cpn = cpnset(page_name)
        if cpn not in tabs:
            tabs.append(cpn)
            tabs_upd(tabs)
    # do not add the same tab twice
    if page_name not in tabs:
        if not tabs:
            tabs.append(page_name)
        else:
            # find index of current page name and insert new tab after that index
            cindex = tabs.index(cpn)
            nindex = cindex + 1
            tabs.insert(nindex, page_name)
        tabs_upd(tabs)


def delete_tab(page_name="") -> dict:
    """Delete tab by page name or current tab/page and return page_dict of the previous tab."""
    ctab = cpname()
    tabs = tab_names()
    if (page_name != ctab and page_name in tabs):
        tab_to_delete = page_name
        tab_to_jump = ctab
    else:
        tab_to_delete = ctab
        _, tab_to_jump = prev_tab()

    if (tab_to_delete in tabs):
        tabs.remove(tab_to_delete)

    tabs_upd(tabs)
    return pdict(tab_to_jump)


def find_tab(fallback=cpdict()) -> dict:
    """Find and return page dict of selected tab or fallback to current tab (by default)."""
    tabs = tab_names()
    mulstr = "\n".join(tabs)  # each list element on it's own line
    tabname = iselect(mulstr, 130)
    # handle cancel of the command
    if tabname == 130:
        return fallback
    return pdict(tabname)


def next_tab() -> tuple[dict, str]:
    """Return (page_dict, page_name) tuple of the next tab (carousel)."""
    tabs = tab_names()
    cindex = tabs.index(cpname())
    nindex = cindex + 1
    if nindex > len(tabs) - 1:
        ntabname = tabs[0]
    else:
        ntabname = tabs[nindex]
    return pdict(ntabname), ntabname


def prev_tab() -> tuple[dict, str]:
    """Return (page_dict, page_name) tuple of the prev tab (carousel)."""
    tabs = tab_names()
    cindex = tabs.index(cpname())
    pindex = cindex - 1
    ptabname = tabs[pindex]
    return pdict(ptabname), ptabname
