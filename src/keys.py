#!/usr/bin/env python3
# coding=utf-8

import curses
import conf


def loop(parent):
    """Infinite loop to read every key press."""
    curses.use_default_colors()
    curses.curs_set(0)  # Turn off cursor
    while True:
        h, w = parent.getmaxyx()
        c = str(parent.get_wch())
        parent.insstr(h - 1, w - 4, c)  # Show last pressed key chars at the bottom-right corner.
        if c == conf.key("quit"):
            break
