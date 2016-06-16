
# filter condition in where clause ##########################

## single condition
from sqlalchemy.sql import  not_

User.ID == 1                    # equal
User.ID == Project.USER_ID      # equal
User.ID != 1                    # not equal
~(User.ID == 1)                 # not equal
not_(User.ID == 1)              # not equal
User.ID > 1                     # bigger than
1 < User.ID                     # smaller than
User.NAME.like('John%')         # like
User.ID.between(1,10)           # between
User.NAME.is_(None)             # is null
User.NAME.isnot(None)           # is not null
User.ID.in_([1,2,3])            # in
User.ID.notin_([1,2,3])         # not in

## conjunction
from sqlalchemy.sql import and_, or_, not_

and_(User.ID == 1,              # and
     User.ID == 1,
     or_(User.ID == 1,          # or
         User.ID == 1
         ),
     not_(User.ID > 5)          # not
     )

((User.ID==1)
 &(User.ID==1)                  # and
 &((User.ID==1)|(User.ID==1))   # or
 & ~(User.ID>5)                 # not
)


# column operation ###########################################
User.ID + Project.ID            # concatenation
User.ID.label('UID')            # aliase
User.ID.asc()                   # order by ID asc


# function
from sqlalchemy.sql import func

Session.query(func.now())       # select now()
Session.query(func.any_func())  # select any_func()



