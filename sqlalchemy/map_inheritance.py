
from sqlalchemy import Column, Integer, String
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
    
    @declared_attr
    def identical_column(cls):
        return Employee.__table__.c.get('identical_column', Column(Integer))


class Engineer(Employee):
    __mapper_args__ = {
        'polymorphic_identity': 'engineer'
    }
    
    @declared_attr
    def identical_column(cls):
        # map a column that already exists.
        return Employee.__table__.c.get('identical_column', Column(Integer))


###############################################################################
#                      dynamic table name in inheritance
###############################################################################

# set tablename to None #########################################
class Tablename:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class Employee2(Tablename, Base):
    pass


class Manager2(Employee2):
    __tablename__ = None


# use method has_inherited_table ################################
class Tablename3(object):
    @declared_attr
    def __tablename__(cls):
        if has_inherited_table(cls):
            return None
        return cls.__name__.lower()


class Employee3(Tablename3, Base):
    pass


class Manager3(Employee3):
    pass
