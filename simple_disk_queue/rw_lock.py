import time

from filelock import FileLock as RawFileLock
from filelock import Timeout

assert Timeout is not None


# TODO: This is still not a read-write lock but just a lock
class FileLock(object):
    """A wrapper for filelock.FileLock"""

    def __init__(self, protected_file_path, timeout=5, verbose=False):
        """Prepare the file locker. Specify the file to lock and optionally
        the maximum timeout and the delay between each attempt to lock.
        """
        self.lock_path = protected_file_path + ".lock"
        self.lock = RawFileLock(self.lock_path, timeout=timeout)
        self.verbose = verbose

    def __enter__(self):
        if self.verbose:
            self._start_time = time.time()
        return self.lock.__enter__()

    def __exit__(self, *args, **kwargs):
        if self.verbose:
            print(f"Critical time: {time.time() - self._start_time:.2f}s")
        return self.lock.__exit__(*args, **kwargs)

    def __del__(self):
        return self.lock.__del__()
