
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import (declarative_base, declared_attr,
                                        has_inherited_table)

Base = declarative_base()


###############################################################################
#                          single table inheritance
###############################################################################
class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(20))
    
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'employee'
    }


class Manager(Employee):
    __mapper_args__ = {
        'polymorphic_identity': 'manager'
    }

    manager_c1 = Column(Integer)
    manager_c2 = Column(Integer)
    
    @declared_attr
    def identical_column(cls):
        return Employee.__table__.c.get('identical_column', Column(Integer))


class Engineer(Employee):
    __mapper_args__ = {
        'polymorphic_identity': 'engineer'
    }

    engineer_c1 = Column(Integer)
    engineer_c2 = Column(Integer)
    
    @declared_attr
    def identical_column(cls):
        # map a column that already exists.
        return Employee.__table__.c.get('identical_column', Column(Integer))


# apply further arguments within the constructor to the
# existing Table.
class EngineerExtend(Engineer):
    __tablename__ = Engineer.__tablename__
    __table_args__ = {
        'extend_existing': True
    }

    engineer_c3 = Column(Integer)

###############################################################################
#                          joined table inheritance
#     In joined table inheritance, each class in a particular class's parent
# list is represented by a unique table. The total set of attributes for a
# particular instance is represented as a join along all tables in its
# inheritance path.
#     Each class in the inheritance path should be specified __tablename__.
# Each table also must contain a primary key column (or columns), and in most
# cases a foreign key reference to the parent table.
#     It is standard practice that the same column is used for both the role of
# primary key as well as foreign key to the parent table, and that the column is
# also named the same as that of the parent table.
###############################################################################

class Employee2(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(20))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'employee'
    }


class Manager2(Employee):
    __tablename__ = 'manager'

    id = Column(Integer, ForeignKey('employ.id'), primary_key=True)
    manager_c1 = Column(Integer)
    manager_c2 = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'manager'
    }


class Engineer2(Employee):
    __tablename__ = 'engineer'

    id = Column(Integer, ForeignKey('employ.id'), primary_key=True)
    engineer_c1 = Column(Integer)
    engineer_c2 = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'engineer'
    }


###############################################################################
#                      dynamic table name in inheritance
###############################################################################

# set tablename to None #########################################
class Tablename:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class Employee3(Tablename, Base):
    pass


class Manager3(Employee2):
    __tablename__ = None


# use method has_inherited_table ################################
class Tablename3(object):
    @declared_attr
    def __tablename__(cls):
        if has_inherited_table(cls):
            return None
        return cls.__name__.lower()


class Employee4(Tablename3, Base):
    pass


class Manager4(Employee3):
    pass
