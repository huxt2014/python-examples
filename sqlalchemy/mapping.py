

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


## augment the Base
##     Every class inherit Base will has its own properties with the same name
## as the properties in Base
class Base(object):
    id = Column(Integer, primary_key=True)

Base = declarative_base(cls=Base)


## use declared_attr
class MyModel(Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    @declared_attr
    def id(cls):
        return Column(Integer)



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



# Map relationship #############################################
#     When using a bidirectional relationship, elements added in one direction 
# automatically become visible in the other direction. This behavior occurs 
# based on attribute on-change events and is evaluated in Python, without using 
# any SQL

## one to many relationship
##     The tag of primary_key and foreign_key is required.
##     Relationship in on class but not in the other is permitted.
##     Many to one is similar
class User(Base):
    __tablename__ = 'user'
    ID = Column(Integer, primary_key=True)
    ADDRESSES = relationship('Address', back_populates='USER')

class Address():
    __tablename__ = 'address'
    ID = Column(Integer, primary_key=True)
    USER_ID = Column(Integer, ForeignKey('User.ID'))
    USER = relationship('User', back_populates='ADDRESSES')


## one to one
##     the uselist flag indicates the relationship is a scalar attribute
class User(Base):
    __tablename__ = 'user'
    ID = Column(Integer, primary_key=True)
    ADDRESS = relationship('Address', uselist=False, back_populates='USER')

class Address():
    __tablename__ = 'address'
    ID = Column(Integer, primary_key=True)
    USER_ID = Column(Integer, ForeignKey('User.ID'))
    USER = relationship('User', back_populates='ADDRESS')


## many to many using secondary argument
association_table = Table('association', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('address_id', Integer, ForeignKey('address.id'))
)

class User(Base):
    __tablename__ = 'user'
    ID = Column(Integer, primary_key=True)
    ADDRESSES = relationship('Address', secondary=association_table)

class Address():
    __tablename__ = 'address'
    ID = Column(Integer, primary_key=True)
    
user.ADDRESSES.remove(someaddress)  # delete from secondary table automatically
session.delete(someaddress)        # whether delete from secondary table depends on the configuration


## many to many using association Object
class Association(Base):
    __tablename__ = 'association'
    USER_ID = Column(Integer, ForeignKey('user.ID'), primary_key=True)
    ADDRESS_ID = Column(Integer, ForeignKey('address.ID'), primary_key=True)
    EXTRA_DATA = Column(Integer)
    ADDRESS = relationship('Address')
    
class User(Base):
    __tablename__ = 'user'
    ID = Column(Integer, primary_key=True)
    ADDRESSES = relationship('Association')

class Address():
    __tablename__ = 'address'
    ID = Column(Integer, primary_key=True)


## use foregin_keys when no foreign key or multiple foreign keys
class Address():
    __tablename__ = 'address'
    ID = Column(Integer, primary_key=True)
    USER_ID = Column(Integer)
    USER = relationship('User', foreign_keys=[USER_ID])
    

## Specifying Alternate Join Conditions
##     The default behavior of relationship() is joining two tables using 
## primary key columns on one side and foreign key columns on the other.
class Address():
    __tablename__ = 'address'
    ID = Column(Integer, primary_key=True)
    USER_ID = Column(Integer)
    USER = relationship('User', foreign_keys=[USER_ID],
                        primaryjoin='and_(User.ID==Address.USER_ID,'
                                         'Address.STATUS=1)')
    


# Map inheritance ##############################################




# use mixin ####################################################

## Basic mixin
class Mixin(object):
    id = Column(Integer, primary_key=True)
    
class MyModel(Mixin, Base):
    name = Column(String(1000))


## relationship in mixin




# inspect table #################################################
from sqlalchemy import inspect
u_insp = inspect(User)
list(u_insp.columns)
u_insp.columns.name


