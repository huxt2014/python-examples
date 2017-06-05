

import threading

###############################################################################
#                               decorator
#     Allowing behavior to be added to an individual object, either statically
# or dynamically, without affecting the behavior of other objects from the same
# class.
#     The decorator pattern is often useful for adhering to the Single
# Responsibility Principle, as it allows functionality to be divided between
# classes with unique areas of concern.
###############################################################################


class App:
    """
    PEP 333 compatible application
    """
    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return ['hello world.']


class Middleware:
    """
    PEP 333 compatible middleware
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):

        def start_mid(status, response_headers, exc_info=None):
            # do extra work
            return start_response(status, response_headers, exc_info)

        # do extra work
        return self.app(environ, start_mid)

app1 = App()
app2 = Middleware(App())


###############################################################################
#                               proxy
#     A proxy is a wrapper or agent object that is being called by the client to
# access the real serving object behind the scenes. Use of the proxy can simply
# be forwarding to the real object, or can provide additional logic. For the
# client, usage of a proxy object is similar to using the real object, because
# both implement the same interface.
###############################################################################


class ConnectionProxy:

    def __init__(self, connection):
        self._connection = connection

    def execute(self, sql):
        return self._connection.execute(sql)

    def close(self):
        self._connection.rollback()
        self._check_in(self._connection)

    def _check_in(self, con):
        # put back to connection pool
        pass

    def __getattr__(self, attr):
        """
        Called if attribute can not be found through proxy's inheritance search
        tree.
        """
        # delegate to _connection
        return getattr(self._connection, attr)


###############################################################################
#                               adapter
#    Like proxy, adapter always exists as a wrapper object. It allows the
# interface of an existing class to be used as another interface.
#     Often used to make existing classes work with others(for example, support
# polymorphic) without modifying their source code.
###############################################################################

class Dog(object):
    def __init__(self):
        self.name = "Dog"

    def bark(self):
        print("woof!")


class Cat(object):
    def __init__(self):
        self.name = "Cat"

    def meow(self):
        print("meow!")


class Adapter:
    def __init__(self, obj, **adapted_methods):
        self.obj = obj
        self.__dict__.update(adapted_methods)

    def __getattr__(self, attr):
        # delegate to obj
        return getattr(self.obj, attr)

dog = Dog()
cat = Cat()
objs = [Adapter(dog, make_noise=dog.bark),
        Adapter(cat, make_noise=cat.meow)]

for obj in objs:
    obj.make_noise()


###############################################################################
#                               facade
#     A facade is an object that provides a simplified interface to a larger
# body of code and so hides the complexities. It can make a software library
# easier to use, more readable and reduce dependencies of outside code on the
# inner workings of a library.
#     The facade design pattern is often used when a system is very complex or
# difficult to understand because the system has a large number of
# interdependent classes or its source code is unavailable.
###############################################################################
class Engine:
    """sqlalchemy.engine.Engine is an example that act as a facade. It provides
    interfaces that make basic operations about connection, raw connection,
    connection pool and transaction simple.
    """

    def __init__(self):
        pass

    def dispose(self):
        """Dispose of the connection pool
        """
        pass

    def begin(self):
        """Return a context manager delivering transaction established
        """
        pass

    def execute(self):
        """Executes the given sql
        """
        pass

    def connect(self):
        """Return a new connection object.
        """
        pass

    def raw_connection(self, ):
        """Return a raw DBAPI connection
        """
        pass


###############################################################################
#                               bridge
#     Bridge pattern often use aggregation to implement the method of a abstract
# class, but not inherit and override. This help decoupling an abstraction from
# its implementation so that the two can vary independently. The bridge pattern
# can also be thought of as two layers of abstraction.
#     Bridge pattern is useful when both the class and what it does vary often.
# Besides, since Python do not support function signatures, it is also often
# used to realize polymorphism.
###############################################################################
class BaseServer:
    """Python 2.X standard library: SocketServer.BaseServer
    """

    def __init__(self, server_address, RequestHandlerClass):
        """Constructor.  May be extended, do not override."""
        self.server_address = server_address
        self.RequestHandlerClass = RequestHandlerClass
        self.__is_shut_down = threading.Event()
        self.__shutdown_request = False

    def finish_request(self, request, client_address):
        """How to handle the request is implemented by another class, but not
        Server's subclass."""
        self.RequestHandlerClass(request, client_address, self)

    def serve_forever(self, poll_interval=0.5):
        pass


class BaseRequestHandler:
    """class that handle the request. Can be inherited.
    """

    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        self.setup()
        try:
            self.handle()
        finally:
            self.finish()

    def setup(self):
        pass

    def handle(self):
        pass

    def finish(self):
        pass


class RequestHandler(BaseRequestHandler):

    def handle(self):
        # override
        pass

server = BaseServer('127.0.0.1', RequestHandler)
server.serve_forever()

