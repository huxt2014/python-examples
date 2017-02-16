
"""
    In ORM, the public API for engine, connection and transaction is under the
control of the session object The session object maintains these objects
internally and offer the interface to deal with database. It also offer other
characters, such as identity map.
    By default, a session that newly constructed has no transaction and
connections. Once it is used to talk to the database, it requests a connection
from an engine and maintains a transaction object from this connection. When the
transactional state is completed after a rollback or commit, the session
releases all transaction and connection, and goes back to the "begin" state.
    For session in autocommit mode, each SQL statement invoked by a
Session.query() or Session.execute() occurs using a new connection from the
connection pool, discarding it after results have been iterated.

transaction
    A session will begin a new transaction if it is used again, subsequent to
the previous transaction ending. From this it follows that a session is capable
of having a lifespan across many transactions, though only one at a time.
    SQLAlchemy by default refreshes data from a previous transaction the first
time it's accessed within a new transaction, so that the most recent state is
available.
    Make sure you have a clear notion of where transactions begin and end, and
keep transactions short.

identity map
    With identity map, all changes to objects maintained by a session are
tracked and no SQL will be emitted to database until a subsequent query(),
flush() or commit().
    The objects associated with a session are proxy objects to the transaction
being held by the session. There are a variety of events that will cause objects
to re-access the database in order to keep synchronized.
    Though the existence of identity map, a session object doesn't do any kind
of query caching. Any query will be issued to the database, get the roll back,
and refresh the identity map if necessary.
    query.get() get objects from identity map and no query is issued.

concurrency
    An session object, and all objects associated with it should be only used in
a single thread at a time.

State Management
"""

from sqlalchemy import create_engine, Column
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.session import Session


class User:
    id = Column()

engine = create_engine()
engine2 = create_engine()

user1 = User()
user2 = User()

###############################################################################
#                            create a session
#     Session is a regular Python class which can be directly instantiated.
# However, to standardize how sessions are configured and acquired, the
# sessionmaker class is normally used to create a top level configuration which
# can then be used throughout an application without the need to repeat the
# configurational arguments.
###############################################################################

# get session factory and keeping configuration.
session_factory = sessionmaker(bind=engine)

# get an empty session factory and configure it later
session_factory2 = sessionmaker()
session_factory2.configure(bind=engine)

# get a session instance from factory
session = session_factory()

# get a session with special arguments
session2 = session_factory(bind=engine2)

# Use Session class directly
session3 = Session(bind=engine)

###############################################################################
#                                usage
###############################################################################

# select #####################################################
#     Retrieve objects from database and store them into
# identity map. Normally, instances loaded into the Session
# are never changed by subsequent queries, unless flush is
# needed.
session.query()

# add ########################################################
#     Place instances in the session. No SQL issued to the
# database until a subsequent query(), flush() or commit().
session.add(user1)
session.add_all([user1, user2])

# delete #####################################################
#     Marked as deleted. While the collection member is marked
# for deletion from the database, this does not impact the
# collection itself in memory until the collection is expired.
session.delete(user1)
session.query(User).filter(User.id == 7).delete()

# flush ######################################################
#     Occurs transparently before any query and within commit
# automatically. If the Session is not in autocommit=True mode,
# an explicit call to rollback() is required after a flush
# fails, even though the underlying transaction will have been
#  rolled back already
session.flush()
session.autoflush = False           # disable auto flush

# roll back ##################################################
#     All transactions are rolled back and all connections
# returned to the connection pool, unless the Session was
#  bound directly to a Connection.
#     Objects which were marked as deleted are promoted back
# to the persistent state, corresponding to their DELETE
# statement being rolled back.
session.rollback()

# commit #####################################################
#      Commit the transaction and expires the state of all
# instances present after the commit is complete..
session.commit()

# close ######################################################
#     Issues a expunge_all(), and releases any
# transactional/connection resources.
session.close()

# transaction demarcation in auto commit mode
session = Session(autocommit=True)
session.begin()
try:
    item1 = session.query(User).get(1)
    item2 = session.query(User).get(2)
    item1.foo = 'bar'
    item2.bar = 'foo'
    session.commit()
except:
    session.rollback()
    raise

with session.begin():
    item1 = session.query(User).get(1)
    item2 = session.query(User).get(2)
    item1.foo = 'bar'
    item2.bar = 'foo'


###############################################################################
#                              scoped_session
# The scoped_session object by default uses threading.local() as storage
###############################################################################

# initial
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# only keep one session instance for each thread
session_1 = Session()
session_2 = Session()
assert session_1 is session_2    # True

# release and recreate session instance
Session.remove()
session_3 = Session()
assert session_3 is session_1    # False

# as a proxy
Session.query()
Session.add()
Session.commit()


# bind to a request scope
def get_current_request():
    # return an scope, for example, coroutine, thread or request
    pass
Session = scoped_session(session_factory, scopefunc=get_current_request)
