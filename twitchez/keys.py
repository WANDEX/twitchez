#!/usr/bin/env python3
# coding=utf-8

from . import data
from . import render
from .clip import clip
from .conf import key as ck
from .notify import notify

keys = {
    "quit": ck("quit"),
    "redraw": ck("redraw"),
    "full_title": ck("full_title"),
    "tab_find": ck("tab_find"),
    "tab_add": ck("tab_add"),
    "tab_delete": ck("tab_delete"),
    "tab_next": ck("tab_next"),
    "tab_prev": ck("tab_prev"),
    "yank_urls": ck("yank_urls"),
    "yank_urls_page": ck("yank_urls_page"),
}

hint_keys = {
    "hint_clip_url": ck("hint_clip_url"),
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


def scroll(c, page_draw):
    """Scroll page."""
    if c in scroll_keys.values():
        grid = page_draw()
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
        return True
    return False


def hints(c):
    """Show hints, and make some action based on key and hint."""
    if c in hint_keys.values():
        hints = render.Hints()
        hint = hints.show_hints_boxes()
        if c == hint_keys.get("hint_clip_url"):
            hints.copy_url(hint)
        else:
            if c == hint_keys.get("hint_open_stream"):
                type = "stream"
            elif c == hint_keys.get("hint_open_video"):
                type = "video"
            elif c == hint_keys.get("hint_open_extra"):
                type = "extra"
            else:
                type = "stream"
            hints.open_url(hint, type)
        return True
    else:
        return False


def yank_urls(full_page=False):
    """Yank urls of visible boxes or all urls of the page."""
    urls = ""
    if full_page:
        page_dict = render.Tabs().fpagedict()  # current tab/page
        json_data = data.page_data(page_dict)
        if "url" in json_data["data"][0]:
            page_urls = data.get_entries(json_data, "url")
            for url in page_urls:
                urls += f"{url}\n"
    else:
        for box in render.Boxes.drawn_boxes:
            urls += f"{box.url}\n"
    if urls:
        clip(urls)
    else:
        notify("This page does not have 'url' entries in json data.")


def yank(c):
    if c == keys.get("yank_urls") or c == keys.get("yank_urls_page"):
        if c == keys.get("yank_urls"):
            yank_urls()
        elif c == keys.get("yank_urls_page"):
            yank_urls(full_page=True)
        return True
    else:
        return False
