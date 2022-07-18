#!/usr/bin/env python3
# coding=utf-8

from itertools import islice
from threading import Thread
from typing import TypeVar
from twitchez import HEADER_H
from twitchez import STDSCR
from twitchez import conf
from twitchez import hints
from twitchez import open_chat
from twitchez import open_cmd
from twitchez import pages
from twitchez import utils
from twitchez.clip import clip
from twitchez.tabs import tab_names_ordered
from twitchez.thumbnails import container_size
import curses


SelfBoxes = TypeVar("SelfBoxes", bound="Boxes")


class Boxes:
    """Operate on list of Boxes"""
    boxlist = []
    drawn_boxes = []

    def add(self, obj):
        """Add box object to list."""
        self.boxlist.append(obj)

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

    def show_hints_boxes(self):
        """Show hints for visible/drawn boxes."""
        boxes = self.drawn_boxes
        hseq = hints.hint(boxes)
        for box, hint in zip(boxes, hseq):
            box.hint = hint
            box.show_hint()
        return hints.find_seq(hseq)

    def show_boxes_hint(self: SelfBoxes) -> tuple[SelfBoxes, str]:
        return self, self.show_hints_boxes()

    def get_box_attr_hint(self, hint, attr):
        """return attribute value of box object found by the hint."""
        boxes = self.drawn_boxes
        if not hasattr(boxes[0], attr):
            raise AttributeError(f"'{attr}' -> {boxes[0]} does not have such attribute!")
        for box in boxes:
            if getattr(box, "hint") == hint:
                return getattr(box, attr)
        raise Exception(f"value of ATTR:'{attr}' by the HINT:'{hint}' not found!")

    def copy_url(self, hint):
        if not hint:
            return
        value = self.get_box_attr_hint(hint, "url")
        clip(value)

    def open_url(self, hint, type):
        if not hint:
            return
        value = self.get_box_attr_hint(hint, "url")
        open_cmd.open_url(value, type)

    def open_chat(self, hint):
        if not hint:
            return
        value = self.get_box_attr_hint(hint, "user_login")
        open_chat.open_chat(value)


class Box:
    """Box with info about the stream/video inside the Grid."""
    w, h = container_size()
    last = h - 2  # last line of the box

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
        if self.fulltitle:
            max_len = int(self.w * 3)  # 3 box widths (lines)
            title = utils.word_wrap_title(self.title, self.w, max_len)
            try:
                win.addnstr(self.last - 2, 0, title, max_len)
            except Exception:
                win.box()
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
    w, h = container_size()

    def __init__(self, key_list: list, page_name: str):
        self.key_list = key_list
        self.page_name = page_name
        self.__ba = BodyArea()
        self.area_cols = self.__ba.cols
        self.area_rows = self.__ba.rows
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
            c = int(self.area_cols - self.w * cols) // cols
        if rows < 1:
            r = 0
        else:
            r = int(self.area_rows - self.h * rows) // rows
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
        self.index(str(start_index))
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
    """Page which renders everything."""

    def __init__(self, page_dict):
        self.pages_class = pages.Pages(page_dict)
        self.page_name = self.pages_class.page_name
        self.grid_func = self.pages_class.grid_func
        self.loaded = False

    def loading(self):
        """Simple animation to show that something is being done (Page loading).
        Currently the animation cycle is very short and ends even
        if the loading is not yet finished, '*' - static indicator of this.

        This is done intentionally to not ruin everything
        if raise() or crash occurred while thread is not yet finished and etc.
        The animation is short to quickly return to the terminal if an error is raised.
        """
        # NOTE: currently ANIMATION introduces extra wait time during draw() calls
        # on simple and fast operations like redraw() => so animation is disabled.
        # It does not feel like the fancy animation is worth it.
        ANIMATION = False

        def animation():
            """Animation length is intentionally short."""
            chars = "-\\|/"  # animation chars
            for _ in range(8):
                for c in chars:
                    win.insstr(c)
                    win.refresh()
                    curses.napms(25)
                    # finish animation right now!
                    if self.loaded:
                        return

        def anima_thread():
            t = Thread(target=animation())
            t.start()
            t.join()

        try:
            win = curses.newwin(1, 1, 0, 0)
        except Exception:
            return

        try:
            if ANIMATION:
                anima_thread()
            else:
                win.insstr("*")
        finally:
            if self.loaded:
                win.erase()
            else:
                # leave a static indicator about not yet finished loading
                # it probably will be cleared by some clear of the screen
                # so we do not bother much about clearing of the static indicator :)
                win.insstr("*")
            win.refresh()

    def draw_header(self):
        """Draw page header."""
        indent = 2  # indent from side
        indent_between = " "
        separator = "|"  # separator between tabs
        between_tabs = indent_between + separator + indent_between
        logo = "[twitchez]"
        c_page = self.page_name  # current page name
        _, w = STDSCR.getmaxyx()
        head = STDSCR.derwin(HEADER_H - 1, w, 0, 0)
        other_tabs = ""
        # tab order where current page is always first in list (to look as carousel)
        taborder = []
        tnames = tab_names_ordered()
        cpni = tnames.index(c_page)
        taborder.extend(tnames[cpni:])
        taborder.extend(tnames[:cpni])
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

    def draw_body(self, grid, fulltitle=False):
        """Draw page body."""
        body = BodyArea().window()
        if fulltitle:
            Boxes().draw(body, grid, fulltitle)
        else:
            Boxes().draw(body, grid)
        return body

    def draw(self, fulltitle=False):
        """return grid and draw full page."""
        self.loading()
        grid = self.grid_func()
        self.draw_body(grid, fulltitle)
        self.draw_header()
        self.loaded = True  # finish animation of loading if not yet ended
        return grid


class BodyArea:
    """Body area size of the window in the terminal cells."""

    def __init__(self):
        self.rows, self.cols = STDSCR.getmaxyx()
        self.rows = self.rows - HEADER_H

    def window(self):
        """Create & return body window."""
        return STDSCR.derwin(self.rows, self.cols, HEADER_H, 0)
