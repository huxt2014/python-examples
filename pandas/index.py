

from datetime import datetime

import pandas as pd
import numpy as np
from pandas import Series
from pandas.tseries.offsets import Hour, Minute, BusinessDay


'''
    Index is immutable.
    An Index instance can only contain hashable objects
'''

###############################################################################
#                               general index
###############################################################################
# construct ##################################################
index = pd.Index(['a', 'b', 'c', 'd'])

# index can be not unique
s = Series([1, 2, 3, 4, 5], index=['a', 'b', 'b', 'c', 'd'])
assert s.index.is_unique is False
assert s['a'] == 1
assert s['b'] == [2, 3]


###############################################################################
#                               DatetimeIndex
#     Elements in DatetimeIndex are Pandas's Timestamp objects. They are stored
# as Numpy's datatime64[ns]. Timestamp objects are generally interchangeable
# with datetime objects
#     If no time zone passed when constructed, we get a naive datetime index, 
# and the scalar looks like 2016-11-01 00:00:00. If time zone is passed, for 
# example 'UTC', we get a localized datetime index, and the scalar looks like
# 2016-11-01 00:00:00+00:00.
#     A localized datetime index can be convert to another time zone. For
# example, convert a utc time 2016-11-01 00:00:00+00:00 to Asia/Shanghai, we get
# 2016-11-01 08:00:00+08:00. They are the same time.
#     Like any pandas index, DatetimeIndex can be used for various index
# operations, such as data alignment, selection, and slicing.
###############################################################################

# construct ##################################################
# get time stamp
ts = pd.Timestamp('2017-03-06')
ts2 = pd.Timestamp('2017-03-06 17:30')
ts3 = pd.Timestamp('17:30')    # current local date
ts4 = pd.Timestamp('now')
ts5 = pd.Timestamp(datetime(2017, 2, 23, 10, 50, 23))

# get index automatically
dates = ['2017-03-05', '2017-03-06']
s = pd.Series([1, 2], index=pd.to_datetime(dates))

# begin at '2016-11-1 00:00:05',
# no later than '2016-11-30 23:59:59', freq='D'
index1 = pd.date_range('2016-11-1 00:00:05', '2016-11-30 23:59:59')

# begin at '2016-11-1 00:00:05', 20 periods, freq='D'
index2 = pd.date_range('2016-11-1 00:00:05', periods=20)

# normalize to midnight
index3 = pd.date_range('2016-11-1 00:00:05', periods=20, normalize=True)

# attach time zone
index4 = pd.date_range('2016-11-1 00:00:05', periods=20, tz='UTC')

# select #####################################################
index5 = pd.date_range('2014-11-1 00:00:05', '2016-11-30 23:59:59')
s5 = pd.Series(0, index5)

# slice using partial date
assert len(s5['2015']) == 365
assert len(s5['2016-7': '2016-8']) == 62

# date offset ################################################
# frequency strings are translated into an instance of the
# pandas DateOffset object

# '2h30min', every two hours and thirty minutes
offset1 = Hour(2) + Minute(30)

# every day
offset2 = pd.DateOffset(days=1)

# every third Friday of each month
'WOM-3FRI'

# Friday of each week
'W-FRI'

dt = datetime(2017, 3, 3)
dt + offset1              # next 150 minutes
dt + 2*BusinessDay(1)     # next two business days


# shift ######################################################
# from 2016-11-1 to 2016-11-30
index5 = pd.date_range('2016-11-1', '2016-11-30')

# from 2016-11-2 to 2016-12-01
index5.shift(1)

# from 2016-11-1 00:30:00 to 2016-12-01 00:30:00
index5.shift(1, freq='30min')

# deal with timezone #########################################
# By default, pandas objects that are time zone-aware do not
# utilize a timezone object for purposes of efficiency.
native_ts = pd.Timestamp('2017-02-23')
native_index = pd.date_range('2016-11-1', periods=10, freq='H')
assert native_ts.tz is None
assert native_index.tz is None
assert native_index[0].tz is None

# specify time zone
utc_index = pd.date_range('2016-11-1', periods=10, freq='H',
                          tz='UTC')
utc_index2 = native_index.tz_localize('UTC')
shanghai_index = utc_index.tz_convert('Asia/Shanghai')


# Timestamp ##################################################
# 2017-02-24 10:50:00
ts.round('5min')


###############################################################################
#                                PeriodIndex
#     Elements in PeriodIndex are Pandas's Period objects. Period allows you to
# specify durations based on frequencies such as daily, weekly, and it will
# provide a specific start and end Timestamp representing the specific bounded
# interval of time.
###############################################################################

# construct ##################################################
aug2016 = pd.Period('2016-08', freq='M')
sep2016 = aug2016 + 1

mp2016 = pd.period_range('2016-01-01', freq='M', periods=12)

# inspect ####################################################
assert isinstance(aug2016.start_time, pd.Timestamp)
assert isinstance(aug2016.end_time, pd.Timestamp)

# select #####################################################
# select through a Period object or string.
s_2016 = pd.Series(0, mp2016)
assert s_2016['2016-01'] == s_2016[mp2016[0]]
assert len(s_2016['2016-01': '2016-05']) == 5

# partial select is allowed
assert len(s_2016['2016']) == 12

###############################################################################
#                             Hierarchical index
#     It enables you to store and manipulate data with an arbitrary number of
# dimensions in lower dimensional data structures.
###############################################################################

# construct ##################################################
# from tuples, three levels
tuples = [('bar', 'one', 'a'),
          ('bar', 'one', 'b'),
          ('bar', 'two', 'a'),
          ('bar', 'two', 'b'),
          ('foo', 'one', 'a'),
          ('foo', 'one', 'b'),
          ('foo', 'two', 'a'),
          ('foo', 'two', 'b')]
l3_index = pd.MultiIndex.from_tuples(
                tuples, names=['first', 'second', 'third'])

# from product
raw_iter = [['bar', 'foo'], ['one', 'two'], ['a', 'b']]
l3_index2 = pd.MultiIndex.from_product(
                raw_iter, names=['first', 'second', 'third'])

# from dataframe
df = pd.DataFrame(np.random.randn(8), index=l3_index2)
l3_index2 = df.index

# inspect ####################################################
# get normal index
d0 = l3_index.get_level_values(0)   # len=8
d1 = l3_index.get_level_values('second')

# get levels
levels = l3_index.levels        # a list of indexes
assert levels[0] == pd.Index(['bar', 'foo'])


# translate ##################################################
# drop the first level
l2_index = l3_index.droplevel(0)

# drop several level
l1_index = l3_index.droplevel([0, 1])

# distinct
l2_index.unique()

# change levels
l3_index_n = l3_index.set_levels(['foo1', 'bar1'], level=0)
assert l3_index_n.levels[0] == pd.Index(['foo1', 'bar1'])

# select row ##################################################
# get a Series object, whose name is the row's index
assert isinstance(df.iloc[0], pd.Series)

# get several row, with l2_index
df.xs('bar')

# can be chained, or pass a tuple
df.xs('bar').xs('one')
df.xs(('bar', 'one'))

# select level, be careful that the level number may mix with
# the index name
df.xs('one', level=1)


###############################################################################
#                             common method
###############################################################################

# set operation ##############################################
index1.difference(index2)     # index1 - index2
index1.union(index2)
index1.intersection(index2)

# A number of string aliases are given to useful common time series frequencies.
# T, min    minutely frequency
# H         hourly frequency
