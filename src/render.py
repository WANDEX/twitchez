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
    w = int(conf.setting("container_box_width")) - 4
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
        self.viewers = ""

    def draw(self, parent):
        """Draw Box."""
        win = parent.derwin(self.h, self.w, self.y, self.x)
        win.addnstr(self.last - 2, 1, f"{self.title}\n", self.lmax)
        win.addnstr(self.last - 1, 1, f"{self.user}\n", self.lmax, curses.A_BOLD)
        win.addnstr(self.last, 1, f"{self.category}\n", self.lmax)
        if self.viewers:
            rside = self.lmax - len(self.viewers)
            win.addstr(self.last, rside, f" {self.viewers} ", curses.A_BOLD)
        win.box()
        Y, X = win.getparyx()
        win.addnstr(0, 1, f"X:{X}-Y:{Y}", self.lmax)  # for debug


class Grid:
    """Grid of boxes inside the Window."""
    h = int(conf.setting("container_box_height"))
    w = int(conf.setting("container_box_width"))

    def __init__(self, page_name):
        """set key_list -> each key will have (X, Y) values on the Grid."""
        # FIXME: temporary hardcoded
        self.area_cols = 230
        self.area_rows = 55
        self.key_list = []
        self.page_name = page_name
        self.key_start_index = self.index()

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

    def index(self, start_index=""):
        """Set/Get initial grid index."""
        if str(start_index):  # str -> to check if not empty (even 0 value)
            index = int(start_index)
            conf.tmp_set("grid_index", index, self.page_name)
        else:
            index = int(conf.tmp_get("grid_index", 0, self.page_name))
            if not index or index < 0:
                index = 0
                conf.tmp_set("grid_index", index, self.page_name)
        self.key_start_index = index
        return index

    def shift_index(self, dir="down", page=False):
        """Shift value of the key start index."""
        cols, _, total = self.capacity()
        elems_total = len(self.key_list)
        remainder = elems_total % cols
        if remainder == 0:
            end_of_page = elems_total - total
        else:
            end_of_page = elems_total - total - remainder + cols
        if elems_total <= total:
            start_index = 0
        else:
            grid_index = self.index()
            if dir == "top":
                start_index = 0
            elif dir == "bot":
                start_index = end_of_page
            elif page:
                if dir == "down":
                    start_index = grid_index + total
                else:
                    start_index = grid_index - total
            else:
                if dir == "down":
                    start_index = grid_index + cols
                else:
                    start_index = grid_index - cols
            if start_index < 0:
                start_index = 0
            elif start_index > end_of_page - start_index:
                start_index = end_of_page
        self.index(start_index)
        return start_index

    def coordinates(self) -> dict:
        """Return dict with: tuple(X, Y) values where each key_list element is the key."""
        initial_x, initial_y = 0, 0
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


class Page:
    """Page."""
    def __init__(self, render_func, page_parent, page_name):
        self.render_func = render_func
        self.page_parent = page_parent
        self.page_name = page_name

    def render_page(self):
        return self.render_func(self.page_parent)


def run(func):
    """
    The curses.wrapper function is an optional function that
    encapsulates a number of lower-level setup and teardown
    functions, and takes a single function to run when
    the initializations have taken place.
    """
    curses.wrapper(func)
