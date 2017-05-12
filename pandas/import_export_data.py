

import pandas as pd
from sqlalchemy.sql import select
from sqlalchemy import create_engine

###############################################################################
#                                   CSV
###############################################################################

# by default, the first row will be treated as column
# name, and the index will be RangeIndex.
data = pd.read_csv('path')

# specify column as index
data2 = pd.read_csv('path', index_col=0)
data3 = pd.read_csv('path', index_col=[0, 1])

# specify column name
data4 = pd.read_csv('path', names=['col1', 'col2'])  # all rows are data
data5 = pd.read_csv('path', header=0,                # skip the first row
                    names=['col1', 'col2'])
data6 = pd.read_csv('path', header=[0, 1])    # take the first 2 rows as columns

###############################################################################
#                                 database
###############################################################################
engine = create_engine()
query = select()
conn = engine.connect()

# read through SQLAlchemy, engine is thread-safe
data7 = pd.read_sql(query, engine, index_col=['col1', 'col2'])
data8 = pd.read_sql(query, conn)         # or use connection

# write through SQLAlchemy
data7.to_sql('table_name', engine,
             chunksize=1000, if_exists='append', index=False)
