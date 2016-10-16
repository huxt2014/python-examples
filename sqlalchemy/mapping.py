

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

## define the user-defined class, describe the table metadata and do mapping 
## at once.
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)   # map to a column named 'id'
    name = Column('user_name', String)       # map to a column named 'user_name'
    fullname = Column(String)

User.password = Column(String)               # add a column later


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
    id = Column(Integer, primary_key=True)
    addresses = relationship('Address', back_populates='user')

class Address():
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='addresses')


## one to one
##     the uselist flag indicates the relationship is a scalar attribute
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    address = relationship('Address', uselist=False, back_populates='user')

class Address():
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='address')


## many to many using secondary argument
association_table = Table('association', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('address_id', Integer, ForeignKey('address.id'))
)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    addresses = relationship('Address', secondary=association_table)

class Address():
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)

## many to many using association Object
class Association(Base):
    __tablename__ = 'association'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    address_id = Column(Integer, ForeignKey('address.id'), primary_key=True)
    other_column = Column(Integer)
    address = relationship('Address')
    user = relationship('User')
    
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    associations = relationship('Association')

class Address():
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    associations = relationship('Association')

## use foregin_keys when no foreign key or multiple foreign keys
class Address():
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    user = relationship('User', foreign_keys=[user_id])
    

## Specifying Alternate Join Conditions
##     The default behavior of relationship() is joining two tables using 
## primary key columns on one side and foreign key columns on the other.
class Address():
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    user = relationship('User', foreign_keys=[USER_ID],
                        primaryjoin='and_(User.id==Address.user_id,'
                                         'Address.status==1)')
    


# Map inheritance ##############################################

## single table inheritance
class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(20))
    
    __mapper_args__ = {
        'polymorphic_on':type,
        'polymorphic_identity':'employee'
    }

class Manager(Employee):
    __mapper_args__ = {
        'polymorphic_identity':'manager'
    }
    
    @declared_attr
    def identical_column(cls):
        return Employee.__table__.c.get('identical_column', Column(Integer))

class Engineer(Employee):
    __mapper_args__ = {
        'polymorphic_identity':'engineer'
    }
    
    @declared_attr
    def identical_column(cls):
        # map a column that already exists.
        return Employee.__table__.c.get('identical_column', Column(Integer))
    

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


