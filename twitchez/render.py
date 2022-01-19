#!/usr/bin/env python3
# coding=utf-8

from . import conf
from . import open_cmd
from . import pages
from . import search
from . import utils
from .clip import clip
from .consts import STDSCR
from .iselect import iselect
from .thumbnails import container_size
from ast import literal_eval
from itertools import islice
from time import sleep
import curses
import re


class Hints:
    hint_chars = str(conf.setting("hint_chars"))
    active_hints = []

    def total(self, items) -> tuple[int, int]:
        """Return (total_seq, hint_length) based on hint_chars,
        individual hint_length formula and len of items.
        total_seq = number of possible sequences,
        hint_length = [1-3] length of each hint.
        """
        hcl = len(self.hint_chars)
        sqr = hcl ** 2
        if hcl >= len(items):
            hint_length = 1
            total_seq = hcl
        elif sqr >= len(items):
            hint_length = 2
            total_seq = sqr
        else:
            hint_length = 3
            total_seq = sqr * 2 - hcl
        return total_seq, hint_length

    def shorten_uniq_seq(self, out_seq):
        """Shorten all unique hint sequences and insert at the beginning."""
        tmp_seq = out_seq.copy()
        # shorten all sequences by one character
        for i, seq in enumerate(tmp_seq):
            wlc = seq[:-1]  # seq without last char
            tmp_seq.pop(i)
            tmp_seq.insert(i, wlc)
        # remove all elements that occurs more than once
        seq_set = set(tmp_seq)  # set() for less loop iterations
        for seq in seq_set:
            occurs = tmp_seq.count(seq)  # the number of times an element occurs
            if occurs > 1:
                while seq in tmp_seq:
                    tmp_seq.remove(seq)
        if not tmp_seq:  # short unique sequences not found
            return out_seq
        # each letter associated with its position index in self.hint_chars
        order = {}
        for i, c in enumerate(self.hint_chars):
            order[c] = i + 3
        # compute the seq score by the order in which the letters appear in the sequence
        seq_score = {}
        for seq in tmp_seq:
            s1 = order[seq[0]]
            s2 = 0
            if len(seq) > 1:
                s2 = order[seq[1]]
            score = s1 * 3 + s2
            seq_score[seq] = score
        # dict of sequences sorted by the sequence score
        sorted_by_score = dict(sorted(seq_score.items(), key=lambda x: x[1]))
        sorted_short_seq = list(sorted_by_score.keys())
        sorted_short_seq.reverse()  # reverse() => we insert at the beginning
        # replace original seq by the shorter sequence as it occurs only once
        for sseq in sorted_short_seq:
            # original long seq found by the short seq
            llseq = [s for s in out_seq if re.search(f"^{sseq}.", s)]
            lseq = str(llseq[0])
            if lseq and lseq in out_seq:
                out_seq.remove(lseq)
            # insert all short sequences at the beginning
            out_seq.insert(0, sseq)
        return out_seq

    def gen_hint_seq(self, items) -> list:
        """Generate from hint_chars list of unique sequences."""
        _, hint_length = self.total(items)

        # one letter length hints
        if hint_length == 1:
            return list(self.hint_chars)[:len(items)]

        # simple repeated values of hint_length
        repeated = []
        for c in self.hint_chars:
            # nn ee oo ... (if length_chars=2)
            repeated.append(c * hint_length)

        # make unique combinations of letters in strict order
        # generates sequence of 2 or 3 letter length hints
        combinations = []
        for r in repeated:
            new_seq = ""
            for ci in range(hint_length, 1, -1):
                pi = ci - 1
                for c in self.hint_chars:
                    new_seq = r[:pi] + c + r[ci:]
                    if new_seq in repeated:
                        continue  # skip
                    if new_seq in combinations:
                        continue  # skip
                    combinations.append(new_seq)

        hint_sequences = []
        hint_sequences.extend(repeated)
        hint_sequences.extend(combinations)
        # limit by the number of sequences that is enough for all items
        out_seq = hint_sequences[:len(items)]
        # NOTE: short seq are more convenient to type
        out_seq = self.shorten_uniq_seq(out_seq)
        # limit the number of sequences, strictly after shortening! (just in case)
        if len(out_seq) > len(items):
            return out_seq[:len(items)]
        else:
            return out_seq

    def hint(self, items: list) -> list:
        """Return hint sequences for items."""
        hints = self.gen_hint_seq(items)
        self.active_hints = hints
        return hints

    def find_seq(self, hints) -> str:
        """Input characters until only one hint sequence is found."""
        cinput = ""
        select = hints
        while len(select) > 1:
            c = str(STDSCR.get_wch())
            cinput += c
            select = [s for s in select if re.search(f"^{cinput}", s)]
        if not select:
            return ""
        if len(select) != 1:
            raise ValueError(f"len:({len(select)}) Only one item should be in the list:\n{select}")
        return str(select[0])

    def show_hints_boxes(self):
        """Show hints for visible/drawn boxes."""
        boxes = Boxes.drawn_boxes
        hints = self.hint(boxes)
        for box, hint in zip(boxes, hints):
            box.hint = hint
            box.show_hint()
        return self.find_seq(hints)

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
        if not hint:
            return
        value = self.get_box_attr_hint(hint, "url")
        clip(value)

    def open_url(self, hint, type):
        if not hint:
            return
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
    try:  # list of tab names
        tabs = literal_eval(conf.tmp_get("tabs", [], "TABS"))
    except ValueError:  # handle literal_eval() error with empty list
        tabs = []

    def curtab(self):
        """Get current page name, or 'Following Live' as fallback."""
        return conf.tmp_get("current_page_name", "Following Live", "TABS")

    def fpagedict(self, tab_name="") -> dict:
        """Find and return page dict by the tab name or for current tab."""
        if not tab_name:  # return page_dict of current tab/page
            page_dict_str = conf.tmp_get("page_dict", "", self.curtab())
        else:
            page_dict_str = conf.tmp_get("page_dict", self.curtab(), tab_name)
        if not page_dict_str or page_dict_str == "Following Live":
            return search.following_live()
        try:
            page_dict = literal_eval(page_dict_str)
        except Exception as e:
            raise ValueError(f"page_dict_str: '{page_dict_str}'\n{e}")
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

    def find_tab(self) -> dict:
        """Find and return page dict of selected tab."""
        mulstr = "\n".join(self.tabs)  # each list element on it's own line
        tabname = iselect(mulstr, 130)
        # handle cancel of the command
        if tabname == 130:
            # fallback to current tab
            return self.fpagedict(self.curtab())
        return self.fpagedict(tabname)

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
    HEADER_H = pages.Pages.HEADER_H

    def __init__(self, page_dict):
        self.pages_class = pages.Pages(page_dict)
        self.page_name = self.pages_class.page_name
        self.grid_func = self.pages_class.grid_func
        self.loaded = False

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

    def draw_header(self):
        """Draw page header."""
        indent = 2  # indent from side
        indent_between = " "
        separator = "|"  # separator between tabs
        between_tabs = indent_between + separator + indent_between
        logo = "[twitchez]"
        c_page = self.page_name  # current page name
        _, w = STDSCR.getmaxyx()
        head = STDSCR.derwin(self.HEADER_H - 1, w, 0, 0)
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
        self.loaded = True  # finish loading animation
        return grid


class BodyArea:
    """Body area size of the window in the terminal cells."""
    HEADER_H = pages.Pages.HEADER_H

    def __init__(self):
        self.rows, self.cols = STDSCR.getmaxyx()
        self.rows = self.rows - self.HEADER_H

    def window(self):
        """Create & return body window."""
        return STDSCR.derwin(self.rows, self.cols, self.HEADER_H, 0)
