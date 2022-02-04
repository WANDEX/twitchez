#!/usr/bin/env python3
# coding=utf-8

from pathlib import Path
import curses

__version__ = "0.0.4"
__license__ = "GPLv3"
__description__ = "TUI client for twitch with thumbnails"
__url_repository__ = "https://github.com/WANDEX/twitchez"
__url_bug_reports__ = "https://github.com/WANDEX/twitchez/issues"
__url_project__ = __url_repository__
__author__ = "WANDEX"

# Constants
ENCODING = "utf-8"
HEADER_H = 2
TWITCHEZDIR = Path(__file__).parent.resolve()

# NOTE: STDSCR defined here for ease of reuse, to be able to see actual curses funcs
# and clarify variable type for: interpreter, diagnostic messages, developer, etc.
# we are initializing the actual application later with the curses.wrapper()
# then we override this global constant by the actual stdscr right after initialization
try:
    STDSCR = curses.initscr()
    # all of the following to safely terminate temporary initialized curses application
    # and restore the terminal to default settings and operating mode.
    STDSCR.keypad(False)
    curses.echo()
    curses.nocbreak()
    curses.endwin()
except Exception:
    try:
        curses.endwin()
    except Exception:
        pass
