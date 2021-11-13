#!/usr/bin/env python3
# coding=utf-8

from os import listdir, sep
from os.path import basename, splitext
from pathlib import Path
from requests import get
import curses
import data
import keys
import render
import thumbnails
import utils

CACHE_FILE_NAME = "followed_live_streams.json"
# TODO: get HEADER_H value from some Page class or smth like that. (to be able to re-use in all tabs/pages)
HEADER_H = 5


def get_followed_live_streams():
    """requests data from twitch API and return json."""
    u_id = data.get_private_data("u_id")    # user_id
    token = data.get_private_data("token")  # auth token
    c_id = data.get_private_data("c_id")    # client-Id of this program
    url = f"https://api.twitch.tv/helix/streams/followed?user_id={u_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": c_id
    }
    r = get(url, headers=headers)
    return r.json()


def cache_path_live_streams():
    return data.cache_file_path(CACHE_FILE_NAME)


def update_live_streams():
    return data.update_cache(CACHE_FILE_NAME, get_followed_live_streams())


def read_live_streams():
    return data.read_cache(CACHE_FILE_NAME)


def time_to_update_live_streams():
    """Return True if path mtime > 5 mins from now.
    (default twitch API update time).
    """
    fnf = not Path(cache_path_live_streams()).is_file()
    if fnf or utils.secs_since_mtime(cache_path_live_streams()) > 300:
        return True
    else:
        return False


def update_data() -> dict:
    """Update json data & return thumbnail paths."""
    if time_to_update_live_streams():
        update_live_streams()
        json_data = read_live_streams()
        ids = data.get_entries(json_data, 'id')
        thumbnail_urls_raw = data.get_entries(json_data, 'thumbnail_url')
        thumbnail_paths = thumbnails.get_thumbnails(ids, thumbnail_urls_raw)
    else:
        # do not download thumbnails, use previously downloaded thumbnails
        json_data = read_live_streams()
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


def prepare_objects():
    """Prepare objects for thumbnails and boxes."""
    thumbnail_paths = update_data()
    json_data = read_live_streams()
    fls = data.create_streams_dict(json_data)  # dict with user name as key
    ids = list(fls.keys())
    boxes = render.Boxes()
    grid = render.Grid()
    grid.key_list = ids
    gcords = grid.coordinates()
    for id, (x, y) in gcords.items():
        user = fls[id]["user_name"]
        if not user:  # if user_name is empty (rare, but those exist!)
            user = fls[id]["user_login"]
        box = render.Box(user, fls[id]["title"], fls[id]["game_name"], x, y)
        box.img_path = thumbnail_paths[id]
        box.viewers = str(fls[id]["viewer_count"])
        thmb = thumbnails.Thumbnail(id, thumbnail_paths[id], x, y + HEADER_H).ue_params
        boxes.add(box)
        boxes.add_thmb(thmb)


def draw_header(parent):
    """Draw page header."""
    _, w = parent.getmaxyx()
    head = parent.derwin(HEADER_H - 1, w, 0, 0)
    head.addstr(0, 0, "\n  Twitch\n  Curses", curses.A_BOLD)
    head.addstr(1, 10, "Following Live", curses.A_REVERSE)  # Tab name
    head.box()
    head.refresh()
    return head


def draw_body(parent):
    """Draw page body."""
    h, w = parent.getmaxyx()
    body = parent.derwin(h - HEADER_H, w, HEADER_H, 0)
    for box in render.Boxes().boxlist:
        box.draw(body)
    body.refresh()
    return body


def following_live_page(stdscr):
    """Main page method."""
    prepare_objects()
    draw_header(stdscr)
    draw_body(stdscr)
    thumbnails.Draw().back_loop()
    keys.loop(stdscr)
    thumbnails.Draw.FINISH = True  # finish back_loop()


render.run(following_live_page)