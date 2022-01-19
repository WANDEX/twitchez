#!/usr/bin/env python3
# coding=utf-8

from . import command
from . import conf
from . import thumbnails
from shutil import which
import curses
import subprocess

ENCODING = "utf-8"

select_cmd = conf.setting("select_cmd")
executable = command.first_cmd_word(select_cmd)
without_funcs = command.without_funcs(executable)
cmd_check = command.cmd_check(executable)


def dmenu_cmd() -> list:
    cmd = "dmenu -i -l 50"
    return cmd.split()


def fzf_cmd() -> list:
    cmd = "fzf --no-multi"
    return cmd.split()


def raise_user_note():
    """raise exception for regular user without traceback."""
    if without_funcs:
        return
    a = "A program for selecting of one line from all was not found at your 'PATH'."
    b = "You can install 'dmenu' or 'fzf' and it will be working by default."
    c = "Also you can set your own program cmd via 'select_cmd = your cmd' in config."
    d = "If you want to use this program without using it's interactive select functions,"
    e = "simply paste next line in your config:"
    f = "select_cmd = false"
    full_text = f"\n{a}\n{b}\n{c}\n{d}\n{e}\n{f}\n"
    raise Exception(full_text)


def get_select_cmd():
    """Check & return cmd if executable is on PATH."""
    cmd = []
    # prefer select_cmd if set in config and found at PATH
    if cmd_check:
        cmd = select_cmd.split()
    elif which("fzf"):
        cmd = fzf_cmd()
    elif which("dmenu"):
        cmd = dmenu_cmd()
    else:
        raise_user_note()
    return cmd


def iselect(multilinestr: str, fallback):
    """Interactive select of one line from all."""
    if without_funcs:
        return 130
    text = multilinestr.strip()
    cmd = get_select_cmd()
    if cmd[0] == "fzf":
        # fix: clearing of the terminal after calling subprocess
        curses.endwin()
        # hide thumbnails, they will be redrawn in the next redraw() call.
        thumbnails.Draw().finish()
    #  p = subprocess.run(cmd, input=text, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #  ^ FIXME: Why with stderr=subprocess.PIPE - we cannot see fzf?
    #  => How to get stderr then? (bug or what?)
    p = subprocess.run(cmd, input=text, text=True, stdout=subprocess.PIPE)
    sel = str(p.stdout).strip()
    if p.returncode == 1 or p.returncode == 130:
        # dmenu(1), fzf(130) => command was canceled (Esc)
        return 130
    elif p.returncode != 0:
        raise Exception(f"select cmd ERROR({p.returncode})\n{p.stderr}")
    # return fallback if input is not a substring of multilinestr
    if sel not in multilinestr:
        return fallback
    return sel
