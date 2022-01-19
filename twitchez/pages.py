#!/usr/bin/env python3
# coding=utf-8

from . import conf
from . import data
from . import render
from . import thumbnails
from . import utils
from .utils import strws
from pathlib import Path


class Pages:
    HEADER_H = 2

    def __init__(self, page_dict: dict):
        self.page_dict = page_dict
        self.page_name = page_dict["page_name"]
        self.cache_file_name = f"{strws(self.page_name)}.json"
        # set page tmp vars for reusing in next/prev tab movement etc.
        conf.tmp_set("page_dict", self.page_dict, self.page_name)
        conf.tmp_set("current_page_name", self.page_name, "TABS")
        # each new Pages instance -> add to tabs page_name (if not already in tabs)
        render.Tabs().add_tab(self.page_name)

    def cache_subdirs(self):
        """Return list of subdirs (to unpack them later as args)."""
        subdirs = []
        pd = self.page_dict
        ptype = pd.get("type", "streams")
        subdirs.append(ptype)
        if ptype == "videos":
            if "user_name" in pd:
                subdirs.append(strws(pd["user_name"]))
        if "category" in pd:
            subdirs.append(strws(pd["category"]))
        return subdirs

    def cache_path(self) -> Path:
        return data.cache_file_path(self.cache_file_name, *self.cache_subdirs())

    def update_cache(self) -> Path:
        return data.update_cache(self.cache_file_name, data.page_data(self.page_dict), *self.cache_subdirs())

    def read_cache(self) -> dict:
        return data.read_cache(self.cache_file_name, *self.cache_subdirs())

    def time_to_update_cache(self) -> bool:
        """Return True if path mtime > 5 mins from now.
        (default twitch API update time).
        """
        fnf = not Path(self.cache_path()).is_file()
        if fnf or utils.secs_since_mtime(self.cache_path()) > 300:
            return True
        else:
            return False

    def update_data(self) -> dict:
        """Update json data & return thumbnail paths."""
        subdirs = self.cache_subdirs()
        if self.time_to_update_cache():
            self.update_cache()
            json_data = self.read_cache()
            ids = data.get_entries(json_data, 'id')
            thumbnail_urls_raw = data.get_entries(json_data, 'thumbnail_url')
            thumbnail_paths = thumbnails.download_thumbnails(ids, thumbnail_urls_raw, *subdirs)
        else:
            # do not download thumbnails, find previously downloaded thumbnails paths
            json_data = self.read_cache()
            ids = data.get_entries(json_data, 'id')
            thumbnail_paths = thumbnails.find_thumbnails(ids, *subdirs)
        return thumbnail_paths

    def grid_func(self):
        """Return grid class object for prepared objects of thumbnails and boxes."""
        if thumbnails.text_mode():
            if self.time_to_update_cache():
                self.update_cache()
            thumbnail_paths = {}
        else:
            thumbnail_paths = self.update_data()
        json_data = self.read_cache()
        did = data.create_id_dict(json_data)  # dict with id as the key
        ids = list(did.keys())
        boxes = render.Boxes()
        grid = render.Grid(ids, self.page_name)
        for id, (x, y) in grid.coords.items():
            d = did[id]
            title = utils.tryencoding(d["title"])
            if "creator_name" in d:  # => clips
                # this is actually not login but name -> we do not need that anyway for clips
                user_login = d["broadcaster_name"]
                user_name = d["creator_name"]
            else:
                # used for composing stream url
                user_login = d["user_login"]
                user_name = d["user_name"]
            if not user_name:  # if user_name is empty (rare, but such case exist!)
                user_name = user_login
            # NOTE: videos DOES NOT HAVE game_name/category!
            if "game_name" in d:  # => live streams
                category = d["game_name"]
            elif "created_at" in d:  # => videos page
                category = utils.sdate(d["created_at"])
            elif "published_at" in d:
                category = utils.sdate(d["published_at"])
            else:
                category = ""
            if "viewer_count" in d:  # => live streams
                views = d["viewer_count"]
            elif "view_count" in d:  # => videos page
                views = d["view_count"]
            else:
                views = ""
            box = render.Box(user_login, user_name, title, category, x, y)
            if "url" in d:
                box.url = d["url"]  # videos have specific url
            if "duration" in d:
                box.duration = utils.duration(str(d["duration"]))
            box.viewers = str(views)
            if thumbnail_paths:
                box.img_path = thumbnail_paths[id]
                thmb = thumbnails.Thumbnail(id, thumbnail_paths[id], x, y + self.HEADER_H).ue_params
                boxes.add_thmb(thmb)
            boxes.add(box)
        return grid
