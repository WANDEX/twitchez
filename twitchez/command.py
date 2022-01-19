#!/usr/bin/env python3
# coding=utf-8

from shutil import which


def first_cmd_word(cmd) -> str:
    return cmd.split()[0]


def without_funcs(executable) -> bool:
    """return True if funcs are disabled via cmd in settings."""
    if "false" in executable.lower():
        return True
    return False


def executable_check(executable) -> bool:
    """return True if executable(first word from cmd) set in config and found at PATH."""
    # written this way for readability
    if executable != "undefined":
        if which(executable):
            return True
    return False


def cmd_check(executable) -> bool:
    """return True if funcs are enabled & checks of executable are passed."""
    # written this way for readability
    if not without_funcs(executable):
        if executable_check(executable):
            return True
    return False
