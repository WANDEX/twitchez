#!/usr/bin/env python3
# coding=utf-8

from json.decoder import JSONDecoder
from requests import get
import data
import keys
import render
import pages

category_query_string = "software development"  # FIXME: temporary hardcoded
# TODO: write those variables to file to not get this data every loop iteration only read it from file
category_id, category_name = data.get_category(category_query_string)
# TODO: after that, i can move this inside loop() function


def get_json_data(category_id) -> JSONDecoder:
    """requests data from twitch API and return json."""
    first = 100  # Maximum number of objects to return. (Twitch API Maximum: 100)
    token = data.get_private_data("token")
    c_id = data.get_private_data("c_id")
    url = f"https://api.twitch.tv/helix/streams?first={first}&game_id={category_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": c_id
    }
    r = get(url, headers=headers)
    return r.json()


def loop(stdscr):
    p = pages.Pages(category_name, get_json_data(category_id))
    page_class = render.Page(stdscr, p)
    keys.loop(page_class)


render.run(loop)
