#!/usr/bin/env python3
# coding=utf-8

from os import listdir
from os.path import basename, splitext
import data
import render
import thumbnails
import utils
import keys
import curses

# TODO: get HEADER_H value from some Page class or smth like that. (to be able to re-use in all tabs/pages)
HEADER_H = 5

# TODO: remove all hardcoded DEBUG & if DEBUG statements -> after update methods are finished & implemented
DEBUG = 1


def auto_update():
    """auto update json data."""
    # TODO: move this method into data.py
    # TODO: check last update time of json_data file if > ??? min -> auto_update_data()
    if DEBUG == 0:
        data.update_live_streams()


def update_thumbnails() -> dict:
    # TODO: check last update time of thumbnails dir if > 5 min -> auto_update_data() & update_thumbnails()
    if DEBUG == 1:
        # do not download thumbnails, use previously downloaded thumbnails
        thumbnail_dir = utils.get_tmp_dir("thumbnails_live")
        thumbnail_list = utils.insert_to_all(listdir(thumbnail_dir), thumbnail_dir, opt_sep="/")
        thumbnail_paths = {}
        for path in thumbnail_list:
            user = basename(splitext(path)[0])  # file basename without .ext
            thumbnail_paths[user] = path
    else:
        json_data = data.read_live_streams()
        user_list = data.get_entries(json_data, 'user_name')
        thumbnail_urls_raw = data.get_entries(json_data, 'thumbnail_url')
        thumbnail_paths = thumbnails.get_thumbnails(user_list, thumbnail_urls_raw)
    return thumbnail_paths


def prepare_objects():
    """Prepare objects for thumbnails and boxes."""
    json_data = data.read_live_streams()
    user_list = data.get_entries(json_data, 'user_name')
    fls = data.create_streams_dict(json_data)  # dict with user name as key
    boxes = render.Boxes()
    grid = render.Grid()
    grid.key_list = user_list
    gcords = grid.coordinates()
    thumbnail_paths = update_thumbnails()
    for user, (x, y) in gcords.items():
        box = render.Box(user, fls[user]["title"], fls[user]["game_name"], x, y)
        box.img_path = thumbnail_paths[user]
        thmb = thumbnails.Thumbnail(user, thumbnail_paths[user], x, y + HEADER_H).ue_params
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
    auto_update()
    prepare_objects()
    draw_header(stdscr)
    draw_body(stdscr)
    thumbnails.Draw().back_loop()
    keys.loop(stdscr)
    thumbnails.Draw.FINISH = True  # finish back_loop()


render.run(following_live_page)
