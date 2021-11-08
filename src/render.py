#!/usr/bin/env python3
# coding=utf-8

from itertools import islice
import curses
import conf


class Boxes:
    """Operate on list of Boxes"""
    boxlist = []
    thmblist = []

    def add(self, obj):
        """Add box object to list."""
        self.boxlist.append(obj)

    def add_thmb(self, obj):
        """Add thumbnail ue params to list."""
        self.thmblist.append(obj)


class Box:
    """Box with info about the stream inside the Grid."""
    h = int(conf.setting("container_box_height"))
    w = int(conf.setting("container_box_width"))
    last = h - 2  # last line before bottom box border
    lmax = w - 2  # max length of string inside box

    def __init__(self, user, title, category, x, y):
        self.user = user
        self.title = title
        self.category = category
        self.url = f"https://www.twitch.tv/{user}"
        self.x = x
        self.y = y
        self.img_path = ""

    def draw(self, parent):
        """Draw Box."""
        win = parent.derwin(self.h, self.w, self.y, self.x)
        win.addnstr(self.last - 2, 1, f"{self.title}\n", self.lmax)
        win.addnstr(self.last - 1, 1, f"{self.user}\n", self.lmax, curses.A_BOLD)
        win.addnstr(self.last - 0, 1, f"{self.category}\n", self.lmax)
        win.box()
        Y, X = win.getparyx()
        win.addnstr(0, 1, f"X:{X}-Y:{Y}", self.lmax)  # for debug


class Grid:
    """Grid of boxes inside the Window."""
    h = int(conf.setting("container_box_height"))
    w = int(conf.setting("container_box_width"))

    def __init__(self):
        """set key_list -> each key will have (X, Y) values on the Grid."""
        # FIXME: temporary hardcoded
        self.area_cols = 230
        self.area_rows = 55
        self.key_list = []
        # TODO: update value after pressing scroll key
        #       particularly: set it to total from capacity()
        self.key_start_index = 0

    def capacity(self, string="all"):
        """Count how many boxes fit in the area.
        returns value based on string: "all", "cols", "rows", "total".
        """
        cols = int(self.area_cols / self.w)
        rows = int(self.area_rows / self.h)
        total = cols * rows
        if "all" in string:
            return cols, rows, total
        elif "total" in string:
            return total
        elif "col" in string:
            return cols
        elif "row" in string:
            return rows
        else:
            raise ValueError(f"Unsupported argument string: '{string}'")

    def spacing(self, cols, rows):
        """Calculate even spacing between grid elements.
        returns spacing: cols, rows.
        """
        c = int((self.area_cols - self.w * cols) / cols)
        r = int((self.area_rows - self.h * rows) / rows)
        return c, r

    def coordinates(self, initial_x=0, initial_y=0) -> dict:  # FIXME: x, y initial values temporary hardcoded
        """Return dict with: tuple(X, Y) values where each key_list element is the key."""
        cols, rows, total = self.capacity()
        total += self.key_start_index  # for scrolling
        scols, srows = self.spacing(cols, rows)
        x = initial_x + scols
        y = initial_y + srows
        current_col = 1
        coordinates = {}
        for key in islice(self.key_list, self.key_start_index, total):
            coordinates[key] = (x, y)
            if current_col < cols:
                current_col += 1
                x += scols + self.w
            else:
                current_col = 1
                x = initial_x + scols
                y += srows + self.h
        return coordinates
