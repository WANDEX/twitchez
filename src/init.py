#!/usr/bin/env python3
# coding=utf-8

from ast import literal_eval
from keys import keys as k
from time import sleep
import conf
import curses
import keys
import pages
import render
import search
import thumbnails


def set_curses_start_defaults():
    """Set curses start defaults."""
    curses.use_default_colors()
    curses.curs_set(0)  # Turn off cursor


def run(stdscr):
    page_name = "Following Live"
    page_dict = {
        "type": "streams",
        "category": page_name,
        "page_name": page_name,
    }
    p = pages.Pages(page_dict)
    page = render.Page(stdscr, p)

    parent = page.parent
    rendergrid = page.draw

    set_curses_start_defaults()

    def redraw():
        """Reinitialize variables & redraw everything."""
        thumbnails.Draw().finish()
        parent.clear()
        rendergrid()
        thumbnails.Draw().start()

    # draw once just before the loop start
    rendergrid()
    thumbnails.Draw().start()

    # Infinite loop to read every key press.
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
        if c == k.get("quit"):
            break
        if c == k.get("redraw"):
            p = pages.Pages(page_dict)
            page = render.Page(stdscr, p)

            parent = page.parent
            rendergrid = page.draw
            redraw()
            continue
        if c == k.get("tab_add"):
            s = search.Search(stdscr)
            rc, page_dict = s.select_page()
            # handle cancel of the command
            if rc == 130:
                continue

            p = pages.Pages(page_dict)
            page = render.Page(stdscr, p)

            parent = page.parent
            rendergrid = page.draw
            redraw()
            continue
        if c == k.get("tab_delete"):
            page_dict = render.Tabs().delete_tab()

            p = pages.Pages(page_dict)
            page = render.Page(stdscr, p)

            parent = page.parent
            rendergrid = page.draw
            redraw()
            continue
        if c == k.get("tab_prev") or c == k.get("tab_next"):
            if c == k.get("tab_next"):
                page_dict = render.Tabs().next_tab()
            else:
                page_dict = render.Tabs().prev_tab()

            p = pages.Pages(page_dict)
            page = render.Page(stdscr, p)

            parent = page.parent
            rendergrid = page.draw
            redraw()
            continue
        if keys.hints(c, rendergrid, parent):
            continue
        keys.scroll(c, rendergrid, parent)
    thumbnails.Draw().finish()
    sleep(0.3)


curses.wrapper(run)
