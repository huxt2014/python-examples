
'''
    The default behavior of relationship() is joining two tables using primary 
key columns on one side and foreign key columns on the other
    When back_populates is used, change in this relationship will become visible
in the other object. For example, assume that p is instance of Parent and
back_populates is used in p.children, when p.children.append(c) finish, c.parent
is assigned p automatically. This behavior occurs based  on attribute on-change 
events and is evaluated in Python, without using any SQL.  

'''

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

###############################################################################
########                        one to many                            ########
###############################################################################

class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    children = relationship('Child', back_populates='parents')

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'))
    parents = relationship('Parent')


###############################################################################
########                       one to one                              ########
###############################################################################

#the uselist flag indicates the relationship is a scalar attribute
class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    child = relationship('Child', uselist=False, back_populates='parent')

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'))
    parent = relationship('Parent', back_populates='child')


###############################################################################
########                        many to many                           ########
###############################################################################

## using secondary argument
association_table = Table('as_parent_child', Base.metadata,
    Column('parent_id', Integer, ForeignKey('parent.id')),
    Column('child_id', Integer, ForeignKey('child.id'))
)

class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    children = relationship('Child', secondary=association_table,
                            back_populates='parents')

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parents = relationship('Parent', secondary=association_table)

## using association Object
##     it’s used when your association table contains additional columns beyond
## those which are foreign keys to the left and right tables.
class Association(Base):
    __tablename__ = 'as_parent_child'
    parent_id = Column(Integer, ForeignKey('parent.id'), primary_key=True)
    child_id = Column(Integer, ForeignKey('child.id'), primary_key=True)
    other_column = Column(Integer)
    parent = relationship('Parent', back_populates='as_children')
    child = relationship('Child', back_populates='as_parents')
    
class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    as_children = relationship('Association')

class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    as_parents = relationship('Association')
    
## Self-Referential with foreign keys
node_to_node = Table("node_to_node", Base.metadata,
    Column("left_node_id", Integer, ForeignKey("node.id"), primary_key=True),
    Column("right_node_id", Integer, ForeignKey("node.id"), primary_key=True)
)

class Node(Base):
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True)
    right_nodes = relationship("Node",
                        secondary=node_to_node,
                        primaryjoin=id==node_to_node.c.left_node_id,
                        secondaryjoin=id==node_to_node.c.right_node_id,
                        backref="left_nodes")


###############################################################################
########            specify foreign key or join condition              ########
###############################################################################

## when there is no foreign key,  foreign_keys and primaryjoin are required.
class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer)
    parent = relationship('Parent',
                          foreign_keys=parent_id,
                          primaryjoin='Parent.id==Child.parent_id')

## when more than on foreign key exist, foreign_keys is required
class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('parent.id'))
    other_id = Column(Integer, ForeignKey('other.id'))
    parent = relationship('Parent', foreign_keys=parent_id)


## Specifying Alternate Join Conditions   .
class Child():
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer)
    parent = relationship('Parent',
                          primaryjoin='(Parent.id==Child.parent_id)&('
                                       'Parent.status==1)')

## Self-Referential without foreign keys
from sqlalchemy.orm import foreign
node_to_node = Table("node_to_node", Base.metadata,
    Column("left_node_id", Integer, primary_key=True),
    Column("right_node_id", Integer, primary_key=True)
)

class Node(Base):
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True)
    right_nodes = relationship("Node",
                        secondary=node_to_node,
                        primaryjoin=id==node_to_node.c.left_node_id,
                        secondaryjoin=id==foreign(node_to_node.c.right_node_id),
                        foreign_keys=[node_to_node.c.left_node_id],
                        backref="left_nodes")
    

###############################################################################
########                 Adjacency List Relationships                  ########
###############################################################################

#     a table contains a foreign key reference to itself. This is the most 
# common way to represent hierarchical data in flat tables.

## by default, parent_id is a remote column
class Node(Base):
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('node.id'))
    data = Column(String(50))
    children = relationship("Node")
    
## change remote column
class Node(Base):
    __tablename__ = 'node'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('node.id'))
    data = Column(String(50))
    parent = relationship("Node", remote_side=[id])


###############################################################################
########                      use mixin                                ########
###############################################################################

## dynamic relationship

class RelaMixin():
    @declared_attr
    def parent(self):
        return relationship('Parent')         # all arguments should use string

class Child(Base, RelaMixin):
    pass





    
