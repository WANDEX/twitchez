#!/usr/bin/env python3
# coding=utf-8

from configparser import ConfigParser
import utils

glob_conf = utils.project_root("config", "default.conf")
user_conf = utils.project_root(utils.get_user_conf_dir(), "config.conf")

glob_keys = utils.project_root("config", "keys.conf")
user_keys = utils.project_root(utils.get_user_conf_dir(), "keys.conf")

config = ConfigParser()
config.read(glob_conf)
config.read(user_conf)  # user config takes precedence over global default config

keymap = ConfigParser()
keymap.read(glob_keys)
keymap.read(user_keys)  # user config takes precedence over global default config


def setting(keyname):
    found = config.get("GENERAL", keyname)
    return found


def key(keyname):
    found = keymap.get("GENERAL", keyname, fallback="")
    return found
