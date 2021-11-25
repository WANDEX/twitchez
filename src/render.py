#!/usr/bin/env python3
# coding=utf-8

from itertools import islice
from notify import notify
import curses
import conf


class Hints:
    prev_hint_index = -1
    hint_chars = str(conf.setting("hint_chars"))
    active_hints_letters = []

    def hint(self):
        """return next letter from hint_chars string."""
        inext = self.prev_hint_index + 1
        if len(self.hint_chars) > inext:  # FIXME: this check is not complete!
            hint = self.hint_chars[inext]
        else:
            # FIXME: this is temporary!
            hint = "E"
        self.prev_hint_index = inext  # set prev hint index
        return hint

    def hints_reset_index(self):
        self.prev_hint_index = -1

    def show_hints(self):
        self.active_hints_letters.clear()
        for box in Boxes.drawn_boxes:
            hint = self.hint()
            self.active_hints_letters.append(hint)
            box.hint = hint
            box.show_hint()
        self.hints_reset_index()

    def get_box_attr_hint(self, hint, attr):
        """return attribute value of box object found by the hint."""
        boxes = Boxes.drawn_boxes
        if not hasattr(boxes[0], attr):
            raise AttributeError(f"'{attr}' -> {boxes[0]} does not have such attribute!")
        for box in boxes:
            if getattr(box, "hint") == hint:
                return getattr(box, attr)
        raise Exception(f"value of ATTR:'{attr}' by the HINT:'{hint}' not found!")

    def copy_url(self, hint):
        value = self.get_box_attr_hint(hint, "url")
        # TODO: add copy to clipboard function
        notify(value, "copied:")


class Boxes:
    """Operate on list of Boxes"""
    boxlist = []
    thmblist = []
    drawn_boxes = []

    def add(self, obj):
        """Add box object to list."""
        self.boxlist.append(obj)

    def add_thmb(self, obj):
        """Add thumbnail ue params to list."""
        self.thmblist.append(obj)

    def draw(self, parent, grid):
        """Draw boxes."""
        self.drawn_boxes.clear()
        stop = len(grid.coordinates())
        for box in islice(self.boxlist, stop):
            self.drawn_boxes.append(box)
            box.draw(parent)
        parent.refresh()
        self.boxlist.clear()


class Box:
    """Box with info about the stream inside the Grid."""
    h = int(conf.setting("container_box_height"))
    w = int(conf.setting("container_box_width")) - 4
    box_borders = int(conf.setting("box_borders"))
    last = h - 2  # last line before bottom box border
    lmax = w - 2  # max length of string inside box

    def __init__(self, user, title, category, x, y):
        self.user = user
        self.title = title
        self.category = category
        self.hint = ""
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
        if self.box_borders:  # show box borders if set in config
            win.box()
        Y, X = win.getparyx()
        win.addnstr(0, 1, f"X:{X}-Y:{Y}", self.lmax)  # for debug

    def show_hint(self):
        """Create window with hint character."""
        if self.hint:  # if hint not empty -> show hint
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
            win = curses.newwin(1, 2, self.y + self.h - 1, self.x + self.w - 3)
            win.addch(self.hint, curses.color_pair(1))
            win.refresh()


class Grid:
    """Grid of boxes inside the Window."""
    h = int(conf.setting("container_box_height"))
    w = int(conf.setting("container_box_width"))

    def __init__(self, parent, page_name):
        """set key_list -> each key will have (X, Y) values on the Grid."""
        self.__window = Window(parent)
        self.area_cols = self.__window.cols
        self.area_rows = self.__window.rows
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
        if cols < 1:
            c = 0
        else:
            c = int((self.area_cols - self.w * cols) / cols)
        if rows < 1:
            r = 0
        else:
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
            elif start_index > end_of_page:
                start_index = end_of_page
        self.index(start_index)
        return start_index

    def coordinates(self) -> dict:
        """Return dict with: tuple(X, Y) values where each key_list element is the key."""
        initial_x, initial_y = 0, 0
        cols, rows, total = self.capacity()
        total += self.key_start_index  # for scrolling
        scols, srows = self.spacing(cols, rows)
        # for more even spacing from both sides
        sc = scols // 2
        sr = srows // 2
        x = initial_x + sc
        y = initial_y + sr
        current_col = 1
        coordinates = {}
        for key in islice(self.key_list, self.key_start_index, total):
            if cols > 2:
                x += sc
            coordinates[key] = (x, y)
            if current_col < cols:
                current_col += 1
                x += sc + self.w
            else:
                current_col = 1
                x = initial_x + sc
                y += sr + self.h
        return coordinates


class Page:
    """Page."""
    def __init__(self, render_func, page_parent, page_name):
        self.render_func = render_func
        self.page_parent = page_parent
        self.page_name = page_name

    def render_page(self):
        return self.render_func(self.page_parent)


class Tab:
    """Each Tab has its own page."""
    # TODO


class Tabs:
    """Tabs."""
    HEADER_HEIGHT = 2
    header_borders = int(conf.setting("header_borders"))
    # TODO

    def draw_header(self, parent):
        """Draw header."""
        # FIXME: temporary function till real realization of Tab & Tabs
        tc = "[Twitch Curses]"
        name = "Following Live"
        s = 3
        full_text = tc + " " * s + name
        _, w = parent.getmaxyx()
        head = parent.derwin(self.HEADER_HEIGHT - 1, w, 0, 0)
        if w > len(name) + 2:
            if self.header_borders:
                head.box()
            head.addnstr(0, 2, name, w, curses.A_REVERSE)  # Tab name
        if w > len(full_text):
            head.addnstr(0, len(name) + s, tc, len(tc), curses.A_BOLD)
        head.refresh()
        return head


class Window:
    """Window."""

    def __init__(self, parent):
        self.__rows, self.__cols = parent.getmaxyx()  # get window size
        self.rows = self.__rows - Tabs.HEADER_HEIGHT
        self.cols = self.__cols


def run(func):
    """
    The curses.wrapper function is an optional function that
    encapsulates a number of lower-level setup and teardown
    functions, and takes a single function to run when
    the initializations have taken place.
    """
    curses.wrapper(func)
