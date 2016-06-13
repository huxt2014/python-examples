
# basic query ########################################

## select instance
for u in  (Session.query(User)
                  .filter_by(ID=1)                  # where clause
                  .filter(User.ID == 1)             # and
                  .filter(User.ID == 1,             # and
                          User.ID == 1,
                          User.ID == 1)
                  .distinct()                       # distinct
                  .order_by(User.ID)                # order by
                  .all()):
    print u

## select several columns
for id, name in (Session.query(User.ID, 
                               User.NAME.label('MY_NAME'))     # aliases
                        .all()):
    print id, name
    
## select instance and columns
for user, id in (Session.query(User, User.ID)
                        .all()):
    print user, project_id

## get query result
result = (Session.query(User)
                 .all()         # list
              #  .first()         instance or None
              #  .one()           instance or NoResultFound or MultipleResultsFound
              #  .one_or_none()   instance or None or MultipleResultsFound
              #  .scalar()        instance or None
              #  [1:3]            list with limit and offset
              )


## using textual SQL
from sqlalchemy import text

resutl = (Session.query(User)
                 .filter(text("id<10"))
                 .filter(text("id<:value and name=:name")).params(value=10, name='hello')
                 .all()) 



# join  ###############################################

## get one instance without duplicate
for u in (Session.query(User)
                 .join(Project, User.ID==Project.USER_ID)
                 .all()):
    print u

## get two instances
for u, p in (Session.query(User, Project)
                    .filter(User.ID==Project.USER_ID)
                    .all()):
    print u, p

## get several columns
for name, p_name in (Session.query(User.NAME, Project.NAME.label('PROJECT_NAME'))
                            .filter(User.ID==Project.USER_ID)):
    print name, p_name

## left outer Join
for u, project_id in (Session.query(User, Project.ID.label('PROJECT_ID'))
                             .outerjoin(Project, 
                                        and_(User.ID==Project.USER_ID,
                                             User.ID==Project.USER_ID))
                             .all()):
    print u, project_id



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



# aggregation ############################################

from sqlalchemy import func

Session.query(User.ID.
              func.sum(User.SALARY).albel('SALARY'),
              func.count('*').label('TOTAL_NUMBER')
       .group_by(User.ID)
       .all())
      


# other ##################################################

## case clause
from sqlalchemy.sql.expression import case

Session.query(User.ID,
              case([(User.SALARY < 1000, 1),
                    (User.SALARY.between(1000,2000), 2)],
                   else_=0
                   ).label('SALARY')
              .all()
              )








