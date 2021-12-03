#!/usr/bin/env python3
# coding=utf-8

from conf import key as ck
from render import Hints
import thumbnails

keys = {
    "quit": ck("quit"),
    "redraw": ck("redraw"),
    "tab_add": ck("tab_add"),
    "tab_delete": ck("tab_delete"),
    "tab_next": ck("tab_next"),
    "tab_prev": ck("tab_prev"),
}

hint_keys = {
    "hint_clip_url": ck("hint_clip_url"),
    "hint_open_url": ck("hint_open_url"),
}

scroll_keys = {
    "scroll_top": ck("scroll_top"),
    "scroll_bot": ck("scroll_bot"),
    "scroll_up": ck("scroll_up"),
    "scroll_down": ck("scroll_down"),
    "scroll_up_page": ck("scroll_up_page"),
    "scroll_down_page": ck("scroll_down_page")
}


def scroll(c, rendergrid, parent):
    """Scroll page and redraw."""
    if c in scroll_keys.values():
        thumbnails.Draw().finish()
        grid = rendergrid()
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
        parent.clear()
        rendergrid()  # redraw after shifting grid index
        thumbnails.Draw().start()


def hints(c, rendergrid, parent):
    """Show hints, and make some action based on key and hint."""
    if c in hint_keys.values():
        hints = Hints()
        hints.show_hints()
        if c == hint_keys.get("hint_open_url"):
            c = str(parent.get_wch())
            if c in hints.active_hints_letters:
                hints.open_url(c)
        elif c == hint_keys.get("hint_clip_url"):
            c = str(parent.get_wch())
            if c in hints.active_hints_letters:
                hints.copy_url(c)
        # to hide previously shown hints
        rendergrid()
        return True
    else:
        return False
