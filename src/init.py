#!/usr/bin/env python3
# coding=utf-8

from keys import keys as k
from time import sleep
import curses
import data
import keys
import pages
import render
import thumbnails


def set_curses_start_defaults():
    """Set curses start defaults."""
    curses.use_default_colors()
    curses.curs_set(0)  # Turn off cursor


def run(stdscr):
    page_name = "Following Live"
    json_data = data.following_live_data()
    p = pages.Pages(page_name, json_data)
    page_class = render.Page(stdscr, p)

    page = page_class
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
            redraw()
            continue
        if c == k.get("tab_add"):
            # TODO: how to select category? with fzf? (only if i can get names of all categories on twitch)
            category_query_string = "software development"  # FIXME: temporary hardcoded
            # TODO: write those variables to file to not get this data every loop iteration only read it from file
            category_id, category_name = data.get_category(category_query_string)

            page_name = category_name
            json_data = data.category_data(category_id)
            p = pages.Pages(page_name, json_data)
            page_class = render.Page(stdscr, p)

            page = page_class
            parent = page.parent
            rendergrid = page.draw
            redraw()
            continue
        if c == k.get("tab_prev"):
            prev_tab_name = render.Tabs().prev_tab(page.page_name)
            json_file_name = prev_tab_name.replace(" ", "_") + ".json"
            if prev_tab_name == "Following Live":
                page_name = "Following Live"
                json_data = data.following_live_data()
            else:
                if data.cache_file_path(json_file_name).is_file():
                    page_name = prev_tab_name
                    json_data = data.read_cache(json_file_name)
                else:
                    category_id, category_name = data.get_category(prev_tab_name)
                    page_name = category_name
                    json_data = data.category_data(category_id)
            p = pages.Pages(page_name, json_data)
            page_class = render.Page(stdscr, p)

            page = page_class
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
