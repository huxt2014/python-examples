

import pandas as pd
from pandas import Series

'''
    Index is immutable.
'''

###############################################################################
#                               general index
###############################################################################
# index can be not unique
s = Series([1, 2, 3, 4, 5], index=['a', 'b', 'b', 'c', 'd'])
assert s.index.is_unique is False        # return False
assert s['a'] == 1                       # return 1
assert s['b'] == [2, 3]                  # return [2,3]


###############################################################################
#                               DatetimeIndex
#     Elements in DatetimeIndex are Pandas's Timestamp objects. They are stored
# as Numpy's datatime64[ns]. 
#     If no time zone passed when constructed, we get a naive datetime index, 
# and the scalar looks like 2016-11-01 00:00:00. If time zone is passed, for 
# example 'UTC', we get a localized datetime index, and the scalar looks like
# 2016-11-01 00:00:00+00:00.
#     A localized datetime index can be convert to another time zone. For
# example, convert a utc time 2016-11-01 00:00:00+00:00 to Asia/Shanghai, we get
# 2016-11-01 08:00:00+08:00. They are the same time.
###############################################################################

# construct #########################################

# begin at '2016-11-1 00:00:05',
# no later than '2016-11-30 23:59:59', freq='D'
index1 = pd.date_range('2016-11-1 00:00:05', '2016-11-30 23:59:59')

# begin at '2016-11-1 00:00:05', 20 periods, freq='D'
index2 = pd.date_range('2016-11-1 00:00:05', periods=20)

# normalize to midnight
index3 = pd.date_range('2016-11-1 00:00:05', periods=20, normalize=True)

# attach time zone
index4 = pd.date_range('2016-11-1 00:00:05', periods=20, tz='UTC')


# date offset and its ################################
from pandas.tseries.offsets import Hour, Minute

Hour(2) + Minute(30)
'2h30min'                   # every two hours and thirty minutes

'WOM-3FRI'                  # every third Friday of each month

# shift ##############################################
index = pd.date_range('2016-11-1', 
                      '2016-11-30')   # from 2016-11-1 to 2016-11-30 
index.shift(1)                        # from 2016-11-2 to 2016-12-01
index.shift(1, freq='30min')          # from 2016-11-1 00:30:00 to 2016-12-01 00:30:00

# deal with timezone #################################
naive_index = pd.date_range('2016-11-1', periods=10, freq='H')
utc_index = naive_index.tz_localize('UTC')
shanghai_index = utc_index.tz_convert('Asia/Shanghai')


# Timestamp ###########################################
ts.round('5min')

###############################################################################
#                                PeriodIndex
#     Elements in PeriodIndex are Pandas's Period objects.
###############################################################################


###############################################################################
#                             Hierarchical index
#     It enables you to store and manipulate data with an arbitrary number of
# dimensions in lower dimensional data structures.
###############################################################################

# construct ###################################################################


d0 = index.get_level_values(0)
d1 = index.get_level_values(1)
d1.unique()


###############################################################################
#                             common method
###############################################################################

# set operation ###########################################
index1.difference(index2)     # index1 - index2
index1.union(index2)
index1.intersaction(index2)


# A number of string aliases are given to useful common time series frequencies.
# T, min    minutely frequency
# H         hourly frequency





