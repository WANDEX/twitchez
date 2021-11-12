#!/usr/bin/env python3
# coding=utf-8

from pathlib import Path
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


def cache_file_path(file_name):
    """Get cache file path by file name."""
    return Path(utils.get_cache_dir(), file_name)


def update_cache(file_name, json_data):
    """Update cache and return file path."""
    file_path = cache_file_path(file_name)
    data = json.dumps(json_data, indent=2)
    with open(file_path, "w") as file:
        file.write(data)
    return file_path


def read_cache(file_name):
    """ read_cache and return data. """
    file_path = cache_file_path(file_name)
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def get_entries(json_data, key, root_key='data') -> list:
    """ parse json data and return list with all entries found by key. """
    found = []
    for entry in json_data[root_key]:
        found.append(entry[key])
    return found


def create_streams_dict(json_data) -> dict:
    """ create and return streams dict with id as a key. """
    streams = {}
    ids = get_entries(json_data, 'id')
    for stream, id in zip(json_data['data'], ids):
        streams[id] = stream
    return streams
