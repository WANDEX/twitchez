#!/usr/bin/env python3
# coding=utf-8

from pathlib import Path
import data
import render
import thumbnails
import utils


class Pages:
    HEADER_H = render.Page.HEADER_H

    def __init__(self, page_name: str, json_data: dict):
        self.page_name = page_name
        self.json_data = json_data
        self.page_name_no_ws = page_name.replace(" ", "_")  # page_name_without_whitespaces
        self.cache_file_name = f"{self.page_name_no_ws}.json"

    def cache_path(self) -> Path:
        return data.cache_file_path(self.cache_file_name)

    def update_live_streams(self) -> Path:
        return data.update_cache(self.cache_file_name, self.json_data)

    def read_live_streams(self) -> dict:
        return data.read_cache(self.cache_file_name)

    def time_to_update_live_streams(self) -> bool:
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
            thumbnail_paths = thumbnails.download_thumbnails(ids, thumbnail_urls_raw, self.page_name_no_ws)
        else:
            # do not download thumbnails, find previously downloaded thumbnails paths
            json_data = self.read_live_streams()
            ids = data.get_entries(json_data, 'id')
            thumbnail_paths = thumbnails.find_thumbnails(ids, self.page_name_no_ws)
        return thumbnail_paths

    def grid_func(self, parent) -> render.Grid:
        """Return grid class object for prepared objects of thumbnails and boxes."""
        thumbnail_paths = self.update_data()
        json_data = self.read_live_streams()
        fls = data.create_streams_dict(json_data)  # dict with stream id as the key
        ids = list(fls.keys())
        boxes = render.Boxes()
        grid = render.Grid(parent, ids, self.page_name)
        for id, (x, y) in grid.coords.items():
            d = fls[id]
            title = d["title"]
            user_login = d["user_login"]  # for composing stream url
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
            if "url" in d:  # => videos page
                box.url = d["url"]  # videos have specific url
            box.viewers = str(views)
            box.img_path = thumbnail_paths[id]
            thmb = thumbnails.Thumbnail(id, thumbnail_paths[id], x, y + self.HEADER_H).ue_params
            boxes.add(box)
            boxes.add_thmb(thmb)
        return grid
