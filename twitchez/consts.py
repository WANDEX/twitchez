#!/usr/bin/env python3
# coding=utf-8

import curses

# NOTE: should be always overridden by the stdscr from wrapper
# defined here just to be able to see actual curses funcs of stdscr
# and clarify variable type for: interpreter, diagnostic messages, developer etc.
STDSCR = curses.initscr()  # save variable type/obj in global constant
# we are initializing the actual application later inside the wrapper
# -> terminate temporary(fake) curses application
curses.nocbreak()
curses.echo()
curses.endwin()
