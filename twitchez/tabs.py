#!/usr/bin/env python3
# coding=utf-8

from ast import literal_eval
from twitchez import conf
from twitchez.iselect import iselect


def tab_names() -> list:
    """Return list of tab names"""
    try:
        tabs = literal_eval(conf.tmp_get("tabs", [], "TABS"))
    except ValueError:  # handle literal_eval() error with empty list
        tabs = []
    return tabs


def tab_upd(page_name: str, page_dict: dict):
    """Update tabs, update current & add page as the new tab (if not exist)."""
    # set page tmp vars for reusing in next/prev tab movement etc.
    conf.tmp_set("page_dict", page_dict, page_name)
    # add/set current/new tab as page_name (if not already in tabs)
    add_tab(page_name)


def cpnset(page_name):
    """Set current page name."""
    conf.tmp_set("current_page_name", page_name, "TABS")
    return page_name


def cpname():
    """Get current page name."""
    return conf.tmp_get("current_page_name", "", "TABS")


def cpdict():
    """Get current page dict."""
    return fpagedict(cpname())


def tabs_upd(tabs: list):
    """Update/set list of tabs."""
    conf.tmp_set("tabs", tabs, "TABS")


def fpagedict(tab_name="") -> dict:
    """Find and return page dict by the tab name or for current tab."""
    if not tab_name:  # return page_dict of current tab/page
        page_dict_str = conf.tmp_get("page_dict", "", cpname())
    else:
        page_dict_str = conf.tmp_get("page_dict", cpname(), tab_name)
    if not page_dict_str or page_dict_str == "Following Live":
        # fix: to bypass probable circular import error
        from twitchez.search import following_live
        return following_live()
    try:
        page_dict = literal_eval(page_dict_str)
    except Exception as e:
        raise ValueError(f"page_dict_str: '{page_dict_str}'\n{e}")
    return page_dict


def add_tab(page_name):
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


def delete_tab(page_name=""):
    """Delete tab by page name or current tab/page and return page_dict of the previous tab."""
    ctab = cpname()
    tabs = tab_names()
    if (page_name != ctab and page_name in tabs):
        tab_to_delete = page_name
        tab_to_jump = ctab
    else:
        tab_to_delete = ctab
        tab_to_jump = prev_tab(tab_name=True)

    if (tab_to_delete in tabs):
        tabs.remove(tab_to_delete)

    tabs_upd(tabs)
    return fpagedict(tab_to_jump)


def find_tab(fallback=cpdict()) -> dict:
    """Find and return page dict of selected tab or fallback to current tab (by default)."""
    tabs = tab_names()
    mulstr = "\n".join(tabs)  # each list element on it's own line
    tabname = iselect(mulstr, 130)
    # handle cancel of the command
    if tabname == 130:
        return fallback
    return fpagedict(tabname)


def next_tab(tab_name=False):
    """Return page_dict for the next tab name (carousel) or simply tab_name."""
    tabs = tab_names()
    cindex = tabs.index(cpname())
    nindex = cindex + 1
    if nindex > len(tabs) - 1:
        ntabname = tabs[0]
    else:
        ntabname = tabs[nindex]
    if tab_name:
        return ntabname
    else:
        return fpagedict(ntabname)


def prev_tab(tab_name=False):
    """Return page_dict for the prev tab name (carousel) or simply tab_name."""
    tabs = tab_names()
    cindex = tabs.index(cpname())
    pindex = cindex - 1
    ptabname = tabs[pindex]
    if tab_name:
        return ptabname
    else:
        return fpagedict(ptabname)
