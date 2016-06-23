

"""
    SQLAlchemy ORM realizes the data mapper pattern and features two distinct  
styles of mapper configuration. The "Classical" style is SQLAlchemy's original
mapping API, whereas "Declarative" is the richer and more succinct system that 
builds on top of "Classical". 
    Both styles may be used interchangeably, as the end result of each is 
exactly the same, that a user-defined class mapped onto a selectable unit, 
typically a Table.
    After the mapping finish, attributes in user-defined is replaced with 
instances of InstrumentedAttribute, with more functions added.
"""

# Declarative Mapping #########################################

## simple mapping
##     define the user-defined class, describe the table metadata and do mapping 
## at once.
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)   # map to a column named 'id'
    name = Column('user_name', String)       # map to a column named 'user_name'
    fullname = Column(String)
    password = Column(String)

## mapping a user-defined class to a table explicitly
class User(Base):
    __table__ = user_table
    id = user_table.c.id
    name = user_table.c.user_name            # a column with different name

## use common mixin
class Mixin(object):
    id = Column(Integer, primary_key=True)
    
class MyModel(Mixin, Base):
    name = Column(String(1000))

## augment the Base
class Base(object):
    id = Column(Integer, primary_key=True)

Base = declarative_base(cls=Base)

class MyModel(Base):
    name = Column(String(1000))
    
## use declared_attr
class MyModel(Base):
    
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()



# Classical Mappings ###########################################

## default mapping
from sqlalchemy import Table, MetaData, Column, Integer, String
from sqlalchemy.orm import mapper

metadata = MetaData()

user = Table('user', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50)),
            Column('fullname', String(50)),
            Column('password', String(12))
        )

class User(object):
    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password

mapper(User, user)


## mapping explicitly
mapper(User, user_table, properties={'id': user_table.c.id,
                                     'name': user_table.c.user_name,
                                     })


# inspect table #################################################
from sqlalchemy import inspect
u_insp = inspect(User)
list(u_insp.columns)
u_insp.columns.name


