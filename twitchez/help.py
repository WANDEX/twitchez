#!/usr/bin/env python3
# coding=utf-8

from twitchez import STDSCR
from twitchez import keys


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
        table += f"{header}\n"
    for name, key in dict.items():
        desc = short_desc(name)
        table += "{:4} {:10}\n".format(key, desc)
    return table


def table_join(*args):
    """Join tables from multiple args."""
    tables = ""
    for arg in args:
        tables += "\n\t{0}".format(arg)
    return tables


def tables():
    sk = table_generate(keys.scroll_keys, "SCROLL")
    tk = table_generate(keys.tab_keys, "TABS")
    hk = table_generate(keys.hint_keys, "HINTS")
    ok = table_generate(keys.other_keys, "OTHER")
    tables = table_join(sk, tk, hk, ok)
    return tables


def help():
    """Draw help window with available keys and their description."""
    h, w = STDSCR.getmaxyx()
    pass


if __name__ == "__main__":
    table = tables()
    print(table)
