#!/usr/bin/env python3
# coding=utf-8

from . import command
from . import conf
from .notify import notify
from shutil import which
import subprocess

ENCODING = "utf-8"

clip_cmd = conf.setting("clip_cmd")
executable = command.first_cmd_word(clip_cmd)
without_funcs = command.without_funcs(executable)
cmd_check = command.cmd_check(executable)


def xclip_cmd() -> list:
    cmd = "xclip -in -selection clipboard"
    return cmd.split()


def xsel_cmd() -> list:
    cmd = "xsel -i --clipboard"
    return cmd.split()


def raise_user_note():
    """raise exception for regular user without traceback."""
    if without_funcs:
        return
    a = "A program for copying content to clipboard was not found at your 'PATH'."
    b = "You can install 'xclip' and it will be working by default."
    c = "Also you can set your own program cmd via 'clip_cmd = your cmd' in config."
    d = "If you want to use this program without using it's clipboard functions,"
    e = "simply paste next line in your config:"
    f = "clip_cmd = false"
    full_text = f"\n{a}\n{b}\n{c}\n{d}\n{e}\n{f}\n"
    raise Exception(full_text)


def get_clip_cmd():
    """Check & return cmd if executable is on PATH."""
    cmd = []
    # prefer clip_cmd if set in config and found at PATH
    if cmd_check:
        cmd = clip_cmd.split()
    elif which("xclip"):
        cmd = xclip_cmd()
    elif which("xsel"):
        cmd = xsel_cmd()
    else:
        raise_user_note()
    return cmd


def clip(content: str):
    """Copy content to clipboard."""
    if without_funcs:
        return
    text = content.strip()
    p = subprocess.Popen(get_clip_cmd(), stdin=subprocess.PIPE, close_fds=True)
    p.communicate(input=text.encode(ENCODING))
    p.wait()  # wait for process to finish
    if p.returncode == 0:
        notify(text, "C:")
    else:
        notify(f"ERROR({p.returncode}): probably malformed cmd!", "NOT copied:", error=True)
