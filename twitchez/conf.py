#!/usr/bin/env python3
# coding=utf-8

from configparser import ConfigParser, NoSectionError
from pathlib import Path
from twitchez import TWITCHEZDIR, fs


def read_conf(*configs):
    """Read config files with omitted section.
    Last config takes precedence over previous configs.
    """
    parser = ConfigParser()
    section = "[GENERAL]\n"
    for f in configs:
        if Path(f).is_file():  # check that file exist
            with open(f) as stream:
                parser.read_string(section + stream.read())
    return parser


glob_conf_dir = Path(TWITCHEZDIR, "config").resolve()

glob_conf = Path(glob_conf_dir, "default.conf").resolve()
user_conf = Path(fs.get_user_conf_dir(), "config.conf").resolve()

glob_keys = Path(glob_conf_dir, "defkeys.conf").resolve()
user_keys = Path(fs.get_user_conf_dir(), "keys.conf").resolve()

temp_vars = Path(fs.get_tmp_dir(), "vars").resolve()
data_vars = Path(fs.get_data_dir("data"), "data").resolve()

config = read_conf(glob_conf, user_conf)
keymap = read_conf(glob_keys, user_keys)


def setting(keyname):
    found = config.get("GENERAL", keyname)
    return found


def key(keyname):
    found = keymap.get("GENERAL", keyname, fallback="")
    return found


def tmp_set(option, value, section="GENERAL"):
    """Set tmp variable value."""
    temp = ConfigParser()
    temp.read(temp_vars)
    if not temp.has_section(section):
        temp.add_section(section)
    temp.set(str(section), str(option), str(value))
    with open(temp_vars, "w") as f:
        temp.write(f, space_around_delimiters=False)


def tmp_get(keyname, fallback, section="GENERAL"):
    """Get tmp variable value."""
    temp = ConfigParser()
    temp.read(temp_vars)
    if not temp.has_section(section):
        temp.add_section(section)
    if fallback or not temp.has_option(section, keyname):
        found = temp.get(section, keyname, fallback=fallback)
    else:
        found = temp.get(section, keyname)
    return found


def cfpath(fallback: Path, fpath="") -> Path:
    """Return fallback path, if fpath is not valid."""
    ppath = Path(fpath)
    if not fpath or not ppath.is_file:
        ppath = fallback
    return ppath.resolve()


def dta_file(fpath="") -> Path:
    """Return fpath path or fallback to the default data file path."""
    return cfpath(data_vars, fpath)


def cp_dta(fpath: Path) -> tuple[ConfigParser, Path]:
    """Set defaults, read config & return class object."""
    fpath = dta_file(fpath.as_posix())
    dta = ConfigParser()
    # fix: preserve capitalization (option as is without transformation)
    # read more: https://docs.python.org/3/library/configparser.html#ConfigParser.optionxform(option)
    dta.optionxform = lambda option: option
    dta.read(fpath)
    return dta, fpath


def dta_set(option, value, section="GENERAL", fpath=""):
    """Set data variable value."""
    fpath = dta_file(fpath)
    dta, fp = cp_dta(fpath)
    if not dta.has_section(section):
        dta.add_section(section)
    dta.set(str(section), str(option), str(value))
    with open(fp, "w") as f:
        dta.write(f, space_around_delimiters=False)


def dta_get(option, fallback, section="GENERAL", fpath=""):
    """Get data variable value."""
    fpath = dta_file(fpath)
    dta, _ = cp_dta(fpath)
    if not dta.has_section(section):
        dta.add_section(section)
    if fallback or not dta.has_option(section, option):
        found = dta.get(section, option, fallback=fallback)
    else:
        found = dta.get(section, option)
    return found


def dta_rmo(option: str, section="GENERAL", fpath=""):
    """Remove data option."""
    fpath = dta_file(fpath)
    dta, fp = cp_dta(fpath)
    dta.remove_option(section, option)
    with open(fp, "w") as f:
        dta.write(f, space_around_delimiters=False)


def dta_list(section="GENERAL", fpath="") -> list:
    """Return a list of (name, value) tuples for each option in a section."""
    fpath = dta_file(fpath)
    dta, _ = cp_dta(fpath)
    try:
        return dta.items(section)
    except NoSectionError:
        return []
