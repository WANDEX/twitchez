#!/usr/bin/env python3
# coding=utf-8

from notify import notify
from shutil import which
import command
import conf
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
    elif which("dmenu"):
        cmd = dmenu_cmd()
    elif which("fzf"):
        cmd = fzf_cmd()
    else:
        raise_user_note()
    return cmd


def iselect(multilinestr: str):
    """Interactive select of one line from all."""
    if without_funcs:
        return 130
    text = multilinestr.strip()
    cmd = get_select_cmd()
    sub = subprocess.Popen
    # FIXME: fzf does not show input lines (selection is working)
    p = sub(cmd, text=True, encoding=ENCODING,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE)
    out, err = p.communicate(input=text)
    p.wait()  # wait for process to finish
    if p.returncode == 1 or p.returncode == 130:
        # dmenu(1), fzf(130) => command was canceled (Esc)
        return 130
    elif p.returncode != 0:
        notify(f"ERROR({p.returncode}): probably malformed cmd!\n{err}", "CANNOT SELECT:", error=True)
        raise Exception(f"ERROR({p.returncode}):\n{err}\n")
    return str(out).strip("\n")
