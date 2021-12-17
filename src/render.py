#!/usr/bin/env python3
# coding=utf-8

from ast import literal_eval
from clip import clip
from itertools import islice
from notify import notify
from time import sleep
import conf
import curses
import open_cmd
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

    def open_url(self, hint, type):
        value = self.get_box_attr_hint(hint, "url")
        open_cmd.open_url(value, type)


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

    def draw(self, parent, grid, fulltitle=False):
        """Draw boxes."""
        self.drawn_boxes.clear()
        stop = len(grid.coordinates())
        for box in islice(self.boxlist, stop):
            if fulltitle:
                box.fulltitle = True
            box.draw(parent)
            self.drawn_boxes.append(box)
        parent.refresh()
        self.boxlist.clear()


class Box:
    """Box with info about the stream inside the Grid."""
    h = int(conf.setting("container_box_height"))
    w = int(conf.setting("container_box_width")) - 4
    last = h - 2  # last line of box

    def __init__(self, user_login, user_name, title, category, x, y):
        self.user_login = user_login  # for composing url
        self.user_name = user_name
        self.title = utils.strclean(title)
        self.category = category
        self.x = x
        self.y = y
        self.url = f"https://www.twitch.tv/{self.user_login}"
        self.hint = ""
        self.img_path = ""
        self.viewers = ""
        self.duration = ""
        self.fulltitle = False

    def draw(self, parent):
        """Draw Box."""
        win = parent.derwin(self.h, self.w, self.y, self.x)
        win.addnstr(self.last, 0, f"{self.category}", self.w)
        if self.duration:
            duration = f"[{self.duration}]"
            rside = self.w - len(duration)
            win.addnstr(self.last - 1, 0, f"{self.user_name}", rside, curses.A_BOLD)
            win.addstr(self.last - 1, rside, duration)
        else:
            win.addnstr(self.last - 1, 0, f"{self.user_name}", self.w, curses.A_BOLD)
        if self.viewers:
            viewers = f" {self.viewers}"
            rside = self.w - len(viewers)
            win.addstr(self.last, rside, viewers, curses.A_BOLD)
        # FIXME: if title contains emoji characters -> "visual width" of one emoji ch may be ~2.
        # TODO: find a way to detect emoji in text, and recalculate max width of str properly.
        if self.fulltitle:
            maxw = int(self.w * 3)  # 3 box widths (lines)
            title = utils.word_wrap_for_box(self.title, self.w)
            win.addnstr(self.last - 2, 0, title, maxw)
        else:
            title = utils.strtoolong(self.title, self.w)
            win.addnstr(self.last - 2, 0, title, self.w)

    def show_hint(self):
        """Create window with hint character."""
        if self.hint:  # if hint not empty -> show hint
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
            if len(self.hint) == 1:
                hint = f" {self.hint} "
            elif len(self.hint) == 2:
                hint = f" {self.hint}"
            else:
                hint = f"{self.hint}"
            lh = len(hint)
            win = curses.newwin(1, lh + 1, self.y + self.h - 1, self.x + self.w - lh)
            win.addstr(hint, curses.color_pair(1))
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


class Tabs:
    """Tabs."""
    # list of tab names
    tabs = literal_eval(conf.tmp_get("tabs", [], "TABS"))

    def curtab(self):
        #  TODO: what page name is fallback? default page set in settings?
        return conf.tmp_get("current_page_name", "Following Live", "TABS")

    def fpagedict(self, tab_name) -> dict:
        """Find and return page dict by the tab name."""
        page_dict_str = conf.tmp_get("page_dict", self.curtab(), tab_name)
        page_dict = literal_eval(page_dict_str)
        return page_dict

    def add_tab(self, page_name):
        current_page_name = self.curtab()
        # don't add the same tab twice
        if page_name not in self.tabs:
            if not self.tabs or current_page_name not in self.tabs:
                self.tabs.append(current_page_name)
                if page_name not in self.tabs:
                    self.tabs.append(page_name)
            else:
                # find index of current page name and insert new tab after that index
                cindex = self.tabs.index(current_page_name)
                nindex = cindex + 1
                self.tabs.insert(nindex, page_name)
            conf.tmp_set("tabs", self.tabs, "TABS")

    def delete_tab(self):
        """Delete current tab and return page_dict of the previous tab."""
        ptabname = self.prev_tab(tab_name=True)
        self.tabs.remove(self.curtab())
        conf.tmp_set("tabs", self.tabs, "TABS")
        return self.fpagedict(ptabname)

    def next_tab(self, tab_name=False):
        """Return page_dict for the next tab name (carousel) or simply tab_name."""
        cindex = self.tabs.index(self.curtab())
        nindex = cindex + 1
        if nindex > len(self.tabs) - 1:
            ntabname = self.tabs[0]
        else:
            ntabname = self.tabs[nindex]
        if tab_name:
            return ntabname
        else:
            return self.fpagedict(ntabname)

    def prev_tab(self, tab_name=False):
        """Return page_dict for the prev tab name (carousel) or simply tab_name."""
        cindex = self.tabs.index(self.curtab())
        pindex = cindex - 1
        ptabname = self.tabs[pindex]
        if tab_name:
            return ptabname
        else:
            return self.fpagedict(ptabname)


class Page:
    """Page which renders everything."""
    HEADER_H = 2

    def __init__(self, parent, pages_class):
        self.parent = parent
        self.pages_class = pages_class
        self.page_name = pages_class.page_name
        self.grid_func = pages_class.grid_func
        self.loaded = False

    def draw_header(self):
        """Draw page header."""
        indent = 2  # indent from side
        indent_between = " "
        separator = "|"  # separator between tabs
        between_tabs = indent_between + separator + indent_between
        logo = "[Twitch Curses]"
        c_page = self.page_name  # current page name
        _, w = self.parent.getmaxyx()
        head = self.parent.derwin(self.HEADER_H - 1, w, 0, 0)
        other_tabs = ""
        # tab order where current page is always first in list (to look as carousel)
        taborder = []
        tabs = Tabs.tabs
        cpni = tabs.index(c_page)
        taborder.extend(tabs[cpni:])
        taborder.extend(tabs[:cpni])
        for tab in taborder:
            if tab == c_page:
                continue  # skip current tab
            # indent_between with separator for each additional tab page
            other_tabs += between_tabs + tab
        icp = indent + len(c_page)  # width of current page with indent
        all_tabs = indent + len(c_page + other_tabs)
        if w > all_tabs:  # if we can fit all tabs
            head.addnstr(0, indent, c_page, len(c_page), curses.A_REVERSE)  # current Tab page
            head.addnstr(0, icp, other_tabs, len(other_tabs))
            if w > all_tabs + len(logo) + 1:  # if window have enough width for logo
                wllimit = w - len(logo) - indent
                head.addnstr(0, wllimit, logo, len(logo), curses.A_BOLD)
        else:
            # crop tabs visually that do not fit into the window
            # > character signalize about cropping (existence of other tabs)
            if w > indent:
                wclimit = w - indent - 1
                c_page = c_page[:wclimit - 1] + ">"
                head.addnstr(0, indent, c_page, wclimit, curses.A_REVERSE)
            if w > icp:
                wolimit = w - icp - 1
                other_tabs = other_tabs[:wolimit - 1] + ">"
                head.addnstr(0, icp, other_tabs, wolimit)
        head.refresh()
        return head

    @utils.background
    def loading(self):
        """Simple animation to show that currently something is being done."""
        chars = "-\\|/"  # animation chars
        win = curses.newwin(1, 1, 0, 0)
        for _ in range(25):
            for c in chars:
                win.insstr(c)
                win.refresh()
                sleep(.1)
                if self.loaded:
                    break
            if self.loaded:
                break
        win.erase()
        win.refresh()

    def draw_body(self, grid, fulltitle=False):
        """Draw page body."""
        h, w = self.parent.getmaxyx()
        body = self.parent.derwin(h - self.HEADER_H, w, self.HEADER_H, 0)
        if fulltitle:
            Boxes().draw(body, grid, fulltitle)
        else:
            Boxes().draw(body, grid)
        return body

    def draw(self, fulltitle=False):
        """return grid and draw full page."""
        self.loading()
        grid = self.grid_func(self.parent)
        self.draw_body(grid, fulltitle)
        self.draw_header()
        self.loaded = True  # finish loading animation
        return grid


class Window:
    """Window."""

    def __init__(self, parent):
        self.__rows, self.__cols = parent.getmaxyx()  # get window size
        self.rows = self.__rows - Page.HEADER_H
        self.cols = self.__cols
