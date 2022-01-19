#!/usr/bin/env python3
# coding=utf-8

from . import fs
from pathlib import Path
from requests import get
import json


def write_private_data(user_id, access_token, client_id):
    """Write private data to file for using in further requests.
    Also set r+w file permissions to owner only.
    """
    file_path = fs.project_root(".private")
    data = {
        "u_id": user_id,
        "token": access_token,
        "c_id": client_id
    }
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    file_path.chmod(0o600)


def get_private_data(key) -> str:
    """Get value by the key from .private file."""
    file_path = fs.project_root(".private")
    with open(file_path, "r") as file:
        data = json.load(file)
    return data[key]


def cache_file_path(file_name, *subdirs) -> Path:
    """Get cache file path by file name, optionally supports subdirs."""
    if subdirs:
        path = Path(fs.get_cache_dir(), *subdirs)
        path.mkdir(parents=True, exist_ok=True)
    else:
        path = fs.get_cache_dir()
    return Path(path, file_name)


def update_cache(file_name, json_data, *subdirs) -> Path:
    """Update json file from cache and return file path."""
    if subdirs:
        file_path = cache_file_path(file_name, *subdirs)
    else:
        file_path = cache_file_path(file_name)
    data = json.dumps(json_data, indent=2)
    with open(file_path, "w") as file:
        file.write(data)
    return file_path


def read_cache(file_name, *subdirs) -> dict:
    """Read json file from cache and return data."""
    if subdirs:
        file_path = cache_file_path(file_name, *subdirs)
    else:
        file_path = cache_file_path(file_name)
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def get_entries(json_data, key, root_key='data') -> list:
    """Create and return list of values from json data where all entries found by key."""
    found = []
    for entry in json_data[root_key]:
        found.append(entry[key])
    return found


def create_id_dict(json_data) -> dict:
    """Create and return dict with id as the key."""
    streams = {}
    ids = get_entries(json_data, 'id')
    for stream, id in zip(json_data['data'], ids):
        streams[id] = stream
    return streams


def following_live_data() -> dict:
    """Return data of user 'following live channels' page."""
    u_id = get_private_data("u_id")    # user_id
    token = get_private_data("token")  # auth token
    c_id = get_private_data("c_id")    # client-Id of this program
    url = f"https://api.twitch.tv/helix/streams/followed?user_id={u_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": c_id
    }
    r = get(url, headers=headers)
    return r.json()


def get_categories(query: str) -> list:
    """Returns a list of categories that match the query via name either entirely or partially."""
    first = 100  # Maximum number of objects to return. (Twitch API Maximum: 100)
    token = get_private_data("token")
    c_id = get_private_data("c_id")
    url = f"https://api.twitch.tv/helix/search/categories?first={first}&query={query}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": c_id
    }
    r = get(url, headers=headers)
    j = r.json()
    return j["data"]


def get_categories_terse_data(query: str) -> dict:
    categories = get_categories(query)
    terse_info = {}
    for c in categories:
        # dict key is id = tuple of ...
        terse_info[c["id"]] = c["name"], c["box_art_url"]
    return terse_info


def get_categories_terse_mulstr(query: str) -> str:
    """Return multiline string with terse categories data. (for interactive select)"""
    d = get_categories_terse_data(query)
    mstr = ""
    names = []
    for v in d.values():
        name, _ = v
        names.append(name)
    maxlen = len(max(names, key=len))  # max length of longest string in list
    for id, v in d.items():
        name, _ = v
        mstr += f"{str(name):<{int(maxlen)}} [{id}]\n"
    return mstr.strip()  # to remove blank line


def category_data(category_id) -> dict:
    """Return json data for streams in certain category."""
    first = 100  # Maximum number of objects to return. (Twitch API Maximum: 100)
    token = get_private_data("token")
    c_id = get_private_data("c_id")
    url = f"https://api.twitch.tv/helix/streams?first={first}&game_id={category_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": c_id
    }
    r = get(url, headers=headers)
    return r.json()


def get_channels(query: str, live_only=False) -> dict:
    """Returns a list of channels that match the query via channel name.
    (users who have streamed within the past 6 months)
    """
    first = 5  # Maximum number of objects to return. (Twitch API Maximum: 100)
    token = get_private_data("token")
    c_id = get_private_data("c_id")
    url = f"https://api.twitch.tv/helix/search/channels?first={first}&live_only={str(live_only)}&query={query}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": c_id
    }
    r = get(url, headers=headers)
    j = r.json()
    return j["data"]


def get_channels_terse_data(query: str, live_only=False) -> dict:
    """Return id dict with channels: (broadcaster_login, display_name, profile_image_url) only."""
    channels = get_channels(query, live_only)
    terse_info = {}
    for ch in channels:
        # dict key is channel id = tuple of ...
        terse_info[ch["id"]] = ch["broadcaster_login"], ch["display_name"], ch["thumbnail_url"]
    return terse_info


def get_channels_terse_mulstr(query: str, live_only=False) -> str:
    """Return multiline string with terse channels data. (for interactive select)"""
    d = get_channels_terse_data(query, live_only)
    mstr = ""
    maxlen = 15
    for id, ch in d.items():
        login, name, _ = ch
        mstr += f"{str(login):<{maxlen}} {str(name):<{maxlen}} [{id}]\n"
    return mstr.strip()  # to remove blank line


def get_channel_videos(user_id, type="all") -> dict:
    """Gets videos information by user ID."""
    first = 100  # Maximum number of objects to return. (Twitch API Maximum: 100)
    token = get_private_data("token")
    c_id = get_private_data("c_id")
    url = f"https://api.twitch.tv/helix/videos?type={type}&first={first}&user_id={user_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": c_id
    }
    r = get(url, headers=headers)
    return r.json()


def get_channel_clips(broadcaster_id) -> dict:
    """Gets clips information by broadcaster ID."""
    first = 100  # Maximum number of objects to return. (Twitch API Maximum: 100)
    token = get_private_data("token")
    c_id = get_private_data("c_id")
    url = f"https://api.twitch.tv/helix/clips?first={first}&broadcaster_id={broadcaster_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": c_id
    }
    r = get(url, headers=headers)
    return r.json()


def page_data(page_dict) -> dict:
    """Get and return page data based on page_dict."""
    pd = page_dict
    ptype = pd.get("type", "streams")
    if ptype == "videos":
        if pd["category"] == "clips":
            json_data = get_channel_clips(pd["user_id"])
        else:
            json_data = get_channel_videos(pd["user_id"], pd["category"])
    else:
        if pd["category"] == "Following Live":
            json_data = following_live_data()
        else:
            json_data = category_data(pd["category_id"])
    return json_data
