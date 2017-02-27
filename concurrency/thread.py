
"""
    For CPython, only the thread that has acquired the GIL may operate on Python 
objects or call Python/C API functions. In order to emulate concurrency of
execution, the interpreter regularly tries to switch threads. The lock is also
released around potentially blocking I/O operations.
    Calling system I/O functions is the most common use case for releasing the
GIL, but it can also be useful before calling long-running computations which
don't need access to Python objects, such as compression or cryptographic
functions operating over memory buffers.
    When threads are created using the dedicated Python APIs, the Python 
interpreter keeps some thread-specific bookkeeping information inside a data
structure called PyThreadState. There's also one global variable pointing to the
current PyThreadState. 
    However, when threads are created from C, they don't hold the GIL, nor is
there a thread state structure for them. If you need to call Python code from
these threads, you must first register these threads with the interpreter by
creating a thread state data structure, then acquiring the GIL, and finally
storing their thread state pointer, before you can start using the Python/C API.


synchronization
    Primitive lock is currently the lowest level synchronization primitive
available.
    Reentrant lock is a synchronization primitive that may be acquired multiple
times by the same thread. If acquire() is called N times, release() should be
called N times to release the lock.
    Condition, support timeout.
    Semaphores

memory visibility
    It seems that no Python implementation performs any advanced optimization
such as statement reordering or temporarily treating shared variables as
thread-local ones.

dead lock
    Require locks by the same order.
    Require all locks, or release all locks.

communication
    Event

"""

import time
import random
import threading
from datetime import datetime
from Queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor


###############################################################################
#                            threading module
###############################################################################
pool = Queue()
for i in range(10):
    pool.put(i)


class MyThread(threading.Thread):
    
    def __init__(self, id, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.id = id
    
    def run(self):
        while True:
            try:
                item = pool.get(True, 0.5)
                print '%s-th do work: %s' % (self.id, item)
                time.sleep(0.5)
            except Empty:
                break
            
threads = []
for i in range(1, 4):
    threads.append(MyThread(id=i))
    threads[-1].start()

for t in threads:
    t.join()
    
print 'finish'


###############################################################################
#                    asynchronously executing using futures
#     An Executor receives asynchronous work requests (in terms of a callable
# and its arguments) and returns a Future to represent the execution of that
# work request.
#     When using an executor as a context manager, __exit__ will call
# Executor.shutdown(wait=True).
#     Deadlock can occur when the callable associated with a Future waits on the
# results of another Future.
#
#     ThreadPoolExecutor use queue.Queue to store the WorkItem. Each submit will
# initial a new Future instance and WorkItem instance.
###############################################################################

# using submit ###############################################
def do_print(seconds):
    print('begin %s' % seconds)
    time.sleep(seconds)
    return seconds

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    begin = datetime.now()    
    for i in range(5):
        f = executor.submit(do_print, random.randint(1, 5))    # start all
        futures.append(f)
    submit = datetime.now()
        
print([f.result() for f in futures])                          # wait all
finish = datetime.now()
print(begin, submit, finish)


# using map ##################################################
#     The returned iterator raises a TimeoutError if __next__()
# is called and the result isn't available after timeout
# seconds from the original call to map().
#     If timeout is not specified or None then there is no
# limit to the wait time.
#     If a call raises an exception then that exception will be
# raised when its value is retrieved from the iterator.

with ThreadPoolExecutor(max_workers=5) as executor:
    begin = datetime.now()
    f_iter = executor.map(do_print, range(5))                 # start all
    submit = datetime.now()

print([result for result in f_iter])                          # wait all
finish = datetime.now()
print(begin, submit, finish)









