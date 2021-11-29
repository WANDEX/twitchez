#!/usr/bin/env python3
# coding=utf-8

from json.decoder import JSONDecoder
from os import listdir, sep
from os.path import basename, splitext
from pathlib import Path
import data
import render
import thumbnails
import utils


class Pages:
    HEADER_H = render.Tabs.HEADER_HEIGHT

    def __init__(self, page_name: str, json_data: JSONDecoder):
        self.page_name = page_name
        self.json_data = json_data
        self.page_name_no_ws = page_name.replace(" ", "_")  # page_name_without_whitespaces
        self.cache_file_name = f"{self.page_name_no_ws}.json"

    def cache_path(self):
        return data.cache_file_path(self.cache_file_name)

    def update_live_streams(self):
        return data.update_cache(self.cache_file_name, self.json_data)

    def read_live_streams(self):
        return data.read_cache(self.cache_file_name)

    def time_to_update_live_streams(self):
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
        if self.time_to_update_live_streams():
            self.update_live_streams()
            json_data = self.read_live_streams()
            ids = data.get_entries(json_data, 'id')
            thumbnail_urls_raw = data.get_entries(json_data, 'thumbnail_url')
            thumbnail_paths = thumbnails.get_thumbnails(ids, thumbnail_urls_raw)
        else:
            # do not download thumbnails, use previously downloaded thumbnails
            json_data = self.read_live_streams()
            ids = data.get_entries(json_data, 'id')
            thumbnail_dir = utils.get_tmp_dir("thumbnails_live")

            tnames = utils.replace_pattern_in_all(listdir(thumbnail_dir), ".jpg", "")
            differ = list(set(tnames).difference(set(ids)))
            fnames = utils.add_str_to_list(differ, ".jpg")  # add file extension back
            for fname in fnames:
                # remove thumbnail files of users who is not live streaming now.
                Path(thumbnail_dir, fname).unlink(missing_ok=True)

            thumbnail_list = utils.insert_to_all(listdir(thumbnail_dir), thumbnail_dir, opt_sep=sep)
            thumbnail_paths = {}
            for path in thumbnail_list:
                id = basename(splitext(path)[0])  # file basename without .ext
                thumbnail_paths[id] = path
        return thumbnail_paths

    def grid_func(self, parent):
        """return grid for prepared objects of thumbnails and boxes."""
        thumbnail_paths = self.update_data()
        json_data = self.read_live_streams()
        fls = data.create_streams_dict(json_data)  # dict with stream id as the key
        ids = list(fls.keys())
        boxes = render.Boxes()
        grid = render.Grid(parent, self.page_name)
        grid.key_list = ids
        gcords = grid.coordinates()
        for id, (x, y) in gcords.items():
            user_login = fls[id]["user_login"]  # for composing stream url
            user_name = fls[id]["user_name"]
            if not user_name:  # if user_name is empty (rare, but such case exist!)
                user_name = user_login
            box = render.Box(user_login, user_name, fls[id]["title"], fls[id]["game_name"], x, y)
            box.img_path = thumbnail_paths[id]
            box.viewers = str(fls[id]["viewer_count"])
            thmb = thumbnails.Thumbnail(id, thumbnail_paths[id], x, y + self.HEADER_H).ue_params
            boxes.add(box)
            boxes.add_thmb(thmb)
        return grid
