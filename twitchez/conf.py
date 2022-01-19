#!/usr/bin/env python3
# coding=utf-8

from . import fs
from configparser import ConfigParser
from pathlib import Path

glob_conf = fs.project_root("config", "default.conf")
user_conf = fs.project_root(fs.get_user_conf_dir(), "config.conf")

glob_keys = fs.project_root("config", "keys.conf")
user_keys = fs.project_root(fs.get_user_conf_dir(), "keys.conf")

config = ConfigParser()
config.read(glob_conf)
config.read(user_conf)  # user config takes precedence over global default config

keymap = ConfigParser()
keymap.read(glob_keys)
keymap.read(user_keys)  # user config takes precedence over global default config

temp_vars = Path(fs.get_tmp_dir(), "vars")
temp = ConfigParser()


def setting(keyname):
    found = config.get("GENERAL", keyname)
    return found


def key(keyname):
    found = keymap.get("GENERAL", keyname, fallback="")
    return found


def tmp_set(option, value, section="GENERAL"):
    """Set tmp variable value."""
    temp.read(temp_vars)
    if not temp.has_section(section):
        temp.add_section(section)
    temp.set(str(section), str(option), str(value))
    with open(temp_vars, "w") as file:
        temp.write(file, space_around_delimiters=False)


def tmp_get(keyname, fallback, section="GENERAL"):
    """Get tmp variable value."""
    temp.read(temp_vars)
    if not temp.has_section(section):
        temp.add_section(section)
    if fallback or not temp.has_option(section, keyname):
        found = temp.get(section, keyname, fallback=fallback)
    else:
        found = temp.get(section, keyname)
    return found
