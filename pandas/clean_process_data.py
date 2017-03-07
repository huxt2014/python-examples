

import pandas as pd
import numpy as np

###############################################################################
#                               tidy data
###############################################################################
# missing data ###################################################
df = pd.DataFrame(np.arange(0, 15).reshape(5, 3),
                  index=['a', 'b', 'c', 'd', 'e'],
                  columns=['c1', 'c2', 'c3'])
df['c4'] = np.nan
df.loc['f'] = 1
df.loc['g'] = np.nan
df['c5'] = np.nan

# check
assert isinstance(df.isnull(), pd.DataFrame)
assert df.isnull().sum().sum() > 0

# drop
df.c4.dropna()         # return a new series
df.dropna()            # drop all rows that contain NaN
df.dropna(how='all')   # drop rows that are all NaN
df.dropna(how='all', axis=1)   # drop columns that are all NaN

# fill
df.fillna(0)            # return a new data frame
df.fillna(0, limit=2)   # 0~2 columns
df.fillna(method='ffill')

values = pd.Series(-1, index=['a', 'b', 'c'])
df.c5.fillna(values)     # fill a column

s_missing = pd.Series([1, np.nan, np.nan, np.nan, 2])
s_missing.interpolate()

# duplicate data #################################################
df_dul = pd.DataFrame({'a': ['x'] * 3 + ['y'] * 4,
                      'b': [1, 1, 2, 3, 3, 4, 4]})

assert isinstance(df_dul.duplicated(), pd.Series)
df_dul.drop_duplicates()        # drop all duplicated rows

# transform data #################################################
# mapping, like left join
x = pd.Series({"one": 1, "two": 2, "three": 3})
y_series = pd.Series({1: "a", 2: "b", 3: "c"})
y_dict = {1: "a", 2: "b", 3: "c"}

x.map(y_series)    # join on x's value and y's index, get y's value
x.map(y_dict)      # join on x's value and y's key

# replace
x.replace(1, 10)   # replace all 1 by 10
x.replace([1, 2], [10, 20])
x_frame = pd.DataFrame({'a': [0, 1, 2, 3, 4],
                        'b': [5, 6, 7, 8, 9]})
x_frame.replace({'a': 1, 'b': 8}, 100)

# apply function
x.apply(lambda x: x*x)
x_frame.apply(lambda col: col.sum())   # apply to each column by default
x_frame.applymap(lambda x: x*x)        # apply to each element


###############################################################################
#                           combining and reshaping
###############################################################################

# concatenating ##################################################
# concat on DataFrame is similar to database-style join, but is
# not join. It can be inner or outer, and can be applied to any axis.
x_s = pd.Series(np.arange(0, 3))
y_s = pd.Series(np.arange(5, 8))
pd.concat([x_s, y_s])      # may get duplicate index
pd.concat([x_s, y_s], keys=['x1', 'x2'])  # get hierarchical index

# append is similar to concat
# add rows by append. may get duplicate index
# return a new df, The resulting DataFrame will
# consist of the union of the columns in both
df.append(df)

# Merging ########################################################
# Merge DataFrame objects by performing a database-style join
# operation by columns or indexes.

# Pivoting #######################################################
# pivot retains the same number of levels on an index
'''
origin:
   interval axis reading
0     0      X     0.0
1     0      Y     0.5
2     0      Z     1.0
3     1      X     0.1
4     1      Y     0.4
5     1      Z     0.4

pivoted = df.pivot(index='interval', columns='axis', values='reading')

after pivot:
axis        X    Y    Z
interval
0         0.0  0.5  1.0
1         0.1  0.4  0.4

'''

# Melting#########################################################
# changing a DataFrame object from wide format to long format.
'''
origin:
    Height  Name    Weight
0    6.1    Mike    220
1    6.0    Mikael  185

pd.melt(data, id_vars=['Name'], value_vars=['Height', 'Weight'])

after:
     Name variable  value
0    Mike   Height    6.1
1  Mikael   Height    6.0
2    Mike   Weight  220.0
3  Mikael   Weight  185.0
'''

# Stacking and Unstacking ########################################
# stack and unstack will always increase the levels on the index
# of one of the axes and decrease the levels on the other axis
'''
origin:
     a  b
two  1  3
one  2  4

stacked = df.stack()

after stack:
two  a    1
     b    3
one  a    2
     b    4

stacked.unstack()

after unstack:
     a  b
two  1  3
one  2  4
'''

###############################################################################
#                         split, apply, and combine (SAC)
# The three steps:
#   1. A data set is split into smaller pieces
#   2. Each of these pieces are operated upon independently
#   3. All of the results are combined back together and presented as a single
#      unit
#
#     Splitting in pandas is performed using the groupby() method of a Series
# or DataFrame object. Once the data is split into groups, aggregation,
# transformation and filtration can be applied.
###############################################################################

# group by #######################################################
# get a GroupBy object
grouped = df.groupby('column_name')       # group by column
grouped2 = df.groupby(['col1', 'col2'])   # group by columns
grouped3 = df.groupby(level=0)            # group by index
grouped4 = df.groupby(level=[0, 1])       # group by indexes
grouped5 = df.groupby(lambda x: x)        # group by function

# inspect
assert grouped.ngroups > 0             # the number of groups
isinstance(grouped.groups, dict)       # element's index of each group
isinstance(grouped.size(), pd.Series)  # number of elements
grouped.get_group('column_name')
grouped.get_group(('col1', 'col2'))
grouped.head(3)                        # first 3 rows of each group
grouped.nth(2)                         # the third row of each group
grouped.describe()                     # each group's describe

# apply ##########################################################
grouped.agg(np.mean)
grouped.agg([np.sum, np.std])
grouped.agg({'col1': np.sum, 'col2': np.mean})
grouped.mean()

# transform ######################################################
# apply function to each column of each group. function passed to
# ransform() must return Series with the same number of rows and
# the same index values. Otherwise, the result will often not be
# what was expected.
grouped.transform(lambda x: x+10)

# filter #########################################################
# The function passed to .filter() should return True if the group
# is to be included in the result and False to exclude it.

# discretization #################################################
#  using the pd.cut() and pd.qcut() functions.

###############################################################################
#                           time series data
###############################################################################

# shift ##########################################################
# If freq is specified then the index values are shifted but the
# data is not realigned.
s = pd.Series([1, 2, 2.5, 1.5, 0.5],
              pd.date_range('2017-03-01', periods=5))

# data is moved forward by 1 period, the index remain
# the same.
s.shift(1)

# move data backward
s.shift(-2)

# calculate the percentage daily change
s/s.shift(1)

# move index, the data remain unchanged
s.shift(1, freq='D')     # move one day
s.shift(5, freq='H')     # move 5 hours

# frequency conversion ###########################################
# use asfreq
s2 = pd.Series(np.arange(0, 31*24),
               pd.date_range('2016-03', freq='H', periods=31*24))
daily_s = s2.asfreq('D')
hours_s = daily_s.asfreq('H')

# down/up resample
s3 = pd.Series(np.arange(0, 24),
               pd.date_range('2016-03-01', freq='H', periods=24))

s_30min = s3.resample('30Min').asfreq()
s_30min2 = s3.resample('30Min').ffill()
s_30min3 = s3.resample('30Min').interpolate()
s_2h = s3.resample('2H').sum()

# rolling ########################################################
