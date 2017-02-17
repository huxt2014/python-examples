

"""
    All the instance corresponding to the same row in the database are identical
in the identity map, which is attached to and managed by a session instance.
    Though the transaction ends by commit or rollback, the objects loaded is 
still maintained by the Session object. Get these objects will not load them
again, but qualify any column or relationship of any object will reload the 
object by emit a query.
    Besides control the transaction, the session also implements the identity
map pattern and unit of work pattern.

Object states
    Transient - an instance that's not in a session, and is not saved to the
database. The only relationship such an object has to the ORM is that its class
has a mapper() associated with it.
    Pending - when you add() a transient instance, it becomes pending.
    Persistent - An instance which is present in the session and has a record in
the database.
    Deleted - An instance which has been deleted within a flush, but the
transaction has not yet completed.
    Detached - an instance which corresponds, or previously corresponded, to a
record in the database, but is not currently in any session.

States changes

      <--------------------------------rollback-------------
     |                                                     |
+-----------+               +---------+               +------------+
| transient | -----add----> | pending | ---flush----> | persistent |
+-----------+               +---------+               +------------+
     |                           |
     <-----rollback/expunge------


database            --------------expunge/close------------------------------>
other session      |                                                         |
   |       +------------+                     +---------+               +----------+
   ------> | persistent | ---delete+flush---> | deleted | ---commit---> | detached |   
           +------------+                     +---------+               +----------+
                 |                                 |                        |
                 <---------------rollback----------                         |
                 <-------------------------------------add------------------
"""

from sqlalchemy import Column, Integer, String, ForeignKey, inspect
from sqlalchemy.orm import joinedload, relationship
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
session = Session()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(16))


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    email_address = Column(String)
    user = relationship(User, backref='addresses')

################################################################################
#                              identity set
#     The session itself acts somewhat like a set-like collection. All items
# present may be accessed using the iterator interface.
################################################################################

user = User()
session.add(user)

for obj in session:
    print obj
    
assert user in session
    
# inspect the current state of an object
state = inspect(user)
assert state.persistent

################################################################################
#                              expunge
# Expunging removes an object from the session.
#     Pending instances are sent to the transient state.
#     Persistent instances from flush() are sent to detached state. Qualify
# their attributes are valid.
#     Persistent instances from query are sent to detached state and expired.
# By default, qualify their attribute will cause DetachedInstanceError, for no
# no session can be used to reload these instances from database again.
#     All the scenes will not change the instances' attributes.
################################################################################
session.expunge(user)


################################################################################
#                              rollback
# rollback DOES NOT remove all the instances from the session.
#     For pending instances and persistent instances that result by flush(),
# they are expunged and set to transient state. Their attributes will not be
# changed.
#     For persistent instances result by query(), they are still persistent
# but expired, which means that qualify their attributes will reload them by
# emitting a query.
#     All objects not expunged are fully expired.
################################################################################
session.rollback() 

################################################################################
#                               expire
# expire erase instances' attributes, and when those attributes are next
# accessed, a query is emitted. Only persistent instances has expired state.
################################################################################

session.expire(user)
session.expire_all() 


################################################################################
#                             manage relationship
#     emit a query and load relationship objects during the first qualification
# if no eager load is applied.
################################################################################

# load ########################################################
# may emit a quer
addresses = user.addresses

# eager load through left join
session.query(User).options('addresses')

# eager load with join. cause the inner join followed by left outer join.
session.query(User).options(joinedload('addresses')).join(User.addresses)


# delete ######################################################
# delete from secondary table automatically
user.addresses.remove(addresses[0])

# whether delete from secondary table depends on the configuration
session.delete(addresses[0])
 



