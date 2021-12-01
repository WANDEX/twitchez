#!/usr/bin/env python3
# coding=utf-8

from clip import clip
from itertools import islice
from notify import notify
from open_stream import open_stream_url
import conf
import curses
import utils


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
            # TODO: maybe i should convert hint_chars to uppercase and start from beginning index?
            # TODO: OR i should start making two letter length hints if one letter hints are already used.
            #       ^ same as surfingkeys etc.
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
        clip(value)

    def open_url(self, hint):
        value = self.get_box_attr_hint(hint, "url")
        open_stream_url(value)


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

    def __init__(self, user_login, user_name, title, category, x, y):
        self.user_login = user_login  # for composing url
        self.user_name = user_name
        self.title = utils.strclean(title)
        self.category = category
        self.url = f"https://www.twitch.tv/{self.user_login}"
        self.hint = ""
        self.x = x
        self.y = y
        self.img_path = ""
        self.viewers = ""

    def draw(self, parent):
        """Draw Box."""
        win = parent.derwin(self.h, self.w, self.y, self.x)
        win.addnstr(self.last - 2, 1, f"{self.title}\n", self.lmax)
        win.addnstr(self.last - 1, 1, f"{self.user_name}\n", self.lmax, curses.A_BOLD)
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

    def __init__(self, parent, key_list: list, page_name: str):
        """sets coords dict from key_list -> each key will have (X, Y) values on the Grid."""
        self.__window = Window(parent)
        self.key_list = key_list
        self.page_name = page_name
        self.area_cols = self.__window.cols
        self.area_rows = self.__window.rows
        self.key_start_index = self.index()
        self.coords = self.coordinates()

    def capacity(self) -> tuple[int, int, int]:
        """Return - how many boxes can fit in: (cols, rows, total)."""
        cols = self.area_cols // self.w
        rows = self.area_rows // self.h
        total = cols * rows
        return cols, rows, total

    def spacing(self, cols, rows) -> tuple[int, int]:
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

    def index(self, start_index="") -> int:
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

    def shift_index(self, dir="down", page=False) -> int:
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


class Tab:
    """Each Tab has its own page."""
    # TODO


class Tabs:
    """Tabs."""
    # TODO




class Page:
    """Page which renders everything."""
    HEADER_H = 2
    header_borders = int(conf.setting("header_borders"))

    def __init__(self, parent, pages_class):
        self.parent = parent
        self.pages_class = pages_class
        self.page_name = pages_class.page_name
        self.grid_func = pages_class.grid_func

    def draw_header(self):
        """Draw page header."""
        # TODO: add support of dynamic Tabs
        indent = 2  # indent from side
        indent_between = 3
        indent_between_tabs = " " * indent_between
        logo = "[Twitch Curses]"
        c_page = self.page_name  # current page name
        _, w = self.parent.getmaxyx()
        head = self.parent.derwin(self.HEADER_H - 1, w, 0, 0)
        if w > len(c_page) + indent:
            if self.header_borders:
                head.box()
            head.addnstr(0, indent, c_page, len(c_page), curses.A_REVERSE)  # current Tab page
        # TODO: calculate length of all page names dynamically
        other_tabs = ""
        # TODO: + indent_between_tabs for each additional tab
        other_tabs += indent_between_tabs
        can_fit_via_tabs = c_page + other_tabs
        if w > len(can_fit_via_tabs + logo):
            head.addnstr(0, w - len(logo) - indent, logo, len(logo), curses.A_BOLD)
        head.refresh()
        return head

    def draw_body(self, grid):
        """Draw page body."""
        h, w = self.parent.getmaxyx()
        body = self.parent.derwin(h - self.HEADER_H, w, self.HEADER_H, 0)
        Boxes().draw(body, grid)
        return body

    def draw(self):
        """return grid and draw full page."""
        grid = self.grid_func(self.parent)
        self.draw_body(grid)
        self.draw_header()
        return grid


class Window:
    """Window."""

    def __init__(self, parent):
        self.__rows, self.__cols = parent.getmaxyx()  # get window size
        self.rows = self.__rows - Page.HEADER_H
        self.cols = self.__cols


def set_curses_start_defaults():
    """Set curses start defaults."""
    curses.use_default_colors()
    curses.curs_set(0)  # Turn off cursor


def run(func):
    """
    The curses.wrapper function is an optional function that
    encapsulates a number of lower-level setup and teardown
    functions, and takes a single function to run when
    the initializations have taken place.
    """
    curses.wrapper(func)
