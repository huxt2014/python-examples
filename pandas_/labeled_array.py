
import numpy as np
import pandas as pd
from pandas import Series, DataFrame, Panel
import matplotlib.pyplot as plt

'''
    Pandas has three data structure: Series, DataFrame and Panel. The latter
acts as container for the former. Series has one axis, DataFrame has two axises
and Panel has three axises. They act as 1-d, 2-d and 3-d array.
    For each axis, an index, which is a set of labels, is attached. Indexing by
label is dictionary-like. 
    When using ndarrays to store 2- and 3-dimensional data, axes are considered
more or less equivalent. In pandas, the axes are intended to lend more semantic
meaning to the data. For a particular data set there is likely to be a "right"
way to orient the data.
    Selection, including index and slice, in pandas has four styles: native, loc 
iloc and ix. Unlike Python native slice, slice by label include not only the
left bound, but also the right bound.
'''


###############################################################################
#                                Series
#     A Series always has an index even if one is not specified. In this default
# case, pandas will create an index that consists of sequential integers
# starting from zero. This is by design, for the compatibility with numpy.
#     Automatic alignment is arguably the most significant change that a Series
# makes over ndarray. The pandas library will first align the two pandas objects
# by the index labels and then apply the operation values with aligned labels.
###############################################################################

# construct #################################################
# a Python list, get a default index.
s = Series([1, 3, 5, np.nan, 6, 8])

# a Python dict, the key become index.
s1 = Series({'1': 1, '2': 2})

# a ndarray
s2 = Series(np.array([1, 2, 3, 4]))

# specify the index
s3 = Series([1, 2, 3, 4], index=['a', 'b', 'c', 'd'])

# native index and slice ####################################
# can use either label or offset, but please always use labels
# to avoid misunderstanding.
assert s3['a'] == s3[0]
assert s3['a':] == s3[1:]

# vectorization #############################################
# For arithmetic operation between two series, the element is
# aligned by label. The label will survive in the result
s4 = Series([1, 2, 3, 4], index=['a', 'b', 'c', 'd'])
s5 = Series([2, 3, 4], index=['a', 'b', 'c'])
s4 + s5                   # [3,5,7,NaN]
s4 > 2                    # [False, False, True, True]
np.exp(s4)

# introspection #############################################
# get 1-d array
a = s.values

# get index
i = s.index

# assign name
s.name = 'name'

# length
assert len(s) == s.size == s.shape[0]

# number of element that a not NaN
s.count()

# get a array of unique values
s.unique()

# count(*) group by non-NaN value, get a Series
s.value_counts()

# aggregation and statistic
s.max()
s.mean()
s.var()

# location of the max element
s.idxmax()

# rank
s = Series([4, 1, 2, 5])
s.rank()                     # return [3,1,2,4]

# plot
s.plot()
plt.show()

# translate ##################################################
# sort
new_s1 = s.sort_index()       # sort by index
new_s2 = s.sort_values()      # sort by values

# reindex includes the following steps:
# 1. Reordering existing data to match a set of labels.
# 2. Inserting NaN markers where no data exists for a label.
# 3. Possibly, filling missing data for a label using some type
#    of logic

# in-place modify ############################################

# change index directly, the new index should
# has the same length
s.index = pd.Index(['A', 'B', 'C', 'D'])
s.index = ['a', 'b', 'c', 'd']

# add a new item
s['e'] = 1

# delete a item by label
del(s['e'])

# assign should has the same length
s['c':] = [1, 2]

# assign and broadcast
s['c':] = 3

###############################################################################
#                                DataFrame
#     DateFrame is dict-like. df.keys() get all the column. A DataFrame object
# can be thought of as a dictionary-like container of one or more Series
# objects.
#     When construct from dict-like index and columns can be used for reorder
# and select row.
###############################################################################

# construct ##################################################
# from tuple list
tuples = [('Bob', 1984), ('John', 1985), ('Marry', 1990)]
df = pd.DataFrame(tuples, columns=['name', 'birth'])

# from dict of list
dict_data = {'name': ['Bob', 'John', 'Marry'],
             'birth': [1984, 1985, 1990]}
df1 = pd.DataFrame(dict_data)                   # default index and column order
df2 = pd.DataFrame(dict_data,
                   columns=['birth', 'name'],   # reorder columns
                   index=[0, 1, 2])             # specify row label

# from dict of dict
dict_data = {'name': {0: 'Bob', 1: 'John', 2: 'Marry'},
             'birth': {0: 1984, 1: 1985, 2: 1990}}
df4 = pd.DataFrame(dict_data)

# from dict of series
s3 = Series([1, 2, 3, 4], index=['a', 'b', 'c', 'd'])
s4 = Series([2, 3, 4], index=['a', 'b', 'c'])
df5 = pd.DataFrame({'col1': s3, 'col2': s4})

# native index and slice #####################################
# index get column, index only by label.
s_name = df['name']
df_new = df[['name', 'birth']]
s_0 = df[0]                             # error
df_new2 = df['name':]                   # error

# property like
s_name2 = df.name

# slice get rows, either offset and label can be used.
df_new3 = df[1:]
df_new4 = df['2016-11-11 00:00:00': '2016-11-11 08:00:00']

# introspection ##############################################
# get shape
assert df.shape == (3, 2)

# get index
assert isinstance(df.index, pd.Index)
assert isinstance(df.columns, pd.Index)

# display dtypes for all columns
isinstance(df.dtypes, pd.Series)

# iteration
for col in df.columns:
    series = df[col]

# display dtypes and memory size
df.info()

# to ndarray
array_2d = df.values

# aggregation and statistic
df.head(5)
df.tail(5)
df.describe()

# vectorization ##############################################
# the index and columns of the result is the union of the two origins'. 
df1 + df2
df1.add(df2, fill_value=0)            # fill NaN

# broadcast is similar with Numpy. The set of columns
# returned will be the union of the labels in the index of both
df1 - s               # broadcast according row
df1.sub(s, axis=0)    # match on axis 0 and broadcast according columns

# ufunc
np.sqrt(df)                           # on each element
df.apply(lambda x: x.sum(), axis=0)   # on each column
df.applymap(lambda x: x*x)            # on each element

# in-place modify ############################################
# change columns and index
df.columns = ['birth1', 'name1']
df.index = [10, 20, 30]
df.index = pd.Index([10, 11, 12])

# add column, Items in the Series that do not have a matching
# label will be ignored, just like left join.
new_c = Series([1, 2, 3, 4, 5])
df['new_column'] = new_c
df.insert(1, 'new_column_2', new_c)

# replace column
df['name'] = df.name*2

# drop a column
del(df['new_column'])
df.pop('new_column')

# insert/replace a row
df.loc[100] = ['Marry', 1990]


# translate ##################################################
# Reindex can be used to insert, remove or reorder
# rows/columns. If value not exists, NaN is set.
df = df.reindex([1, 0, 2, 3], columns=['name', 'birth'])

# reset index, abstract values in the index as a column
df.reset_index()

# set index, set a column as index, original index and column
# will disappear.
df.set_index('birth1')

# change index and return a copy
df.rename(index=['birth1', 'name1'])

# drop a column/row, return a new df
df.drop(['new_column'], axis=1)

# sort
df.sort_index()                       # sort by index
df.sort_values('col1')                # SQL-like order by

###############################################################################
#                            Panel
###############################################################################

# panel.axes


###############################################################################
#                            index by loc and iloc                            #
#     loc is primarily label based, but may also be used with a boolean array.
#     iloc is primarily integer position based, but may also be used with a
# boolean array.
#     ix supports mixed integer and label based access. It is primarily label
# based, but will fall back to integer positional access unless the
# corresponding axis is of integer type.
#     native index/slice can only be used on single axis. loc, iloc and ix can
# be used on multiple axis.
#     multi-axis selection is similar to Numpy. Indexer can be a single value,
# slice object or list/ndarray.
#     You may access an index on a Series, column on a DataFrame, and an item on
# a Panel directly as an attribute
###############################################################################


# loc style ##################################################
# get one row as Series
s = df.loc['2016-11-11 00:00:00']

# index using list return several rows as DataFrame
sub_df = df.loc[['2016-11-11', '2016-11-15']]

# slice return several rows as DataFrame
sub_df2 = df.loc['2016-11-11': '2016-11-15']


# iloc style #################################################
s3 = df.iloc[1]                    # one row
sub_df3 = df.iloc[[1, 3]]           # several rows
sub_df4 = df.iloc[1:3]             # several rows

# ix stype ###################################################
s4 = df.ix[1]

# multi-axis selection #######################################
value = df.iloc[0, 0]
s5 = df.iloc[:, 0]
sub_df5 = df.iloc[:, 0:1]
# p.loc[item_indexer, major_indexer, minor_indexer]


###############################################################################
#                               missing data                                  
#     missing data is denoted by NaN(Not a Number) internally. For datetime64
# types, missing value is represented by NaT.
###############################################################################

# checking, get the same shape result ########################
df['one'].isnull()              # return Series with Boolean element
df['one'].notnull()
df.isnull()

# drop NaN ###################################################
s.dropna()
df.dropna()                   # drop all rows that contain one or more NaN
df.dropna(how='all')          # drop the rows whose all element are NaN

# set all #########NA to the same value ######################
df.fillna(value, inplace=True)

# fill method ################################################
df.fillna(method='ffill')  # propagate last valid observation forward to next NA
df.fillna(method='bfill')  # use NEXT valid observation to fill gap


###############################################################################
#                                   Resample
###############################################################################

# down sampling ##############################################
dt_index = pd.date_range('2016-11-1 00:02:00', periods=12, freq='1min')
s = Series(np.arange(12), index=dt_index)

s.resample('5min', closed='left').sum()   # 00, 01, 02, 03, 04 as 00
s.resample('5min', closed='right').sum()  # 01, 02, 03, 04, 05 as 00

# up sampling ################################################
