#!/usr/bin/env python3
# coding=utf-8

from keys import keys as k
from render import STDSCR  # noqa: F401
from time import sleep
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
    global STDSCR
    STDSCR = stdscr  # override global STDSCR by the stdscr from wrapper
    page_dict = render.Tabs().fpagedict()  # last used tab/page

    p = pages.Pages(page_dict)
    page = render.Page(p)

    set_curses_start_defaults()

    def redraw():
        """Reinitialize variables & redraw everything."""
        thumbnails.Draw().finish()
        STDSCR.clear()
        h, w = STDSCR.getmaxyx()
        if h < 3 or w < 3:
            return
        page.draw()
        thumbnails.Draw().start()

    redraw()  # draw once just before the loop start

    # Infinite loop to read every key press.
    while True:
        c = STDSCR.get_wch()
        if isinstance(c, int) and c == curses.KEY_RESIZE:  # terminal resize event
            # fix: handle crazy multiple repeated window resizing initiated by the user
            # NOTE: this introduces slight redraw delay after resize but fixes crashes
            while True:
                sleep(.25)
                nlines, ncols = STDSCR.getmaxyx()
                if curses.is_term_resized(nlines, ncols):
                    sleep(.75)
                    continue
                else:
                    break
            # redraw & start loop again without further more complex execution
            redraw()
            continue
        c = str(c)  # convert character to string
        h, w = STDSCR.getmaxyx()
        # Show last pressed key chars at the bottom-right corner.
        STDSCR.insstr(h - 1, w - 4, c)
        if c == k.get("quit"):
            break
        if c == k.get("redraw"):
            p = pages.Pages(page_dict)
            page = render.Page(p)

            redraw()
            continue
        if c == k.get("full_title"):
            STDSCR.clear()
            fbox = render.Boxes.drawn_boxes[0]
            # toggle full title drawing
            if not fbox.fulltitle:
                page.draw(fulltitle=True)
            else:
                page.draw()
            continue
        if c == k.get("tab_find"):
            page_dict = render.Tabs().find_tab()
            p = pages.Pages(page_dict)
            page = render.Page(p)

            redraw()
            continue
        if c == k.get("tab_add"):
            page_dict = search.select_page(page_dict)

            p = pages.Pages(page_dict)
            page = render.Page(p)

            redraw()
            continue
        if c == k.get("tab_delete"):
            page_dict = render.Tabs().delete_tab()

            p = pages.Pages(page_dict)
            page = render.Page(p)

            redraw()
            continue
        if c == k.get("tab_prev") or c == k.get("tab_next"):
            if c == k.get("tab_next"):
                page_dict = render.Tabs().next_tab()
            else:
                page_dict = render.Tabs().prev_tab()

            p = pages.Pages(page_dict)
            page = render.Page(p)

            redraw()
            continue
        if keys.hints(c):
            # clear possible fulltitle str
            # hide previously shown hints etc.
            STDSCR.clear()
            page.draw()
            continue
        if keys.yank(c):
            continue
        keys.scroll(c, page.draw)
    thumbnails.Draw().finish()
    sleep(0.3)


if __name__ == "__main__":
    curses.wrapper(run)
