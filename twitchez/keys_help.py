#!/usr/bin/env python3
# coding=utf-8

from twitchez import HEADER_H
from twitchez import STDSCR
from twitchez import __version__
from twitchez import keys
from twitchez import thumbnails
import curses
import re

SIMPLE_TEXT = True


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


def table_lines(keysdict, header) -> list:
    """Generate simple list of strings with key and short description.
    Each line in the list is the same length (trailing whitespaces).
    """
    kws = 4        # num of ws after key char
    hws = kws + 1  # num of ws before header
    maxlen = 15
    for t in keysdict.keys():
        maxlen = max(maxlen, len(short_desc(t)))  # max length of longest line
    # header leading & trailing whitespaces
    hlws = " " * hws
    htws = " " * (maxlen - len(header) - len(hlws) + hws)
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


def simple_tables(area_width) -> tuple[int, str]:
    """Simple string tables as grid that fit in area_width.
    returns: total line count, multiline string as table.
    """
    sk = table_lines(keys.scroll_keys, "[SCROLL]")
    tk = table_lines(keys.tab_keys, "[TABS]")
    hk = table_lines(keys.hint_keys, "[HINTS]")
    ok = table_lines(keys.other_keys, "[OTHER]")
    tables = [sk, tk, hk, ok]
    maxln = len(max(tables, key=len))  # max num of lines in table (max num of elements in list)
    maxlen = len(max(max(t, key=len) for t in tables))  # max length of longest line
    # make all tables of equal line count
    sk = append_blank_lines(sk, maxln)
    tk = append_blank_lines(tk, maxln)
    hk = append_blank_lines(hk, maxln)
    ok = append_blank_lines(ok, maxln)
    tables = [sk, tk, hk, ok]

    # even spacing and indent from left
    maxcolnum = area_width // maxlen
    if maxcolnum > 4:  # limit max number of table columns
        maxcolnum = 4
    free_cols = area_width - int(maxlen * maxcolnum)
    if free_cols < maxcolnum or maxcolnum < 2:
        rem_on_col = 0
    else:
        rem_on_col = free_cols // maxcolnum - 1
    if rem_on_col == 0 or maxcolnum < 2:
        indentstr = ""
    else:
        # NOTE: the difference with one non-half indent is especially noticeable
        #       that the center is shifted at large terminal widths (200-239 cols)
        indentstr = " " * (rem_on_col // 2)
    strtemplateraw = indentstr + "{}" + indentstr

    out = ""
    add_row = "\n\n"  # new lines for the new row of tables
    for num in range(len(tables), 0, -1):
        strtemplate = strtemplateraw * num
        if num == 4:
            out += "\n".join(strtemplate.format(t1, t2, t3, t4) for t1, t2, t3, t4 in zip(sk, tk, hk, ok))
            out += add_row
        elif num == 3:
            out += "\n".join(strtemplate.format(t1, t2, t3) for t1, t2, t3 in zip(sk, tk, hk))
            out += add_row
            out += "\n".join(strtemplateraw.format(t4) for t4 in ok)
        elif num == 2:
            out += "\n".join(strtemplate.format(t1, t2) for t1, t2 in zip(sk, tk))
            out += add_row
            out += "\n".join(strtemplate.format(t3, t4) for t3, t4 in zip(hk, ok))
        elif num == 1:
            for _t in tables:
                out += "\n".join(strtemplateraw.format(t1) for t1 in _t)
                out += add_row
        else:
            out = "E" * area_width
        out = out.rstrip()  # trim empty lines from the end of the out string & trailing ws
        maxlinelen = len(max(out.splitlines(), key=len))  # max length of longest line
        if maxlinelen <= area_width:
            break
        else:
            out = ""  # clear
    # replace repeating empty lines by a single empty line
    out = re.sub(r'\n\s*\n', '\n\n', out, re.MULTILINE)
    tln = out.count("\n") + 1  # total lines count
    return tln, out


def push_text(win, text: str, pos=0):
    """Add text str into window respecting it's height.
    Also update text after changing scroll position.
    (simple text string scrolling).
    """
    win.clear()
    h, _ = win.getmaxyx()
    lines = text.splitlines()
    if h >= len(lines):
        # all lines of text can simply be placed inside a win
        win.addstr(text)
    else:
        # addstr only slice of text that can fit inside a win
        text_slice = "\n".join(lines[pos:h + pos])
        win.addstr(text_slice)
    win.refresh()


def table_generate(keysdict, header) -> str:
    """Generate simple string as table of keys and their description.
    (for table using curses windows)
    """
    table = ""
    if header:
        table += f"\t{header}\n"
    for name, key in keysdict.items():
        desc = short_desc(name)
        table += "{:4} {:10}\n".format(key, desc)
    return table


def curse_tables(pad, pos=0):
    pad.clear()
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
    pad.scroll(pos)
    pad.refresh()
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

    table = ""
    if SIMPLE_TEXT:
        tln, table = simple_tables(pad_w)
        push_text(pad, table)
    else:
        tln = curse_tables(pad)

    end = tln - pad_h
    pos = 0

    while True:
        c = STDSCR.get_wch()
        # enable scrolling only if content doesn't fit in height entirely
        if tln > pad_h:
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
                if SIMPLE_TEXT:
                    push_text(pad, table, pos)
                else:
                    curse_tables(pad, pos)
                continue
        if c in close_help_keys:
            pad.clear()
            pad.refresh()
            break


if __name__ == "__main__":
    def print_w_info(width):
        """To be able to see where are: width limit, center."""
        ln, table = simple_tables(width)
        fstring = " w:[{0}] ln:({1}) "
        info = fstring.format(width, ln)
        half = width // 2  # approx (as this is terminal cells)
        halfs = "─" * (half - 2)  # 2 = "x" as center + extra "─" in beg
        beg = "┌─" + info + halfs[len(info):]
        end = halfs + "┐"
        bar = beg + "x" + end
        print(bar)
        print(table)

    print("=" * 100)
    print_w_info(70)
    print_w_info(80)
    print_w_info(100)
    print_w_info(130)
