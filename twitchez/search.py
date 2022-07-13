#!/usr/bin/env python3
# coding=utf-8

from twitchez import ENCODING
from twitchez import STDSCR
from twitchez import data
from twitchez import iselect
from twitchez import paged
from twitchez.notify import notify
import curses
import re


def inputwin(prompt: str) -> str:
    """Show input window at the last line of the stdscr window,
    return input str after pressing Enter key.
    """
    h, w = STDSCR.getmaxyx()
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


def selected_category(fallback: dict) -> dict:
    input = inputwin("category:")
    if not input:
        return fallback
    mulstr = data.get_categories_terse_mulstr(input)
    selection = iselect.iselect(mulstr, 130)
    if selection == 130:
        return fallback
    id_pattern = re.compile(r"\[(\d+)\]$")
    sel_name = re.sub(id_pattern, "", selection).strip()
    sel_id = re.search(id_pattern, selection).group(1)
    category_id = sel_id
    category_name = sel_name
    page_dict = paged.stream(category_name, category_id)
    return page_dict


def selected_channel(video_type, fallback: dict) -> dict:
    input = inputwin("channel:")
    if not input:
        return fallback
    mulstr = data.get_channels_terse_mulstr(input)
    selection = iselect.iselect(mulstr, 130)
    if selection == 130:
        return fallback
    id_pattern = re.compile(r"\[(\d+)\]$")
    sel_id = re.search(id_pattern, selection).group(1)
    __sel_user = re.sub(id_pattern, "", selection).strip()
    sel_user = re.sub(r"^.*\s", "", __sel_user).strip()
    user_id = sel_id
    user_name = sel_user
    page_dict = paged.video(video_type, user_id, user_name)
    return page_dict


def select_page(fallback: dict) -> dict:
    """Interactive select of page to open, return page_dict of that page or fallback page."""
    msel = "category streams\nchannel videos\nfollowing live"
    main_sel = iselect.iselect(msel, 130)
    if main_sel == 130:  # handle cancel of the command
        return fallback
    if "following" in main_sel:
        return paged.following_live()
    elif "streams" in main_sel:
        return selected_category(fallback)
    # => videos page
    vtypes = "archive\nclips\nhighlight\nupload"
    video_type = iselect.iselect(vtypes, 130)
    if video_type == 130:
        return fallback
    return selected_channel(video_type, fallback)
