#!/usr/bin/env python3
# coding=utf-8

from time import sleep
import conf
import curses
import thumbnails


scroll_keys = {
    "scroll_top": conf.key("scroll_top"),
    "scroll_bot": conf.key("scroll_bot"),
    "scroll_up": conf.key("scroll_up"),
    "scroll_down": conf.key("scroll_down"),
    "scroll_up_page": conf.key("scroll_up_page"),
    "scroll_down_page": conf.key("scroll_down_page")
}


def scroll(c, renderfunc, parent):
    """Scroll page and redraw."""
    if c in scroll_keys.values():
        thumbnails.Draw().finish()
        grid = renderfunc()
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
        renderfunc()  # redraw after shifting grid index
        thumbnails.Draw().start()


def loop(page_class):
    """Infinite loop to read every key press."""
    page = page_class
    parent = page.page_parent
    renderfunc = page.render_page

    curses.use_default_colors()
    curses.curs_set(0)  # Turn off cursor

    renderfunc()
    thumbnails.Draw().start()

    while True:
        h, w = parent.getmaxyx()
        c = str(parent.get_wch())
        parent.insstr(h - 1, w - 4, c)  # Show last pressed key chars at the bottom-right corner.
        if c == conf.key("quit"):
            break
        scroll(c, renderfunc, parent)
    thumbnails.Draw().finish()
    sleep(0.5)
