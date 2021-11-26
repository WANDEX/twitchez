#!/usr/bin/env python3
# coding=utf-8

from shutil import which


def first_cmd_word(cmd) -> str:
    return cmd.split()[0]


def executable_check(executable) -> bool:
    """return True if executable(first word from cmd) set in config and found at PATH."""
    # written this way for readability
    if executable != "undefined":
        if which(executable):
            return True
    return False
