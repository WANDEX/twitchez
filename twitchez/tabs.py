#!/usr/bin/env python3
# coding=utf-8

from ast import literal_eval
from twitchez import conf
from twitchez import search
from twitchez.iselect import iselect


class Tabs:
    """Tabs."""
    try:  # list of tab names
        tabs = literal_eval(conf.tmp_get("tabs", [], "TABS"))
    except ValueError:  # handle literal_eval() error with empty list
        tabs = []

    def curtab(self):
        """Get current page name, or 'Following Live' as fallback."""
        return conf.tmp_get("current_page_name", "Following Live", "TABS")

    def fpagedict(self, tab_name="") -> dict:
        """Find and return page dict by the tab name or for current tab."""
        if not tab_name:  # return page_dict of current tab/page
            page_dict_str = conf.tmp_get("page_dict", "", self.curtab())
        else:
            page_dict_str = conf.tmp_get("page_dict", self.curtab(), tab_name)
        if not page_dict_str or page_dict_str == "Following Live":
            return search.following_live()
        try:
            page_dict = literal_eval(page_dict_str)
        except Exception as e:
            raise ValueError(f"page_dict_str: '{page_dict_str}'\n{e}")
        return page_dict

    def add_tab(self, page_name):
        current_page_name = self.curtab()
        # don't add the same tab twice
        if page_name not in self.tabs:
            if not self.tabs or current_page_name not in self.tabs:
                self.tabs.append(current_page_name)
                if page_name not in self.tabs:
                    self.tabs.append(page_name)
            else:
                # find index of current page name and insert new tab after that index
                cindex = self.tabs.index(current_page_name)
                nindex = cindex + 1
                self.tabs.insert(nindex, page_name)
            conf.tmp_set("tabs", self.tabs, "TABS")

    def delete_tab(self):
        """Delete current tab and return page_dict of the previous tab."""
        ptabname = self.prev_tab(tab_name=True)
        self.tabs.remove(self.curtab())
        conf.tmp_set("tabs", self.tabs, "TABS")
        return self.fpagedict(ptabname)

    def find_tab(self) -> dict:
        """Find and return page dict of selected tab."""
        mulstr = "\n".join(self.tabs)  # each list element on it's own line
        tabname = iselect(mulstr, 130)
        # handle cancel of the command
        if tabname == 130:
            # fallback to current tab
            return self.fpagedict(self.curtab())
        return self.fpagedict(tabname)

    def next_tab(self, tab_name=False):
        """Return page_dict for the next tab name (carousel) or simply tab_name."""
        cindex = self.tabs.index(self.curtab())
        nindex = cindex + 1
        if nindex > len(self.tabs) - 1:
            ntabname = self.tabs[0]
        else:
            ntabname = self.tabs[nindex]
        if tab_name:
            return ntabname
        else:
            return self.fpagedict(ntabname)

    def prev_tab(self, tab_name=False):
        """Return page_dict for the prev tab name (carousel) or simply tab_name."""
        cindex = self.tabs.index(self.curtab())
        pindex = cindex - 1
        ptabname = self.tabs[pindex]
        if tab_name:
            return ptabname
        else:
            return self.fpagedict(ptabname)
