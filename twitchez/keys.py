#!/usr/bin/env python3
# coding=utf-8

from twitchez import STDSCR
from twitchez import bmark
from twitchez import data
from twitchez import search
from twitchez import tabs
from twitchez import thumbnails
from twitchez import utils
from twitchez.clip import clip
from twitchez.conf import key as ck
from twitchez.notify import notify
from twitchez.render import Boxes

from collections.abc import Callable
import curses

bmark_keys = {
    "bmark_add": ck("bmark_add"),
    "bmark_delete": ck("bmark_delete"),
    "bmark_open": ck("bmark_open"),
}

hint_keys = {
    "hint_clip_url": ck("hint_clip_url"),
    "hint_open_chat": ck("hint_open_chat"),
    "hint_open_stream": ck("hint_open_stream"),
    "hint_open_extra": ck("hint_open_extra"),
    "hint_open_video": ck("hint_open_video"),
}

scroll_keys = {
    "scroll_top": ck("scroll_top"),
    "scroll_bot": ck("scroll_bot"),
    "scroll_up": ck("scroll_up"),
    "scroll_down": ck("scroll_down"),
    "scroll_up_page": ck("scroll_up_page"),
    "scroll_down_page": ck("scroll_down_page")
}

tab_keys = {
    "tab_add": ck("tab_add"),
    "tab_delete": ck("tab_delete"),
    "tab_find": ck("tab_find"),
    "tab_next": ck("tab_next"),
    "tab_prev": ck("tab_prev"),
}

other_keys = {
    "quit": ck("quit"),
    "redraw": ck("redraw"),
    "full_title": ck("full_title"),
    "keys_help": ck("keys_help"),
    "yank_urls": ck("yank_urls"),
    "yank_urls_page": ck("yank_urls_page"),
}


def rkt(timeout=500, fallback="") -> str:
    """Read key with timeout, without raising exception.
    (No exception if no input -> return fallback key or empty string.)
    """
    _rsw = STDSCR.derwin(0, 0)
    _rsw.timeout(timeout)
    try:
        c = str(_rsw.get_wch())
    except curses.error:  # "no input" etc.
        c = fallback
    return c


def bmark_action(ch: str, fallback: dict):
    """Bookmark action based on key."""
    page_dict = fallback
    if ch == bmark_keys.get("bmark_add"):
        bmark.bmark_add()
    elif ch == bmark_keys.get("bmark_delete"):
        bmark.bmark_del()
    elif ch == bmark_keys.get("bmark_open"):
        page_dict = bmark.bmark_open(fallback)
    return page_dict


def hints(ch: str):
    """Show box hints, and make some action based on key and hint.
    If terminal was resized while hints were being shown -> cancel & redraw all.
    """
    # get the initial sum to check later if terminal was resized
    xysum = utils.was_resized(0)

    boxes, hint = Boxes().show_boxes_hint()
    type = ""

    if ch == hint_keys.get("hint_clip_url"):
        type = "copy_url"
    elif ch == hint_keys.get("hint_open_chat"):
        type = "open_chat"
    elif ch == hint_keys.get("hint_open_stream"):
        type = "stream"
    elif ch == hint_keys.get("hint_open_video"):
        type = "video"
    elif ch == hint_keys.get("hint_open_extra"):
        type = "extra"

    if type == "copy_url":
        if not boxes.copy_url(hint) and not utils.was_resized(xysum):
            return False
    elif type == "open_chat":
        if not boxes.open_chat(hint) and not utils.was_resized(xysum):
            return False
    elif type:
        if not boxes.open_url(hint, type) and not utils.was_resized(xysum):
            return False

    # redraw all including thumbnails
    return True


def scroll_grid(redraw: Callable) -> str:
    """Scroll page grid based on the input key."""
    c = rkt(100)
    STDSCR.clear()
    grid = redraw()
    if c == scroll_keys.get("scroll_down"):
        grid.shift_index("down")
    elif c == scroll_keys.get("scroll_up"):
        grid.shift_index("up")
    elif c == scroll_keys.get("scroll_down_page"):
        grid.shift_index("down", page=True)
    elif c == scroll_keys.get("scroll_up_page"):
        grid.shift_index("up", page=True)
    elif c == scroll_keys.get("scroll_top"):
        grid.shift_index("top")
    elif c == scroll_keys.get("scroll_bot"):
        grid.shift_index("bot")
    return c


def scroll(ch: str, redraw: Callable, redrawall: Callable):
    """Scroll page, especially handle repeated scroll keys."""
    if ch in scroll_keys.values():
        thumbnails.draw_stop()
        c = rkt(100)
        curses.unget_wch(ch)
        # if no next input key after timeout -> scroll once
        if not c:
            c = scroll_grid(redraw)
        else:
            # if next character is also a scroll key
            # -> loop in simple redraw without thumbnails
            while c in scroll_keys.values():
                c = scroll_grid(redraw)
        redrawall()
        return True
    return False


def tabs_action(ch: str, fallback: dict):
    """Tabs actions."""
    if ch == tab_keys.get("tab_add"):
        page_dict = search.select_page(fallback)
    elif ch == tab_keys.get("tab_delete"):
        page_dict = tabs.delete_tab()
    elif ch == tab_keys.get("tab_find"):
        page_dict = tabs.find_tab()
    elif ch == tab_keys.get("tab_next"):
        page_dict, _ = tabs.next_tab()
    elif ch == tab_keys.get("tab_prev"):
        page_dict, _ = tabs.prev_tab()
    else:
        page_dict = fallback
    return page_dict


def yank_urls(full_page=False):
    """Yank urls of visible boxes or all urls of the page."""
    urls = ""
    if full_page:
        page_dict = tabs.cpdict()  # current page/tab
        json_data = data.page_data(page_dict)
        if "url" in json_data["data"][0]:
            page_urls = data.get_entries(json_data, "url")
            for url in page_urls:
                urls += f"{url}\n"
    else:
        for box in Boxes.drawn_boxes:
            urls += f"{box.url}\n"
    if urls:
        clip(urls)
    else:
        notify("This page does not have 'url' entries in json data.")


def yank(ch: str):
    if ch == other_keys.get("yank_urls") or ch == other_keys.get("yank_urls_page"):
        if ch == other_keys.get("yank_urls"):
            yank_urls()
        elif ch == other_keys.get("yank_urls_page"):
            yank_urls(full_page=True)
        return True
    return False
