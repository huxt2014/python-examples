

from datetime import datetime

import pandas as pd
import numpy as np
from pandas import Series
from pandas.tseries.offsets import Hour, Minute


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
# as Numpy's datatime64[ns]. 
#     If no time zone passed when constructed, we get a naive datetime index, 
# and the scalar looks like 2016-11-01 00:00:00. If time zone is passed, for 
# example 'UTC', we get a localized datetime index, and the scalar looks like
# 2016-11-01 00:00:00+00:00.
#     A localized datetime index can be convert to another time zone. For
# example, convert a utc time 2016-11-01 00:00:00+00:00 to Asia/Shanghai, we get
# 2016-11-01 08:00:00+08:00. They are the same time.
###############################################################################

# construct ##################################################

# begin at '2016-11-1 00:00:05',
# no later than '2016-11-30 23:59:59', freq='D'
index1 = pd.date_range('2016-11-1 00:00:05', '2016-11-30 23:59:59')

# begin at '2016-11-1 00:00:05', 20 periods, freq='D'
index2 = pd.date_range('2016-11-1 00:00:05', periods=20)

# normalize to midnight
index3 = pd.date_range('2016-11-1 00:00:05', periods=20, normalize=True)

# attach time zone
index4 = pd.date_range('2016-11-1 00:00:05', periods=20, tz='UTC')


# date offset and its ########################################
Hour(2) + Minute(30)
'2h30min'                   # every two hours and thirty minutes

'WOM-3FRI'                  # every third Friday of each month

# shift ######################################################
# from 2016-11-1 to 2016-11-30
index5 = pd.date_range('2016-11-1', '2016-11-30')

# from 2016-11-2 to 2016-12-01
index5.shift(1)

# from 2016-11-1 00:30:00 to 2016-12-01 00:30:00
index5.shift(1, freq='30min')

# deal with timezone #########################################
naive_index = pd.date_range('2016-11-1', periods=10, freq='H')
utc_index = naive_index.tz_localize('UTC')
shanghai_index = utc_index.tz_convert('Asia/Shanghai')


# Timestamp ##################################################
# 2017-02-24 10:50:23
ts = pd.Timestamp(datetime(2017, 2, 23, 10, 50, 23))

# 2017-02-24 10:50:00
ts.round('5min')

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


###############################################################################
#                                PeriodIndex
#     Elements in PeriodIndex are Pandas's Period objects.
###############################################################################

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
