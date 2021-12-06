#!/usr/bin/env python3
# coding=utf-8

import curses
import re
import data
import iselect

ENCODING = "utf-8"


class Search:
    """Search."""

    def __init__(self, parent):
        self.parent = parent

    def inputwin(self, prompt: str) -> str:
        """Show input window at the last line of the parent window,
        return input str after pressing Enter key.
        """
        h, w = self.parent.getmaxyx()
        win = curses.newwin(1, w // 3, h - 1, 0)
        win.addstr(0, 0, prompt, curses.A_REVERSE)
        win.refresh()
        curses.echo()
        # indent from the prompt by one character
        input = win.getstr(0, len(prompt) + 1)
        curses.noecho()
        win.erase()
        # convert bytes to string (remove the b prefix)
        return str(input, ENCODING).strip()

    def selected_category(self) -> tuple[str, dict]:
        input = self.inputwin("category:")
        mulstr = data.get_categories_terse_mulstr(input)
        selection = iselect.iselect(mulstr)
        if selection == 130:
            # handle cancel of the command
            return selection, {}
        id_pattern = re.compile(r"\[(\d+)\]$")
        sel_name = re.sub(id_pattern, "", selection).strip()
        sel_id = re.search(id_pattern, selection).group(1)
        category_id = sel_id
        category_name = sel_name
        page_name = category_name
        json_data = data.category_data(category_id)
        return page_name, json_data
