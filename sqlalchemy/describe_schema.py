
"""
    The core of SQLAlchemy’s query and object mapping operations are supported 
by database metadata, which is comprised of Python objects that describe tables
and other schema-level objects. These objects are at the core of three major
types of operations: SQL DDL, constructing SQL queries, and expressing 
information about structures that already exist within the database.
    A key feature of SQLAlchemy’s database metadata constructs is that they are
designed to be used in a declarative style. Also it is most intuitive to those
who have some background in creating real schema generation scripts.
    MetaData is a thread-safe object for read operations. Construction of new 
tables within a single MetaData object, either explicitly or via reflection, may
not be completely thread-safe.

"""

# describe explicitly ######################################

## describe table at module level
from sqlalchemy import MetaData, Table

metadata = MetaData()

user = Table('user', metadata, 
             Column('user_id', Integer, primary_key=True),
             Column('user_name', String(16))
             )

## describe dynamically
user = Table('user', metadata)
user.append_column(Column('user_id', Integer, primary_key=True))



# reflect database object #################################

## autoload
##     THe first time accessing the table that not exists, reflection queries
## is issued and the table is created automatically. THe dependent tables will
## be  loaded too.
##     Reflect view is supported
##     Reflection process only get the table schema that stored in the database. 
## Some aspects of a schema may not be stored in database.
user = Table('user', meta, autoload=True)

user = Table('user', meta,
             Column('id', Integer, primary_key=True),      # override a column
             autoload=True)

## reflect all tables at once
meta.reflect(bind=engine, views=True)




# inspect metadata ##########################################

## inspect tables
for t in metadata.sorted_tables:
    pass

user.columns.user_id
user.c.user_id
user.c['user_id']
for c in user.c:
    pass

## a low level interface for backend-agnostic system
from sqlalchemy.engine import reflection

insp = reflection.Inspector.from_engine(engine)
print insp.get_table_names()
print insp.get_view_names()

insp.get_columns(table_name)



## create and drop
metadata.create_all(engine)
metadata.drop_all(engine, checkfirst=True)

user.create(engine)
user.drop(engine)



# client side default ########################################

## scalar default
Column('c', Integer, defalut=12)

## python function
import datetime

Column('c', DateTime, onupdate=datetime.datetime.now)

## context-sensitive function
def mydefault(context):
    return context.current_parameters['counter'] + 12

t = Table('mytable', meta,
          Column('counter', Integer),
          Column('counter_plus_twelve', Integer, default=mydefault, 
                 onupdate=mydefault)
          )

## SQL expressions
Column('create_date', DateTime, default=func.now())

Column('key', String(20), 
       default=atable.select(atable.c.type=='type1', limit=1)  # subquery
       )



# server side default ########################################
Column('created_at', DateTime, server_default=text("sysdate"))



# customize DDL #############################################
event.listen(metadata, 'after_create',
             DDL("alter table ..."))

evemt.listen(metadata, 'after_create',
             DDL('alter table ...').execute_if(dialect='postgresql'))


# type ########################################################

## for mysql dialect
from sqlalchemy.dialects.mysql import (VARCHAR, INTEGER, DATETIME, BOOLEAN,
                                       TEXT)

## dumps automatically
from sqlalchemy.types import PickleType

