

###############################################################################
#######                  single table inheritance                      ########
###############################################################################

## 
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


###############################################################################
#######                dynamic table name in inheritance               ########
###############################################################################
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import has_inherited_table

## set tablename to None
class Tablename:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
class Person(Tablename, Base):
    pass

class Engineer(Person):
    __tablename__ = None
    
## use method has_inherited_table
class Tablename(object):
    @declared_attr
    def __tablename__(cls):
        if has_inherited_table(cls):
            return None
        return cls.__name__.lower()

class Person(Tablename, Base):
    pass

class Engineer(Person):
    pass


