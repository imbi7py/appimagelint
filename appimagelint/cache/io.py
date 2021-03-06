import json
import os
import time
from typing import Union, Iterable, Mapping

from . import OutOfDateError
from .codebase_hasher import CodebaseHasher


# use a function to simulate "const values"
def cache_timeout():
    # update caches every week
    return 7 * 24 * 60 * 60


def store_json(path: str, data: Union[Mapping, Iterable]):
    json_root = {
        "codebase_digest": CodebaseHasher().digest_md5(),
        "data": data,
    }

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        json.dump(json_root, f, indent=2)


def load_json(path):
    with open(path, "r") as f:
        json_root = json.load(f)

    cached_codebase_digest = json_root["codebase_digest"]
    data = json_root["data"]

    mtime = os.path.getmtime(path)
    if mtime + cache_timeout() < time.time():
        # should be safe to ignore, forwarding data
        raise OutOfDateError("cache file outdated, update required", cached_data=data)

    codebase_digest = CodebaseHasher().digest_md5()
    try:
        if cached_codebase_digest != codebase_digest:
            # should be safe to ignore, forwarding data
            raise OutOfDateError("codebase changed since last update, forcing update", cached_data=data)

        return data

    # capture all "invalid data format" kind of errors and force update
    except KeyError as e:
        raise OutOfDateError("file in invalid format, forcing update") from e
