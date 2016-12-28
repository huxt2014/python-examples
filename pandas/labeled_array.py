
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
iloc and ix. Unlike Python native slice, slice by label include not only the begin one,
but also the end one.
'''

import numpy as np
import pandas as pd
from pandas import Series, DataFrame, Panel
import matplotlib.pyplot as plt

###############################################################################
#                            Series                                           #
###############################################################################

# construct #######################################
s = Series([1,3,5,np.nan,6,8])            # a Python list, get a default index.
s = Series({'1': 1, '2':2})               # a Python dict, the key become index.
s = Series(np.array([1,2,3,4]))           # a ndarray
s = Series([1,2,3,4], index=['a', 'b', 'c', 'd'])   # specify the index

# native index and slice ##########################
s = Series([1,2,3,4], index=['a', 'b', 'c', 'd'])
s['a'] == s[0]
s['a':] == s[1:]                  #can use either label or offset

# vectorization ###################################
# For arithmetic operation between two series, the element is aligned by label.
# The label will survive in the result
s1 = Series([1,2,3,4], index=['a', 'b', 'c', 'd'])
s2 = Series([2,3,4], index=['a', 'b', 'c'])
s1 + s2         # [3,5,7,NaN]
s1 > 2          # [False, False, True, True]
np.exp(s1)

# introspection ###################################
s.values                   # return 1-d array
s.index                    # return the index
s.name = 'name'
s.index.name = 'name'
s.index = other_index

# plot
s.plot()
plt.show()

# ufunc ############################################
s.map(some_func)             # apply function to each element

# sort #############################################
new_s = s.sort_index()       # sort by index
new_s = s.sort_values()      # sort by values

# rank #############################################
s = Series([4,1,2,5])
s.rank()                     # return [3,1,2,4]

# aggregation and statistic ########################
s.max()
s.unique()


###############################################################################
#                            DataFrame                                        #
#    DateFrame is dict-like. df.keys() get all the column.
#    When construct from dict-like index and columns can be used for reorder and
#select row.
###############################################################################

# construct ########################################

# from tuple list
tuples = [('Bob', 1984), ('John', 1985), ('Marry', 1990)]
df = pd.DataFrame(tuples, columns=['name', 'birth'])

# from dict of list
dict_data = {'name': ['Bob', 'John', 'Marry'],
             'birth': [1984, 1985, 1990]}
df = pd.DataFrame(dict_data)            # default index, default column order
df = pd.DataFrame(dict_data, 
                  columns=['birth', 'name'])           # reorder columns
df = pd.DataFrame(dict_data, 
                  index=['one', 'two', 'three'])       # specify row label

# from dict of dict
dict_data = {'name': {0:'Bob', 1:'John', 2:'Marry'},
             'birth': {0:1984, 1:1985, 2:1990}}
df = pd.DataFrame(dict_data)

# native index and slice ###########################

# index get column, only index by label.
df['name']                   # get a column
df[['name', 'birth']]        # get two columns
df[0]                        # error
df['name':]                  # error

# slice get rows, either offset and label can be used.
df[1:]                       # several rows, by offset
df['2016-11-11 00:00:00': '2016-11-11 08:00:00']       # by label

# introspection ####################################
df.dtypes                         # display dtypes for all columns
df.info()                         # display dtypes and memory size
df.values                         # to ndarray

# vectorization ####################################
# the index and columns of the result is the union of the two origins'. 
df1 + df2
df1.add(df2, fill_value=0)            # fill NaN

# broadcast is similar with Numpy
df1 - s               # broadcast according row
df1.sub(s, axis=0)    # match on axis 0 and broadcast according columns

# ufunc ############################################
np.sqrt(df)                           # apply function to each element
df.apply(some_func, axis=0)           # apply function on each column or row
df.applymap(some_func)                # apply function on each element

# sort #############################################
df.sort_index()                       # sort by index
df.sort_values('col1')                # SQL-like order by

# aggregation and statistic ########################
df.head(5)
df.tail(5)


###############################################################################
#                            index by loc and iloc                            #
#    loc is primarily label based, but may also be used with a boolean array.
#    iloc is primarily integer position based, but may also be used with a
#boolean array.
#    ix supports mixed integer and label based access. It is primarily label
#based, but will fall back to integer positional access unless the corresponding
#axis is of integer type.
#    native index/slice can only be used on single axis. loc, iloc and ix can be
#used on multiple axis.
#    multi-axis selection is similar to Numpy. Indexer can be a single value,
#slice object or list/ndarray.
#    You may access an index on a Series, column on a DataFrame, and an item on
#a Panel directly as an attribute
###############################################################################


# loc style #########################################
df.loc['2016-11-11 00:00:00']           # index get Series
df.loc[['2016-11-11','2016-11-15']]     # index using list, get DataFrame
df.loc['2016-11-11': '2016-11-15']      # slice return several rows as DataFrame


# iloc style #########################################
df.iloc[1]
df.iloc[[1,3]]
df.iloc[1:3]

# ix stype ###########################################
df.ix[1]


# multi-axis selection ###############################
s.loc[indexer]
df.loc[row_indexer, column_indexer]
p.loc[item_indexer, major_indexer, minor_indexer]


###############################################################################
#                               missing data                                  
#     missing data is denoted by NaN(Not a Number) internally. For datetime64
# types, missing value is represented by NaT.
###############################################################################

# checking, get the same shape result ###############
fd['one'].isnull()              # return Series with Boolean element
fd['one'].notnull()
df.isnull()

# drop NaN ##########################################
s.dropna()
df.dropna()                   # drop all rows that contain one or more NaN
df.dropna(how='all')          # drop the rows whose all element are NaN

# set all NA to the same value ######################
df.fillna(value, inplace=True)

# fill method #######################################
df.fillna(method='ffill')  #propagate last valid observation forward to next NA
df.fillna(method='bfill')  #use NEXT valid observation to fill gap


###############################################################################
#                                   Resample
###############################################################################

# down sampling #####################################
dt_index=pd.date_range('2016-11-1 00:02:00', periods=12, freq='1min')
s = Series(np.arange(12), index=dt_index)

s.resample('5min', closed='left').sum()   # 00, 01, 02, 03, 04 as 00
s.resample('5min', closed='right').sum()  # 01, 02, 03, 04, 05 as 00

# group by index function ###########################
s.groupby(lambda x: x.month).sum()

# up sampling #######################################



###############################################################################
#                              other common operator
###############################################################################

# Reindex can be used to insert, remove or reorder rows/columns. If value not   
# exists, NaN is set.
s.reindex(a_list)
df.reindex(row_index, columns=c_index)

# drop row
new_s = s.drop('a')
new_s = s.drop(['a', 'b'])

###############################################################################
#                            iteration                                        #
###############################################################################


#iteration
for col in df.columns:
    series = df[col]
    
    
    