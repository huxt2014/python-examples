

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
###############################################################################
#######                Declarative Mapping                             ########
###############################################################################

## define the user-defined class, describe the table metadata and do mapping 
## at once.
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Parent(Base):
    __tablename__ = 'parent'

    id = Column(Integer, primary_key=True)   # specify primary key
    name = Column('full_name', String)       # map to a column named 'full_name'
    job = Column(String)                     # map to a column named 'job'

Parent.hobby = Column(String)                # add a column later

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id')) # specify foreign key
    parent = relationship('Parent')          # map relationship


## use declared_attr
class MyModel(Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    @declared_attr
    def id(cls):
        return Column(Integer)


## mapping a user-defined class to a table explicitly
class Parent(Base):
    __table__ = parent
    id = parent.c.id
    name = parent.c.full_name            # a column with different name


###############################################################################
########         send extra args to low level function                 ########
###############################################################################

# these arguments will be passed to sqlalchemy.orm.mapper function
class Parent(Base):
    __mapper_args__ = {
            'column_prefix': '_',    # add prefix to each column
            'include_properties': ['column1', 'column2'],  # only include
            'exclude_properties': ['column1', 'column2'],  # exclude
            }
    
# these arguments will be passed to table constructor
class Child(Base):
    __table_args__ = (
            ForeignKeyConstraint('parent_id', 'parent.id'),
            UniqueConstraint('col'),
            {'mysql_engine': 'InnoDB'}
            )


###############################################################################
########               SQL expression as attribute                     ########
###############################################################################

from sqlalchemy.ext.hybrid import hybrid_property

class Parent(Base):
    firstname = Column(String(50))
    lastname = Column(String(50))
    fullname = column_property(firstname + ' ' + lastname)
    
    @hybrid_property
    def fullname(self):
        return self.firstname + ' ' + self.lastname


###############################################################################
########                     use mixin                                 ########
###############################################################################

## column mixin
class BaseMixin(object):
    id = Column(Integer, primary_key=True)

## dynamic table name mixin
class TableName:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class MyModel(BaseMixin, TableName, Base):
    name = Column(String(1000))


## Every class inherit Base will has its own properties with the same name
## as the properties in Base
class Base(object):
    id = Column(Integer, primary_key=True)

Base = declarative_base(cls=Base)


###############################################################################
########                       inspect table                           ########
###############################################################################

from sqlalchemy import inspect
p_insp = inspect(Parent)
list(p_insp.columns)
p_insp.columns.name


###############################################################################
########                    Classical Mappings                         ########
###############################################################################

## default mapping
from sqlalchemy import Table, MetaData, Column, Integer, String
from sqlalchemy.orm import mapper

metadata = MetaData()

parent = Table('parent', metadata,
             Column('id', Integer, primary_key=True),
             Column('name', String(50)),
             Column('job', String(50)),
             Column('hobby', String(12))
             )

class Parent(object):
    def __init__(self, name, job, hobby):
        self.name = name
        self.job = job
        self.hobby = hobby

mapper(Parent, parent)


## mapping explicitly
mapper(Child, child, 
       properties={'id': child.c.id,
                   'parent_id': child.c.parent_id,
                   'parent': relationship('Parent')}
       )




