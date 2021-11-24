#!/usr/bin/env python3
# coding=utf-8

from conf import key as ck
from render import Hints
from time import sleep
import curses
import thumbnails

keys = {
    "quit": ck("quit"),
    "redraw": ck("redraw"),
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


def hints(c, renderfunc, parent):
    """Show hints, and make some action based on key and hint."""
    if c in hint_keys.values():
        hints = Hints()
        hints.show_hints()
        if c == hint_keys.get("hint_open_url"):
            # TODO
            pass
        elif c == hint_keys.get("hint_clip_url"):
            c = str(parent.get_wch())
            if c in hints.active_hints_letters:
                hints.copy_url(c)
        # to hide previously shown hints
        renderfunc()
        return True
    else:
        return False


def loop(page_class):
    """Infinite loop to read every key press."""
    page = page_class
    parent = page.page_parent
    renderfunc = page.render_page

    curses.use_default_colors()
    curses.curs_set(0)  # Turn off cursor

    def redraw():
        """Reinitialize variables & redraw everything."""
        thumbnails.Draw().finish()
        parent.clear()
        renderfunc()
        thumbnails.Draw().start()

    # draw once just before the loop start
    renderfunc()
    thumbnails.Draw().start()

    while True:
        c = parent.get_wch()
        if isinstance(c, int) and c == curses.KEY_RESIZE:  # terminal resize event
            # redraw & start loop again without further more complex execution
            redraw()
            continue
        c = str(c)  # convert character to string
        h, w = parent.getmaxyx()
        # Show last pressed key chars at the bottom-right corner.
        parent.insstr(h - 1, w - 4, c)
        if c == keys.get("quit"):
            break
        elif c == keys.get("redraw"):
            redraw()
            continue
        if hints(c, renderfunc, parent):
            continue
        scroll(c, renderfunc, parent)
    thumbnails.Draw().finish()
    sleep(0.3)
