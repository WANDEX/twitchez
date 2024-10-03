#!/usr/bin/env python3
# coding=utf-8

from twitchez import command
from twitchez import conf
from twitchez import fs
from twitchez import utils

from pathlib import Path
from shutil import which
from sys import version_info, stdout
from threading import Timer

import aiohttp
import asyncio
import json
import os                       # listdir, sep, devnull, basename, splitext
import subprocess


# check if executables at PATH
HAS_UEBERZUG = bool(which("ueberzugpp")) | bool(which("ueberzug"))
# also check user cmd in case executable provided via full path
HAS_UEBERZUG |= command.conf_cmd_check("ueberzug_cmd")[0]


def raise_user_note():
    """raise exception for regular user without traceback."""
    raise Exception(
        "\n\n"
        "Neither ueberzugpp nor ueberzug were found at PATH. While text_mode is not enabled.\n"
        "You can install 'ueberzugpp' and it will be working by default.\n"
        "It supports more output options and platforms than old version of ueberzug written in python.\n"
        "Also you can set your own program cmd via 'ueberzug_cmd = your cmd' in config.\n"
        "This will allow you to override default ueberzugpp layer --output for you machine, etc.\n"
        "If you want to use this program without thumbnails,\n"
        "simply paste next line in your config:\n"
        "text_mode = 3\n"
    )


def get_ueberzug_cmd() -> list:
    """Check & return cmd if executable is on PATH."""
    cmd = ""
    user_cmd_ok, ueberzug_cmd = command.conf_cmd_check("ueberzug_cmd")
    if user_cmd_ok:
        # prefer ueberzug_cmd if set in config and found at PATH or if full path provided
        cmd = ueberzug_cmd
    elif which("ueberzugpp"):
        # NOTE: --no-cache is important, without it ueberzugpp will show old cached thumbnails!
        cmd = "ueberzugpp layer --no-cache --silent"
    elif which("ueberzug"):
        # seems like python version of ueberzug have no layer specific options
        cmd = "ueberzug layer"
    else:
        raise_user_note()
    return cmd.split()


def text_mode() -> int:
    """Text mode: 0 => thumbnails mode (min: 0, max: 3).
    [1-3] => do not do anything with thumbnails do not even download them!
    The higher the value, the more rows of cells there will be in the grid.
    """
    tm = int(conf.setting("text_mode"))
    if tm < 0:
        tm = 0
    elif tm > 3:
        tm = 3
    # explicit text mode if ueberzug not found (optional dependency)
    if not HAS_UEBERZUG and tm < 1:
        tm = 1
    return tm


def rdiv() -> int:
    """Thumbnail resolution divisor (min: 2, max: 10)."""
    div = 1 + int(conf.setting("grid_size"))
    if div < 2:
        div = 2
    elif div > 10:
        div = 10
    return div


def container_size(thumbnail=False) -> tuple[int, int]:
    """Return tuple: (width, height) - based on divisor key in table.
    Selected values are close as possible to the real resolution of the thumbnails.
    Except couple values where visual result more appropriate: with (2,3,4) as divisor.
    """
    table = {
        10: (24, 7),
        9: (27, 8),
        8: (30, 9),
        7: (35, 10),
        6: (40, 11),
        5: (48, 13),
        4: (56, 15),
        3: (76, 20),
        2: (90, 24),
    }
    # use fallback key if div key not found
    _def_fix: tuple = (40, 11)  # fix: None is not assignable
    w, h = tuple(table.get(rdiv(), table.get(6, _def_fix)))
    # width/height modifier for perfect placement of thumbnails in the grid (very font dependent)
    w += int(conf.setting("wmod"))
    h += int(conf.setting("hmod"))
    tm = text_mode()
    if tm:
        return w, h - tm
    elif thumbnail:
        return w, h
    else:
        NLC = 3  # num of content lines in the box
        return w, h + NLC


def thumbnail_resolution() -> tuple[int, int]:
    """Return tuple: (width, height) - based on divisor key in table.
    really simple:  divisor = 10
    (1920, 1080) / 10 = (192, 108)
    The only values that don't match the actual result: divisor=2.
    """
    table = {
        10: (192, 108),
        9: (213, 120),
        8: (240, 135),
        7: (274, 154),
        6: (320, 180),
        5: (384, 216),
        4: (480, 270),
        3: (640, 360),
        2: (720, 405),  # actual (960, 540) is overkill!
    }
    # use fallback key if div key not found
    _def_fix: tuple = (320, 180)  # fix: None is not assignable
    return table.get(rdiv(), table.get(6, _def_fix))


def get_thumbnail_urls(rawurls) -> list:
    """Return thumbnail urls with {width} and {height} replaced."""
    width, height = thumbnail_resolution()
    urls = []
    for url in rawurls:
        # fix: video thumbnails currently have weird format with % characters
        if url and "%{" in url:
            # remove % character from thumbnail url
            url = url.replace("%{", "{")
        if not url:
            url = ""
        else:
            url = url.format(width=width, height=height)
        urls.append(url)
    return urls


async def fetch_image(session, url):
    """Asynchronously fetch image from url."""
    if not url:
        return None
    async with session.get(url) as response:
        return await response.read()


async def get_thumbnails_async(ids: list, rawurls: list, *subdirs) -> dict:
    """Asynchronously download thumbnails and return paths.
    (Actual realization)
    """
    thumbnail_paths = {}
    urls = get_thumbnail_urls(rawurls)
    tmpd = fs.get_tmp_dir("thumbnails", *subdirs)
    blank_thumbnail = Path(conf.glob_conf_dir, "blank.jpg")
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(fetch_image(session, url))
        # wait until all thumbnails with non empty url are fetched
        thumbnails = await asyncio.gather(*tasks)

    for tid, thumbnail in zip(ids, thumbnails):
        thumbnail_fname = f"{tid}.jpg"
        thumbnail_path = Path(tmpd, thumbnail_fname)
        if thumbnail is None:
            if thumbnail_path.is_file() and thumbnail_path.samefile(blank_thumbnail):
                pass
            else:
                # remove symlink or file before creating new symlink
                if thumbnail_path.is_file():
                    thumbnail_path.unlink(missing_ok=True)
                # create symlink of blank_thumbnail
                thumbnail_path.symlink_to(blank_thumbnail)
        else:
            # NOTE: if existing thumbnail_path is symlink, original blank thumbnail
            # will be replaced by the thumbnail_path image, to prevent that
            # => remove symlink before writing new image file
            if thumbnail_path.is_symlink():
                thumbnail_path.unlink(missing_ok=True)
            with open(thumbnail_path, 'wb') as f:
                f.write(thumbnail)
        thumbnail_paths[tid] = str(thumbnail_path)
    return thumbnail_paths


def download_thumbnails(ids: list, rawurls: list, *subdirs) -> dict:
    """Asynchronously download thumbnails and return paths.
    (Wrapper with asyncio run/run_until_complete)
    """
    if version_info >= (3, 7):  # Python 3.7+
        return asyncio.run(get_thumbnails_async(ids, rawurls, *subdirs))
    else:  # Python 3.5-3.6
        loop = asyncio.get_event_loop()
        try:
            return loop.run_until_complete(get_thumbnails_async(ids, rawurls, *subdirs))
        finally:
            loop.close()


def find_thumbnails(ids: list, *subdirs) -> dict:
    """Find and return previously downloaded thumbnails paths."""
    tmpd = fs.get_tmp_dir("thumbnails", *subdirs)
    blank_thumbnail = Path(conf.glob_conf_dir, "blank.jpg")

    tnames = utils.replace_pattern_in_all(os.listdir(tmpd), ".jpg", "")
    differ = list(set(tnames).difference(set(ids)))
    fnames = utils.add_str_to_list(differ, ".jpg")  # add file extension back
    for fname in fnames:
        # remove thumbnail files/symlinks which id not in ids list
        Path(tmpd, fname).unlink(missing_ok=True)

    thumbnail_list = utils.insert_to_all(os.listdir(tmpd), tmpd, opt_sep=os.sep)
    thumbnail_paths = {}
    for path in thumbnail_list:
        tid = os.path.basename(os.path.splitext(path)[0])  # file basename without .ext
        thumbnail_paths[tid] = path
    # fix: if thumbnail_paths does not have id from ids
    # this usually happens if text mode without thumbnails was previously set
    for tid in ids:
        if tid not in thumbnail_paths.keys():
            thumbnail_paths[tid] = str(blank_thumbnail)
    return thumbnail_paths


class Thumbnail:
    """Prepare Thumbnail ueberzug parameters and add to Thumbnails."""
    w, h = container_size(thumbnail=True)

    def __init__(self, identifier, img_path, x, y):
        self.identifier = identifier
        self.img_path = img_path
        self.x = x
        self.y = y
        self.ue_params = self._ue_params()

    def _ue_params(self) -> dict[str, str]:
        """Return dict for thumbnail with all parameters required by ueberzug.
        Append parameters of the Thumbnail to the list of Thumbnails parameters.
        """
        uep = {
            "action": "add",
            "scaler": "fit_contain",
            "identifier": self.identifier,
            "path": self.img_path,
            "height": self.h,
            "width": self.w,
            "y": self.y,
            "x": self.x,
        }
        if not text_mode():
            Thumbnails.uepl.append(uep)
        return uep


class Thumbnails:
    uepl: list[dict[str, str]] = []  # ueberzug list of thumbnail parameters
    tm = text_mode()

    is_initialized = False
    working_dir = fs.get_tmp_dir()

    @staticmethod
    def json_schema_thumbnails(uepl: list) -> str:
        """New Line Delimited JSON, one ueberzug thumbnail parameters data per line."""
        nl_json = ""
        for th_params in uepl:
            nl_json += json.dumps(th_params) + '\n'
        return nl_json

    @staticmethod
    def PopenType() -> subprocess.Popen:
        """Get proper type and object properties at initialization.
        By executing common/smallest/fastest program existing in nearly every OS.
        """
        return subprocess.Popen(["echo"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)

    def __init__(self):
        self.sub_proc = self.PopenType()

    def init_check(self) -> bool:
        return self.is_initialized and self.sub_proc.poll() is None

    def init(self):
        """start ueberzug subprocess."""
        assert (self.sub_proc.stdin is not None)  # "None" [reportOptionalMemberAccess]
        if (self.init_check()):
            return
        cmd: list = get_ueberzug_cmd()
        # we do not want to close subprocess because that stops the drawing.
        with open(os.devnull, "wb", 0) as devnull:
            self.sub_proc = subprocess.Popen(
                cmd,
                cwd=self.working_dir,
                stderr=devnull,
                stdout=stdout.buffer,
                stdin=subprocess.PIPE,
                universal_newlines=True,
            )
        self.is_initialized = True

    def execute(self, **kwargs):
        """execute ueberzug action/cmd."""
        self.init()
        assert (self.sub_proc.stdin is not None)  # "None" [reportOptionalMemberAccess]
        # NOTE: direct interaction with the stdin as we do not want to close subprocess.
        if kwargs:
            # NOTE: mainly for the cleanup (remove action)
            self.sub_proc.stdin.write(json.dumps(kwargs) + '\n')
        else:
            self.sub_proc.stdin.write(self.json_schema_thumbnails(self.uepl))
        self.sub_proc.stdin.flush()

    def clear(self):
        """cleanup from the old thumbnails data."""
        assert (self.sub_proc.stdin is not None)  # "None" [reportOptionalMemberAccess]
        if self.sub_proc and not self.sub_proc.stdin.closed:
            for th_params in self.uepl:
                # remove previously added but no longer needed thumbnails
                self.execute(action="remove", identifier=th_params["identifier"])
        # clear list of the thumbnails parameters
        self.uepl.clear()

    def quit(self):
        """wrapper for the fast & safe termination of subprocess."""
        if self.init_check():
            timer_kill = Timer(1, self.sub_proc.kill, [])
            try:
                self.sub_proc.terminate()
                timer_kill.start()
                self.sub_proc.communicate()
            finally:
                timer_kill.cancel()

    def start(self):
        """Start drawing images via subprocess."""
        if self.tm:
            return
        self.execute()

    def finish(self, safe=False):
        """Finish drawing images and optionally terminate subprocess."""
        if self.tm:
            return
        self.clear()
        if safe:
            self.quit()


THUMBNAILS: Thumbnails = Thumbnails()


def draw_start():
    if not HAS_UEBERZUG:
        return
    THUMBNAILS.start()


def draw_stop(safe=False):
    if not HAS_UEBERZUG:
        return
    THUMBNAILS.finish(safe)
