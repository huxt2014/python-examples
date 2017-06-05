"""
    Concurrency can be implemented in a number of ways, with the most important
difference being whether shared data is accessed directly (e.g.,using shared
memory)or indirectly (e.g.,using inter-process communication—IPC).
    Threaded concurrency typically access shared data in a process using
serialized access to shared memory, with the serialization enforced by the
programmer using some kind of locking mechanism.
    Concurrent processes typically access shared data using IPC, although they
could also use shared memory if the language or its library supported it.
    Concurrency based on “concurrent waiting” take advantage of asynchronous
I/O.

    Low-Level Concurrency makes explicit use of atomic operations. This kind of
concurrency is for library writers rather than for application developers.
Python doesn’t support this kind of concurrency.
    Mid-Level Concurrency does not use any explicit atomic operations but does
use explicit locks. Python provides support for concurrent programming at this
level
    High-Level Concurrency does not explicitly use atomic operations locks, but
use tools and API offered by library.
    Generally, low- and medium-level approaches to concurrency are very error
prone. Avoiding the use of explicit locks, and by making use of Python’s
high-level queue and multiprocessing modules’ queues, or the concurrent.futures
module.
"""
