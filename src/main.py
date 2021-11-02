#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import conf
import data
import utils


def container_box(parent, obj, h, w, y, x):
    """ create stream container_box
    each stream box created inside it.
    window dimensions:
        h, w, top_y, left_x
    return bot_x, right_x
    """
    game_name = obj["game_name"]
    user_name = obj["user_name"]
    title = obj["title"]
    last = h - 2  # last line before bottom box border
    max = w - 2  # max length of string inside box

    win = parent.derwin(h, w, y, x)

    win.addnstr(last - 2, 1, f"{title}\n", max)
    win.addnstr(last - 1, 1, f"{user_name}\n", max, curses.A_BOLD)
    win.addnstr(last - 0, 1, f"{game_name}\n", max)
    # win.addnstr(last, 1, "text inside container box xxxxxx\n", max)
    win.box()
    Y, X = win.getparyx()
    # window - right X, bottom Y, for debugging.
    win.addnstr(last + 1, 1, f"X:{X} Y:{Y}", max)
    return Y, X


def create_sub_windows(parent, rows, cols):
    """ create sub windows for all streams. """
    new_x = 0  # init
    new_y = 0  # init
    bias_x = 0
    bias_y = 0
    h = int(conf.setting("container_box_height"))
    w = int(conf.setting("container_box_width"))
    JSON_DATA = data.read_live_streams()
    # iterate over all streams
    for stream in JSON_DATA["data"]:
        prev_y, prev_x = container_box(parent, stream, h, w, new_y, new_x)
        expected_x = prev_x + bias_x + w
        expected_y = prev_y + bias_y + h
        if expected_x + w > cols:
            new_x = 0
            new_y = expected_y
        else:
            new_x = expected_x
            new_y = prev_y
        parent.refresh(0, 0, 0, 0, rows, cols)

    last_line = rows - 1  # without -1 it will crash
    parent.addstr(last_line - 1, 0, f" the next window could be x:{new_x} y:{new_y}\n")
    parent.addstr(last_line, 0, f" last win x:{prev_x} y:{prev_y} | total streams({len(JSON_DATA['data'])})")


def draw(screen):
    curses.curs_set(0)           # Turn off cursor
    curses.use_default_colors()  # terminal colors & transparency

    # get screen size
    screen_h_rows, screen_w_cols = screen.getmaxyx()
    screen.refresh()

    # two_screens_h = screen_h_rows + screen_h_rows
    # pad is the main root scrollable window
    pad = curses.newpad(screen_h_rows, screen_w_cols)
    pad.scrollok(True)
    pad.addstr("\n Following live streams:\n")
    pad.addstr(f" screen rows:{screen_h_rows} cols:{screen_w_cols}\n")

    # Start printing text from (0,2) of the pad (first line, 3rd char)
    # on the screen at position (5,5)
    # with the maximum portion of the pad displayed being 20 chars x 15 lines
    # Since we only have one line, the 15 lines is overkill, but the 20 chars
    # will only show 20 characters before cutting off
    # left here as example:
    # pad.refresh(0, 2, 5, 5, 15, 20)
    pad.refresh(0, 0, 0, 0, screen_h_rows, screen_w_cols)

    create_sub_windows(pad, screen_h_rows, screen_w_cols)
    pad.refresh(0, 0, 0, 0, screen_h_rows, screen_w_cols)

    screen.getch()      # wait for a key press to exit
    curses.curs_set(1)  # Turn cursor back on


def main():
    """
    The curses.wrapper function is an optional function that
    encapsulates a number of lower-level setup and teardown
    functions, and takes a single function to run when
    the initializations have taken place.
    """
    #  data.update_live_streams()
    curses.wrapper(draw)


main()
