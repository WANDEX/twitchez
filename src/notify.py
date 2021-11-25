#!/usr/bin/env python3
# coding=utf-8

from shutil import which
import conf
import subprocess

notify_cmd = conf.setting("notify_cmd")


def first_cmd_word() -> str:
    return notify_cmd.split()[0]


def without_notifications() -> bool:
    """return True if notifications disabled via notify_cmd in settings."""
    if "false" in first_cmd_word().lower():
        return True
    return False


def notify_cmd_check() -> bool:
    """return True if notify_cmd set in config and executable(first word) found at PATH"""
    # written this way for readability
    if not without_notifications():
        executable = first_cmd_word()
        if executable != "undefined":
            if which(executable):
                return True
    return False


def dunstify_cmd() -> list:
    DST = "string:x-dunst-stack-tag"
    cmd = f"dunstify -u low -h {DST}:TFL -h {DST}:hi"
    return cmd.split()


def notify_send_cmd() -> list:
    cmd = "notify-send -u low"
    return cmd.split()


def raise_user_note():
    """raise exception for regular user without traceback."""
    if without_notifications():
        return
    try:
        a = "A program to send desktop notifications was not found at your 'PATH'."
        b = "You can install 'notify-send' and it will be working by default."
        c = "Also you can set your own program cmd via 'notify_cmd = your cmd' in config."
        d = "If you want to use this program without seeing any notifications from it,"
        e = "simply paste next line in your config:"
        f = "notify_cmd = false"
        full_text = f"\n{a}\n{b}\n{c}\n{d}\n{e}\n{f}\n"
        raise Exception(full_text)
    except (Exception, KeyboardInterrupt) as exc:
        exit(exc)


def get_notify_cmd() -> list:
    """Check & return cmd if executable is on PATH."""
    cmd = []
    # prefer notify_cmd if set in config and found at PATH
    if notify_cmd_check():
        cmd = notify_cmd.split()
    elif which("dunstify"):
        cmd = dunstify_cmd()
    elif which("notify-send"):
        cmd = notify_send_cmd()
    else:
        raise_user_note()
    return cmd


def notify(body="", summary=""):
    """Show user notification."""
    if without_notifications():
        return
    s = f"[TFL] {summary}"
    b = f"{body}"
    cmd = get_notify_cmd()
    cmd.append(s)
    cmd.append(b)
    subprocess.Popen(cmd)
