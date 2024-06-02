# source script defining an expensive function
import functools
import time


def worker_fn(t):
    print(f"Sleeping {t} seconds")
    time.sleep(t)
    if t == 1:
        raise ValueError("Error!")
    print(f"Done {t}")
    return t

@functools.lru_cache(1)
def printer_fn(t=123):
    print(f"Done {t}")
    return t

