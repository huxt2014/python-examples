
# scoped_session ##########################

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

## initial
session_factory = sessionmaker(bind=some_engine)
Session = scoped_session(session_factory)

## only keep one session instance for each thread
session_1 = Session()
session_2 = Session()
session_1 is session_2    # True

## release and recreate session instance
Session.remove()
session_3 = Session()
session_3 is session_1    # False

## as a proxy
Session.query()
Session.add()
Session.commit()

## bind to a request scope
Session = scoped_session(session_factory, copefunc=get_current_request)

