

"""
    The SQLAlchemy Expression Language presents a system of representing 
relational database structures and expressions using Python constructs. Also, 
it presents a method of writing backend-neutral SQL expressions.
    The SQLAlchemy ORM, which is built on the top of the Expression Language, 
show an example of applied usage of the Expression Language. Most of the query
begin with session.query() which return an Query object.
    The class Query features a generative interface whereby successive calls 
return a new Query object, a copy of the former with additional criteria and 
options associated with it.
    These constructs usually represent SQL as intermediate format. When bind 
with an engine, the ultimate SQL can be generated with the help of dialect.
"""


# ORM select ########################################################
#     session.query() takes a variable number of arguments, any combination of  
# mapped class, a Mapper object, an orm-enabled descriptor, or an AliasedClass 
# object.
#     In join query, table on the left side of the join is decided by the 
# leftmost entity in the Query object’s list of entities by default. Use 
# select_from() to specify a table.

## query one object
session.query(User)

## cross join without filter condition that get the Cartesian product. Return a 
## m*n list. 
session.query(User, Address)                  # return tow instances
session.query(User.name, Address.location)    # return two columns
session.query(User, Address.location)         # return an instance and an column

## inner join without condition. If only one foreign key exists between them,
## an on clause will be applied automatically (with poor readability). Return a 
## list of User instance.
session.query(User).join(Address)

## inner join with condition
session.query(User).join(User.addresses)   # through relationship.
session.query(User).join('addresses')      # the same
session.query(User).join(Address, User.addresses)  # the same, specify constrain
session.query(User).join(Address, User.id==Address.user_id)  # any condition

## specify which TABLE is on the left side of the join.
session.query(User, Address).select_from(User).join(User.addresses)

## query by function
from sqlalchemy import func
session.query(func.max(User.id))
session.query(func.count('*')).select_from(User)
session.query(func.now())                              # select now()
session.query(func.any_func())                         # select any_func()

## filter and filter_by
## filter support any SQL expression object
query.filter_by(id=1)                  # uses keyword arguments
query.filter(User.id == 1)             # use SQL expression object
query.filter(text("id<10"))            # use textual SQL
(query.filter(text("id<:value and name=:name"))   # bind parameters
      .params(value=10, name='hello'))

## aggregation
(session.query(User.department.
               func.sum(User.salary).albel('salary'),
               func.count('*').label('total_number'))
        .group_by(User.department))

## case clause
from sqlalchemy.sql.expression import case

session.query(User.id,
              case([(User.salary < 1000, 1), (User.salary.between(1000,2000), 2)],
                   else_=0).label('salary'))

## other option
query.order_by(User.id)        ## order by
query.distinct()               ## distinct


## get query result
## the Query instance will not emit a query until the following method invoked
query.all()              # fetch all as list
query.first()            # fetch one or None
query.one()              # fetch one or NoResultFound or MultipleResultsFound
query.one_or_none()      # fetch one or None or MultipleResultsFound
query.scalar()           # invokes the one() method and return the first column
query[1:3]               # list with limit and offset


# ORM update #####################################################

## batch update will emit the query immediately, return the number of row that
## changed
changed_number = (session.query(User)
                         .filter_by(name='a')
                         .update({user.name: 'b'}, synchronize_session=False))

## update through identity map, emit update query for each instance one by one
assert user in session
user.name = 'another-name'
session.commit()


# ORM insert######################################################
session.add(User(name='name'))                          # add one
session.add_all([User(name='a'), User(name='b')])       # add set


# ORM delete#######################################################
delete_number = session.query(User).filter_by(ID=6).delete()   ## batch delete
session.delete(user)             ## delete one by one





# insert ##########################################################

## default with all columns
ins = user.insert()
            
## limit to several columns
## the values is not rendered into the SQL, but bind with insert.
ins = user.insert().values(name='name', email='email')

## multiple insertion
## each dictionary must have the same set of keys
con.execute(user.insert(), [{'name': 'name1', 'email': 'email1'},
                            {'name': 'name2', 'email': 'email2'}])


# Expression Language select #############################

## select all columns, get all columns as named tuple
s = select([user])

## select several columns
s = select([user.c.name, user.c.email])

## label
s = select([user.c.id.label('user_id')])

## join implicitly
s = select([user, address])

## order
from sqlalchemy import desc

s = select([user]).order_by('id')
s = select([user]).order_by(user.c.id)
s = select([user]).order_by(desc('id'))
s = select([user]).order_by(user.c.id.asc())

## where


# execute and get result for expression language #####################

## select query
result = con.execute(sel)

result.fetchone()
result.fetchall()

for row in result:
    print row
    print row['name'], row['email']
    print row[0], row[1]
    print row[user.c.name], row[user.c.email]



# column operators

## simple
user.c.id == 7                              # equal
user.c.id == address.c.user_id
user.c.id != 7                              # not equal
~(user.c.id == 7)                           # not equal
users.c.id > 7                              # lager than
user.c.name.like('John%')                   # like
user.c.name.between(1,10)                   # between
user.c.name.is_(None)                       # is null
user.c.name.isnot(None)                     # is not null
user.c.id.in_([1,2,3])                      # in
user.c.id.notin_([1,2,3])                   # not in
user.c.id + user.c.id                       # concatenation

## conjunction
((user.c.id==1)
 &(user.c.id==1)                            # and
 &((user.c.id==1)|(user.c.id==1))           # or
 & ~(user.c.id>5)                           # not
)

## conjunction by function
from sqlalchemy import and_, or_, not_

not_(user.c.id == 1)                        # not equal
and_(user.c.id==1, user.c.id==1)            # and
or_(user.c.id==1, user.c.id==1)             # or


# textual SQL ###########################################

## basic
from sqlalchemy.sql import text
s = text(
     "SELECT users.fullname || ', ' || addresses.email_address AS title "
     "FROM users, addresses "
     "WHERE users.id = addresses.user_id "
       "AND users.name BETWEEN :x AND :y "
       "AND (addresses.email_address LIKE :e1 "
             "OR addresses.email_address LIKE :e2)")

con.execute(s, x='m', y='z', e1='%@aol.com', e2='%@msn.com').fetchall()

## bind
text('select ...').bindparams(x='', y='')              # simple
text('select ...').bindparams(bindparam('x', String))  # bind with type



# Implicit Execution #####################################
#     Implicit execution is also connectionless, but it is a very old usage 
# pattern that in most cases is more confusing than it is helpful, and its usage
# is discouraged.

# bind the engine
meta.bind = engine
result = user_table.select().execute()
for row in result:
    print row
    


