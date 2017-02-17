

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

from sqlalchemy import (Table, MetaData, Column, Integer, String, ForeignKey,
                        PrimaryKeyConstraint, ForeignKeyConstraint,
                        UniqueConstraint, Index)
from sqlalchemy.orm import relationship, mapper, column_property
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.hybrid import hybrid_property


###############################################################################
#                          Declarative Mapping
#     define the user-defined class, describe the table metadata and do mapping
# at once.
###############################################################################
Base = declarative_base()


# basic map ###################################################
class Parent(Base):
    __tablename__ = 'parent'

    id = Column(Integer, primary_key=True)
    name = Column('full_name', String)
    job = Column(String)

# add a column later
Parent.hobby = Column(String)


class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'))
    parent = relationship('Parent')


# use declared_attr
class Child2(Base):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    @declared_attr
    def id(cls):
        return Column(Integer)


# mapping a class to a table explicitly ########################
class Parent(Base):
    __table__ = parent
    id = parent.c.id
    name = parent.c.full_name


# send extra args to low level function#########################
# these arguments will be passed to sqlalchemy.orm.mapper
# function
class Parent3(Base):
    __mapper_args__ = {
        'column_prefix': '_',
        'include_properties': ['column1', 'column2'],
        'exclude_properties': ['column1', 'column2'],
        }


# these arguments will be passed to table constructor
class Child3(Base):
    __table_args__ = (
        PrimaryKeyConstraint('col1', 'col2', name='pk_child'),
        ForeignKeyConstraint(('parent_id',), ('parent.id',)),
        UniqueConstraint('col'),
        Index('ix_col1', 'col1'),
        {'autoload': True,
         'mysql_engine': 'InnoDB',
         'mysql_charset': 'utf8',
         'mysql_collate': 'utf8_bin'}
         )


# SQL expression as attribute ##################################
class Parent4(Base):
    firstname = Column(String(50))
    lastname = Column(String(50))
    fullname = column_property(firstname + ' ' + lastname)
    
    @hybrid_property
    def fullname(self):
        return self.firstname + ' ' + self.lastname


# use mixin ###################################################
# column mixin
class BaseMixin(object):
    id = Column(Integer, primary_key=True)


# dynamic table name mixin
class TableName:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class MyModel(BaseMixin, TableName, Base):
    name = Column(String(1000))


# Every class inherit Base will has its own properties with
# the same name as the properties in Base
class Base(object):
    id = Column(Integer, primary_key=True)

Base = declarative_base(cls=Base)


###############################################################################
#                           Classical Mappings
###############################################################################

metadata = MetaData()

# basic mapping ################################################
parent = Table('parent', metadata,
               Column('id', Integer, primary_key=True),
               Column('name', String(50)),
               Column('job', String(50)),
               Column('hobby', String(12)))


class Parent6(object):
    def __init__(self, name, job, hobby):
        self.name = name
        self.job = job
        self.hobby = hobby

mapper(Parent, parent)


# mapping explicitly #############################################
child = Table('child', metadata,
              Column('id', Integer, primary_key=True),
              Column('parent_id', Integer,  ForeignKey('parent.id')),
              )


class Child6(object):
    def __init__(self, id, parent_id):
        self.id = id
        self.parent_id = parent_id

mapper(Child6, child,
       properties={'id': child.c.id,
                   'parent_id': child.c.parent_id,
                   'parent': relationship('Parent')}
       )




