

import sys
import queue
import threading

###############################################################################
#                        replace observer with signal/event
###############################################################################

import blinker


class Supervisor(object):
        
    sig_alarm = blinker.signal('alarm')
    
    def __init__(self, id):
        self.id = id
    
    def alarm(self):
        print('%s-th supervisor alarm.' % self.id)
        self.sig_alarm.send(self)


class Worker(object):
    
    def __init__(self, id):
        self.id = id
        Supervisor.sig_alarm.connect(self.on_alarm)
        
    def on_alarm(self, sup):
        print('%s-th worker get alarm from %s-th supervisor' % (self.id, sup.id))


s = Supervisor(1)
workers = [Worker(i) for i in range(1, 5)]
s.alarm()


###############################################################################
#                        chain of responsibility
#     Avoid coupling the sender of a request to its receiver by giving more than
# one object a chance to handle the request. Chain the receiving objects and
# pass the request along the chain until an object handles it.
#     The logging package in Python's standard library is a good example.
###############################################################################
class PlaceHolder(object):

    def __init__(self, alogger):
        self.loggerMap = {alogger: None}

    def append(self, alogger):
        if alogger not in self.loggerMap:
            self.loggerMap[alogger] = None


class Manager(object):
    def __init__(self, rootnode):
        """
        Initialize the manager with the root node of the logger hierarchy.
        """
        self.root = rootnode
        self.disable = 0
        self.emittedNoHandlerWarning = 0
        self.loggerDict = {}

    def getLogger(self, name):
        """
        Get a logger with the specified name (channel name), creating it
        if it doesn't yet exist. This name is a dot-separated hierarchical
        name, such as "a", "a.b", "a.b.c" or similar.

        If a PlaceHolder existed for the specified name [i.e. the logger
        didn't exist but a child of it did], replace it with the created
        logger and fix up the parent/child references which pointed to the
        placeholder to now point to the logger.
        """
        rv = None

        if name in self.loggerDict:
            rv = self.loggerDict[name]
            if isinstance(rv, PlaceHolder):
                ph = rv
                rv = Logger(name)
                rv.manager = self
                self.loggerDict[name] = rv
                self._fixupChildren(ph, rv)
                self._fixupParents(rv)
        else:
            rv = Logger(name)
            rv.manager = self
            self.loggerDict[name] = rv
            self._fixupParents(rv)

        return rv

    def _fixupParents(self, alogger):
        """
        Ensure that there are either loggers or placeholders all the way
        from the specified logger to the root of the logger hierarchy.
        """
        name = alogger.name
        i = name.rfind(".")
        rv = None
        while (i > 0) and not rv:
            substr = name[:i]
            if substr not in self.loggerDict:
                self.loggerDict[substr] = PlaceHolder(alogger)
            else:
                obj = self.loggerDict[substr]
                if isinstance(obj, Logger):
                    rv = obj
                else:
                    assert isinstance(obj, PlaceHolder)
                    obj.append(alogger)
            i = name.rfind(".", 0, i - 1)
        if not rv:
            rv = self.root
        alogger.parent = rv

    def _fixupChildren(self, ph, alogger):
        """
        Ensure that children of the placeholder ph are connected to the
        specified logger.
        """
        name = alogger.name
        namelen = len(name)
        for c in ph.loggerMap.keys():
            # The if means ... if not c.parent.name.startswith(nm)
            if c.parent.name[:namelen] != name:
                alogger.parent = c.parent
                c.parent = alogger


class Logger:

    name = None
    parent = None
    disabled = None

    def info(self, msg, *args, **kwargs):
        if self.isEnabledFor(20):
            self._log(20, msg, args, **kwargs)

    def _log(self, level, msg, args, exc_info=None, extra=None):
        """
        Low-level logging routine which creates a LogRecord and then calls
        all the handlers of this logger to handle the record.
        """
        record = self.makeRecord()
        self.handle(record)

    def handle(self, record):
        if (not self.disabled) and self.filter(record):
            self.callHandlers(record)

    def callHandlers(self, record):
        """
        Pass a record to all relevant handlers.

        Loop through all handlers for this logger and its parents in the
        logger hierarchy. If no handler was found, output a one-off error
        message to sys.stderr. Stop searching up the hierarchy whenever a
        logger with the "propagate" attribute set to zero is found - that
        will be the last logger whose handlers are called.
        """
        c = self
        found = 0
        while c:
            for hdlr in c.handlers:
                found += 1
                if record.levelno >= hdlr.level:
                    hdlr.handle(record)
            if not c.propagate:
                c = None    # break out
            else:
                c = c.parent

    def findCaller(self):
        return None, None, None

    def makeRecord(self):
        return 'record'

    def filter(self, record):
        pass

    def isEnabledFor(self, level):
        pass


###############################################################################
#                            iterator
#     Provide a way to access the elements of an aggregate object sequentially
# without exposing its underlying representation.
###############################################################################
class SkipObject:
    """can iterate multiple times"""

    class Iter:
        def __init__(self, iterable):
            self.iterable = iterable
            self.offset = 0

        def __next__(self):
            if self.offset < len(self.iterable.content):
                item = self.iterable.content[self.offset]
                self.offset += 2
                return item
            else:
                raise StopIteration

        # Python 2
        next = __next__

    def __init__(self, content):
        self.content = content

    def __iter__(self):
        return SkipObject.Iter(self)


class SkipObject2:
    """can iterate only one time"""
    def __init__(self, content):
        self.content = content
        self.offset = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.offset < len(self.content):
            item = self.content[self.offset]
            self.offset += 2
            return item
        else:
            raise StopIteration

    # Python 2
    next = __next__


def skip_gen(content):
    offset = 0
    while offset < len(content):
        yield content[offset]
        offset += 2

for obj in (SkipObject, SkipObject2, skip_gen):
    for item in obj('hello world'):
        print(item)


###############################################################################
#                             command
#     An object is used to encapsulate all information needed to perform an
# action. This information includes how the method is invoked and the parameters
# of the method.
#     The thread/process pool in Python 3's standard library concurrent.futures
# is an example.
###############################################################################
class Future:
    pass


class _WorkItem(object):
    def __init__(self, future, fn, args, kwargs):
        self.future = future
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        if not self.future.set_running_or_notify_cancel():
            return

        try:
            result = self.fn(*self.args, **self.kwargs)
        except BaseException:
            e, tb = sys.exc_info()[1:]
            self.future.set_exception_info(e, tb)
        else:
            self.future.set_result(result)

_shutdown = False


def _worker(executor_reference, work_queue):

    while True:
        work_item = work_queue.get(block=True)
        if work_item is not None:
            work_item.run()
            # Delete references to object. See issue16284
            del work_item
            continue
        executor = executor_reference()
        # Exit if:
        #   - The interpreter is shutting down OR
        #   - The executor that owns the worker has been collected OR
        #   - The executor that owns the worker has been shutdown.
        if _shutdown or executor is None or executor._shutdown:
            # Notice other workers
            work_queue.put(None)
            return
        del executor


class ThreadPoolExecutor:
    def __init__(self, max_workers):
        """Initializes a new ThreadPoolExecutor instance.

        Args:
            max_workers: The maximum number of threads that can be used to
                execute the given calls.
        """
        self._max_workers = max_workers
        self._work_queue = queue.Queue()
        self._threads = set()
        self._shutdown = False
        self._shutdown_lock = threading.Lock()

    def submit(self, fn, *args, **kwargs):
        with self._shutdown_lock:
            if self._shutdown:
                raise RuntimeError('cannot schedule new futures after shutdown')

            f = Future()
            w = _WorkItem(f, fn, args, kwargs)

            self._work_queue.put(w)
            return f

