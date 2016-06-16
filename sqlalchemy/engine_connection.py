
'''
                          Pool
                        /       \
                       /         \
connect() <---- Engine           DBAPI ------- Database
                       \         /
                        \       /
                         Dialect

    The Engine refers to a connection pool by default. When an Engine is garbage 
collected, the pool and its connections will also be garbage collected (if none 
of its connections are still checked out). 
    Connections that are checked out are not discarded when the engine is 
disposed or garbage collected, as these connections are still strongly 
referenced elsewhere. When they are closed, they will be returned to their 
now-orphaned connection pool which will ultimately be garbage collected.
    Get connection from engine is intended to be called upon in a concurrent 
fashion. But an engine with pool for a multiple-process application, it’s  
usually required that a separate Engine be used for each child process. Because 
DBAPI connections in pool tend to not be portable across process boundaries. An 
Engine that is configured not to use pooling does not have this requirement.
    Applications that not use ORM would care the API of engine and connection.
For ORM, Session object is used as the interface to the database most of the 
time.
'''

# initial engine #########################################
#     Typically initialed once per particular database URL, and held globally  
# for the lifetime of a single application process. 

## mysql-python as default DBAPI (mysqldb)
from sqlalchemy import create_engine
engine = create_engine('mysql://user:password@host/db_name') 

## specify DBAPI
engine = create_engine('mysql+mysqlconnector://user:password@host/db_name')

## create from configuration
from sqlalchemy import engine_from_config
engine = engine_from_config(dict_config)

## using URL
URL = sqlalchemy.engine.url.URL('mysql', username='user', password='password',
                                host='host')
engine = create_engine(URL)


# release engine ##########################################
#     When an Engine is garbage collected, its connection pool is no longer 
# referred to by that Engine. However there are some cases whhere it's not a 
# good idea to rely on Python garbage collection. THese cases include:
#     1. Release all the connections and no longer connect to that database at
# all for any future operations.
#     2. In multiprocessing situation, such as after fork(), for database 
# connections generally do not travel across process boundaries.
#     3. Within test suites or multitenancy scenarios where many ad-hoc, 
# short-lived Engine objects may be created and disposed.
#
#     It is strongly recommended that Engine.dispose() is called only after all 
# checked out connections are checked in or otherwise de-associated from their 
# pool.

engine.dispose()


# custom DBAPI connect() arguments #########################

## through engine's db url
engine = create_engine('mysql://user:password@host/db_name?arg1=foo&arg2=bar')

## through create_engine function
engine = create_engine(db_url, connect_args={'arg1': 'foo', 'arg2': 'bar'})

# emit a query #############################################
result = engine.execute(query)       # acquires a new Connection on its own

# Threadlocal Execution Strategy ###########################
## The “threadlocal” feature is generally discouraged.
db = create_engine('mysql://localhost/test', strategy='threadlocal')



# check out and release connection ###########################
#     Connection is a proxy object for an actual DBAPI connection. When the 
# close() method is called, the referenced DBAPI connection is released to the 
# connection pool. From the perspective of the database itself, nothing is 
# actually “closed”, if pooling is in use. 
#     ResultProxy references a DBAPI cursor. The DBAPI cursor will be closed by  
# the ResultProxy when all of its result rows (if any) are exhausted. A 
# ResultProxy that returns no rows, such as that of an UPDATE statement, 
# releases cursor resources immediately upon construction.

## use connection explicitly
connection = engine.connect()
result = connection.execute(query)
for row in result:
    print row
connection.close()

## use connection implicitly through engine
##     when underlying DBAPI cursor is closed, the Connection object itself is  
## also closed.
result = engine.execute(query)
for row in result:
    print row
    
## close result explicitly if needed.
result.close()


# transaction ################################################
#     The core behavior of DBAPI per PEP-0249 is that a transaction is always in 
# progress, providing only rollback() and commit() methods but no begin(). 
# SQLAlchemy assumes this is the case for any given DBAPI.
#     In the context that transaction is not used explicitly, the statement with
# autocommit=True execution option will issue COMMIT automatically. If the 
# statement is a text-only statement and the flag is not set, commit 
# automatically.
#     The autocommit feature is only in effect when no Transaction is declared.

## transaction is used implicitly
connection = engine.connect()
connection.execute('update query')                       # auto commit
connection.execute(text('selete query')
                   .execution_options(autocommit=True))  # auto commit

## use transaction explicitly
connection = engine.connect()
trans = connection.begin()
try:
    connection.execute(query)
    trans.commit()
except:
    trans.rollback()
    raise

## use transaction through context manager
with connection.being():
    connection.execute(query)

## transaction through engine and context manager
with engine.begin() as connection:
    connection.execute(query)
    
## nested transaction
trans1 = connection.begin()
try:
    try:
        trans2 = connection.begin()
        connection.execute(query)
        trans2.commit()                     # transaction is not committed yet
    except:
        trans2.rollback()                   # rollback the whole transaction
        raise
    connection.execute(query)
    trans1.commit()                         # transaction is committed here 
except:
    trans1.rollback()                       # rollback the whole transaction
    raise



# get raw DBAPI connection ############################

## from an already present connection object directly
##     As this DBAPI connection is still contained within the scope of an owning
## Connection object, it is best to make use of the Connection object for most 
## features such as transaction control as well as calling the 
## Connection.close() method; if these operations are performed on the DBAPI 
## connection directly, the owning Connection will not be aware of these changes
## in state.
dbapi_conn = connection.connection()

## from engine
dbapi_conn = engine.raw_connection()

## release
dbapi_conn.close()



# use connection pool

## basic configuration for default pool, QueuePool
engine = create_engine(url, pool_size=20, max_overflow=0)

## switch pool implementations
from sqlalchemy.pool import NullPool
engine = create_engine(url, poolclass=NullPool)      # disable pool

## custom connection creator in pool
##    creator is there as a last resort for when a DBAPI has some form of 
## connect that is not at all supported by SQLAlchemy.
import sqlalchemy.pool as pool
import psycopg2

def getconn():
    c = psycopg2.connect()
    return c

engine = create_engine(url, creator=getconn)

## construct a pool
import sqlalchemy.pool as pool
import psycopg2

def getconn():
    c = psycopg2.connect(username='ed', host='127.0.0.1', dbname='test')
    return c

mypool = pool.QueuePool(getconn, max_overflow=10, pool_size=5)

connection = mypool.connect()                 # get DBAPI connection
connection.close()                            # release, not really close

engine = create_engine(url, pool=mypool)      # shared with one or more engines



# deal with disconnection
#     The connection pool has the ability to refresh individual connections as 
# well as its entire set of connections. Situations where a connections is set
# as invalid include:
#     1. The database server is restarted and all previously established 
# connections are no longer functional. 
#     2. When using an Engine, Connection.invalidate() cause an explicit 
# invalidation.
#     3. A DBAPI exception such as OperationalError, raised when a method like 
# connection.execute() is called, is detected as indicating a so-called 
# “disconnect” condition.
#     4. When the connection is returned to the pool, and calling the 
# connection.rollback() or connection.commit() methods, and throws an exception.
#     5. A listener for PoolEvents.checkout() raise the DisconnectionError 
# exception.
 

## let engine handle an unexpected disconnection
##     This assumes the Pool is used in conjunction with a Engine. The Engine 
## has logic which can detect disconnection events and refresh the pool 
## automatically.
from sqlalchemy import exc

c = engine.connect()
try:
    c.execute('query')
    c.close()
except exc.DBAPIError, e:
    # an unexpected disconnection will raise an exception, the 'disconnect' 
    # event is emitted, the engine will handle it and refresh the DBAPI 
    # connections
    if e.connection_invalidated:                
        print("Connection was invalidated!")      # do nothing

c = e.connect()                                   # engine will do recovery
c.execute(query)                                  # successful for the next query

## let engine handler an expected disconnect
##     Set a connection as invalid after a certain age. Note that the 
## invalidation only occurs during checkout.
engine = create_engine(url, pool_recycle=3600)

## detect an invalid disconnection forehead
##    Some extra SQL emitted for each connection checked out from the pool and
## detect an invalid connection before it is used. Engine will refresh the whole
## pool.
from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy import select

@event.listens_for(some_engine, "engine_connect")
def ping_connection(connection, branch):
    if branch:
        # "branch" refers to a sub-connection of a connection,
        # we don't want to bother pinging on these.
        return

    # turn off "close with result".  This flag is only used with
    # "connectionless" execution, otherwise will be False in any case
    save_should_close_with_result = connection.should_close_with_result
    connection.should_close_with_result = False

    try:
        # use a core select() for all backend
        connection.scalar(select([1]))
    except exc.DBAPIError as err:
        if err.connection_invalidated:
            # run the same SELECT again - the connection will re-validate
            # itself and establish a new connection.
            connection.scalar(select([1]))
        else:
            raise
    finally:
        # restore "close with result"
        connection.should_close_with_result = save_should_close_with_result


## invalidate a connection when no engine used
from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.pool import Pool

@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()
    cursor.close()


# use pool with multiprocessing
#     The pooled connections are not shared to a forked process.

## use Engine.dispose() explicitly
engine = create_engine()

def run_in_process():
  engine.dispose()                            # bind a new pool

  with engine.connect() as conn:
      conn.execute("...")

p = Process(target=run_in_process)


## use event to trigger it
from sqlalchemy import event
from sqlalchemy import exc
import os

engine = create_engine("...")

@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    connection_record.info['pid'] = os.getpid()

@event.listens_for(engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    pid = os.getpid()
    if connection_record.info['pid'] != pid:
        connection_record.connection = connection_proxy.connection = None
        raise exc.DisconnectionError(
                "Connection record belongs to pid %s, "
                "attempting to check out in pid %s" %
                (connection_record.info['pid'], pid)
        )





