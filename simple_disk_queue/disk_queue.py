import hashlib
import importlib
import os
import random
from collections import deque
from typing import Any, Callable, List, Optional, Tuple, Union

from . import _utils
from .config import Config, get_default_config
from .rw_lock import FileLock, Timeout


def _hash(x: int):
    return int(hashlib.md5(str(x).encode()).hexdigest(), 16)


class DiskQueue:
    def __init__(
        self,
        id: str,
        config: Config = None,
        overwrite: bool = False,
        verbose: bool = False,
    ) -> None:
        """Initialize the DiskQueue object.

        :param id: The id of the queue. This is used to create the file name and to identify the queue.
        :type id: str
        :param config: Configurations , defaults to None.
            Right now it only specifies where all queues are stored, and there is no need to set it.
        :type config: Config, optional
        :param overwrite: Overwrite any existing queue with the same id or not, defaults to False
        :type overwrite: bool, optional
        :param verbose: Verbose mode or not, defaults to False
        :type verbose: bool, optional
        """
        if config is None:
            config = get_default_config()
        self.config = config

        self.queue_file = os.path.join(self.config.get_queue_location(), f"{id}.pkl")
        if overwrite:
            self.clear(id)
        self.id = id
        self.verbose = verbose

    def __len__(self):
        with FileLock(self.queue_file, verbose=self.verbose):
            if not os.path.isfile(self.queue_file):
                _utils.to_pickle(deque(), self.queue_file)
            curr_queue = _utils.read_pickle(self.queue_file)
            return len(curr_queue)

    def __getitem__(self, idx):
        with FileLock(self.queue_file, verbose=self.verbose):
            if not os.path.isfile(self.queue_file):
                _utils.to_pickle(deque(), self.queue_file)
            curr_queue = _utils.read_pickle(self.queue_file)
            return curr_queue[idx]

    def add_task(self, func, *args, **kwargs) -> None:
        """Add a task to the queue.

        :param func: The function to be added to the queue.
        :type func: Callable
        """
        with FileLock(self.queue_file, verbose=self.verbose):
            if not os.path.isfile(self.queue_file):
                _utils.to_pickle(deque(), self.queue_file)
            curr_queue = _utils.read_pickle(self.queue_file)
            func_str = f"{func.__module__}.{func.__name__}"
            args = tuple([_ for _ in args])
            curr_queue.append((func_str, args, kwargs))
            _utils.to_pickle(curr_queue, self.queue_file)

    def pop_task(self):
        """Pop the next task from the queue.

        :return: (func, args, kwargs)
        :rtype: Tuple[Callable, Tuple, dict]
        """
        job = None
        with FileLock(self.queue_file, timeout=20, verbose=self.verbose):
            curr_queue = _utils.read_pickle(self.queue_file)
            if len(curr_queue):
                job = curr_queue.popleft()
                _utils.to_pickle(curr_queue, self.queue_file)
        if job is None:
            return None
        func_str, args, kwargs = job
        _module = importlib.import_module(".".join(func_str.split(".")[:-1]))
        func = getattr(_module, func_str.split(".")[-1])
        return (func, args, kwargs)

    def peek_task(self):
        """Peek the next task from the queue.

        :return: (func_str, args, kwargs), where func_str is only a reference to the function.
        :rtype: Tuple[str, Tuple, dict]
        """
        with FileLock(self.queue_file, timeout=20, verbose=self.verbose):
            curr_queue = _utils.read_pickle(self.queue_file)
            return None if len(curr_queue) == 0 else curr_queue[0]

    def shuffle(self):
        with FileLock(self.queue_file, timeout=self.timeout):
            curr_queue = _utils.read_pickle(self.queue_file)
            curr_queue = list(curr_queue)
            random.shuffle(curr_queue)
            curr_queue = deque(curr_queue)
            _utils.to_pickle(curr_queue, self.queue_file)

    @classmethod
    def run(
        cls, id: str, max_attempts: int = 30, verbose=False, raise_error=False
    ) -> None:
        """Run a queue with the given id.

        :param id: id of the queue to run
        :type id: str
        :param max_attempts: Maximum number of attempts to try, defaults to 30
        :type max_attempts: int, optional
        :param verbose: Verbose mode or not, defaults to False
        :type verbose: bool, optional
        :param raise_error: Raise error or not, defaults to False
        :type raise_error: bool, optional
        :return: None
        :rtype: None
        """
        queue = cls(id, verbose=verbose, overwrite=False)
        failed_cnt = 0
        while failed_cnt < max_attempts:
            job = queue.pop_task()
            if job is None:
                break
            func, args, kwargs = job
            try:
                if verbose:
                    print(
                        f"Running job {func.__module__}.{func.__name__} {args} {kwargs}"
                    )
                func(*args, **kwargs)
            except KeyboardInterrupt as err:
                queue.add_task(func, *args, **kwargs)
                raise err
            except Exception as err:
                if raise_error:
                    raise err
                failed_cnt += 1
                if verbose:
                    print(
                        f"Job {func.__module__}.{func.__name__} {args} {kwargs} failed with error {err}"
                    )
                queue.add_task(func, *args, **kwargs)

    @classmethod
    def exists(cls, id: str):
        return os.path.isfile(cls.queue_file(id))

    @classmethod
    def queue_file(cls, id: str):
        config = get_default_config()
        return os.path.join(config.get_queue_location(), f"{id}.pkl")

    @classmethod
    def clear(cls, id: str):
        """Clear the queue with the given id.

        :param id: id of the queue to clear
        :type id: str
        """
        queue_file = cls.queue_file(id)
        if not cls.exists(id):
            return
        with FileLock(queue_file):
            os.remove(queue_file)
