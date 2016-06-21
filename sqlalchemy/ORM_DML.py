

# basic query ########################################
#     The class Query is used for ORM-level SQL construction. It features a  
# generative interface whereby successive calls return a new Query object, a 
# copy of the former with additional criteria and options associated with it.
#     session.query() takes a variable number of arguments, any combination of  
# mapped class, a Mapper object, an orm-enabled descriptor, or an AliasedClass 
# object. And then return the query instance.
#     query.all() and other functions emit the SQL and return result. WHen query 
# more than one entity, the result is expressed as named tuple.

## query
session.query(User)                       # mapped class
session.query(User.id, User.fullname)     # descriptor
session.query(User, User.id)              # combination

## filter
##     The criterion is any SQL expression object applicable to the WHERE clause
## of a select.
query = session.query(User)
query.filter_by(id=1)                  # uses keyword arguments
query.filter(User.id == 1)             # use SQL expression object
query.filter(text("id<10"))            # use textual SQL
(query.filter(text("id<:value and name=:name"))   # bind parameters
      .params(value=10, name='hello'))

## get query result
result = Session.query(User)

result.all()             # fetch all as list
result.first()           # fetch one or None
result.one()             # fetch one or NoResultFound or MultipleResultsFound
result.one_or_none()     # fetch one or None or MultipleResultsFound
result.scalar()          # invokes the one() method and return the first column
result[1:3]              # list with limit and offset
for row in result:       # iterate all
    pass



# join  ###############################################

## join implicitly
(Session.query(User, Project)                     # get two instances
        .filter(User.ID==Project.USER_ID))

(Session.query(User.NAME, Project.NAME)           # get several columns
        .filter(User.ID==Project.USER_ID))

## join explicitly
(Session.query(User)                              # without duplicate
        .join(Project, User.ID==Project.USER_ID))

(Session.query(User, Project.ID)                  # left outer Join
        .outerjoin(Project, 
                   and_(User.ID==Project.USER_ID,
                        User.ID==Project.USER_ID)))
                        


# update ##############################################

## normal update
changed_row_number = (Session.query(User)
                             .filter(User.ID==5)
                             .update({User.NAME: 'John'}))

## update instance
user = Session.query(User).first()
user.NAME = 'John'
Session.add(user)



# insert ###############################################

## add instance
user = User(NAME='John')
Session.add(user)

## add list
users = [User(NAME='John'), User(NAME='Jammy')]
Session.add_all(users)



# delete ################################################

## normal delete
delete_row_number = Session.query(User).filter_by(ID=6).delete()

## delete instance
Session.delete(user)



# other option

## order by
query.order_by(User.id)

## distinct
query.distinct()            

## aggregation
from sqlalchemy import func

(Session.query(User.ID.
              func.sum(User.SALARY).albel('SALARY'),
              func.count('*').label('TOTAL_NUMBER'))
        .group_by(User.ID)
        .all())

## case clause
from sqlalchemy.sql.expression import case

(Session.query(User.ID,
               case([(User.SALARY < 1000, 1),
                     (User.SALARY.between(1000,2000), 2)],
                    else_=0).label('SALARY'))
        .all())

## function
from sqlalchemy.sql import func

Session.query(func.now())       # select now()
Session.query(func.any_func())  # select any_func()







