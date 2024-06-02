
# Installation

`pip install .` or `pip install simple-disk-queue`

**By default, a folder called `.cache/simple_disk_queue` is created under your home directory, and will be used to store queues.**
If you want to change it, see "Global Settings" below.

# Quick Start

An example can be found in `examples/test.py`.
We can first call `init_queue()` to initialize the jobs, and then run `sdq.DiskQueue.run('test')` in different processes.