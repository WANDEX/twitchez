#!/usr/bin/env python3
# coding=utf-8

from . import conf
from . import fs
from . import render
from . import utils
from multiprocessing.pool import ThreadPool
from os import listdir, sep
from os.path import basename, splitext
from pathlib import Path
from sys import version_info
from time import sleep
import aiohttp
import asyncio
try:
    import ueberzug.lib.v0 as ueberzug
except ImportError:
    has_ueberzug = False
else:
    has_ueberzug = True


def text_mode() -> int:
    """Text mode: 0 => thumbnails mode (min: 0, max: 3).
    [1-3] => don't do anything with thumbnails don't even download them!
    The higher the value, the more rows of cells there will be in the grid.
    """
    # TODO: if not X11 (Wayland) -> return 1 (only X11 supported by ueberzug)
    tm = int(conf.setting("text_mode"))
    if tm < 0:
        tm = 0
    elif tm > 3:
        tm = 3
    # explicit text mode if ueberzug not found (optional dependency)
    if not has_ueberzug and tm < 1:
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
    w, h = tuple(table.get(rdiv(), table.get(6)))
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
    return table.get(rdiv(), table.get(6))


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


async def __get_thumbnails_async(ids: list, rawurls: list, *subdirs) -> dict:
    """Asynchronously download thumbnails and return paths.
    (Actual realization)
    """
    thumbnail_paths = {}
    urls = get_thumbnail_urls(rawurls)
    tmpd = fs.get_tmp_dir("thumbnails", *subdirs)
    blank_thumbnail = fs.project_root("config", "blank.jpg")
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
        return asyncio.run(__get_thumbnails_async(ids, rawurls, *subdirs))
    else:  # Python 3.5-3.6
        loop = asyncio.get_event_loop()
        try:
            return loop.run_until_complete(__get_thumbnails_async(ids, rawurls, *subdirs))
        finally:
            loop.close()


def find_thumbnails(ids: list, *subdirs) -> dict:
    """Find and return previously downloaded thumbnails paths."""
    tmpd = fs.get_tmp_dir("thumbnails", *subdirs)
    blank_thumbnail = fs.project_root("config", "blank.jpg")

    tnames = utils.replace_pattern_in_all(listdir(tmpd), ".jpg", "")
    differ = list(set(tnames).difference(set(ids)))
    fnames = utils.add_str_to_list(differ, ".jpg")  # add file extension back
    for fname in fnames:
        # remove thumbnail files/symlinks which id not in ids list
        Path(tmpd, fname).unlink(missing_ok=True)

    thumbnail_list = utils.insert_to_all(listdir(tmpd), tmpd, opt_sep=sep)
    thumbnail_paths = {}
    for path in thumbnail_list:
        tid = basename(splitext(path)[0])  # file basename without .ext
        thumbnail_paths[tid] = path
    # fix: if thumbnail_paths does not have id from ids
    # this usually happens if text mode without thumbnails was previously set
    for tid in ids:
        if tid not in thumbnail_paths.keys():
            thumbnail_paths[tid] = str(blank_thumbnail)
    return thumbnail_paths


class Thumbnail:
    """Prepare Thumbnail object."""
    w, h = container_size(thumbnail=True)

    def __init__(self, identifier, img_path, x, y):
        self.identifier = identifier
        self.img_path = img_path
        self.x = x
        self.y = y
        self.ue_params = self.__ue_params()

    def __ue_params(self) -> dict:
        """Return dict for thumbnail with all parameters required by ueberzug."""
        ueberzug_parameters = {
            "identifier": self.identifier,
            "height": self.h,
            "width": self.w,
            "y": self.y,
            "x": self.x,
            "scaler": ueberzug.ScalerOption.FIT_CONTAIN.value,
            "path": self.img_path,
            "visibility": ueberzug.Visibility.VISIBLE
        }
        return ueberzug_parameters


class Draw:
    """Draw all images from list of ue_params with ueberzug."""
    FINISH = False
    images = []
    tm = text_mode()

    def __init__(self):
        self.ue_params_list = render.Boxes.thmblist

    def __check_wait(self):
        """Check FINISH condition every sleep interval N loops.
        formula: loops_num * sleep_time = blink interval in sec
        (time after which thumbnails will blink once and will be redrawn)
        """
        loops_num = 1200
        sleep_time = .25
        for _ in range(loops_num):
            sleep(sleep_time)
            if self.FINISH:
                return

    def __draw(self):
        with ueberzug.Canvas() as c:
            with c.lazy_drawing:
                for thumbnail in self.ue_params_list:
                    ueberzug.Placement(c, **thumbnail)
            self.__check_wait()

    def __loop(self):
        while not self.FINISH:
            self.__draw()

    def __back_loop(self):
        """Draw images in background."""
        ue = ThreadPool(processes=1)
        ue.apply_async(self.__loop)
        return ue

    def start(self):
        """Start drawing images in background,
        add new object to the images list.
        """
        if self.tm:
            return
        img = Draw()
        self.images.append(img)
        return img.__back_loop()

    def finish(self):
        """Finish all what was start()."""
        if self.tm:
            return
        for img in self.images:
            img.FINISH = True  # finish __back_loop()
            self.images.remove(img)
        self.ue_params_list.clear()
