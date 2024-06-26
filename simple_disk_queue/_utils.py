"""Util functions"""

import os
import pickle

from .rw_lock import FileLock

PICKLE_PROTOCOL = 4


def dump(obj, file, **kwargs):
    """like pickle.dump but fix a default protocol for compatibility."""
    kwargs.setdefault("protocol", PICKLE_PROTOCOL)
    return pickle.dump(obj, file, **kwargs)


def to_pickle(obj, filepath, **kwargs):
    """Like to_pickle in pandas, but avoids pandas dependency."""
    with open(filepath, "wb") as fout:
        dump(obj, fout, **kwargs)


def read_pickle(filepath, **kwargs):
    """Like read_pickle in pandas, but avoids pandas dependency."""
    with open(filepath, "rb") as fin:
        return pickle.load(fin, **kwargs)


def locked_to_pickle(obj, filepath, **kwargs):
    """Like to_pickle in pandas, but avoids pandas dependency and adds a lock."""
    with FileLock(filepath):
        to_pickle(obj, filepath, **kwargs)


def locked_read_pickle(filepath, **kwargs):
    """Like read_pickle in pandas, but avoids pandas dependency and adds a lock."""
    with FileLock(filepath):
        return read_pickle(filepath, **kwargs)


def make_dir_if_necessary(dirname, max_depth=3):
    """Check if a directory exists. If not make it with lock.
    Will create nested directories (up to depth=max_depth).

    Args:
        dirname (_type_):
            Target directory.
        max_depth (int, optional):
            Maximum depth for nested creation.
            Defaults to 3.
    """
    if os.path.isdir(dirname):
        return
    assert (
        max_depth >= 0
    ), f"Cannot make too many nested directories. Something could be wrong!, dirname={dirname}"
    if not os.path.isdir(os.path.dirname(dirname)):
        make_dir_if_necessary(os.path.dirname(dirname), max_depth - 1)
    fl = FileLock(dirname)
    with fl:
        print(f"{dirname} does not exist. Creating it for persist_to_disk")
        os.makedirs(dirname)
    return
