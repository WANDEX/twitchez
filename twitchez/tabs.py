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


def curtab():
    """Get current page name, or 'Following Live' as fallback."""
    return conf.tmp_get("current_page_name", "Following Live", "TABS")


def fpagedict(tab_name="") -> dict:
    """Find and return page dict by the tab name or for current tab."""
    if not tab_name:  # return page_dict of current tab/page
        page_dict_str = conf.tmp_get("page_dict", "", curtab())
    else:
        page_dict_str = conf.tmp_get("page_dict", curtab(), tab_name)
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
    current_page_name = curtab()
    tabs = tab_names()
    # don't add the same tab twice
    if page_name not in tabs:
        if not tabs or current_page_name not in tabs:
            tabs.append(current_page_name)
            if page_name not in tabs:
                tabs.append(page_name)
        else:
            # find index of current page name and insert new tab after that index
            cindex = tabs.index(current_page_name)
            nindex = cindex + 1
            tabs.insert(nindex, page_name)
        conf.tmp_set("tabs", tabs, "TABS")


def delete_tab():
    """Delete current tab and return page_dict of the previous tab."""
    ptabname = prev_tab(tab_name=True)
    tabs = tab_names()
    tabs.remove(curtab())
    conf.tmp_set("tabs", tabs, "TABS")
    return fpagedict(ptabname)


def find_tab() -> dict:
    """Find and return page dict of selected tab."""
    tabs = tab_names()
    mulstr = "\n".join(tabs)  # each list element on it's own line
    tabname = iselect(mulstr, 130)
    # handle cancel of the command
    if tabname == 130:
        # fallback to current tab
        return fpagedict(curtab())
    return fpagedict(tabname)


def next_tab(tab_name=False):
    """Return page_dict for the next tab name (carousel) or simply tab_name."""
    tabs = tab_names()
    cindex = tabs.index(curtab())
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
    cindex = tabs.index(curtab())
    pindex = cindex - 1
    ptabname = tabs[pindex]
    if tab_name:
        return ptabname
    else:
        return fpagedict(ptabname)
