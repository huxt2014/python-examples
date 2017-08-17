
"""
    On most systems with fork(), after a process forks only the thread that
issued the fork will exist. That also means any locks held by other threads will
never be released. Python solves this for os.fork() by acquiring the locks it
uses internally before the fork, and releasing them afterwards. In addition, it
resets any Lock Objects in the child.


Synchronization primitives
    Mutex Lock/RLock
    Condition
    Semaphore/BoundedSemaphore
    Event
    
    No read-write lock in standard library
    No record lock in standard library
"""

import os
import sys
import mmap
import fcntl
import signal
import subprocess
from threading import Timer
from multiprocessing import Pipe, Queue, Process, Value, Array, Pool


###############################################################################
#                           basic communication method
###############################################################################

# pipe ###########################################################
# the shared data resides within the kernel
# process persistence
# no name
r, w = os.pipe()

w_h = os.fdopen(w, 'w')
w_h.write('hello\n')
os.read(r, 6)

w_h.close()
os.close(r)

# fifo ###########################################################
# the shared data resides within the kernel, not disk
# process persistence
# pathname
os.mkfifo('/tmp/fifo')
r_h = os.fdopen(os.open('/tmp/fifo', os.O_NONBLOCK), 'r')
w_h = open('/tmp/fifo', 'w')

w_h.write('hello\n')
w_h.close()
print(r_h.read())
r_h.close()
os.unlink('/tmp/fifo')


# Pipe/message ###################################################
# Like message, can send and receive picklable objects.
# Implemented by pipe or socket.
p1, p2 = Pipe()

p1.send([1, 2, 'a'])
print(p2.recv())

p2.send_bytes('hello world', 6, 5)  # offset=6, size=5
print(p1.recv_bytes())              # get 'world'

p1.close()
p2.close()

# Queue ##########################################################
# The object is stored in collections.deque temporarily.
# A thread is running background, writing the object into
# Pipe. So, object should be picklable.
pool = Queue()
pool.put(['a', 1])
print(pool.get(True))


# mmap and shared memory #########################################
# call map with MAP-SHARED before calling fork
def f(n, a):
    n.value = 3.1415927
    for i in range(len(a)):
        a[i] = -a[i]

num = Value('d', 0.0)
arr = Array('i', range(10))
p = Process(target=f, args=(num, arr))
p.start()
p.join()

print(num.value)
print(arr[:])


# mmap and file ##################################################
with open("hello.txt", "w+") as f:
    f.write("Hello Python!\n")
    f.flush()
    mm = mmap.mmap(f.fileno(), 0)

print(mm.readline())
print(mm[:5])


def f():
    mm[6:13] = 'World!\n'

p = Process(target=f)
p.start()
p.join()

print(mm[:])


###############################################################################
#                             file  lock
#     The flock() system call places a single lock on the open file description.
# Locks are automatically released when the corresponding file descriptor is
# closed.
#     When a file descriptor is duplicated, the new file descriptor refers
# to the same file lock. However, if we use open() to obtain a second file
# descriptor (and associated open file description) referring to the same file,
# this second descriptor is treated independently by flock().
#     These types of locks are normally maintained within the kernel, and the
# owner of a lock is identified by its process ID.
#     With Posix record locking, the granularity is a single byte.
###############################################################################
# advisory locking################################################
# for fcntl.LOCK_EX, w and b is needed, for fcntl.LOCK_SH, r is
# needed.
f = open('/tmp/test', 'wb+')
fcntl.lockf(f, fcntl.LOCK_EX, 0, 0, os.SEEK_SET)   # lock entire file
fcntl.lockf(f, fcntl.LOCK_UN)                      # unlock


###############################################################################
#                           high level module
###############################################################################

# multiprocessing#################################################
# Using Pipe for IPC. Tasks are cached in Queue.Queue.
def f(x):
    return x*x

processes = Pool(2)
print(processes.map(f, range(5)))
print(processes.apply(f, (10,)))

r = processes.apply_async(f, (15,))
print(r.get())

processes.close()
processes.join()


# using futures ##################################################


###############################################################################
#                              other
###############################################################################


class SubprocessHandler:
    def __init__(self, prefix=True):
        """
        :param prefix: insert sys.prefix to PATH, useful for virtualenv,
        ``boolean`` 
        """
        self.stdout = None
        self.stderr = None
        self.rc = None

        if prefix:
            prefix_path = os.path.join(os.path.abspath(sys.prefix), 'bin')
            if prefix_path not in os.environ['PATH'].split(':'):
                os.environ['PATH'] = '%s:%s' % (prefix_path,
                                                os.environ['PATH'])

    def run(self, cmd, timeout=5):
        """
        :param cmd: command to run. Similar with cmd in subprocess.Popen, but
        list only, ``list``.
        :param timeout: timeout threshold, ``float``
        """
        timer = None
        try:
            p = subprocess.Popen(cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            timer = Timer(timeout, lambda process: process.kill(), args=(p,))
            timer.start()
            self.stdout, self.stderr = p.communicate()
            self.rc = p.returncode
        except Exception as e:
            e.args = (' '.join(cmd),) + e.args
            raise e
        finally:
            if timer:
                timer.cancel()

        if self.rc == -signal.SIGKILL:
            raise TimeoutError(' '.join(cmd))
        elif self.rc != 0:
            raise Exception(' '.join(cmd))
