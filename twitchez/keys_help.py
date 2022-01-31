#!/usr/bin/env python3
# coding=utf-8

from twitchez import HEADER_H
from twitchez import STDSCR
from twitchez import __version__
from twitchez import keys
from twitchez import thumbnails
import curses


def short_desc(string: str) -> str:
    """Make short readable description by removing one of specific patterns from string.
    Also replace _ characters by whitespace.
    """
    # Python 3.10.1 BUG:
    # >>> "tab_add".lstrip("tab_") => produces "dd" while it should be "add"
    patterns_to_strip = ["scroll_", "hint_", "tab"]
    for pattern in patterns_to_strip:
        if string.startswith(pattern):
            string = string.lstrip(pattern)
            break  # remove only the first pattern found
    out = string.replace("_", " ").strip()
    return out


def table_generate(dict, header=""):
    """Generate simple string as table of keys and their description."""
    table = ""
    if header:
        table += f"\t{header}\n"
    for name, key in dict.items():
        desc = short_desc(name)
        table += "{:4} {:10}\n".format(key, desc)
    return table


def table_lines(keysdict, header) -> list:
    """Generate simple list of strings with key and short description.
    Each line in the list is the same length (trailing whitespaces).
    """
    kws = 4  # num of ws after key char
    maxlen = 15
    for t in keysdict.keys():
        maxlen = max(maxlen, len(t))  # max length of longest line
    # TODO: DOUBTS: maybe i should calculate maxlen of short_desc
    hlws = " " * 4  # header leading whitespaces
    htws = " " * (maxlen - len(header) - len(hlws) + kws + 1)  # header trailing whitespaces
    outheader = hlws + header + htws
    list_of_lines = []
    list_of_lines.append(outheader)
    frmtstr = "{:" + str(kws) + "} {:" + str(maxlen) + "}"
    for name, key in keysdict.items():
        desc = short_desc(name)
        string = frmtstr.format(key, desc)
        list_of_lines.append(string)
    return list_of_lines


def append_blank_lines(table: list, num_of_out_lines: int) -> list:
    """Append to the table empty lines of the same max width till num of total lines.
    Used to make all tables of equal line count.
    """
    maxlen = len(max(table))  # max length of longest line (max len of element)
    blank_line = " " * maxlen
    while len(table) < num_of_out_lines:
        table.append(blank_line)
    return table


def table_join(*args):
    """Join tables from multiple args."""
    tables = ""
    for arg in args:
        tables += "\n{0}".format(arg)
    return tables


def simple_tables():
    sk = table_generate(keys.scroll_keys, "SCROLL")
    tk = table_generate(keys.tab_keys, "TABS")
    hk = table_generate(keys.hint_keys, "HINTS")
    ok = table_generate(keys.other_keys, "OTHER")
    tables = table_join(sk, tk, hk, ok)
    return tables


def dumb_table(pad):
    sk = table_generate(keys.scroll_keys, "SCROLL")
    tk = table_generate(keys.tab_keys, "TABS")
    hk = table_generate(keys.hint_keys, "HINTS")
    ok = table_generate(keys.other_keys, "OTHER")
    tables = [sk, tk, hk, ok]
    maxln, maxlen = 0, 16
    for t in tables:
        longest_line = max(str(t).splitlines())  # longest line in table
        maxlen = max(maxlen, len(longest_line))  # max length of longest line
        maxln = max(maxln, t.count("\n"))  # max total lines in table
    H, W = pad.getmaxyx()
    # spacing between elements
    spacing = maxlen + 4
    cols = W // spacing
    try:  # for more even spacing between elements
        sc = (W - int(cols * spacing)) // cols
    except ZeroDivisionError:
        sc = 0
    spacing += sc
    y, x = 1, sc
    current_col = 1
    next_row = maxln + 1
    for t in tables:
        # fix: if not enough space -> do not try to create subwin
        if cols < 1 or W < x or H < y + next_row:
            break
        subwin = pad.derwin(y, x)
        subwin.addstr(t)
        subwin.refresh()
        if current_col < cols:
            current_col += 1
            x += spacing
        else:
            current_col = 1
            x = sc
            y += next_row
    return maxln


def help():
    """Draw help window with key mappings and their description."""
    H, W = STDSCR.getmaxyx()
    if H < 10 or W < 20:
        return

    thumbnails.Draw().finish()

    y, x = HEADER_H - 1, 2
    h, w = H - y * 2, W - x * 2

    close_help_keys = [
        curses.KEY_RESIZE,  # close on terminal resize event
        curses.KEY_F1,
        keys.other_keys.get("keys_help"),
        keys.other_keys.get("quit"),
    ]
    scroll_help_keys = keys.scroll_keys.values()

    v_str = f"v{__version__}"
    title = f" twitchez {v_str} "
    t_h_c = w // 2 - len(title) // 2  # title horizontal center

    win = STDSCR.derwin(h, w, y, x)
    win.clear()
    win.border()
    win.addstr(0, t_h_c, title, curses.A_BOLD)
    win.refresh()

    pad_y, pad_x = 2, 5
    pad_h = h - pad_y
    pad_w = w - pad_x

    pad = win.subpad(pad_h, pad_w, pad_y, pad_x)
    pad.scrollok(True)
    tln = dumb_table(pad)
    pad.refresh()

    end = tln
    if tln > pad_h:
        end = tln - pad_h
    else:
        end = 0
    pos = 0

    while True:
        c = STDSCR.get_wch()
        # enable scrolling only if content doesn't fit in height entirely
        if tln < end:
            if c in scroll_help_keys:
                if c == keys.scroll_keys.get("scroll_down"):
                    pos += 1
                elif c == keys.scroll_keys.get("scroll_up"):
                    pos -= 1
                elif c == keys.scroll_keys.get("scroll_down_page"):
                    pos += 5
                elif c == keys.scroll_keys.get("scroll_up_page"):
                    pos -= 5
                elif c == keys.scroll_keys.get("scroll_top"):
                    pos = 0
                elif c == keys.scroll_keys.get("scroll_bot"):
                    pos = end
                # limit scroll
                if pos < 0:
                    pos = 0
                elif pos > end:
                    pos = end
                pad.clear()
                dumb_table(pad)
                pad.scroll(pos)
                pad.refresh()
                continue
        if c in close_help_keys:
            pad.clear()
            pad.refresh()
            break


if __name__ == "__main__":
    table = simple_tables()
    print(table)
