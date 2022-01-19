#!/usr/bin/env python3
# coding=utf-8

from . import command
from . import conf
from shutil import which
import subprocess

ENCODING = "utf-8"

notify_cmd = conf.setting("notify_cmd")
executable = command.first_cmd_word(notify_cmd)
without_funcs = command.without_funcs(executable)
cmd_check = command.cmd_check(executable)


def expire_time():
    """return expire time for notifications from config."""
    return conf.setting("notify_time")


def dunstify_cmd() -> list:
    # NOTE: dunst stack tag 'hi' stands for 'history ignore' and can be used for that purpose.
    # (requires creating matching rule in dunst config)
    t = expire_time()
    DST = "string:x-dunst-stack-tag"
    cmd = f"dunstify -t {t} -u low -h {DST}:TFL -h {DST}:hi"
    return cmd.split()


def notify_send_cmd() -> list:
    t = expire_time()
    cmd = f"notify-send -t {t} -u low"
    return cmd.split()


def raise_user_note():
    """raise exception for regular user without traceback."""
    if without_funcs:
        return
    a = "A program to send desktop notifications was not found at your 'PATH'."
    b = "You can install 'notify-send' and it will be working by default."
    c = "Also you can set your own program cmd via 'notify_cmd = your cmd' in config."
    d = "If you want to use this program without seeing any notifications from it,"
    e = "simply paste next line in your config:"
    f = "notify_cmd = false"
    full_text = f"\n{a}\n{b}\n{c}\n{d}\n{e}\n{f}\n"
    raise Exception(full_text)


def get_notify_cmd() -> list:
    """Check & return cmd if executable is on PATH."""
    cmd = []
    # prefer notify_cmd if set in config and found at PATH
    if cmd_check:
        cmd = notify_cmd.split()
    elif which("dunstify"):
        cmd = dunstify_cmd()
    elif which("notify-send"):
        cmd = notify_send_cmd()
    else:
        raise_user_note()
    return cmd


def notify(body="", summary="", error=False):
    """Show user notification."""
    if without_funcs:
        return
    s = f"[TFL] {summary}"
    b = f"{body}"
    cmd = get_notify_cmd()
    # FIXME: if user specified custom notify_cmd that does not support additional args
    #        like we do here, it will break. (because we add -u & -t options after getting cmd)
    if error:
        cmd.append("-u")
        cmd.append("critical")
        cmd.append("-t")
        cmd.append("8000")
    cmd.append(s)
    cmd.append(b)
    subprocess.Popen(cmd, text=True, encoding=ENCODING)
