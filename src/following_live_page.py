#!/usr/bin/env python3
# coding=utf-8

from requests import get
import data
import keys
import render
import pages

PAGE_NAME = "Following Live"


def get_json_data() -> dict:
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


def loop(stdscr):
    p = pages.Pages(PAGE_NAME, get_json_data())
    page_class = render.Page(stdscr, p)
    keys.loop(page_class)


render.run(loop)
