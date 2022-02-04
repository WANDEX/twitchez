#!/usr/bin/env python3
# coding=utf-8

from twitchez import command
from twitchez import conf
import subprocess
try:
    import webbrowser
except ImportError:
    has_webbrowser = False
else:
    has_webbrowser = True
    import os


chat_cmd = conf.setting("open_chat_cmd")
executable = command.first_cmd_word(chat_cmd)
without_funcs = command.without_funcs(executable)
cmd_check = command.cmd_check(executable)


def open_chat(channel_login):
    """Open twitch chat of the channel."""
    url = f"https://www.twitch.tv/popout/{channel_login}/chat?popout="
    if cmd_check:
        cmd = chat_cmd.split()
        cmd.append(url)
        sub = subprocess.Popen
        sub(cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
    elif has_webbrowser and not without_funcs:
        """Open in default browser using webbrowser module.
        Following (currently) are the only way to suppress stdout & stderr produced by webbrowser.open().
        We suppress everything for the case if webbrowser.open() outputs something before opening.
        Read more here: 'https://stackoverflow.com/a/2323563'.
        """
        savout = os.dup(1)  # stdout
        saverr = os.dup(2)  # stderr
        os.close(1)
        os.close(2)
        os.open(os.devnull, os.O_RDWR)
        try:
            webbrowser.open_new(url)
        finally:
            os.dup2(savout, 1)
            os.dup2(saverr, 2)


if __name__ == "__main__":
    open_chat("LIRIK")
