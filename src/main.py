#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import environ
from pathlib import Path
import json
import requests

FLS_JSON = "followed_live_streams.json"


def get_project_root() -> Path:
    """ simply return project_root path. """
    return Path(__file__).parent.parent


def get_private_data(key):
    """ get value by the key from .private file. """
    file_path = Path(get_project_root(), ".private")
    with open(file_path, "r") as file:
        data = json.load(file)
    return data[key]


def get_followed_live_streams():
    """ requests data from twitch API and return json. """
    u_id = get_private_data("u_id")     # user_id
    token = get_private_data("token")   # auth token
    c_id = get_private_data("c_id")     # Client-Id of this program
    url = f"https://api.twitch.tv/helix/streams/followed?user_id={u_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": c_id
    }
    r = requests.get(url, headers=headers)
    return r.json()


def get_cache_dir():
    """ check ENV variables, create cache dir and return it's path. """
    dirname = "twitch-following-live"
    if "TWITCH_FL_CACHE_DIR" in environ:
        cache_home = environ["TWITCH_FL_CACHE_DIR"]
    elif "XDG_CACHE_HOME" in environ:
        cache_home = environ["XDG_CACHE_HOME"]
    else:
        cache_home = Path(Path.home(), ".cache")
    cache_dir = Path(cache_home, dirname)
    # create cache_dir if not exist
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    return cache_dir


def update_cache(file_name):
    """ update_cache and return file_path. """
    file_path = Path(get_cache_dir(), file_name)
    data = json.dumps(get_followed_live_streams(), indent=2)
    with open(file_path, "w") as file:
        file.write(data)
    return file_path


def read_cache(file_name):
    """ read_cache and return data. """
    file_path = Path(get_cache_dir(), file_name)
    with open(file_path, "r") as file:
        data = json.load(file)
    print(data)
    return data


def get_entries(json_data, key, root_key='data') -> list:
    """ parse json data and return list with all entries found by key. """
    found = []
    for entry in json_data[root_key]:
        found.append(entry[key])
    return found


update_cache(FLS_JSON)
read_cache(FLS_JSON)
