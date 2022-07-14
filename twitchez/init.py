#!/usr/bin/env python3
# coding=utf-8

from twitchez import STDSCR
from twitchez import keys
from twitchez import keys_help
from twitchez import render
from twitchez import tabs
from twitchez import thumbnails
from twitchez.keys import other_keys as k

from collections.abc import Callable
import curses


def set_curses_start_defaults():
    """Set curses start defaults."""
    curses.use_default_colors()
    curses.curs_set(0)   # Turn off cursor
    STDSCR.keypad(True)  # human friendly: curses.KEY_LEFT etc.


def wch() -> tuple[str, int, bool]:
    """Handle exceptions, and return character variables with explicit type."""
    try:
        wch = STDSCR.get_wch()
    except KeyboardInterrupt:
        thumbnails.Draw().finish()
        STDSCR.clear()
        curses.endwin()
        curses.napms(300)
        return "", 0, True  # fail/interrupt is True => break
    # explicit type conversion to be absolutely sure about character type!
    ci = int(wch) if isinstance(wch, int) else 0  # int else fallback to 0
    ch = str(wch)
    return ch, ci, False


def handle_resize(ci: int, redrawall: Callable):
    """Handle resize events, short pause(in case many), redraw everything."""
    if ci == curses.KEY_RESIZE:  # terminal resize event
        # fix: handle crazy multiple repeated window resizing initiated by the user
        # NOTE: this introduces slight redraw delay after resize but fixes crashes
        while True:
            curses.napms(250)
            nlines, ncols = STDSCR.getmaxyx()
            if curses.is_term_resized(nlines, ncols):
                curses.napms(750)
                continue
            else:
                break
        # redraw -> True -> continue -> start loop from beginning
        # without further more complex execution
        redrawall()
        return True
    return False


def show_pressed_chars(ch: str, ci: int):
    """Show last pressed key chars at the bottom-right corner."""
    h, w = STDSCR.getmaxyx()
    try:
        if ci != 0:
            STDSCR.insstr(h - 1, w - 8, f" ci:{ci} ")
        else:
            STDSCR.insstr(h - 1, w - 8, ch)
    except ValueError:  # bypass ValueError: embedded null character
        pass


def run(stdscr):
    global STDSCR
    STDSCR = stdscr  # override global STDSCR by the stdscr from wrapper
    page_dict = tabs.cpdict()  # last used page/tab
    page = render.Page(page_dict)

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
        ch, ci, interrupt = wch()
        if interrupt:
            break
        if handle_resize(ci, redraw):
            continue
        show_pressed_chars(ch, ci)

        if ch == k.get("quit"):
            break
        if ch == k.get("redraw"):
            page = render.Page(page_dict)
            redraw()
            continue
        if ch == k.get("keys_help") or ci == curses.KEY_F1:
            keys_help.help()
            redraw()
            continue
        if ch == k.get("full_title"):
            STDSCR.clear()
            fbox = render.Boxes.drawn_boxes[0]
            # toggle full title drawing
            if not fbox.fulltitle:
                page.draw(fulltitle=True)
            else:
                page.draw()
            continue
        if ch in keys.bmark_keys.values():
            page_dict = keys.bmark_action(ch, page_dict)
            page = render.Page(page_dict)
            redraw()
            continue
        if keys.scroll(ch, page.draw):
            redraw()
            continue
        if ch in keys.tab_keys.values():
            page_dict = keys.tabs_action(ch, page_dict)
            page = render.Page(page_dict)
            redraw()
            continue
        if keys.yank(ch):
            continue
        if ch in keys.hint_keys.values():
            # FIXME: redraw all if resize occurred after hints drawing!
            #  if STDSCR.get_wch() == curses.KEY_RESIZE:
            #      redraw()
            if keys.hints(ch):
                # clear possible fulltitle str
                # hide previously shown hints etc.
                STDSCR.clear()
                page.draw()
            else:
                # redraw all especially thumbnails!
                redraw()
            continue
    thumbnails.Draw().finish()
    curses.napms(300)


def main():
    curses.wrapper(run)


if __name__ == "__main__":
    main()
