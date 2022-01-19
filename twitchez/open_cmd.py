#!/usr/bin/env python3
# coding=utf-8

from . import command
from . import conf
from .notify import notify
from shutil import which
import subprocess


def custom_cmd_check(type) -> tuple[bool, str]:
    if type == "stream":
        type_cmd = conf.setting("open_stream_cmd")
    elif type == "video":
        type_cmd = conf.setting("open_video_cmd")
    elif type == "extra":
        type_cmd = conf.setting("open_extra_cmd")
    else:
        type_cmd = conf.setting("open_stream_cmd")
    if type_cmd == "undefined":
        return False, ""
    executable = command.first_cmd_word(type_cmd)
    cmd_check = command.cmd_check(executable)
    return cmd_check, type_cmd


def custom_cmd(type_cmd, url) -> list:
    cmd = f"{type_cmd} {url}"
    return cmd.split()


def streamlink_cmd(url) -> list:
    streamlink_title_format = True
    quality = "best"  # hardcoded default
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
    a = "A program for opening stream url was not found at your 'PATH'."
    b = "You can install 'streamlink' and/or 'mpv' and it will be working by default."
    c = "Also you can set your own program cmd via 'open_*_cmd = your cmd' in config."
    full_text = f"\n{a}\n{b}\n{c}\n"
    raise Exception(full_text)


def get_open_cmd(url, type):
    """Check & return cmd if executable is on PATH."""
    cmd = []
    # DOUBTS TODO: also add built-in support for youtube-dl/yt-dlp
    #  ^ RESEARCH: already work like that with simple mpv call?
    # prefer custom open_cmd if set in config and found at PATH
    cmd_check, type_cmd = custom_cmd_check(type)
    if cmd_check and type_cmd:
        cmd = custom_cmd(type_cmd, url)
    # following are defaults and fallback if custom open cmd not set in config
    elif which("streamlink"):
        cmd = streamlink_cmd(url)
    elif which("mpv"):
        cmd = mpv_cmd(url)
    else:
        raise_user_note()
    return cmd


def open_url(url, type):
    """Open stream/video url with external/custom program."""
    cmd = get_open_cmd(url, type)
    notify(url, "opening:")
    sub = subprocess.Popen
    sub(cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
