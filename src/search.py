#!/usr/bin/env python3
# coding=utf-8

from notify import notify
import curses
import data
import iselect
import re

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
        # convert bytes to string (remove the b prefix)
        decoded = str(input, ENCODING).strip()
        curses.noecho()
        win.erase()
        win.refresh()

        # Esc = b'\x1b', ^C = b'\x03'
        ignorebyte = ['\x1b', '\x03']
        ignorelist = ['/', '\\']
        ignorelist.extend(ignorebyte)

        # handle Esc or ^C from input as cancel command
        if any(_ in decoded for _ in ignorelist):
            notify("input was ignored!")
            return ""
        return decoded

    def selected_category(self) -> tuple[str, dict]:
        input = self.inputwin("category:")
        if not input:
            return 130, {}
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

    def selected_channel(self, video_type) -> tuple[str, dict]:
        input = self.inputwin("channel:")
        if not input:
            return 130, {}
        mulstr = data.get_channels_terse_mulstr(input)
        selection = iselect.iselect(mulstr)
        if selection == 130:
            # handle cancel of the command
            return 130, {}
        id_pattern = re.compile(r"\[(\d+)\]$")
        sel_id = re.search(id_pattern, selection).group(1)
        __sel_user = re.sub(id_pattern, "", selection).strip()
        sel_user = re.sub(r"^.*\s", "", __sel_user).strip()
        user_id = sel_id
        user_name = sel_user
        page_name = user_name
        json_data = data.get_channel_videos(user_id, video_type)
        return page_name, json_data

    def select_page(self):
        """Interactive select of page to open."""
        msel = "category streams\nchannel videos"
        main_sel = iselect.iselect(msel)
        if main_sel == 130:
            # handle cancel of the command
            return 130, {}
        if "streams" in main_sel:
            return self.selected_category()
        # => videos page
        vtypes = "all\narchive\nhighlight\nupload"
        video_type = iselect.iselect(vtypes)
        if video_type == 130:
            # handle cancel of the command
            return 130, {}
        return self.selected_channel(video_type)
