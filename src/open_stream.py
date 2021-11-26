#!/usr/bin/env python3
# coding=utf-8

from notify import notify
from shutil import which
import command
import conf
import subprocess

open_cmd = conf.setting("open_cmd")
executable = command.first_cmd_word(open_cmd)
without_funcs = command.without_funcs(executable)
cmd_check = command.cmd_check(executable)


def streamlink_cmd(url, quality) -> list:
    streamlink_title_format = True
    cmd = "streamlink --quiet".split()
    if streamlink_title_format:
        # those are streamlink formatting variables
        title = '{author} - {category} -- {title}'
        cmd.append("--title")
        cmd.append(title)
    cmd_args = f"{url} {quality}".split()
    cmd.extend(cmd_args)
    return cmd


def mpv_cmd(url) -> list:
    cmd = f"mpv {url}"
    return cmd.split()


def raise_user_note():
    """raise exception for regular user without traceback."""
    if without_funcs:
        return
    try:
        a = "A program for opening stream url was not found at your 'PATH'."
        b = "You can install 'streamlink' and it will be working by default."
        c = "Also you can set your own program cmd via 'open_cmd = your cmd' in config."
        d = "If you want to use this program without using it's open stream functions,"
        e = "simply paste next line in your config:"
        f = "open_cmd = false"
        full_text = f"\n{a}\n{b}\n{c}\n{d}\n{e}\n{f}\n"
        raise Exception(full_text)
    except (Exception, KeyboardInterrupt) as exc:
        exit(exc)


def get_open_stream_cmd(url):
    """Check & return cmd if executable is on PATH."""
    cmd = []
    # DOUBTS TODO: also add built-in support for youtube-dl/yt-dlp
    #  ^ RESEARCH: already work like that with simple mpv call?
    # prefer open_cmd if set in config and found at PATH
    if cmd_check:
        # TODO: pass url to that custom cmd
        cmd = open_cmd.split()
    elif which("streamlink"):
        quality = "best"  # FIXME: temporary hardcoded
        cmd = streamlink_cmd(url, quality)
    elif which("mpv"):
        cmd = mpv_cmd(url)
    else:
        raise_user_note()
    return cmd


def open_stream_url(url):
    """Open stream url."""
    if without_funcs:
        return False
    cmd = get_open_stream_cmd(url)
    notify(url, "opening:")
    sub = subprocess.Popen
    sub(cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
