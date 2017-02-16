
'''
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
'''

###############################################################################
#                           basic communication method
###############################################################################


# pipe ######################################################
# the shared data resides within the kernel
# process persistence
# no name
r, w = os.pipe()

w_h = os.fdopen(w, 'w')
w_h.write('hello\n')
os.read(r, 6)

w_h.close()
os.close(r)

# fifo ######################################################
# the shared data resides within the kernel, not disk
# process persistence
# pathname
os.mkfifo('/tmp/fifo')
r_h = os.fdopen(os.open('/tmp/fifo', os.O_NONBLOCK), 'r')
w_h = open('/tmp/fifo', 'w')

w_h.write('hello\n')
w_h.close()
print r_h.read()
r_h.close()
os.unlink('/tmp/fifo')


# Pipe/message ##############################################
# Like message, can send and receive picklable objects.
# Implemented by pipe or socket.
from multiprocessing import Pipe

p1, p2 = Pipe()

p1.send([1,2,'a'])
print p2.recv()

p2.send_bytes('hello world', 6, 5)  # offset=6, size=5
print p1.recv_bytes()               # get 'world'

p1.close()
p2.close()

# Queue ####################################################
# The object is stored in collections.deque temporarily.
# A thread is running background, writing the object into
# Pipe. So, object should be picklable.
from multiprocessing import Queue

pool = Queue()
pool.put(['a', 1])
print pool.get(True)

# mmap and shared memory ###################################
# call map with MAP-SHARED before calling fork
from multiprocessing import Process, Value, Array

def f(n, a):
    n.value = 3.1415927
    for i in range(len(a)):
        a[i] = -a[i]

num = Value('d', 0.0)
arr = Array('i', range(10))
p = Process(target=f, args=(num, arr))
p.start()
p.join()

print num.value
print arr[:]


# mmap and file ############################################
import mmap
from multiprocessing import Process

with open("hello.txt", "w+") as f:
    f.write("Hello Python!\n")
    f.flush()
    mm = mmap.mmap(f.fileno(), 0)

print mm.readline()
print mm[:5]

def f():
    mm[6:13] = 'World!\n'

p = Process(target=f)
p.start()
p.join()

print mm[:]


###############################################################################
#                             fcntl  lock
#     These types of locks are normally maintained within the kernel, and the
# owner of a lock is identified by its process ID.
#     With Posix record locking, the granularity is a single byte.
###############################################################################

import fcntl

# advisory locking####################################
f = open('/tmp/test', 'w')
fcntl.lockf(f.fileno(), fcntl.LOCK_EX, 0, 0, os.SEEK_SET)   # lock entire file
fcntl.lockf(f.fileno(), fcntl.LOCK_UN)                      # unlock



###############################################################################
#                           high level module
###############################################################################

# multiprocessing############################################
# Using Pipe for IPC. Tasks are cached in Queue.Queue.

from multiprocessing import Pool

def f(x):
    return x*x
    
processes = Pool(2)
print processes.map(f, range(5))
print processes.apply(f, (10,))

r = processes.apply_async(f, (15,))
print r.get()

processes.close()
processes.join()
    

# using futures ##############################################









