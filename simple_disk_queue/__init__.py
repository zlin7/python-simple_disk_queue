"""Main functions for persist_to_disk."""

from .config import Config
from .disk_queue import DiskQueue

# Global config so user could set the root directory for persist ops


run_queue = DiskQueue.run

__all__ = ["DiskQueue", "run_queue"]

__version__ = "0.0.3"
__author__ = "Zhen Lin"
__credits__ = ""
