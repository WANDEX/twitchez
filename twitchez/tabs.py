#!/usr/bin/env python3
# coding=utf-8

from ast import literal_eval
from pathlib import Path
from twitchez import conf
from twitchez import fs
from twitchez import paged
from twitchez.iselect import iselect

FILE = Path(fs.get_data_dir("data"), "tabs").resolve().as_posix()
LTABS = "LTABS"
DTABS = "DTABS"


def tabs_list() -> list:
    """Return list of tabs (name, dict) tuples."""
    return conf.dta_list(DTABS, FILE)


def tabs_dnames() -> list:
    """Return list of tab names (keys) of the dictionaries."""
    return [tname for tname, _ in tabs_list()]


def tab_names_ordered() -> list:
    """Return an ordered list of opened tab names."""
    names_list_str = conf.dta_get("ltabs", "", LTABS, FILE)
    try:
        names_list = literal_eval(names_list_str)
    except Exception as e:
        raise ValueError(f"names_list_str: '{names_list_str}'\n{e}")
    return names_list


def tabs_upd(tabs: list):
    """Update/set list of tabs."""
    conf.dta_set("ltabs", tabs, LTABS, FILE)
    # remove all not opened tabs (real tabs data with dicts)
    for tname in tabs_dnames():
        if tname not in tabs:
            conf.dta_rmo(tname, DTABS, FILE)


def cpname_set(pname: str):
    """Set value of the current page/tab name."""
    conf.dta_set("cpname", pname, LTABS, FILE)


def tab_upd(page_name: str, page_dict: dict):
    """Update tabs, set current page name, add page to the tabs list (if not exist)."""
    cpname_set(page_name)  # set the new current page name (NOTE: before everything else!)
    conf.dta_set(page_name, page_dict, DTABS, FILE)
    tab_add_new(page_name)


def cpname() -> str:
    """Get current page name, set to the first tab name as fallback."""
    cpn = conf.dta_get("cpname", "", LTABS, FILE)
    tabs = tab_names_ordered()
    if not cpn or cpn not in tabs:
        if not tabs:
            cpn = paged.FLPN  # fallback to following live page
        else:
            cpn = tabs[0]  # set first tab name as the current page name
        cpname_set(cpn)
    return cpn


def cpdict() -> dict:
    """Get current page dict."""
    return pdict(cpname())


def pdict(page_name="") -> dict:
    """Return page dict by the page name or (current tab/page by default)."""
    if not page_name:  # return page_dict of current tab/page
        pdict_str = conf.dta_get(cpname(), "", DTABS, FILE)
    else:
        pdict_str = conf.dta_get(page_name, cpname(), DTABS, FILE)
    if not pdict_str or pdict_str == paged.FLPN or page_name == paged.FLPN:
        return paged.following_live()  # fallback to following live page
    try:
        page_dict = literal_eval(pdict_str)
    except Exception as e:
        raise ValueError(f"pdict_str: '{pdict_str}'\n{e}")
    return page_dict


def tab_add_new(page_name: str):
    """Add new tab/page to the tabs list (if not exist)."""
    tabs = tab_names_ordered()
    if not tabs:
        tabs.append(page_name)
        tabs_upd(tabs)
        cpn = cpname()
        return
    # do not add the same tab twice
    if page_name not in tabs:
        cpn = cpname()
        # find index of current page name and insert new tab after that index
        cindex = tabs.index(cpn)
        nindex = cindex + 1
        tabs.insert(nindex, page_name)
        tabs_upd(tabs)
        return


def delete_tab(page_name="") -> dict:
    """Delete tab by page name or current tab/page and return page_dict of the previous tab."""
    ctab = cpname()
    tabs = tab_names_ordered()
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
    tabs = tab_names_ordered()
    mulstr = "\n".join(tabs)  # each list element on it's own line
    tabname = iselect(mulstr, 130)
    # handle cancel of the command
    if tabname == 130:
        return fallback
    return pdict(tabname)


def next_tab() -> tuple[dict, str]:
    """Return (page_dict, page_name) tuple of the next tab (carousel)."""
    tabs = tab_names_ordered()
    cindex = tabs.index(cpname())
    nindex = cindex + 1
    if nindex > len(tabs) - 1:
        ntabname = tabs[0]
    else:
        ntabname = tabs[nindex]
    return pdict(ntabname), ntabname


def prev_tab() -> tuple[dict, str]:
    """Return (page_dict, page_name) tuple of the prev tab (carousel)."""
    tabs = tab_names_ordered()
    cindex = tabs.index(cpname())
    pindex = cindex - 1
    ptabname = tabs[pindex]
    return pdict(ptabname), ptabname
