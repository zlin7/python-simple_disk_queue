import functools
import os
from pathlib import Path

SETTING_PATH = os.path.join(Path.home(), ".cache", "simple_disk_queue")

QUEUE_DIR = os.path.join(SETTING_PATH, "queue")
os.makedirs(QUEUE_DIR, exist_ok=True)


class Config(object):
    def __init__(self) -> None:
        pass

    def get_queue_location(self):
        return QUEUE_DIR


@functools.lru_cache(maxsize=1)
def get_default_config():
    return Config()
