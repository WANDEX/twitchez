#!/usr/bin/env python3
# coding=utf-8

from pathlib import Path
import requests
import json
import utils


def write_private_data(user_id, access_token, client_id):
    """ Write private data to file for using in further connections.
        Also set r+w file permissions to owner only.
    """
    file_path = utils.project_root(".private")
    data = {
        "u_id": user_id,
        "token": access_token,
        "c_id": client_id
    }
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    file_path.chmod(0o600)


def get_private_data(key):
    """ get value by the key from .private file. """
    file_path = utils.project_root(".private")
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


def update_cache(file_name):
    """ update_cache and return file_path. """
    file_path = Path(utils.get_cache_dir(), file_name)
    data = json.dumps(get_followed_live_streams(), indent=2)
    with open(file_path, "w") as file:
        file.write(data)
    return file_path


def read_cache(file_name):
    """ read_cache and return data. """
    file_path = Path(utils.get_cache_dir(), file_name)
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def update_live_streams():
    return update_cache("followed_live_streams.json")


def read_live_streams():
    return read_cache("followed_live_streams.json")


def get_entries(json_data, key, root_key='data') -> list:
    """ parse json data and return list with all entries found by key. """
    found = []
    for entry in json_data[root_key]:
        found.append(entry[key])
    return found
