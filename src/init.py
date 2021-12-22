#!/usr/bin/env python3
# coding=utf-8

from keys import keys as k
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
    s = search.Search(stdscr)
    page_dict = render.Tabs().fpagedict()  # last used tab/page
    if not page_dict:  # fallback to following live page
        page_dict = s.following_live()
    p = pages.Pages(page_dict)
    page = render.Page(stdscr, p)

    parent = page.parent
    rendergrid = page.draw

    set_curses_start_defaults()

    def redraw():
        """Reinitialize variables & redraw everything."""
        thumbnails.Draw().finish()
        parent.clear()
        h, w = parent.getmaxyx()
        if h < 3 or w < 3:
            return
        rendergrid()
        thumbnails.Draw().start()

    # draw once just before the loop start
    rendergrid()
    thumbnails.Draw().start()

    # Infinite loop to read every key press.
    while True:
        c = parent.get_wch()
        if isinstance(c, int) and c == curses.KEY_RESIZE:  # terminal resize event
            # fix: handle crazy multiple repeated window resizing initiated by the user
            # NOTE: this introduces slight redraw delay after resize but fixes crashes
            while True:
                sleep(.25)
                nlines, ncols = parent.getmaxyx()
                if curses.is_term_resized(nlines, ncols):
                    sleep(.75)
                    continue
                else:
                    break
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
        if c == k.get("full_title"):
            page.parent.clear()
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
            page = render.Page(stdscr, p)

            parent = page.parent
            rendergrid = page.draw
            redraw()
            continue
        if c == k.get("tab_add"):
            page_dict = s.select_page(page_dict)

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
        if keys.hints(c, parent):
            # clear possible fulltitle str
            # hide previously shown hints etc.
            page.parent.clear()
            page.draw()
            continue
        if keys.yank(c):
            continue
        keys.scroll(c, rendergrid, parent)
    thumbnails.Draw().finish()
    sleep(0.3)


curses.wrapper(run)
