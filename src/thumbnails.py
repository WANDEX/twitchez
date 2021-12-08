#!/usr/bin/env python3
# coding=utf-8

from multiprocessing.pool import ThreadPool
from os import listdir, sep
from os.path import basename, splitext
from pathlib import Path
from sys import version_info
from time import sleep
import aiohttp
import asyncio
import conf
import render
import ueberzug.lib.v0 as ueberzug
import utils


def thumbnail_resolution(div=6) -> tuple[int, int]:
    """Return tuple: (width, height) - based on div key in table."""
    table = {
        12: (160, 90),
        11: (174, 98),
        10: (192, 108),
        9: (213, 120),
        8: (240, 135),
        7: (274, 154),
        6: (320, 180),
        5: (384, 216),
        4: (480, 270),
        3: (640, 360),
        2: (960, 540),
        1: (1920, 1080),
    }
    # use fallback key if div key not found
    return table.get(div, table.get(6))


def get_thumbnail_urls(rawurls) -> list:
    """Return thumbnail urls with {width} and {height} replaced."""
    # TODO: DOUBTS: calculate closest resolution based on Screen/Window Resolution/DPI, Terminal font size, etc.
    # TODO: closest resolution to approx box size.
    width, height = thumbnail_resolution(int(conf.setting("thumbnail_size")))
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
    tmpd = utils.get_tmp_dir("thumbnails", *subdirs)
    blank_thumbnail = utils.project_root("config", "blank.jpg")
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(fetch_image(session, url))
        # wait until all thumbnails with non empty url are fetched
        thumbnails = await asyncio.gather(*tasks)

    for id, thumbnail in zip(ids, thumbnails):
        thumbnail_fname = f"{id}.jpg"
        thumbnail_path = Path(tmpd, thumbnail_fname)
        if thumbnail is None:
            if not thumbnail_path.is_file():
                # create symlink of blank_thumbnail
                thumbnail_path.symlink_to(blank_thumbnail)
        else:
            with open(thumbnail_path, 'wb') as f:
                f.write(thumbnail)
        thumbnail_paths[id] = str(thumbnail_path)
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
    thumbnail_dir = utils.get_tmp_dir("thumbnails", *subdirs)

    tnames = utils.replace_pattern_in_all(listdir(thumbnail_dir), ".jpg", "")
    differ = list(set(tnames).difference(set(ids)))
    fnames = utils.add_str_to_list(differ, ".jpg")  # add file extension back
    for fname in fnames:
        # remove thumbnail files/symlinks which id not in ids list
        Path(thumbnail_dir, fname).unlink(missing_ok=True)

    thumbnail_list = utils.insert_to_all(listdir(thumbnail_dir), thumbnail_dir, opt_sep=sep)
    thumbnail_paths = {}
    for path in thumbnail_list:
        id = basename(splitext(path)[0])  # file basename without .ext
        thumbnail_paths[id] = path
    return thumbnail_paths


class Thumbnail:
    """Prepare Thumbnail object."""
    h = int(conf.setting("container_box_height")) - 4
    w = int(conf.setting("container_box_width"))

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
    # FIXME: TODO: if not X11 - Wayland -> Do not even try to draw thumbnails
    # -> only X11 supported by ueberzug

    def __init__(self):
        self.ue_params_list = render.Boxes.thmblist

    def __check_wait(self, loops_num):
        """Check FINISH condition every sleep interval N loops."""
        for _ in range(loops_num):
            sleep(0.25)
            if self.FINISH:
                return

    def __draw(self):
        with ueberzug.Canvas() as c:
            with c.lazy_drawing:
                for thumbnail in self.ue_params_list:
                    ueberzug.Placement(c, **thumbnail)
            self.__check_wait(240)

    def __loop(self):
        while not self.FINISH:
            self.__draw()

    def back_loop(self):
        """Draw images in background."""
        ue = ThreadPool(processes=1)
        ue.apply_async(self.__loop)
        return ue

    def start(self):
        """Start drawing images in background,
        add new object to the images list.
        """
        img = Draw()
        self.images.append(img)
        return img.back_loop()

    def finish(self):
        """Finish all what was start()."""
        for img in self.images:
            img.FINISH = True  # finish back_loop()
            self.images.remove(img)
        self.ue_params_list.clear()
