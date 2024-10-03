#!/usr/bin/env python3
# coding=utf-8

from twitchez import conf

from shutil import which


def first_cmd_word(cmd: str) -> str:
    return cmd.split()[0]


def without_funcs(executable: str) -> bool:
    """return True if funcs are disabled via cmd in settings."""
    if "false" in executable.lower():
        return True
    return False


def executable_check(executable: str) -> bool:
    """return True if executable(first word from cmd) set in config and found at PATH."""
    if executable != "undefined":
        if which(executable):
            return True
    return False


def cmd_check(executable: str) -> bool:
    """return True if funcs are enabled & checks of executable are passed."""
    if not without_funcs(executable):
        if executable_check(executable):
            return True
    return False


def conf_cmd_check(conf_cmd: str) -> tuple[bool, str]:
    """check, return cmd from config."""
    cmd = conf.setting(conf_cmd)
    executable = first_cmd_word(cmd)
    cmd_ok = cmd_check(executable)
    return cmd_ok, cmd

