from importlib import reload

import examples.src as src
import simple_disk_queue as sdq


def init_queue():
    queue = sdq.DiskQueue('test_ref', overwrite=True)
    queue.add_task(src.printer_fn)
    for i in range(10):
        queue.add_task(src.printer_fn, i)

    return queue


if __name__ == '__main__':
    queue = init_queue()
    sdq.run_queue('test_ref')